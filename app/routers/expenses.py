from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Expense, User
from app.schemas import ExpenseCreate, ExpenseOut
from app.schemas.serializers import dt_iso, uuid_str

router = APIRouter(prefix="/expenses", tags=["expenses"])


def _expense_out(e: Expense) -> ExpenseOut:
    return ExpenseOut(
        id=uuid_str(e.id),
        date=e.date,
        amount=e.amount,
        category=e.category,
        note=e.note,
        created_at=dt_iso(e.created_at) or "",
    )


@router.get("", response_model=list[ExpenseOut])
def list_expenses(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Expense).filter(Expense.user_id == user.id).order_by(Expense.created_at.desc()).all()
    return [_expense_out(e) for e in rows]


@router.post("", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(body: ExpenseCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    expense = Expense(
        user_id=user.id,
        date=body.date,
        amount=body.amount,
        category=body.category,
        note=body.note,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return _expense_out(expense)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user.id).first()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
