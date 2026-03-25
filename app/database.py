from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Absolute path to project root for stable SQLite file location.
BASE_DIR = Path(__file__).resolve().parent.parent

SQLALCHEMY_DATABASE_URL = f"sqlite:///{BASE_DIR / 'products.db'}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # needed for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

