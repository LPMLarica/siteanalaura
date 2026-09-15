import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.patient_service import create_patient


def seed():

    create_patient(
        {
            "full_name": "Paciente Teste",
            "phone": "(34)99999-9999",
            "email": "paciente@email.com",
        }
    )

    print("Paciente inserido.")


if __name__ == "__main__":
    seed()
