from typing import List, Type
from datetime import date, timedelta

from fastapi import HTTPException, status

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from contacts.database.models import Contact
from contacts.schemas import ContactModel, ContactResponse


async def get_contacts(skip: int, limit: int, db: Session) -> List[Type[Contact]]:
    return db.query(Contact).offset(skip).limit(limit).all()


async def create_contact(body: ContactModel, db: Session) -> Contact:
    try:
        contact = Contact(**body.model_dump())
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact

    except IntegrityError as err:
        db.rollback()

        if "duplicate key" in str(err):
            duplicate_fields = []
            if db.query(Contact).filter_by(email=contact.email).first():
                duplicate_fields.append("email")
            if db.query(Contact).filter_by(phone_number=contact.phone_number).first():
                duplicate_fields.append("phone_number")

            if duplicate_fields:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Duplicate fields: {', '.join(duplicate_fields)}")

        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Data already exist")


async def get_contact(contact_id: int, db: Session) -> Type[Contact] | None:
    contact = db.query(Contact).filter_by(id=contact_id).first()
    return contact


async def delete_contact(contact_id: int, db: Session):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
        return f"{contact.first_name} {contact.last_name} was deleted"


async def put_update_contact(contact_id: int, body: ContactModel, db: Session) -> Type[Contact]:
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday = body.birthday
        contact.position = body.position

        db.commit()
        db.refresh(contact)

        return contact


async def patch_update_contact(contact_id: int, body: ContactResponse, db: Session) -> Type[Contact]:
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact:
        contact.email = body.email or contact.email
        contact.phone_number = body.phone_number or contact.phone_number
        contact.position = body.position or contact.position

        db.commit()
        return contact


async def search_contacts(q: str, skip: int, limit: int, db: Session) -> List[Type[Contact]]:
    required_contacts = db.query(Contact).filter(
        func.lower(Contact.first_name).like(f"%{q.lower()}%") |
        func.lower(Contact.last_name).like(f"%{q.lower()}%") |
        func.lower(Contact.email).like(f"%{q.lower()}%")
    ).offset(skip).limit(limit)

    return required_contacts.all()


async def get_upcoming_birthdays(days: int, db: Session) -> List[Type[Contact]]:
    upcoming_birthdays = []

    today = date.today()
    end_date = today + timedelta(days=days)

    all_contacts = db.query(Contact).all()
    for contact in all_contacts:
        if end_date >= contact.birthday.replace(year=today.year) > today:  # birthdays in this year
            upcoming_birthdays.append(contact)

        if end_date >= contact.birthday.replace(year=today.year + 1) > today:  # birthdays in the next year
            upcoming_birthdays.append(contact)

    if upcoming_birthdays:
        return upcoming_birthdays
