from typing import Annotated

from typer import Option, Typer

from kanban_cli.config import settings
from kanban_cli.app.models import db
from kanban_cli.categories.categories_app import (
    create_app as create_categories_app,
)
from kanban_cli.tasks.tasks_app import create_app as create_tasks_app


def create_app() -> Typer:
    """Build a cli kanban app"""

    app = Typer()

    @app.callback()
    def main(
        filename: Annotated[
            str, Option("-f", "--filename", help="File name")
        ] = settings.db_name,
    ) -> None:
        """Simple Kanban management in the command line"""
        # Local import to prevent circular imports
        from kanban_cli.tasks.models import MODELS  # noqa: E402

        db.init(filename)
        db.create_tables(MODELS)

    app.add_typer(create_tasks_app(), name="tasks")
    app.add_typer(create_categories_app(), name="categories")

    return app


def run_app() -> None:
    app = create_app()
    app()
