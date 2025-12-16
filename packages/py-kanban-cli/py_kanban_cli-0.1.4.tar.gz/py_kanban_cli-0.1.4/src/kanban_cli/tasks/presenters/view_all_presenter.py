from __future__ import annotations

from rich.align import Align
from rich.console import Console
from rich.markup import escape
from rich.rule import Rule
from rich.table import Table

from kanban_cli.config import settings
from kanban_cli.tasks.models.task import Task


class ViewAllPresenter:
    """A class to display a summary list of tasks"""

    NO_CATEGORY_STR = "<No category>"
    EMPTY_STR = ""

    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()

    def present(self, tasks_by_status: dict[int, list[Task]]) -> None:
        """Display a table view with all existing tasks

        The tasks are grouped by status, each one in a column.
        The rows should be viewed as follows:

        Status 1 | Status 2 | Status 3
        ==============================
        task 11  | task 12  | task 13
        -------  |          | -------
        task 21  |          | task 23
        -------  |          |
        task 31  |          |

        Notice, for each status column, if a given task has an upcoming task,
        they are separated by rules, otherwise we get an empty string.
        """

        table = Table(expand=True, title="Tasks")
        for status in settings.statuses:
            table.add_column(
                Align(status, align="center"), justify="left", ratio=1
            )

        tasks_rows = self._build_tasks_rows(tasks_by_status)
        rules_rows = self._build_rules_rows(tasks_rows)
        rows = self._build_all_rows(tasks_rows, rules_rows)
        for row in rows:
            table.add_row(*row)

        self._console.print(table)

    def _build_tasks_rows(
        self, tasks_by_status: dict[int, list[Task]]
    ) -> list[list[str]]:
        """Build a table with the tasks in a presentation-like view

        This method groups only the rows with tasks.
        If, for the i-th status, the j-th row has no task, the EMPTY_STR is
        used instead.
        """
        max_num_tasks_in_status = max(
            len(tasks) for tasks in tasks_by_status.values()
        )

        def get_ith_task_or_empty(status_index: int, i: int) -> str:
            tasks = tasks_by_status[status_index]
            if i >= len(tasks):
                return self.EMPTY_STR

            task = tasks[i]
            return self._present_task(task)

        return [
            [
                get_ith_task_or_empty(status_index, i)
                for status_index in Task.iter_status_indices()
            ]  # build each column of a row
            for i in range(max_num_tasks_in_status)
        ]

    def _build_rules_rows(
        self, task_rows: list[list[str]]
    ) -> list[list[str | Rule]]:
        """Build rules rows

        The rules separate one task from its subsequent one. In case a given
        task has no next one, the EMPTY_STR is used instead.
        """

        def get_ith_rule_or_empty(
            task_row: list[str], status_index: int
        ) -> Rule | str:
            if task_row[status_index] == self.EMPTY_STR:
                return self.EMPTY_STR

            return Rule()

        return [
            [
                get_ith_rule_or_empty(next_task_row, status_index)
                for status_index in Task.iter_status_indices()
            ]
            for next_task_row in task_rows[1:]
        ]

    def _build_all_rows(
        self, tasks_rows: list[list[str]], rules_rows: list[list[str | Rule]]
    ) -> list[list[str | Rule]]:
        """Combine the tasks and rules rows into a full table"""
        rows = []
        for task_row, rule_row in zip(tasks_rows, rules_rows):
            rows.append(task_row)
            rows.append(rule_row)

        rows.append(tasks_rows[-1])
        return rows

    def _present_task(self, task: Task) -> str:
        """Display a single task

        Writes a task in the format:

            #<task_id> [<task_priority>] [<task_category>]
            <task_title>
        """
        category_str = f"[{task.category_name}]"
        priority_str = f"[{task.priority_str}]"

        return (
            f"#{task.id} "
            f"[underline]{escape(priority_str)}[/underline] "
            f"[bold]{escape(category_str)}[/bold]\n"
            f"{task.title}"
        )
