from database.database import Base
from database.database import engine
import database.database
import database.models


def migrate():

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":

    migrate()

    print("Banco criado com sucesso.")