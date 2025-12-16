from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from datetime import date
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from expenses_manager.core.service import ExpenseService
from expenses_manager.core.models import Expense, ExpenseIn
from expenses_manager.core.database import get_db, init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    init_db()
    yield


app = FastAPI(title="Expense Manager API", lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Expense Manager API"}


@app.post("/api/expenses", response_model=Expense)
def create_expense(expense: ExpenseIn, db: Session = Depends(get_db)):
    service = ExpenseService(db)
    return service.add_expense(expense)


@app.get("/api/expenses", response_model=List[Expense])
def list_expenses(
    user_id: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    db: Session = Depends(get_db),
):
    date_range = (
        (start_date.isoformat(), end_date.isoformat())
        if start_date and end_date
        else None
    )
    amount_range = (
        (min_amount, max_amount)
        if min_amount is not None and max_amount is not None
        else None
    )

    service = ExpenseService(db)
    return service.list_expenses(
        user_id=user_id,
        category=category,
        date_range=date_range,
        amount_range=amount_range,
    )


@app.get("/api/expenses/{expense_id}", response_model=Expense)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    service = ExpenseService(db)
    expense = service.get_expense(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.put("/api/expenses/{expense_id}", response_model=Expense)
def update_expense(expense_id: int, updated: ExpenseIn, db: Session = Depends(get_db)):
    service = ExpenseService(db)
    expense = service.update_expense(expense_id, updated.model_dump())
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.delete("/api/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    service = ExpenseService(db)
    if not service.delete_expense(expense_id):
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted"}


@app.get("/api/stats/total_by_category")
def total_by_category(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    service = ExpenseService(db)
    return service.total_by_category(user_id)


@app.get("/api/stats/monthly_summary")
def monthly_summary(user_id: str, year: int, month: int, db: Session = Depends(get_db)):
    service = ExpenseService(db)
    return service.monthly_summary(user_id, year, month)


@app.get("/api/export")
def export_expenses(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    service = ExpenseService(db)
    file_path = "expenses_export.csv"
    service.export_csv(file_path, user_id)
    return {"message": f"Expenses exported to {file_path}"}
