from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.validation import ValidationError, Validator

from kanban_cli.config import settings

if TYPE_CHECKING:
    from prompt_toolkit.document import Document


class TitlePrompt:
    def __init__(self, default_value: str = "") -> None:
        self._default_value = default_value

    def prompt(self) -> str:
        """Pick task title from user"""
        return prompt(
            "Title: ",
            validator=TitleValidator(),
            validate_while_typing=False,
            default=self._default_value,
        )


class TitleValidator(Validator):
    def validate(self, document: Document) -> None:
        """Ensure the title is not empty and not larger than the max allowed"""
        text = document.text

        if not text:
            raise ValidationError(
                message="Title is required", cursor_position=0
            )

        if len(text) > settings.task__title_max_length:
            raise ValidationError(
                message=(
                    "Title cannot be larger than "
                    f"{settings.task__title_max_length} characters"
                ),
                cursor_position=settings.task__title_max_length,
            )
