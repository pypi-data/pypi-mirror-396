from kanban_cli.categories.controllers.view_all_controller import (
    view_all_controller,
)
from kanban_cli.categories.models.category import Category
from kanban_cli.categories.presenters.cannot_delete_category_presenter import (
    CannotDeleteCategoryPresenter,
)
from kanban_cli.categories.presenters.no_category_presenter import (
    NoCategoryPresenter,
)
from kanban_cli.tasks.models.task import Task
from kanban_cli.tasks.prompts.confirm_prompt import ConfirmPrompt


def delete_controller(category_id: int) -> None:
    """Delete a category via its id"""
    category: Category = Category.get_or_none(Category.id == category_id)
    if not category:
        NoCategoryPresenter().present(category_id=category_id)
        return

    linked_task_ids = [
        r.id for r in category.tasks.select(Task.id).namedtuples()
    ]
    if len(linked_task_ids) > 0:
        CannotDeleteCategoryPresenter().present(
            category_name=category.name, linked_task_ids=linked_task_ids
        )
        return

    if ConfirmPrompt(
        message=(
            f"Confirm deletion of category #{category.id} [{category.name}]?"
        )
    ).prompt():
        category.delete_instance()

    view_all_controller()
