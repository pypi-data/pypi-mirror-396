from typer import Typer

from kanban_cli.tasks.controllers.add_controller import add_controller
from kanban_cli.tasks.controllers.delete_controller import delete_controller
from kanban_cli.tasks.controllers.edit_controller import edit_controller
from kanban_cli.tasks.controllers.promote_controller import promote_controller
from kanban_cli.tasks.controllers.regress_controller import regress_controller
from kanban_cli.tasks.controllers.view_all_controller import (
    view_all_controller,
)
from kanban_cli.tasks.controllers.view_controller import view_controller


def create_app() -> Typer:
    """Build a cli kanban app"""

    app = Typer()

    @app.command()
    def view_all() -> None:
        """List all existing tasks in a tabular format"""
        view_all_controller()

    @app.command()
    def view(task_id: int) -> None:
        """Show a specific task with full details"""
        view_controller(task_id)

    @app.command()
    def add() -> None:
        """Add a new task"""
        add_controller()

    @app.command()
    def edit(task_id: int) -> None:
        """Edit an existing task"""
        edit_controller(task_id)

    @app.command()
    def delete(task_id: int) -> None:
        """Delete a task forever"""
        delete_controller(task_id)

    @app.command()
    def promote(task_ids: list[int]) -> None:
        """Move a list of tasks one status up

        \b
        Tasks at the highest status are kept at this level.
        Also, non-existing tasks are skipped.
        """
        promote_controller(task_ids)

    @app.command()
    def regress(task_ids: list[int]) -> None:
        """Move a list of tasks one status down

        \b
        Tasks at the lowest status are kept at this level.
        Also, non-existing tasks are skipped.
        """
        regress_controller(task_ids)

    return app
