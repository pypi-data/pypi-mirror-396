import asyncio
from datetime import datetime
from enum import Enum
from typing import Annotated, Any

import typer
from langsmith import Client, aevaluate
from langsmith.utils import LangSmithConflictError

from evals.dataset import load_dataset
from evals.evaluators import (
    codeact_evaluator,
    correctness_evaluator,
)
from universal_mcp.agentr.client import AgentrClient
from universal_mcp.agentr.registry import AgentrRegistry
from universal_mcp.agents import get_agent

# 2. Evaluator Registry
EVALUATORS: dict[str, Any] = {
    "correctness": correctness_evaluator,
    "codeact": codeact_evaluator,
}


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


async def agent_runner(inputs: dict) -> dict:
    """
    Runs the agent and returns a dictionary with the final output.
    """
    agent_name = "codeact-repl"
    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client = AgentrClient()
    registry = AgentrRegistry(client=client)
    common_params = {
        "instructions": f"You are a helpful assistant. The current date and time is {current_date_time}",
        "model": "anthropic:claude-haiku-4-5",
        "registry": registry,
        "tools": inputs.get("tools", {}),
    }
    agent = get_agent(agent_name)(name=agent_name, **common_params)
    result = await agent.invoke(user_input=inputs["user_input"])
    # The trajectory evaluator expects the raw output dict, with serialized messages
    # result["messages"] = messages_to_list(result["messages"])
    return result


async def run_evaluation(
    dataset_name: str,
    difficulty_split: str | None = None,
    dataset_version: str | None = None,
    max_concurrency: int = 1,
    description: str | None = None,
):
    """
    The main async function for the evaluation.
    """
    agent_name = "codeact-repl"
    evaluators = [correctness_evaluator]  # TODO: Add codeact_evaluator

    # Create a callable for aevaluate
    async def target_func(inputs: dict):
        return await agent_runner(inputs)

    # 2. Run the evaluation
    client = Client()
    data = dataset_name
    if difficulty_split or dataset_version:
        kwargs = {"dataset_name": dataset_name}
        if difficulty_split:
            kwargs["metadata"] = {"difficulty": difficulty_split}
        if dataset_version:
            kwargs["as_of"] = dataset_version
        data = client.list_examples(**kwargs)

    await aevaluate(
        target_func,
        data=data,
        evaluators=evaluators,
        experiment_prefix=f"{agent_name}-eval",
        max_concurrency=max_concurrency,
        description=description,
    )


def upload_dataset(
    dataset_path: str,
):
    """
    Loads a dataset from a file and uploads it to LangSmith, creating a new version.
    If a dataset with the same name already exists, all previous examples are deleted
    before adding the new ones, ensuring a clean new version.
    """
    dataset_examples = load_dataset(dataset_path)

    client = Client()
    dataset_name = f"{dataset_path.split('/')[-1].split('.')[0]}"

    try:
        dataset = client.create_dataset(
            dataset_name,
            description="Dataset for codeact-repl agent evaluation.",
        )
    except LangSmithConflictError:
        dataset = client.read_dataset(dataset_name=dataset_name)
        # Delete existing examples to create a clean slate for the new version
        example_ids = [example.id for example in client.list_examples(dataset_id=dataset.id)]
        if example_ids:
            client.delete_examples(example_ids=example_ids)

    examples = []
    for ex in dataset_examples:
        metadata = {}
        if "difficulty" in ex:
            difficulty = ex["difficulty"]
            metadata["difficulty_score"] = difficulty
            if difficulty in {1, 2}:
                metadata["difficulty"] = "easy"
            elif difficulty == 3:
                metadata["difficulty"] = "medium"
            elif difficulty in {4, 5}:
                metadata["difficulty"] = "hard"

        examples.append(
            {
                "inputs": {"user_input": ex["user_input"], "tools": ex.get("required_tools", {})},
                "outputs": {
                    "expected_output": ex.get("expected_output", ""),
                    "required_tools": ex.get("required_tools", {}),
                },
                "metadata": metadata,
            }
        )

    client.create_examples(
        dataset_id=dataset.id,
        examples=examples,
    )


app = typer.Typer()


@app.command()
def upload(
    dataset_path: Annotated[
        str,
        typer.Argument(help="Path to the dataset file (e.g., src/evals/datasets/tasks.jsonl)."),
    ],
):
    """
    Uploads a dataset to LangSmith.
    """
    upload_dataset(dataset_path)


@app.command()
def run(
    dataset_name: Annotated[str, typer.Argument(help="The name of the dataset in LangSmith.")],
    difficulty: Annotated[
        Difficulty | None,
        typer.Option(
            help="The difficulty split to use from the dataset.",
            case_sensitive=False,
        ),
    ] = None,
    dataset_version: Annotated[
        str | None,
        typer.Option(
            help="The dataset version to use (e.g., 'latest', a timestamp, or a tag).",
        ),
    ] = None,
    concurrency: Annotated[
        int,
        typer.Option(
            help="The number of concurrent runs to execute.",
        ),
    ] = 5,
    description: Annotated[
        str | None,
        typer.Option(
            help="A description for the evaluation experiment.",
        ),
    ] = None,
):
    """
    Run evaluations on the codeact-repl agent.
    """
    difficulty_value = difficulty.value if difficulty else None
    asyncio.run(
        run_evaluation(
            dataset_name=dataset_name,
            difficulty_split=difficulty_value,
            dataset_version=dataset_version,
            max_concurrency=concurrency,
            description=description,
        )
    )


if __name__ == "__main__":
    app()
