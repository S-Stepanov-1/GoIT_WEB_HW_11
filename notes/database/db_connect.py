import configparser
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


current_folder = os.path.dirname(os.path.abspath(__file__))
parent_folder = os.path.dirname(current_folder)
base_folder = os.path.dirname(parent_folder)

init_file = os.path.join(base_folder, "config.ini")


config = configparser.ConfigParser()
config.read(init_file)

host = config.get("DB", "host")
port = config.get("DB", "port")
name = config.get("DB", "name")
user = config.get("DB", "user")
password = config.get("DB", "password")


SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
