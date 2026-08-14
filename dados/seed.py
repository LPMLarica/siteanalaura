import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from dados.crud import create_patient


def seed():

    create_patient(

        "Paciente Teste",

        "(34)99999-9999",

        "paciente@email.com"

    )

    print("Paciente inserido.")


if __name__ == "__main__":

    seed()