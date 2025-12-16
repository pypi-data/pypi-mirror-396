from kanban_cli.categories.models.category import Category
from kanban_cli.tasks.controllers.view_controller import view_controller
from kanban_cli.tasks.models.task import Task
from kanban_cli.tasks.presenters.no_task_presenter import NoTaskPresenter
from kanban_cli.tasks.prompts.category_prompt import CategoryPrompt
from kanban_cli.tasks.prompts.details_prompt import DetailsPrompt
from kanban_cli.tasks.prompts.priority_prompt import PriorityPrompt
from kanban_cli.tasks.prompts.status_prompt import StatusPrompt
from kanban_cli.tasks.prompts.title_prompt import TitlePrompt


def edit_controller(task_id: int) -> None:
    """Run a sequence of prompts to edit an existing task"""
    task: Task = Task.get_or_none(Task.id == task_id)
    if not task:
        NoTaskPresenter().present(task_id=task_id)
        return

    title = TitlePrompt(default_value=task.title).prompt()
    status = StatusPrompt(default_value=task.status).prompt()
    priority = PriorityPrompt(default_value=task.priority).prompt()
    category_names = Category.category_names()
    category_name = CategoryPrompt(
        default_value=task.category_name, category_names=category_names
    ).prompt()
    details = DetailsPrompt(
        default_value=task.details, is_editing=True
    ).prompt()

    task.edit_from_prompt(
        title=title,
        status=status,
        priority=priority,
        category_name=category_name,
        details=details,
    )

    # Print the updated task in full
    view_controller(task_id=task.id)
