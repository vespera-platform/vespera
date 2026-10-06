from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from vespera.common.config import get_settings

engine = create_engine(get_settings().database_url.get_secret_value())

SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()