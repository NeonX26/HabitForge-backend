from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import PomodoroSession, User
from app.schemas import PomodoroCreate, PomodoroOut
from app.schemas.serializers import dt_iso, uuid_str

router = APIRouter(prefix="/pomodoro", tags=["pomodoro"])


def _pomodoro_out(s: PomodoroSession) -> PomodoroOut:
    return PomodoroOut(
        id=uuid_str(s.id),
        date=s.date,
        task_id=uuid_str(s.task_id),
        duration_mins=s.duration_mins,
        type=s.type,
        completed_at=dt_iso(s.completed_at) or "",
    )


@router.get("/sessions", response_model=list[PomodoroOut])
def list_sessions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(PomodoroSession)
        .filter(PomodoroSession.user_id == user.id)
        .order_by(PomodoroSession.completed_at.desc())
        .all()
    )
    return [_pomodoro_out(s) for s in rows]


@router.post("/sessions", response_model=PomodoroOut, status_code=status.HTTP_201_CREATED)
def create_session(body: PomodoroCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    completed = (
        datetime.fromisoformat(body.completed_at.replace("Z", "+00:00"))
        if body.completed_at
        else datetime.now(UTC)
    )
    session = PomodoroSession(
        user_id=user.id,
        date=body.date,
        task_id=UUID(body.task_id) if body.task_id else None,
        duration_mins=body.duration_mins,
        type=body.type,
        completed_at=completed,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return _pomodoro_out(session)
