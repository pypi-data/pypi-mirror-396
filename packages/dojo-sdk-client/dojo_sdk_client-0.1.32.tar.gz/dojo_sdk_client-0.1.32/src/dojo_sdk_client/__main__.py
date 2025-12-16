import argparse
import asyncio
import logging
import os

from dojo_sdk_client.agents.seed_cua import SeedCUA

from .agents.seed_cua import ThinkingMode

from .agents.anthropic_cua import AnthropicCUA
from .dojo_eval_client import DojoEvalClient
from .engines import Engine, select_engine
from .utils import load_tasks_from_hf_dataset

API_KEY = os.getenv("DOJO_API_KEY")

logger = logging.getLogger(__name__)


agent = AnthropicCUA(model="claude-4-sonnet-20250514", image_context_length=4, verbose=False)
## agent = ExampleAgent()
# model_name = os.getenv("MODEL_NAME")
# api_key = os.getenv("MODEL_API_KEY")
# model_base_url = os.getenv("MODEL_BASE_URL")
# agent = SeedCUA(
#     model=model_name,
#     api_key=api_key,
#     base_url=model_base_url,
#     image_context_length=3,
#     verbose=True,
#     thinking_mode=ThinkingMode.UNRESTRICTED_THINK,
# )


async def main():
    """Main entry point for the dojo package."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="Dojo Client - Run AI agent evaluations")
    parser.add_argument(
        "--hf-dataset",
        type=str,
        help="HuggingFace dataset name to load tasks from (e.g., 'chakra-labs/dojo-bench-customer-colossus')",
    )
    parser.add_argument("--tasks", nargs="*", help="Specific tasks to run (e.g., 'action-tester/must-click')")

    args = parser.parse_args()

    engine = select_engine(API_KEY)

    if args.hf_dataset:
        print(f"Loading tasks from HuggingFace dataset: {args.hf_dataset}")
        await run_hf_dataset_tasks(args.hf_dataset, args.tasks, engine)
    else:
        print("Evaluating by dojos")
        await by_task_name(args.tasks, engine)


async def run_hf_dataset_tasks(dataset_name: str, specific_tasks: list[str] = None, engine: Engine = None):
    """Run tasks from HuggingFace dataset."""
    client = DojoEvalClient(agent, verbose=False, engine=engine)

    if specific_tasks:
        # Use the specific tasks provided
        task_names = specific_tasks
        logger.info(f"Running {len(task_names)} specific tasks from HF dataset")
    else:
        # Load all tasks from the dataset
        task_names = load_tasks_from_hf_dataset(dataset_name)
        logger.info(f"Running all {len(task_names)} tasks from HF dataset")

    logger.info("Tasks to run:")
    for task_name in task_names:
        logger.info(f"  - {task_name}")

    await client.evaluate(tasks=task_names, num_runners=1)


async def by_task_name(specific_tasks: list[str] = None, engine: Engine = None):
    """Run tasks using the traditional dojo loader."""
    client = DojoEvalClient(agent, verbose=False, engine=engine)

    if specific_tasks:
        task_names = specific_tasks
    else:
        # Default tasks for backward compatibility
        task_names = ["action-tester/must-complete-all-actions", "2048/get-256-tile", "tic-tac-toe/lose-game"]

    logger.info(f"Running {len(task_names)} tasks using traditional dojo loader")

    await client.evaluate(tasks=task_names, num_runners=1)


if __name__ == "__main__":
    asyncio.run(main())
