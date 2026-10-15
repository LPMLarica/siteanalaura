"""
Conexão com o banco de dados (PostgreSQL do Supabase em produção, SQLite
local apenas para desenvolvimento).
"""

import logging
import re
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

from sqlalchemy import create_engine, make_url, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config.settings import settings


logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


_DIRECT_HOST = re.compile(r"db\.([a-z0-9]{20})\.supabase\.co")
_POOLER_SUFFIX = ".pooler.supabase.com"


def _project_ref():
    match = re.search(r"https://([a-z0-9]{20})\.supabase\.co", settings.SUPABASE_URL or "")
    return match.group(1) if match else None


def candidate_urls(parsed):
    """
    Endereços a tentar, em ordem.

    A conexão direta do Supabase (db.<ref>.supabase.co) só existe em IPv6
    no plano gratuito, e o Streamlit Cloud só tem IPv4. Quando a URL é a
    direta, tentamos antes o pooler (IPv4) da região do projeto. Também
    corrigimos o usuário do pooler, que precisa ser "postgres.<ref>".
    """

    host = parsed.host or ""
    direct = _DIRECT_HOST.fullmatch(host)

    if direct:
        ref = direct.group(1)
        user = parsed.username or "postgres"

        if "." not in user:
            user = f"{user}.{ref}"

        pooled = [
            parsed.set(
                host=f"aws-{n}-{settings.SUPABASE_REGION}{_POOLER_SUFFIX}",
                port=5432,
                username=user,
            )
            for n in (0, 1)
        ]
        return pooled + [parsed]

    if host.endswith(_POOLER_SUFFIX) and "." not in (parsed.username or ""):
        ref = _project_ref()

        if ref:
            return [parsed.set(username=f"{parsed.username or 'postgres'}.{ref}")]

    return [parsed]


def _engine_for(url):
    connect_args = {
        "connect_timeout": 8,
        "application_name": "agenda-ana-laura",
    }

    # Supabase exige SSL; bancos locais de desenvolvimento normalmente não.
    if "sslmode" not in url.query and url.host not in ("localhost", "127.0.0.1", None):
        connect_args["sslmode"] = "require"

    return create_engine(
        url,
        # O pooler do Supabase encerra conexões ociosas; pre_ping evita
        # erros de "server closed the connection unexpectedly".
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=3,
        max_overflow=2,
        connect_args=connect_args,
    )


def _error_weight(message):
    message = message.lower()

    if "password authentication failed" in message:
        return 3  # credencial errada: é o que precisa ser corrigido

    if "tenant or user not found" in message:
        return 1  # pooler de outro cluster: tente o próximo

    if any(term in message for term in ("could not translate host", "unreachable", "timeout", "timed out", "cannot assign", "connection refused")):
        return 0  # rede: endereço inalcançável daqui

    return 2


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

    parsed = make_url(url)

    if settings.DATABASE_PASSWORD:
        # O objeto URL do SQLAlchemy cuida do escape; a senha pode ter
        # qualquer caractere.
        parsed = parsed.set(password=settings.DATABASE_PASSWORD)

    candidates = candidate_urls(parsed)

    if len(candidates) == 1:
        return _engine_for(candidates[0])

    best, best_weight = None, -1

    for candidate in candidates:
        engine = _engine_for(candidate)

        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception as error:
            weight = _error_weight(str(error))
            logger.warning("Banco não respondeu em %s:%s — %s", candidate.host, candidate.port, str(error).splitlines()[0][:200])

            if weight > best_weight:
                best, best_weight = engine, weight

            if weight == 3:
                break

            continue

        logger.info("Banco conectado via %s:%s", candidate.host, candidate.port)
        return engine

    return best


def reset_engine():
    """Descarta a conexão em cache para tentar de novo na próxima carga."""

    try:
        get_engine().dispose()
    except Exception:
        pass

    get_engine.cache_clear()
    _session_factory.cache_clear()


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
