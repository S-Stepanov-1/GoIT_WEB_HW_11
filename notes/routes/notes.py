from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session

from notes.database.db_connect import get_db
from notes.repository import notes
from notes.schemas import NoteResponse, NoteModel, NoteUpdate

router = APIRouter(prefix='/notes')


@router.get("/", response_model=List[NoteResponse])
async def read_notes(query: str | None = None, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    if query:
        return await notes.search_notes(query, skip, limit, db)
    else:
        return await notes.get_notes(skip, limit, db)


@router.get("/{note_id}", response_model=NoteResponse)
async def read_note(note_id: int, db: Session = Depends(get_db)):
    note = await notes.get_note(note_id, db)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.post("/", response_model=NoteResponse,  status_code=status.HTTP_201_CREATED)
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
