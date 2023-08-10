from typing import List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from notes.database.models import Note  # noqa
from notes.schemas import NoteModel, NoteResponse


async def get_notes(skip: int, limit: int, db: Session) -> List[Note]:
    return db.query(Note).offset(skip).limit(limit).all()


async def create_note(body: NoteModel, db: Session) -> Note:
    note = Note(**body.model_dump())
    db.add(note)
    db.commit()
    return note


async def get_note(note_id: int, db: Session) -> Note:
    note = db.query(Note).filter(Note.id == note_id).first()
    return note


async def delete_note(note_id: int, db: Session):
    note = db.query(Note).filter_by(id=note_id).first()
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    db.delete(note)
    db.commit()
    return f"{note.first_name} {note.last_name} was deleted"
