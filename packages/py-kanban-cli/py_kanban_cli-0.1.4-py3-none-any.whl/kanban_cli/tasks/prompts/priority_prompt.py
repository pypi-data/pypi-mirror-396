from prompt_toolkit.shortcuts import choice

from kanban_cli.config import settings


class PriorityPrompt:
    """Select among possible priorities"""

    def __init__(
        self, default_value: int = len(settings.priorities) // 2
    ) -> None:
        self._default_value = default_value

    def prompt(self) -> int:
        options = [(i, status) for i, status in enumerate(settings.priorities)]
        return choice(
            message="Priority: ", options=options, default=self._default_value
        )
