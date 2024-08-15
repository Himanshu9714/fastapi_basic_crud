from sqlalchemy.orm import Session
from core.db.session import SessionLocal


def get_database_session():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
