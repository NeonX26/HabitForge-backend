from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import MoodLog, User
from app.schemas import MoodOut, MoodUpsert

router = APIRouter(prefix="/mood", tags=["mood"])


@router.get("/{date}", response_model=MoodOut | None)
def get_mood(date: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(MoodLog).filter(MoodLog.user_id == user.id, MoodLog.date == date).first()
    return MoodOut(date=row.date, mood=row.mood) if row else None


@router.put("/{date}", response_model=MoodOut)
def upsert_mood(
    date: str,
    body: MoodUpsert,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.query(MoodLog).filter(MoodLog.user_id == user.id, MoodLog.date == date).first()
    if row is None:
        row = MoodLog(user_id=user.id, date=date, mood=body.mood)
        db.add(row)
    else:
        row.mood = body.mood
    db.commit()
    db.refresh(row)
    return MoodOut(date=row.date, mood=row.mood)
