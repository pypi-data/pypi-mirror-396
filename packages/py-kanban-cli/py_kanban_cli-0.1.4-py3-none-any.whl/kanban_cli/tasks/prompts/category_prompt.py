from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import prompt as prompt0


class CategoryPrompt:
    def __init__(
        self, default_value: str = "", category_names: list[str] | None = None
    ) -> None:
        self._default_value = default_value
        self._category_names = category_names or []

    def prompt(self) -> str:
        """Pick a category for a task. It can come from an existing one"""
        return prompt0(
            "Category: ",
            completer=WordCompleter(self._category_names),
            default=self._default_value,
        )
