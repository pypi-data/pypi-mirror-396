from kanban_cli.categories.models.category import Category
from kanban_cli.categories.presenters.no_categories_presenter import (
    NoCategoriesPresenter,
)
from kanban_cli.categories.presenters.view_all_presenter import (
    ViewAllPresenter,
)


def view_all_controller() -> None:
    """Query and list all existing categories, if any"""
    # Efficient test if any category exists
    if not Category.select().limit(1).exists():
        NoCategoriesPresenter().present()
        return

    ViewAllPresenter().present(categories=Category.list_categories())
