from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Note, User
from app.schemas import NoteCreate, NoteOut, NoteUpdate
from app.schemas.serializers import dt_iso, uuid_str

router = APIRouter(prefix="/notes", tags=["notes"])


def _note_out(n: Note) -> NoteOut:
    return NoteOut(
        id=uuid_str(n.id),
        title=n.title,
        content=n.content,
        pinned=n.pinned,
        created_at=dt_iso(n.created_at) or "",
        updated_at=dt_iso(n.updated_at) or "",
    )


@router.get("", response_model=list[NoteOut])
def list_notes(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(Note)
        .filter(Note.user_id == user.id)
        .order_by(Note.pinned.desc(), Note.updated_at.desc())
        .all()
    )
    return [_note_out(n) for n in rows]


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(body: NoteCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = Note(user_id=user.id, title=body.title, content=body.content, pinned=body.pinned)
    db.add(note)
    db.commit()
    db.refresh(note)
    return _note_out(note)


@router.patch("/{note_id}", response_model=NoteOut)
def update_note(
    note_id: UUID,
    body: NoteUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    note.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(note)
    return _note_out(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()


@router.post("/{note_id}/pin", response_model=NoteOut)
def toggle_pin(note_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    note.pinned = not note.pinned
    note.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(note)
    return _note_out(note)
