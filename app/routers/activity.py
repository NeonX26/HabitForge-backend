from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import ActivityLogEntry, User
from app.schemas import ActivityCreate, ActivityOut
from app.schemas.serializers import dt_iso, uuid_str

router = APIRouter(prefix="/activity", tags=["activity"])


def _activity_out(a: ActivityLogEntry) -> ActivityOut:
    return ActivityOut(
        id=uuid_str(a.id),
        type=a.type,
        message=a.message,
        date=a.date,
        created_at=dt_iso(a.created_at) or "",
    )


@router.get("", response_model=list[ActivityOut])
def list_activity(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(200, le=500),
):
    rows = (
        db.query(ActivityLogEntry)
        .filter(ActivityLogEntry.user_id == user.id)
        .order_by(ActivityLogEntry.created_at.desc())
        .limit(limit)
        .all()
    )
    return [_activity_out(a) for a in rows]


@router.post("", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
def create_activity(body: ActivityCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = ActivityLogEntry(
        user_id=user.id,
        type=body.type,
        message=body.message,
        date=body.date,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _activity_out(entry)
