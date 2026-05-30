from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import User, UserSettings, WellnessLog
from app.schemas import WellnessOut, WellnessPatch

router = APIRouter(prefix="/wellness", tags=["wellness"])


def _wellness_out(w: WellnessLog) -> WellnessOut:
    return WellnessOut(
        date=w.date,
        water_glasses=w.water_glasses,
        water_goal=w.water_goal,
        sleep=w.sleep,
        body=w.body,
    )


def _default_wellness(user: User, db: Session, date: str) -> WellnessLog:
    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    goal = settings.water_goal if settings else 8
    return WellnessLog(user_id=user.id, date=date, water_glasses=0, water_goal=goal)


@router.get("/{date}", response_model=WellnessOut)
def get_wellness(date: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    log = db.query(WellnessLog).filter(WellnessLog.user_id == user.id, WellnessLog.date == date).first()
    if log is None:
        log = _default_wellness(user, db, date)
    return _wellness_out(log)


@router.patch("/{date}", response_model=WellnessOut)
def patch_wellness(
    date: str,
    body: WellnessPatch,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    log = db.query(WellnessLog).filter(WellnessLog.user_id == user.id, WellnessLog.date == date).first()
    if log is None:
        log = _default_wellness(user, db, date)
        db.add(log)
    for field, value in body.model_dump(exclude_unset=True, by_alias=False).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return _wellness_out(log)
