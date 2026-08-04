from database.crud import create_patient


def seed():

    create_patient(

        "Paciente Teste",

        "(34)99999-9999",

        "paciente@email.com"

    )

    print("Paciente inserido.")


if __name__ == "__main__":

    seed()