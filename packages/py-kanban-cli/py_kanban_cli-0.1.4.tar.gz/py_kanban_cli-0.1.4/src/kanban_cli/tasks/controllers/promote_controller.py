from kanban_cli.tasks.controllers.view_all_controller import (
    view_all_controller,
)
from kanban_cli.tasks.models.task import Task


def promote_controller(task_ids: list[int]) -> None:
    """Move up the status of selected todos"""
    Task.promote(task_ids)

    # Print all tasks back
    view_all_controller()
