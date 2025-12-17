import asyncio


async def execute_python_code(self, brief_explanation: str, code: str, display_output_to_user: bool = False):
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
    output = ""
    try:
        output, new_context, _ = await asyncio.wait_for(
            self.sandbox.eval_unsafe(code, self.sandbox.context, {}),
            timeout=self.sandbox.sandbox_timeout,
        )
        self.sandbox.update_context(new_context)
    except TimeoutError:
        output = f"Code timeout with {self.sandbox.sandbox_timeout}s. Try with smaller snippet"

    return output
