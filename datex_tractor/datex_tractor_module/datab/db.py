from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = "sqlite:///datex_tractor/datex_tractor_module/datab/issues.db"

ngin = create_engine(DB_URL, echo=True)

SessionLocal = sessionmaker(bind=ngin)

Base = declarative_base()
