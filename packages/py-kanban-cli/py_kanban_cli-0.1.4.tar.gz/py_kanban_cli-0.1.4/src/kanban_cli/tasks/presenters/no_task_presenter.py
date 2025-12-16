from rich.console import Console


class NoTaskPresenter:
    """A helper presenter showing that no task matches a given id"""

    MSG = "No task exists with id #{}."

    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()

    def present(self, task_id: int) -> None:
        self._console.print(self.MSG.format(task_id))
