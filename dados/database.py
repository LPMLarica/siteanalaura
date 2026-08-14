from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config.settings import settings

# Garante que a pasta do banco SQLite exista antes de conectar
if settings.DATABASE_URL.startswith("sqlite"):
    db_path = settings.DATABASE_URL.split("sqlite:///")[-1]
    Path(db_path).resolve().parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=(
        {"check_same_thread": False}
        if settings.DATABASE_URL.startswith("sqlite")
        else {}
    )
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    import dados.models  # noqa: F401  (garante que os modelos sejam registrados)
    Base.metadata.create_all(bind=engine)

    from dados.seed import seed_db
    seed_db()

    print("Banco atualizado com sucesso.")

    return engine

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

    return


