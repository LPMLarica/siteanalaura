import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database.models import Base
from database.database import engine


def migrate():

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":

    migrate()

    print("Banco criado com sucesso.")