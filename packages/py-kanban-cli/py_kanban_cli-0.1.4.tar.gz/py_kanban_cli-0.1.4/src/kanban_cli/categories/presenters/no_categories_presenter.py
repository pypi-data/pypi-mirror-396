from rich.console import Console


class NoCategoriesPresenter:
    MSG = "No categories available."

    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()

    def present(self) -> None:
        self._console.print(self.MSG)
