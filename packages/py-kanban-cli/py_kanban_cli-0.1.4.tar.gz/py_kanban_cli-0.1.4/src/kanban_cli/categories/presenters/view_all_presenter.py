from __future__ import annotations

from rich.console import Console
from rich.table import Table

from kanban_cli.categories.models.category import Category


class ViewAllPresenter:
    """A class to display a summary list of categories"""

    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()

    def present(self, categories: list[Category]) -> None:
        """Display a table view with all existing categories"""

        table = Table(expand=True, title="Categories")
        table.add_column("Id", justify="center")
        table.add_column("Name", justify="left")

        for category in categories:
            table.add_row(str(category.id), category.name)

        self._console.print(table)
