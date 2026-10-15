"""
Conexão com o banco de dados (PostgreSQL do Supabase em produção, SQLite
local apenas para desenvolvimento).
"""

from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

from sqlalchemy import create_engine, make_url, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config.settings import settings


class Base(DeclarativeBase):
    pass


@lru_cache(maxsize=1)
def get_engine():

    url = settings.DATABASE_URL

    if url.startswith("sqlite"):
        db_path = url.split("sqlite:///", 1)[-1]

        if db_path and db_path != ":memory:":
            Path(db_path).resolve().parent.mkdir(parents=True, exist_ok=True)

        return create_engine(
            url,
            connect_args={"check_same_thread": False},
        )

    connect_args = {
        "connect_timeout": 10,
        "application_name": "agenda-ana-laura",
    }

    parsed = make_url(url)

    if settings.DATABASE_PASSWORD:
        # O objeto URL do SQLAlchemy cuida do escape; a senha pode ter
        # qualquer caractere.
        parsed = parsed.set(password=settings.DATABASE_PASSWORD)

    # Supabase exige SSL; bancos locais de desenvolvimento normalmente não.
    if "sslmode" not in parsed.query and parsed.host not in ("localhost", "127.0.0.1", None):
        connect_args["sslmode"] = "require"

    return create_engine(
        parsed,
        # O pooler do Supabase encerra conexões ociosas; pre_ping evita
        # erros de "server closed the connection unexpectedly".
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=3,
        max_overflow=2,
        connect_args=connect_args,
    )


@lru_cache(maxsize=1)
def _session_factory():
    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        # Os objetos continuam legíveis depois do commit/fechamento da
        # sessão — as telas usam os dados depois que o serviço retorna.
        expire_on_commit=False,
    )


@contextmanager
def session_scope():
    """Abre uma sessão, faz commit ao final e rollback em caso de erro."""

    session = _session_factory()()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """
    Garante que as tabelas existam. Idempotente: não altera tabelas já
    criadas. No Postgres do Supabase, também garante que o RLS esteja
    ligado, para que a API pública (Data API) não exponha nenhum dado —
    o app acessa o banco diretamente pela connection string.
    """

    import dados.models  # noqa: F401  (registra os modelos)

    engine = get_engine()

    Base.metadata.create_all(bind=engine)

    if engine.dialect.name == "postgresql":
        names = [table.name for table in Base.metadata.sorted_tables]

        with engine.begin() as conn:
            without_rls = conn.execute(
                text(
                    "SELECT c.relname FROM pg_class c "
                    "JOIN pg_namespace n ON n.oid = c.relnamespace "
                    "WHERE n.nspname = 'public' AND c.relkind = 'r' "
                    "AND NOT c.relrowsecurity AND c.relname = ANY(:names)"
                ),
                {"names": names},
            ).scalars().all()

            for name in without_rls:
                conn.execute(
                    text(f'ALTER TABLE public."{name}" ENABLE ROW LEVEL SECURITY')
                )

    return engine


def check_connection():
    """Retorna None se o banco responde, ou a mensagem de erro."""

    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return None
    except Exception as error:  # pragma: no cover - depende de rede
        return str(error).splitlines()[0][:300]
