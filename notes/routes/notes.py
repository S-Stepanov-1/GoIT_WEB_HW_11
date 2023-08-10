from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from notes.database.db_connect import get_db
from notes.repository import notes
from notes.schemas import NoteResponse, NoteModel

router = APIRouter(prefix='/notes')


@router.get("/", response_model=List[NoteResponse])
async def read_notes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return await notes.get_notes(skip, limit, db)


@router.get("/{note_id}", response_model=NoteResponse)
async def read_note(note_id: int, db: Session = Depends(get_db)):
    note = await notes.get_note(note_id, db)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.post("/", response_model=NoteResponse)
async def create_note(body: NoteModel, db: Session = Depends(get_db)):
    return await notes.create_note(body, db)


@router.delete("/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    return await notes.delete_note(note_id, db)
