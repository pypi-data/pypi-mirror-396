from __future__ import annotations

from typing import TYPE_CHECKING

from pygments.lexers.markup import MarkdownLexer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

if TYPE_CHECKING:
    from kanban_cli.tasks.models.task import Task


class ViewPresenter:
    """Display a single task with full details"""

    EMPTY_DETAILS = "<No details provided>"

    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()

    def present(self, task: Task) -> None:
        table = Table(
            title=f"Task #{task.id}", show_header=False, show_lines=True
        )
        table.add_column(justify="right")
        table.add_column(justify="left")

        table.add_row("Id", str(task.id))
        table.add_row("Title", task.title)
        table.add_row("Status", task.status_str)
        table.add_row("Priority", task.priority_str)
        table.add_row("Category", task.category_name)
        table.add_row("Created at", str(task.created_at_str))
        table.add_row(
            "Details",
            Syntax(
                str(task.details or self.EMPTY_DETAILS),
                lexer=MarkdownLexer(),
                background_color="default",
                theme="solarized-light",
            ),
        )

        self._console.print(table)
