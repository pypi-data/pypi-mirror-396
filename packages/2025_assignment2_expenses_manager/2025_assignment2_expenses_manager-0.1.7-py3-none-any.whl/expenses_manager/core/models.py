from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime


class ExpenseIn(BaseModel):
    user_id: str
    amount: float
    category: str
    description: Optional[str] = ""
    date: date

    @field_validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("L'importo deve essere maggiore di zero")
        return v


class Expense(ExpenseIn):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted: bool = False
