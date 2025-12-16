from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime
from sqlalchemy.sql import func
from expenses_manager.core.database import Base


class ExpenseModel(Base):
    """
    SQLAlchemy model for Expense table.
    """
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, index=True, nullable=False)
    description = Column(String, default="")
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted = Column(Boolean, default=False, index=True)

    def __repr__(self):
        return f"<Expense(id={self.id}, user_id={self.user_id}, amount={self.amount}, category={self.category})>"
