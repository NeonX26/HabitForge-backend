from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.deps import get_current_user, get_db
from app.models import Habit, HabitCompletion, User
from app.schemas import CompletionCreate, CompletionOut, HabitCreate, HabitOut, HabitUpdate
from app.schemas.serializers import dt_iso, uuid_str

router = APIRouter(prefix="/habits", tags=["habits"])


def _habit_out(h: Habit) -> HabitOut:
    return HabitOut(
        id=uuid_str(h.id),
        name=h.name,
        category=h.category,
        icon=h.icon,
        description=h.description,
        reminder_time=h.reminder_time,
        created_at=dt_iso(h.created_at) or "",
    )


@router.get("", response_model=list[HabitOut])
def list_habits(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    habits = db.query(Habit).filter(Habit.user_id == user.id).order_by(Habit.created_at).all()
    return [_habit_out(h) for h in habits]


@router.post("", response_model=HabitOut, status_code=status.HTTP_201_CREATED)
def create_habit(body: HabitCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    habit = Habit(
        user_id=user.id,
        name=body.name,
        category=body.category,
        icon=body.icon,
        description=body.description,
        reminder_time=body.reminder_time,
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return _habit_out(habit)


@router.get("/{habit_id}", response_model=HabitOut)
def get_habit(habit_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return _habit_out(habit)


@router.patch("/{habit_id}", response_model=HabitOut)
def update_habit(
    habit_id: UUID,
    body: HabitUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    for field, value in body.model_dump(exclude_unset=True, by_alias=False).items():
        setattr(habit, field, value)
    db.commit()
    db.refresh(habit)
    return _habit_out(habit)


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(habit_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    db.delete(habit)
    db.commit()


@router.post("/{habit_id}/completions", response_model=CompletionOut, status_code=status.HTTP_201_CREATED)
def add_completion(
    habit_id: UUID,
    body: CompletionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.user_id == user.id).first()
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    existing = (
        db.query(HabitCompletion)
        .filter(HabitCompletion.habit_id == habit_id, HabitCompletion.date == body.date)
        .first()
    )
    if existing:
        return CompletionOut(habit_id=uuid_str(habit_id), date=body.date)
    completion = HabitCompletion(habit_id=habit_id, date=body.date)
    db.add(completion)
    db.commit()
    return CompletionOut(habit_id=uuid_str(habit_id), date=body.date)


@router.delete("/{habit_id}/completions/{date}", status_code=status.HTTP_204_NO_CONTENT)
def delete_completion(
    habit_id: UUID,
    date: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = (
        db.query(Habit)
        .options(joinedload(Habit.completions))
        .filter(Habit.id == habit_id, Habit.user_id == user.id)
        .first()
    )
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    completion = (
        db.query(HabitCompletion)
        .filter(HabitCompletion.habit_id == habit_id, HabitCompletion.date == date)
        .first()
    )
    if completion:
        db.delete(completion)
        db.commit()
