from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime

import peewee as pw

from kanban_cli.config import settings
from kanban_cli.app.models import BaseModel
from kanban_cli.categories.models.category import Category


class Task(BaseModel):
    NO_CATEGORY_STR = "<No category>"
    STATUS_CHOICES = [(i, val) for i, val in enumerate(settings.statuses)]
    _allowed_statuses = ", ".join(str(i) for i, _ in STATUS_CHOICES)
    PRIORITY_CHOICES = [(i, val) for i, val in enumerate(settings.priorities)]
    _allowed_priorities = ", ".join(str(i) for i, _ in PRIORITY_CHOICES)

    title = pw.CharField(
        max_length=settings.task__title_max_length,
        constraints=[
            pw.Check(f"length(title) <= {settings.task__title_max_length}")
        ],
    )
    status = pw.IntegerField(
        choices=STATUS_CHOICES,
        default=0,  # first status by default
        constraints=[pw.Check(f"status IN ({_allowed_statuses})")],
    )
    priority = pw.IntegerField(
        choices=PRIORITY_CHOICES,
        default=len(PRIORITY_CHOICES) // 2,  # average priority by default
        constraints=[pw.Check(f"priority IN ({_allowed_priorities})")],
    )
    category = pw.ForeignKeyField(Category, backref="tasks", null=True)
    created_at = pw.DateTimeField(default=datetime.now())
    details = pw.TextField(null=True)

    def __str__(self) -> str:
        return (
            f"Title: {self.title}; "
            f"Status: {self.status_str}; "
            f"Priority: {self.priority_str}; "
            f"Category: {self.category}; "
            f"Created at: {self.created_at_str}"
        )

    @property
    def status_str(self) -> str:
        """Human-readable visualization of status"""
        return settings.statuses[self.status]

    @property
    def priority_str(self) -> str:
        """Human-readable visualization of priority"""
        return settings.priorities[self.priority]

    @property
    def created_at_str(self) -> str:
        """Human-readable visualization of creation date"""
        return self.created_at.strftime("%Y-%m-%d %H:%M")

    @property
    def category_name(self) -> str:
        return (
            f"{self.category.name}"
            if self.category
            else f"{self.NO_CATEGORY_STR}"
        )

    @staticmethod
    def iter_status_indices() -> Iterator[int]:
        """Convenient method to iterate over the statuses indices"""
        return (
            status_index for status_index, _ in enumerate(settings.statuses)
        )

    @staticmethod
    def group_by_status() -> dict[int, list[Task]]:
        """
        List all existing tasks by status and sorted by priority (descending)
        and creation date (ascending)
        """
        tasks = (
            Task.select()
            .join(
                Category,
                on=(Task.category == Category.id),
                join_type=pw.JOIN.LEFT_OUTER,
            )
            .order_by(Task.priority.desc(), Task.created_at)
        )

        tasks_by_status = {i: [] for i, _ in enumerate(settings.statuses)}
        for task in tasks:
            tasks_by_status[task.status].append(task)

        return tasks_by_status

    @staticmethod
    def add_from_prompt(
        title: str,
        status: int,
        priority: int,
        category_name: str,
        details: str,
    ) -> Task:
        category, _ = (
            Category.get_or_create(name=category_name)
            if category_name
            else (None, False)
        )
        return Task.create(
            title=title,
            status=status,
            priority=priority,
            category=category,
            details=details,
        )

    def edit_from_prompt(
        self,
        title: str,
        status: int,
        priority: int,
        category_name: str,
        details: str,
    ) -> None:
        category, _ = (
            Category.get_or_create(name=category_name)
            if category_name
            else (None, False)
        )
        query = Task.update(
            {
                Task.title: title,
                Task.status: status,
                Task.priority: priority,
                Task.category: category,
                Task.details: details,
            }
        ).where(Task.id == self.id)
        query.execute()

    @staticmethod
    def promote(task_ids: list[int]) -> None:
        """Move up task status, truncating at the highest one"""
        max_status_level = len(Task.STATUS_CHOICES) - 1

        query = Task.update(
            status=pw.fn.MIN(Task.status + 1, max_status_level)
        ).where(Task.id.in_(task_ids))

        query.execute()

    @staticmethod
    def regress(task_ids: list[int]) -> None:
        """Move down task status, truncating at the lowest one"""
        min_status_level = 0

        query = Task.update(
            status=pw.fn.MAX(Task.status - 1, min_status_level)
        ).where(Task.id.in_(task_ids))

        query.execute()
