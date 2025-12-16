import csv
from typing import Optional, List, Tuple
from collections import defaultdict
from sqlalchemy.orm import Session
from expenses_manager.core.models import ExpenseIn, Expense
from expenses_manager.core.repository import ExpenseRepository


class ExpenseService:
    """
    Service layer for expense management business logic.
    """

    def __init__(self, db: Session):
        self.repo = ExpenseRepository(db)

    def add_expense(self, expense_in: ExpenseIn) -> Expense:
        expense = Expense(id=0, **expense_in.model_dump())
        return self.repo.add(expense)

    def get_expense(self, expense_id: int) -> Optional[Expense]:
        return self.repo.get_by_id(expense_id)

    def list_expenses(
        self,
        user_id: Optional[str] = None,
        category: Optional[str] = None,
        date_range: Optional[Tuple[str, str]] = None,
        amount_range: Optional[Tuple[float, float]] = None,
        text_search: Optional[str] = None,
        sort_by: str = "date",
        order: str = "asc",
    ) -> List[Expense]:

        expenses = [e for e in self.repo.get_all() if not e.deleted]

        if user_id:
            expenses = [e for e in expenses if e.user_id == user_id]
        if category:
            expenses = [e for e in expenses if e.category == category]
        if date_range:
            start, end = date_range
            expenses = [e for e in expenses if start <= e.date.isoformat() <= end]
        if amount_range:
            min_amt, max_amt = amount_range
            expenses = [e for e in expenses if min_amt <= e.amount <= max_amt]
        if text_search:
            expenses = [
                e for e in expenses if text_search.lower() in e.description.lower()
            ]

        reverse = order == "desc"
        if sort_by == "date":
            expenses.sort(key=lambda e: e.date, reverse=reverse)
        elif sort_by == "amount":
            expenses.sort(key=lambda e: e.amount, reverse=reverse)

        return expenses

    def update_expense(self, expense_id: int, updated: dict) -> Optional[Expense]:
        return self.repo.update(expense_id, updated)

    def delete_expense(self, expense_id: int) -> bool:
        return self.repo.delete(expense_id)

    def total_by_category(self, user_id: Optional[str] = None) -> dict:
        expenses = self.repo.get_all()
        totals = defaultdict(float)

        for e in expenses:
            if not e.deleted and (user_id is None or e.user_id == user_id):
                totals[e.category] += e.amount

        return dict(totals)

    def monthly_summary(self, user_id: str, year: int, month: int) -> dict:
        expenses = [
            e for e in self.repo.get_all() if not e.deleted and e.user_id == user_id
        ]
        summary = defaultdict(float)
        for e in expenses:
            if e.date.year == year and e.date.month == month:
                summary[e.category] += e.amount
        return dict(summary)

    def export_csv(self, file_path: str, user_id: Optional[str] = None):
        expenses = self.repo.get_all()
        if user_id:
            expenses = [e for e in expenses if e.user_id == user_id and not e.deleted]
        else:
            expenses = [e for e in expenses if not e.deleted]

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "id",
                    "user_id",
                    "amount",
                    "category",
                    "description",
                    "date",
                    "created_at",
                    "updated_at",
                ]
            )
            for e in expenses:
                writer.writerow(
                    [
                        e.id,
                        e.user_id,
                        e.amount,
                        e.category,
                        e.description,
                        e.date.isoformat(),
                        e.created_at.isoformat(),
                        e.updated_at.isoformat(),
                    ]
                )
