from typing import List

from sqlalchemy.orm import Session

from notes.database.models import Note  # noqa
from notes.schemas import NoteModel, NoteResponse


async def get_notes(skip: int, limit: int, db: Session) -> List[Note]:
    return db.query(Note).offset(skip).limit(limit).all()


async def create_note(body: NoteModel, db: Session) -> Note:
    note = Note(**body.model_dump())
    db.add(note)
    db.commit()
    return note
