from rich.console import Console
from rich.markup import escape


class CannotDeleteCategoryPresenter:
    """
    Helper class with display message preventing deletion of a category with
    linked tasks
    """

    def __init__(self, console: Console | None = None):
        self._console = console or Console()

    def present(self, category_name: str, linked_task_ids: list[int]) -> None:
        linked_task_ids_str = ", ".join(
            f"#{task_id}" for task_id in linked_task_ids
        )
        category_str = f"[{category_name}]"
        msg = (
            f"Cannot delete category {escape(category_str)}. "
            f"The following task ids depend on it: {linked_task_ids_str}"
        )
        self._console.print(msg)
