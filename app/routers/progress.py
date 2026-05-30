from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import User, UserAchievement, UserProgress
from app.schemas import ProgressOut, ProgressPatch

router = APIRouter(prefix="/me", tags=["me"])


def _progress_out(p: UserProgress) -> ProgressOut:
    return ProgressOut(xp=p.xp, level=p.level, daily_awards=p.daily_awards or {})


def _get_or_create_progress(user: User, db: Session) -> UserProgress:
    progress = db.query(UserProgress).filter(UserProgress.user_id == user.id).first()
    if progress is None:
        progress = UserProgress(user_id=user.id, xp=0, level=1, daily_awards={})
        db.add(progress)
        db.commit()
        db.refresh(progress)
    return progress


@router.get("/progress", response_model=ProgressOut)
def get_progress(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _progress_out(_get_or_create_progress(user, db))


@router.patch("/progress", response_model=ProgressOut)
def patch_progress(
    body: ProgressPatch,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    progress = _get_or_create_progress(user, db)
    if body.xp is not None:
        progress.xp = body.xp
    if body.level is not None:
        progress.level = body.level
    if body.daily_awards is not None:
        progress.daily_awards = body.daily_awards
    db.commit()
    db.refresh(progress)
    return _progress_out(progress)


@router.get("/achievements", response_model=list[str])
def list_achievements(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(UserAchievement).filter(UserAchievement.user_id == user.id).all()
    return [r.achievement_id for r in rows]


@router.post("/achievements/{achievement_id}", status_code=status.HTTP_201_CREATED)
def unlock_achievement(
    achievement_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(UserAchievement)
        .filter(UserAchievement.user_id == user.id, UserAchievement.achievement_id == achievement_id)
        .first()
    )
    if existing:
        return {"achievement_id": achievement_id}
    row = UserAchievement(user_id=user.id, achievement_id=achievement_id)
    db.add(row)
    db.commit()
    return {"achievement_id": achievement_id}
