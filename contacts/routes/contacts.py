from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session

from contacts.database.db_connect import get_db
from contacts.repository import contacts
from contacts.schemas import ContactResponse, ContactModel, ContactUpdate

router = APIRouter(prefix="/contacts")


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(query: str = Query(None, description="Search by name, last name, or email"),
                        skip: int = Query(0, description="Number of records to skip"),
                        limit: int = Query(10, description="Number of records to retrieve"),
                        db: Session = Depends(get_db)):
    if query:
        contact_list = await contacts.search_contacts(query, skip, limit, db)
    else:
        contact_list = await contacts.get_contacts(skip, limit, db)

    if len(contact_list) != 0:
        return contact_list
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contacts were found")


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get("/upcoming_birthdays/", response_model=List[ContactResponse])
async def get_upcoming_birthdays(days: int = Query(7, description="Upcoming birthdays in the next 7 days"),
                                 db: Session = Depends(get_db)):
    upcoming_birthdays = await contacts.get_upcoming_birthdays(days, db)
    if upcoming_birthdays:
        return upcoming_birthdays
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found")


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, db: Session = Depends(get_db)):
    return await contacts.create_contact(body, db)


@router.delete("/{contact_id}")
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await contacts.delete_contact(contact_id, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND"
        )

    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def put_update_contact(body: ContactModel, contact_id: int, db: Session = Depends(get_db)):
    contact = await contacts.put_update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.patch("/{contact_id}", response_model=ContactResponse)
async def patch_update_contact(body: ContactUpdate, contact_id: int, db: Session = Depends(get_db)):
    contact = await contacts.patch_update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
