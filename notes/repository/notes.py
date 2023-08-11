from typing import List, Type

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from notes.database.models import Note  # noqa
from notes.schemas import NoteModel, NoteResponse


async def get_notes(skip: int, limit: int, db: Session) -> List[Type[Note]]:
    return db.query(Note).offset(skip).limit(limit).all()


async def create_note(body: NoteModel, db: Session) -> Note:
    try:
        note = Note(**body.model_dump())
        db.add(note)
        db.commit()
        db.refresh(note)
        return note
    except IntegrityError as err:
        db.rollback()

        if "duplicate key" in str(err):
            duplicate_fields = []
            if db.query(Note).filter_by(email=note.email).first():
                duplicate_fields.append("email")
            if db.query(Note).filter_by(phone_number=note.phone_number).first():
                duplicate_fields.append("phone_number")

            if duplicate_fields:
                raise HTTPException(status_code=409, detail=f"Duplicate fields: {', '.join(duplicate_fields)}")

        raise HTTPException(status_code=409, detail="Data already exist")


async def get_note(note_id: int, db: Session) -> Type[Note] | None:
    note = db.query(Note).filter_by(id=note_id).first()
    return note


async def delete_note(note_id: int, db: Session):
    note = db.query(Note).filter_by(id=note_id).first()
    if note:
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
