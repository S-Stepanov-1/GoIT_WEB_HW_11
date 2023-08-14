from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session

from notes.database.db_connect import get_db
from notes.repository import notes
from notes.schemas import NoteResponse, NoteModel, NoteUpdate

router = APIRouter(prefix='/notes')


@router.get("/", response_model=List[NoteResponse])
async def read_notes(query: str = Query(None, description="Search by name, last name, or email"),
                     skip: int = Query(0, description="Number of records to skip"),
                     limit: int = Query(10, description="Number of records to retrieve"),
                     db: Session = Depends(get_db)):
    if query:
        note_list = await notes.search_notes(query, skip, limit, db)
    else:
        note_list = await notes.get_notes(skip, limit, db)

    if len(note_list) != 0:
        return note_list
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No notes were found")


@router.get("/{note_id}", response_model=NoteResponse)
async def read_note(note_id: int, db: Session = Depends(get_db)):
    note = await notes.get_note(note_id, db)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.get("/upcoming_birthdays/", response_model=List[NoteResponse])
async def get_upcoming_birthdays(days: int = Query(7, description="Upcoming birthdays in the next 7 days"),
                                 db: Session = Depends(get_db)):

    upcoming_birthdays = await notes.get_upcoming_birthdays(days, db)
    if upcoming_birthdays:
        return upcoming_birthdays
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notes not found")


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(body: NoteModel, db: Session = Depends(get_db)):
    return await notes.create_note(body, db)


@router.delete("/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = await notes.delete_note(note_id, db)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )

    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(body: NoteModel, note_id: int, db: Session = Depends(get_db)):
    note = await notes.put_update_note(note_id, body, db)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_status_note(body: NoteUpdate, note_id: int, db: Session = Depends(get_db)):
    note = await notes.patch_update_note(note_id, body, db)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note
