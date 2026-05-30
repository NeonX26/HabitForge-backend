from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Task, User
from app.schemas import TaskCreate, TaskOut, TaskUpdate
from app.schemas.serializers import dt_iso, uuid_str

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _task_out(t: Task) -> TaskOut:
    return TaskOut(
        id=uuid_str(t.id),
        title=t.title,
        category=t.category,
        priority=t.priority,
        notes=t.notes,
        due_date=t.due_date,
        time_block=t.time_block,
        recurring=t.recurring,
        recurring_id=uuid_str(t.recurring_id),
        is_recurring_template=t.is_recurring_template,
        status=t.status,
        created_at=dt_iso(t.created_at) or "",
        completed_at=dt_iso(t.completed_at),
    )


@router.get("", response_model=list[TaskOut])
def list_tasks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.user_id == user.id).order_by(Task.created_at).all()
    return [_task_out(t) for t in tasks]


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(body: TaskCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    recurring_id = UUID(body.recurring_id) if body.recurring_id else None
    task = Task(
        user_id=user.id,
        title=body.title,
        category=body.category,
        priority=body.priority,
        notes=body.notes,
        due_date=body.due_date,
        time_block=body.time_block,
        recurring=body.recurring,
        recurring_id=recurring_id,
        is_recurring_template=body.is_recurring_template,
        status="pending",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_out(task)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return _task_out(task)


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: UUID,
    body: TaskUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    data = body.model_dump(exclude_unset=True, by_alias=False)
    if "recurring_id" in data and data["recurring_id"] is not None:
        data["recurring_id"] = UUID(data["recurring_id"])
    if "completed_at" in data and data["completed_at"] is not None:
        data["completed_at"] = datetime.fromisoformat(data["completed_at"].replace("Z", "+00:00"))
    elif "status" in data and data["status"] == "done" and task.completed_at is None:
        data["completed_at"] = datetime.now(UTC)
    elif "status" in data and data["status"] == "pending":
        data["completed_at"] = None
    for field, value in data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return _task_out(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
