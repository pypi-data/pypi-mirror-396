from kanban_cli.categories.controllers.view_all_controller import (
    view_all_controller,
)
from kanban_cli.categories.models.category import Category
from kanban_cli.tasks.prompts.category_prompt import CategoryPrompt


def add_controller() -> None:
    """Run a sequence of prompts to add a new category"""
    category_names = Category.category_names()
    category_name = CategoryPrompt(category_names=category_names).prompt()

    if category_name:
        Category.get_or_create(name=category_name)

    view_all_controller()
