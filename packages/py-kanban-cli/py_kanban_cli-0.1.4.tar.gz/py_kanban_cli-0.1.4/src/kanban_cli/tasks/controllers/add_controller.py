from kanban_cli.categories.models.category import Category
from kanban_cli.tasks.controllers.view_all_controller import (
    view_all_controller,
)
from kanban_cli.tasks.models.task import Task
from kanban_cli.tasks.prompts.category_prompt import CategoryPrompt
from kanban_cli.tasks.prompts.details_prompt import DetailsPrompt
from kanban_cli.tasks.prompts.priority_prompt import PriorityPrompt
from kanban_cli.tasks.prompts.status_prompt import StatusPrompt
from kanban_cli.tasks.prompts.title_prompt import TitlePrompt


def add_controller() -> None:
    """Run a sequence of prompts to add a new task"""
    title = TitlePrompt().prompt()
    status = StatusPrompt().prompt()
    priority = PriorityPrompt().prompt()
    category_names = Category.category_names()
    category_name = CategoryPrompt(category_names=category_names).prompt()
    details = DetailsPrompt().prompt()

    Task.add_from_prompt(title, status, priority, category_name, details)

    # Print all tasks back
    view_all_controller()
