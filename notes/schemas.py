from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, PastDate
from pydantic_extra_types.phone_numbers import PhoneNumber


class NoteModel(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr]
    phone_number: PhoneNumber
    birthday: Optional[PastDate]
    position: Optional[str]


class NoteResponse(NoteModel):
    id: int = 1

    class Config:
        from_attributes = True



