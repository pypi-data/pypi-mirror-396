from prompt_toolkit.shortcuts import choice

YES_PROMPT = "y"
NO_PROMPT = "n"


class ConfirmPrompt:
    def __init__(self, message: str) -> None:
        self._message = message

    def prompt(self) -> bool:
        """Returns `True` if prompt is positive, and `False` otherwise"""
        yes_or_no = [(NO_PROMPT, "No"), (YES_PROMPT, "Yes")]

        option = choice(
            message=self._message,
            options=yes_or_no,
            default=NO_PROMPT,
        )

        return option == YES_PROMPT
