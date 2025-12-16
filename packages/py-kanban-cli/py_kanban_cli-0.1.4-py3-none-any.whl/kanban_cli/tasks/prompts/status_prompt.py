from prompt_toolkit.shortcuts import choice

from kanban_cli.config import settings


class StatusPrompt:
    """Select among possible status"""

    def __init__(self, default_value: int = 0) -> None:
        self._default_value = default_value

    def prompt(self) -> int:
        options = [(i, status) for i, status in enumerate(settings.statuses)]
        return choice(
            message="Status: ", options=options, default=self._default_value
        )
