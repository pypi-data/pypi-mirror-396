import logging

from dojo_sdk_core.tasks import RemoteTaskLoader

logger = logging.getLogger(__name__)


def load_tasks_from_hf_dataset(dataset_name: str) -> list[str]:
    """Load all tasks from HuggingFace dataset and return as dojo_name/task_id format."""
    loader = RemoteTaskLoader(dataset_name)
    all_tasks = loader._get_all_tasks()

    task_list = []
    for task in all_tasks:
        task_path = f"{task.spa}/{task.id}"
        task_list.append(task_path)

    logger.info(f"Loaded {len(task_list)} tasks from HF dataset {dataset_name}")
    return task_list
