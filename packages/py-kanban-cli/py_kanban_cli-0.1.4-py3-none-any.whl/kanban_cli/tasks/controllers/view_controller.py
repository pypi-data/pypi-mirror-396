from kanban_cli.tasks.models.task import Task
from kanban_cli.tasks.presenters.no_task_presenter import NoTaskPresenter
from kanban_cli.tasks.presenters.view_presenter import ViewPresenter


def view_controller(task_id: int) -> None:
    """Shows a single task with full details"""
    task = Task.get_or_none(Task.id == task_id)
    if not task:
        NoTaskPresenter().present(task_id=task_id)
        return

    ViewPresenter().present(task)
