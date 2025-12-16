from rich.console import Console


class NoCategoryPresenter:
    """A helper presenter showing that no category matches a given id"""

    MSG = "No category exists with id #{}."

    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()

    def present(self, category_id: int) -> None:
        self._console.print(self.MSG.format(category_id))
