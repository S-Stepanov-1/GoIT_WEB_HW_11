from typing import List, Type

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from notes.database.models import Note  # noqa
from notes.schemas import NoteModel, NoteResponse


async def get_notes(skip: int, limit: int, db: Session) -> List[Type[Note]]:
    return db.query(Note).offset(skip).limit(limit).all()


async def create_note(body: NoteModel, db: Session) -> Note:
    note = Note(**body.model_dump())
    db.add(note)
    db.commit()
    return note


async def get_note(note_id: int, db: Session) -> Type[Note] | None:
    note = db.query(Note).filter_by(id=note_id).first()
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


async def put_update_note(note_id: int, body: NoteModel, db: Session) -> Type[Note]:
    note = db.query(Note).filter_by(id=note_id).first()
    if note:
        note.first_name = body.first_name
        note.last_name = body.last_name
        note.email = body.email
        note.phone_number = body.phone_number
        note.birthday = body.birthday
        note.position = body.position

        db.commit()
        return note


async def patch_update_note(note_id: int, body: NoteResponse, db: Session):
    note = db.query(Note).filter_by(id=note_id).first()
    if note:
        note.email = body.email or note.email
        note.phone_number = body.phone_number or note.phone_number
        note.position = body.position or note.position

        db.commit()
        return note
