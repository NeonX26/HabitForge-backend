from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import JournalEntry, User
from app.schemas import JournalOut, JournalUpsert
from app.schemas.serializers import dt_iso, uuid_str

router = APIRouter(prefix="/journal", tags=["journal"])


def _journal_out(e: JournalEntry) -> JournalOut:
    return JournalOut(
        id=uuid_str(e.id),
        date=e.date,
        went_well=e.went_well,
        improve=e.improve,
        win=e.win,
        gratitude=e.gratitude or ["", "", ""],
        created_at=dt_iso(e.created_at) or "",
        updated_at=dt_iso(e.updated_at) or "",
    )


@router.get("/{date}", response_model=JournalOut | None)
def get_journal(date: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = (
        db.query(JournalEntry)
        .filter(JournalEntry.user_id == user.id, JournalEntry.date == date)
        .first()
    )
    return _journal_out(entry) if entry else None


@router.put("/{date}", response_model=JournalOut)
def upsert_journal(
    date: str,
    body: JournalUpsert,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = (
        db.query(JournalEntry)
        .filter(JournalEntry.user_id == user.id, JournalEntry.date == date)
        .first()
    )
    if entry is None:
        entry = JournalEntry(user_id=user.id, date=date)
        db.add(entry)
    entry.went_well = body.went_well
    entry.improve = body.improve
    entry.win = body.win
    entry.gratitude = body.gratitude
    entry.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(entry)
    return _journal_out(entry)
