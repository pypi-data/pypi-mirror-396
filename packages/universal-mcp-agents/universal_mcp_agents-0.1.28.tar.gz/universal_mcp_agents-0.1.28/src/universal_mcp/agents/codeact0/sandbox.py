import ast
import contextlib
import importlib
import inspect
import io
import pickle
import queue
import re
import socket
import threading
import types
from typing import Any

from langchain_core.tools import tool


@tool(parse_docstring=True)
def execute_python_code(brief_explanation: str, snippet: str, display_output_to_user: bool = False) -> str:
    """
    Executes a Python code snippet in a sandbox with retained context (top level defined functions, variables, loaded functions using `load_functions` are retained). Briefly describe (in one line) what you intend to do before each tool call. Do not put this line as a comment inside the snippet, it should be before the tool call.


    **Design Principles**:
    - Write concise code and avoid repeating lines from previous snippets that have already executed.
    - Break logic into multiple small helper functions (with names starting with _, and having max 20 lines each), that each do a single atomic task.
    - ALL functions MUST be declared with `async def`**. Never use `def` for any function. Use `await` when calling async functions.
    - Keep large constants (e.g., multiline strings, dicts, json schemas) global or in a dedicated helper function. Do not declare them inside a function responsible for performing another task.
    - Modify only the relevant helper during debugging—context persists across executions.
    - ALWAYS use smart_print() to examine external function outputs if they are dict/list[dict] before using them, or displaying them to the user.
    - Example:
        async def _get_json_schema():
            return {"key1":"many details"...}
        async def _helper_function_1(...):
            ...

        async def _helper_function_2(...):
            ...
        result1 = await _helper_function_1(..., await _get_json_schema())
        smart_print(result1[:1]) #As an example, to check if it has been processed correctly
        result2 = await _helper_function_2(...)
        smart_print(result2[:1])
        final_result = ...
        smart_print(final_result)
        - Thus, while debugging, if you face an error in result2, you do not need to rewrite _helper_function_1() or _get_json_schema().
    - You have preloaded functions, including a web_search and intelligent language processing and generation functions (llm). Follow the following with respect to LLM functions-
        **CRITICAL INSTRUCTION VIOLATIONS TO CHECK BEFORE EXECUTION:**
        - [ ] Am I using regex/manual parsing/string manipulation for data extraction? -> STOP, use llm__extract_data
        - [ ] Am I hardcoding patterns for text analysis? -> STOP, use llm__classify_data
        - [ ] Am I writing textual/report or any large static text content myself-> STOP, use llm__generate_text

        **MANDATORY Pre-execution Checklist:**
        Before writing ANY code that processes or generates text content:
        1. Is this data extraction? → Use llm__extract_data
        2. Is this classification/comparison? → Use llm__classify_data
        3. Is this text analysis? → Use LLM tools
        4. Is this text generation (e.g. a markdown report, content for a document, HTML report, large multiline strings etc) → use llm__generate_text
        5. Only use manual parsing for: file paths, URLs, structured data formats

    - You can only import libraries that come pre-installed with Python. However, do consider using preloaded functions or searching for external functions first, using the search and load tools to access them in the code.
    - Use loops to process multiple items—test once before scaling.
    - Do not use this tool to think or communicate to the user (through comments or otherwise), except when using this to summarize your work done as the final step with display_output_to_user=True. Communication to the user should be in a normal message right before this tool call, briefly informing them about your plan for the tool call.

    Args:
        brief_explanation (str): A 1-2 line non-technical explanation for the user explaining the snippet (e.g. "Fetching data from the product's website")
        snippet (str): Python code to execute.
        display_output_to_user (bool, default - False): To show the output of a snippet directly to the user. Use this when displaying final results. Only use this when you are sure that the code will execute correctly, and the output will be in Markdown format (i.e. Markdown formatting of titles, sections and no dictionaries, poorly formatted outputs printed). Prefer using existing variables with f-string for displaying details (e.g. links, data).

    Returns:
        Execution result or error as a string.

    Raises:
        ValueError: If snippet is empty.
    """
    # Validate required parameters
    if not snippet or not snippet.strip():
        raise ValueError("Parameter 'snippet' is required and cannot be empty or whitespace")

    # Your actual execution logic would go here
    return f"Successfully executed {len(snippet)} characters of Python code"


