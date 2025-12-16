from typer import Typer

from kanban_cli.categories.controllers.add_controller import add_controller
from kanban_cli.categories.controllers.delete_controller import (
    delete_controller,
)
from kanban_cli.categories.controllers.edit_controller import edit_controller
from kanban_cli.categories.controllers.view_all_controller import (
    view_all_controller,
)


def create_app() -> Typer:
    """Build app to handle categories"""

    app = Typer()

    @app.command()
    def view_all() -> None:
        """List all existing categories in a tabular format"""
        view_all_controller()

    @app.command()
    def add() -> None:
        """Add a new category"""
        add_controller()

    @app.command()
    def edit(category_id: int) -> None:
        """Edit an existing category"""
        edit_controller(category_id)

    @app.command()
    def delete(category_id: int) -> None:
        """Delete a category forever, but only if it has no tasks linked"""
        delete_controller(category_id)

    return app
