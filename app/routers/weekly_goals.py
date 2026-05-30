from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import User, WeeklyGoal
from app.schemas import WeeklyGoalsOut, WeeklyGoalsUpsert

router = APIRouter(prefix="/weekly-goals", tags=["weekly-goals"])


@router.get("/{week_start}", response_model=WeeklyGoalsOut | None)
def get_weekly_goals(
    week_start: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = (
        db.query(WeeklyGoal)
        .filter(WeeklyGoal.user_id == user.id, WeeklyGoal.week_start == week_start)
        .first()
    )
    return WeeklyGoalsOut(week_start=row.week_start, goals=row.goals) if row else None


@router.put("/{week_start}", response_model=WeeklyGoalsOut)
def upsert_weekly_goals(
    week_start: str,
    body: WeeklyGoalsUpsert,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = (
        db.query(WeeklyGoal)
        .filter(WeeklyGoal.user_id == user.id, WeeklyGoal.week_start == week_start)
        .first()
    )
    if row is None:
        row = WeeklyGoal(user_id=user.id, week_start=week_start, goals=body.goals)
        db.add(row)
    else:
        row.goals = body.goals
    db.commit()
    db.refresh(row)
    return WeeklyGoalsOut(week_start=row.week_start, goals=row.goals)