class Sandbox:
    def __init__(self, sandbox_timeout=20):
        self.sandbox_timeout = sandbox_timeout
        self.context = {}

    def update_context(self, context: dict):
        self.context.update(context)

    @staticmethod
    def smart_truncate(
        output: str, max_chars_full: int = 2000, max_lines_headtail: int = 20, summary_threshold: int = 10000
    ) -> str:
        """
        Truncates or summarizes output intelligently to avoid filling the context too fast.

        Args:
            output (str): The string output from code execution.
            max_chars_full (int): Max characters to keep full output.
            max_lines_headtail (int): Number of lines to keep from head and tail for medium outputs.
            summary_threshold (int): If truncated output exceeds this, hard-truncate.

        Returns:
            str: Truncated or summarized output.
        """
        if len(output) <= max_chars_full:
            return output  # Small output, include fully

        lines = output.splitlines()
        if len(lines) <= 2 * max_lines_headtail:
            return output  # Medium output, include fully

        # Medium-large output: take head + tail
        head = "\n".join(lines[:max_lines_headtail])
        tail = "\n".join(lines[-max_lines_headtail:])
        truncated = f"{head}\n... [truncated {len(lines) - 2 * max_lines_headtail} lines] ...\n{tail}"

        # If still too big, cut to summary threshold
        if len(truncated) > summary_threshold:
            truncated = truncated[:summary_threshold] + "\n... [output truncated to fit context] ..."

        return truncated

    def _inject_context(
        self, context_dict: dict[str, list[str]], existing_namespace: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Inject Python entities from a dictionary into a namespace.

        This function takes a dictionary where keys represent entity types (imports, classes, functions, etc.)
        and values are lists of entity definitions. It attempts to import or create these entities and returns
        them in a namespace dictionary. Can optionally build upon an existing namespace and apply additional aliases.

        Args:
            context_dict: Dictionary with entity types as keys and lists of entity definitions as values.
                        Supported keys: 'imports', 'classes', 'functions'
                        - 'imports': List of import statements as strings (e.g., ['import pandas', 'import numpy as np'])
                        - 'classes': List of class definitions as strings
                        - 'functions': List of function definitions as strings
            existing_namespace: Optional existing namespace to build upon. If provided, new entities
                            will be added to this namespace rather than creating a new one.

        Returns:
            Dictionary containing the injected entities as key-value pairs

        Example:
            context = {
                'imports': ['import pandas as pd', 'import numpy as np'],
                'classes': ['class MyClass:\n    def __init__(self, x):\n        self.x = x'],
                'functions': ['def my_function(x):\n    return x * 2']
            }
            existing_ns = {'math': <math module>, 'data': [1, 2, 3]}
            namespace = inject_context(context, existing_ns)
            # namespace will contain: {'math': <math module>, 'data': [1, 2, 3], 'pandas': <module>, 'pd': <module>, 'numpy': <module>, 'np': <module>, 'MyClass': <class>, 'MC': <class>, 'my_function': <function>, ...}
        """

        # Start with existing namespace or create new one
        namespace: dict[str, Any] = existing_namespace.copy() if existing_namespace is not None else {}

        # Handle imports (execute import statements as strings)
        if "imports" in context_dict:
            for import_statement in context_dict["imports"]:
                try:
                    # Execute the import statement in the current namespace
                    exec(import_statement, namespace)
                except Exception as e:
                    # If execution fails, try to extract module name and create placeholder

                    # Handle different import patterns
                    import_match = re.search(r"import\s+(\w+)(?:\s+as\s+(\w+))?", import_statement)
                    if import_match:
                        module_name = import_match.group(1)
                        alias_name = import_match.group(2)

                        try:
                            # Try to import the module manually
                            module = importlib.import_module(module_name)
                            namespace[module_name] = module
                            if alias_name:
                                namespace[alias_name] = module
                        except ImportError:
                            # Create placeholders for missing imports
                            namespace[module_name] = f"<import '{module_name}' not available>"
                            if alias_name:
                                namespace[alias_name] = f"<import '{module_name}' as '{alias_name}' not available>"
                    else:
                        # If we can't parse the import statement, create a generic placeholder
                        namespace[f"import_{len(namespace)}"] = f"<import statement failed: {str(e)}>"

        # Handle classes - execute class definitions as strings
        if "classes" in context_dict:
            for class_definition in context_dict["classes"]:
                try:
                    # Execute the class definition in the current namespace
                    exec(class_definition, namespace)
                except Exception:
                    # If execution fails, try to extract class name and create placeholder

                    class_match = re.search(r"class\s+(\w+)", class_definition)
                    if class_match:
                        class_name = class_match.group(1)

                        # Create a placeholder class
                        class PlaceholderClass:
                            def __init__(self, *args, **kwargs):
                                raise NotImplementedError("Class '{class_name}' failed to load")

                        namespace[class_name] = PlaceholderClass
                    else:
                        # If we can't extract class name, create a generic placeholder
                        class GenericPlaceholderClass:
                            def __init__(self, *args, **kwargs):
                                raise NotImplementedError("Class definition failed to load")

                        namespace[f"class_{len(namespace)}"] = GenericPlaceholderClass

        # Handle functions - execute function definitions as strings
        if "functions" in context_dict:
            for function_definition in context_dict["functions"]:
                try:
                    # Execute the function definition in the current namespace
                    exec(function_definition, namespace)
                except Exception:
                    # If execution fails, try to extract function name and create placeholder
                    func_match = re.search(r"(async\s+)?def\s+(\w+)", function_definition)
                    if func_match:
                        func_name = func_match.group(2)
                        is_async = bool(func_match.group(1))

                        if is_async:

                            async def placeholder_func(*args, **kwargs):
                                raise NotImplementedError(f"Async function '{func_name}' failed to load")
                        else:

                            def placeholder_func(*args, **kwargs):
                                raise NotImplementedError(f"Function '{func_name}' failed to load")

                        placeholder_func.__name__ = func_name
                        namespace[func_name] = placeholder_func

        return namespace

    def _derive_context(self, code: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Derive context from code by extracting classes, functions, and import statements.

        Args:
            code: Python code as a string
            context: Existing context dictionary to append to

        Returns:
            Updated context dictionary with extracted entities
        """

        # Initialize context keys if they don't exist
        if "imports" not in context:
            context["imports"] = []
        if "classes" not in context:
            context["classes"] = []
        if "functions" not in context:
            context["functions"] = []

        try:
            # Parse the code into an AST
            tree = ast.parse(code)

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.asname:
                            import_stmt = f"import {alias.name} as {alias.asname}"
                        else:
                            import_stmt = f"import {alias.name}"
                        if import_stmt not in context["imports"]:
                            context["imports"].append(import_stmt)

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    # Handle multiple imports in a single from statement
                    import_names = []
                    for alias in node.names:
                        if alias.asname:
                            import_names.append(f"{alias.name} as {alias.asname}")
                        else:
                            import_names.append(alias.name)

                    import_stmt = f"from {module} import {', '.join(import_names)}"
                    if import_stmt not in context["imports"]:
                        context["imports"].append(import_stmt)

            # Extract class definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Get the class definition as a string
                    class_lines = code.split("\n")[node.lineno - 1 : node.end_lineno]
                    class_def = "\n".join(class_lines)

                    # Clean up the class definition (remove leading/trailing whitespace)
                    class_def = class_def.strip()

                    if class_def not in context["classes"]:
                        context["classes"].append(class_def)

            # Extract function definitions (including async)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_lines = code.split("\n")[node.lineno - 1 : node.end_lineno]
                    func_def = "\n".join(func_lines)

                    # Only top-level functions (col_offset == 0)
                    if node.col_offset == 0:
                        func_def = func_def.strip()
                        if func_def not in context["functions"]:
                            context["functions"].append(func_def)

        except SyntaxError:
            # If the code has syntax errors, try a simpler regex-based approach

            # Extract import statements using regex
            import_patterns = [
                r"import\s+(\w+(?:\.\w+)*)(?:\s+as\s+(\w+))?",
                r"from\s+(\w+(?:\.\w+)*)\s+import\s+(\w+(?:\s+as\s+\w+)?)",
            ]

            for pattern in import_patterns:
                matches = re.finditer(pattern, code)
                for match in matches:
                    if "from" in pattern:
                        module = match.group(1)
                        imports = match.group(2).split(",")
                        for import_name in imports:
                            imp = import_name.strip()
                            if " as " in imp:
                                name, alias = imp.split(" as ")
                                import_stmt = f"from {module} import {name.strip()} as {alias.strip()}"
                            else:
                                import_stmt = f"from {module} import {imp}"
                            if import_stmt not in context["imports"]:
                                context["imports"].append(import_stmt)
                    else:
                        module = match.group(1)
                        alias = match.group(2)
                        if alias:
                            import_stmt = f"import {module} as {alias}"
                        else:
                            import_stmt = f"import {module}"
                        if import_stmt not in context["imports"]:
                            context["imports"].append(import_stmt)

            # Extract class definitions using regex
            class_pattern = r"class\s+(\w+).*?(?=class\s+\w+|def\s+\w+|$)"
            class_matches = re.finditer(class_pattern, code, re.DOTALL)
            for match in class_matches:
                class_def = match.group(0).strip()
                if class_def not in context["classes"]:
                    context["classes"].append(class_def)

            # Extract function definitions using regex
            func_pattern = r"def\s+(\w+).*?(?=class\s+\w+|def\s+\w+|$)"
            func_matches = re.finditer(func_pattern, code, re.DOTALL)
            for match in func_matches:
                func_def = match.group(0).strip()
                if func_def not in context["functions"]:
                    context["functions"].append(func_def)

        return context

    async def eval_unsafe(
        self, code: str, _locals: dict[str, Any], add_context: dict[str, Any]
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Execute code safely with a timeout.
        - Returns (output_str, filtered_locals_dict, new_add_context)
        - Errors or timeout are returned as output_str.
        - Previous variables in _locals persist across calls.
        """

        EXCLUDE_TYPES = (
            types.ModuleType,
            type(re.match("", "")),
            type(re.compile("")),
            type(threading.Lock()),
            type(threading.RLock()),
            threading.Event,
            threading.Condition,
            threading.Semaphore,
            queue.Queue,
            socket.socket,
            io.IOBase,
        )

        result_container = {"output": "<no output>"}

        try:
            compiled_code = compile(code, "<string>", "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
            with contextlib.redirect_stdout(io.StringIO()) as f:
                coroutine = eval(compiled_code, _locals, _locals)
                # Await the coroutine to run the code if it's async
                if coroutine:
                    await coroutine
            result_container["output"] = f.getvalue() or "<code ran, no output printed to stdout>"
        except Exception as e:
            result_container["output"] = f"Error during execution: {type(e).__name__}: {e}"

        # If NameError for provider__tool occurred, append guidance (no retry)
        try:
            m = re.search(r"NameError:\s*name\s*'([^']+)'\s*is\s*not\s*defined", result_container["output"])
            if m and "__" in m.group(1):
                result_container["output"] += "\nHint: If it is a valid tool, load it before running this snippet."
        except Exception:
            pass

        # Filter locals for picklable/storable variables
        all_vars = {}
        for key, value in _locals.items():
            if key.startswith("__"):
                continue
            if inspect.iscoroutine(value) or inspect.iscoroutinefunction(value):
                continue
            if inspect.isasyncgen(value) or inspect.isasyncgenfunction(value):
                continue
            if isinstance(value, EXCLUDE_TYPES):
                continue
            if not callable(value) or not hasattr(value, "__name__"):
                # Only keep if it can be pickled (serialized) successfully
                try:
                    pickle.dumps(value)
                    all_vars[key] = value
                except Exception:
                    pass

        # Safely derive context
        try:
            new_add_context = self._derive_context(code, add_context)
        except Exception:
            new_add_context = add_context

        return result_container["output"], all_vars, new_add_context

    async def handle_execute_python_code(
        self,
        code: str,
        tools_context: dict[str, Any],
        effective_previous_add_context: dict[str, Any],
        effective_existing_context: dict[str, Any],
        display: bool,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """
        Execute a code cell with shared state, supporting both sync and async eval functions.

        Returns (output, new_context, new_add_context).
        """
        context = {**tools_context, **effective_existing_context}
        context = self._inject_context(effective_previous_add_context, context)
        output, new_context, new_add_context = await self.eval_unsafe(code, context, effective_previous_add_context)
        if not display:
            output = self.smart_truncate(output)
        return output, new_context, new_add_context
