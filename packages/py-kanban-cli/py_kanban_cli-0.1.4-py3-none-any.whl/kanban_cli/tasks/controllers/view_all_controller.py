from kanban_cli.tasks.models.task import Task
from kanban_cli.tasks.presenters.no_tasks_presenter import NoTasksPresenter
from kanban_cli.tasks.presenters.view_all_presenter import ViewAllPresenter


def view_all_controller() -> None:
    """Query and list all existing tasks, if any"""
    # Efficient test if any task exists
    if Task.select().limit(1).exists() == 0:
        NoTasksPresenter().present()
        return

    tasks_by_status = Task.group_by_status()
    ViewAllPresenter().present(tasks_by_status=tasks_by_status)
