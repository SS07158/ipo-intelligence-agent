from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from database.models import Base

engine = create_engine(
    settings.database_url,
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit = False
)

def init_db() -> None:
    """
    Create all database tabels.
    """

    Base.metadata.create_all(bind=engine)