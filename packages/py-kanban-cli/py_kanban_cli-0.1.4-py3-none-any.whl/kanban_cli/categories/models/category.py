from __future__ import annotations

import peewee as pw

from kanban_cli.config import settings
from kanban_cli.app.models import BaseModel


class Category(BaseModel):
    name = pw.CharField(
        max_length=settings.category__name_max_length,
        constraints=[
            pw.Check(f"length(name) <= {settings.category__name_max_length}")
        ],
        unique=True,
    )

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def category_names() -> list[str]:
        """Convenience method to list all existing category names"""
        return [cat.name for cat in Category.select(Category.name)]

    @staticmethod
    def list_categories() -> list[Category]:
        """Convenience method to return a list of all categories"""
        return list(Category.select())

    def edit_from_prompt(self, category_name: str) -> None:
        """Update current's category name"""
        query = Category.update({Category.name: category_name}).where(
            Category.id == self.id
        )
        query.execute()
