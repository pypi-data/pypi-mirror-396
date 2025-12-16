from typing import Optional, List
from datetime import datetime, date
from sqlalchemy.orm import Session
from expenses_manager.core.models import Expense
from expenses_manager.core.db_models import ExpenseModel


class ExpenseRepository:
    """
    Repository for managing Expense entities using SQLAlchemy.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Expense]:
        """
        Retrieve all expenses from the database.
        """
        db_expenses = self.db.query(ExpenseModel).all()
        return [self._to_domain_model(e) for e in db_expenses]

    def get_by_id(self, expense_id: int) -> Optional[Expense]:
        """
        Retrieve a single expense by ID.
        """
        db_expense = self.db.query(ExpenseModel).filter(
            ExpenseModel.id == expense_id,
            ExpenseModel.deleted.is_(False)
        ).first()
        return self._to_domain_model(db_expense) if db_expense else None

    def add(self, expense: Expense) -> Expense:
        """
        Add a new expense to the database.
        """
        db_expense = ExpenseModel(
            user_id=expense.user_id,
            amount=expense.amount,
            category=expense.category,
            description=expense.description,
            date=expense.date,
        )
        self.db.add(db_expense)
        self.db.commit()
        self.db.refresh(db_expense)
        return self._to_domain_model(db_expense)

    def update(self, expense_id: int, updated: dict) -> Optional[Expense]:
        """
        Update an existing expense.
        """
        db_expense = self.db.query(ExpenseModel).filter(
            ExpenseModel.id == expense_id,
            ExpenseModel.deleted.is_(False)
        ).first()

        if not db_expense:
            return None

        # Update fields
        for key, value in updated.items():
            if key in ["date", "created_at", "updated_at"]:
                if isinstance(value, str):
                    if key == "date":
                        value = date.fromisoformat(value)
                    else:
                        value = datetime.fromisoformat(value)
            if hasattr(db_expense, key):
                setattr(db_expense, key, value)

        db_expense.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(db_expense)
        return self._to_domain_model(db_expense)

    def delete(self, expense_id: int) -> bool:
        """
        Soft delete an expense.
        """
        db_expense = self.db.query(ExpenseModel).filter(
            ExpenseModel.id == expense_id,
            ExpenseModel.deleted.is_(False)
        ).first()

        if not db_expense:
            return False

        db_expense.deleted = True
        db_expense.updated_at = datetime.now()
        self.db.commit()
        return True

    @staticmethod
    def _to_domain_model(db_expense: ExpenseModel) -> Expense:
        """
        Convert SQLAlchemy model to Pydantic domain model.
        """
        return Expense(
            id=db_expense.id,
            user_id=db_expense.user_id,
            amount=db_expense.amount,
            category=db_expense.category,
            description=db_expense.description or "",
            date=db_expense.date,
            created_at=db_expense.created_at,
            updated_at=db_expense.updated_at,
            deleted=db_expense.deleted,
        )
