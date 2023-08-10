from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from notes.database.db_connect import get_db
from notes.database.models import Note
from notes.repository import notes
from notes.schemas import NoteResponse, NoteModel

router = APIRouter(prefix='/notes')


@router.get("/", response_model=List[NoteResponse])
async def read_notes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return await notes.get_notes(skip, limit, db)


@router.post("/", response_model=NoteResponse)
async def create_note(body: NoteModel, db: Session = Depends(get_db)):
    return await notes.create_note(body, db)
