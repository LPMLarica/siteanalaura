from pathlib import Path

import os
import sys

from sqlalchemy import create_engine

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker
)


ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


if ROOT_DIR not in sys.path:

    sys.path.insert(
        0,
        ROOT_DIR
    )


from config.settings import settings


Base = declarative_base()


database_url = settings.DATABASE_URL


if database_url.startswith(
    "sqlite"
):

    db_path = database_url.split(
        "sqlite:///",
        1
    )[-1]

    Path(
        db_path
    ).resolve().parent.mkdir(
        parents=True,
        exist_ok=True
    )


engine = create_engine(

    database_url,

    connect_args=(
        {
            "check_same_thread": False
        }

        if database_url.startswith(
            "sqlite"
        )

        else {}
    )

)


SessionLocal = sessionmaker(

    autocommit=False,

    autoflush=False,

    bind=engine

)


def init_db():

    # Importante:
    # registra todos os modelos no SQLAlchemy
    import dados.models  # noqa: F401

    Base.metadata.create_all(
        bind=engine
    )

    return engine


def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()