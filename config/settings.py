import os
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()


class Settings:

    APP_NAME = os.getenv(
        "APP_NAME",
    )

    # Connection string do Postgres do seu projeto Supabase (Project
    # Settings -> Database -> Connection string -> URI). Sem essa
    # variável, cai no SQLite local (só para desenvolvimento rápido —
    # não recomendado em produção, já que os dados não persistem entre
    # deploys em muitos ambientes de hospedagem).
    DATABASE_URL = os.getenv("DATABASE_URL")
    connection = psycopg2.connect(DATABASE_URL)

    # URL e chave "anon" do projeto Supabase (Project Settings -> API),
    # usadas apenas para autenticação (login/cadastro) via Supabase
    # Auth. O acesso aos dados (pacientes, consultas etc.) é feito
    # separadamente, via SQLAlchemy, usando DATABASE_URL acima.
    SUPABASE_URL = os.getenv(
        "SUPABASE_URL"
    )
    url = psycopg2.connect(SUPABASE_URL)

    SUPABASE_KEY = os.getenv(
        "SUPABASE_KEY"
    )
    key = psycopg2.connect(SUPABASE_KEY)

    # Sem fallback hardcoded de propósito: uma chave padrão conhecida
    # anularia a criptografia dos prontuários que depende dela.
    # security/encription.py levanta um erro claro na inicialização se
    # isso não estiver definido ou não for uma chave Fernet válida.
    SECRET_KEY = os.getenv(
        "SECRET_KEY"
    )
    

    TIMEZONE = os.getenv(
        "TIMEZONE",
        "America/Sao_Paulo"
    )

    @property
    def supabase_configured(self):

        return bool(
            self.SUPABASE_URL
            and self.SUPABASE_KEY
        )


settings = Settings()
