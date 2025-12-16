from kanban_cli.categories.controllers.view_all_controller import (
    view_all_controller,
)
from kanban_cli.categories.models.category import Category
from kanban_cli.categories.presenters.no_category_presenter import (
    NoCategoryPresenter,
)
from kanban_cli.tasks.prompts.category_prompt import CategoryPrompt


def edit_controller(category_id: int) -> None:
    """Allows editing a category"""
    category: Category = Category.get_or_none(Category.id == category_id)
    if not category:
        NoCategoryPresenter().present(category_id=category_id)
        return

    category_names = Category.category_names()
    edited_category_name = CategoryPrompt(
        default_value=category.name, category_names=category_names
    ).prompt()
    category.edit_from_prompt(category_name=edited_category_name)

    # Print all categories back
    view_all_controller()
