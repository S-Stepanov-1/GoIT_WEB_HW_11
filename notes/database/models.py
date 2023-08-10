from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.sqltypes import Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(25), nullable=True, unique=True)
    phone_number = Column(String(20), nullable=False, unique=True)
    birthday = Column(Date, nullable=True)
    position = Column(String(50), nullable=True)
