from typing import List, Type
from datetime import date, timedelta

from fastapi import HTTPException

from sqlalchemy import func
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
        db.refresh(note)

        return note


async def patch_update_note(note_id: int, body: NoteResponse, db: Session) -> Type[Note]:
    note = db.query(Note).filter_by(id=note_id).first()
    if note:
        note.email = body.email or note.email
        note.phone_number = body.phone_number or note.phone_number
        note.position = body.position or note.position

        db.commit()
        return note


async def search_notes(q: str, skip: int, limit: int, db: Session) -> List[Type[Note]]:
    required_notes = db.query(Note).filter(
        func.lower(Note.first_name).like(f"%{q.lower()}%") |
        func.lower(Note.last_name).like(f"%{q.lower()}%") |
        func.lower(Note.email).like(f"%{q.lower()}%")
    ).offset(skip).limit(limit)

    return required_notes.all()


async def get_upcoming_birthdays(days: int, db: Session) -> List[Type[Note]]:
    upcoming_birthdays = []

    today = date.today()
    end_date = today + timedelta(days=days)

    all_notes = db.query(Note).all()
    for note in all_notes:
        if end_date >= note.birthday.replace(year=today.year) > today:  # birthdays in this year
            upcoming_birthdays.append(note)

        if end_date >= note.birthday.replace(year=today.year + 1) > today:  # birthdays in the next year
            upcoming_birthdays.append(note)

    if upcoming_birthdays:
        return upcoming_birthdays
