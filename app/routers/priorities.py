from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import TopPriority, User
from app.schemas import PrioritiesOut, PrioritiesUpsert

router = APIRouter(prefix="/priorities", tags=["priorities"])


@router.get("/{date}", response_model=PrioritiesOut | None)
def get_priorities(date: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(TopPriority).filter(TopPriority.user_id == user.id, TopPriority.date == date).first()
    return PrioritiesOut(date=row.date, items=row.items) if row else None


@router.put("/{date}", response_model=PrioritiesOut)
def upsert_priorities(
    date: str,
    body: PrioritiesUpsert,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.query(TopPriority).filter(TopPriority.user_id == user.id, TopPriority.date == date).first()
    if row is None:
        row = TopPriority(user_id=user.id, date=date, items=body.items)
        db.add(row)
    else:
        row.items = body.items
    db.commit()
    db.refresh(row)
    return PrioritiesOut(date=row.date, items=row.items)
