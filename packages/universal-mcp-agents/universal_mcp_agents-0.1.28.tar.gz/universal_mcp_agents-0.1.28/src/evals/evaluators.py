from openevals.llm import create_llm_as_judge

from evals.prompts import CODEACT_EVALUATOR_PROMPT, CORRECTNESS_PROMPT

correctness_evaluator = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    model="anthropic:claude-4-sonnet-20250514",
)


codeact_evaluator = create_llm_as_judge(
    prompt=CODEACT_EVALUATOR_PROMPT,
    model="anthropic:claude-4-sonnet-20250514",
)
