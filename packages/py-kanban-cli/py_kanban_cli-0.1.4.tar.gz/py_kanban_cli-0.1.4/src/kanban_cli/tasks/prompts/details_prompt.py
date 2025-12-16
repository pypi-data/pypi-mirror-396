from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.shortcuts import prompt as prompt0
from pygments.lexers.markup import MarkdownLexer

from kanban_cli.tasks.prompts.confirm_prompt import ConfirmPrompt

DETAILS_PROMPT_CHAR = "> "


class DetailsPrompt:
    def __init__(
        self, default_value: str = "", is_editing: bool = False
    ) -> None:
        self._default_value = default_value
        self._is_editing = is_editing

    def prompt(self) -> str:
        command = "edit" if self._is_editing else "add"
        should_add_or_edit_details = ConfirmPrompt(
            message=f"Do you want to {command} details? "
        ).prompt()

        if not should_add_or_edit_details:
            return self._default_value

        return prompt0(
            DETAILS_PROMPT_CHAR,
            multiline=True,
            lexer=PygmentsLexer(MarkdownLexer),
            bottom_toolbar=self._bottom_toolbar,
            prompt_continuation=self._prompt_continuation,
            default=self._default_value,
        )

    @staticmethod
    def _bottom_toolbar() -> str:  # pragma: no cover
        return (
            "Write details in markdown style. "
            "Type Alt+Enter or Esc+Enter when done."
        )

    @staticmethod
    def _prompt_continuation(
        width: int, line_number: int, is_soft_wrap: bool
    ) -> str:  # pragma: no cover
        return DETAILS_PROMPT_CHAR
