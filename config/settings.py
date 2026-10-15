"""
Configurações do aplicativo.

Ordem de leitura de cada valor:
1. ``st.secrets`` (Streamlit Community Cloud ou ``.streamlit/secrets.toml``);
2. variáveis de ambiente / arquivo ``.env`` (desenvolvimento local);
3. valor padrão definido aqui.

Nada é conectado no momento da importação: a conexão com o banco e com o
Supabase só é aberta quando realmente for usada.
"""

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def _read(name, default=None):
    try:
        if name in st.secrets:
            value = st.secrets[name]
            return value if not isinstance(value, str) else value.strip()
    except Exception:
        # Sem secrets.toml (ex.: rodando só com .env) — segue para o .env.
        pass

    value = os.getenv(name)

    if value is None or value == "":
        return default

    return value.strip()


def _as_bool(value, default=False):
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {"1", "true", "sim", "yes", "on"}


def _normalize_database_url(url):
    if not url:
        return url

    # O Supabase mostra "postgresql://..." (às vezes "postgres://...");
    # o SQLAlchemy precisa do driver explícito.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    if url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]

    return url


class Settings:

    @property
    def APP_NAME(self):
        return _read("APP_NAME", "Agenda Psicóloga Ana Laura")

    @property
    def PROFESSIONAL_NAME(self):
        return _read("PROFESSIONAL_NAME", "Ana Laura")

    @property
    def DATABASE_URL(self):
        return _normalize_database_url(
            _read("DATABASE_URL", "sqlite:///storage/agenda.db")
        )

    @property
    def DATABASE_PASSWORD(self):
        """Senha do banco em separado: evita ter de codificar caracteres
        especiais (@, #, /, %...) dentro da DATABASE_URL."""
        value = _read("DATABASE_PASSWORD")

        if value in (None, "") or str(value).startswith("COLE-AQUI"):
            return None

        return str(value)

    @property
    def SUPABASE_URL(self):
        return _read("SUPABASE_URL")

    @property
    def SUPABASE_KEY(self):
        return _read("SUPABASE_KEY")

    @property
    def SECRET_KEY(self):
        return _read("SECRET_KEY")

    @property
    def TIMEZONE(self):
        return _read("TIMEZONE", "America/Sao_Paulo")

    @property
    def ALLOW_SIGNUP(self):
        return _as_bool(_read("ALLOW_SIGNUP"), default=True)

    @property
    def ALLOWED_EMAILS(self):
        raw = _read("ALLOWED_EMAILS", "")

        if isinstance(raw, (list, tuple)):
            items = raw
        else:
            items = str(raw).split(",")

        return {item.strip().lower() for item in items if item and item.strip()}

    @property
    def SESSION_TIMEOUT_MINUTES(self):
        try:
            return int(_read("SESSION_TIMEOUT_MINUTES", 120))
        except (TypeError, ValueError):
            return 120

    @property
    def is_sqlite(self):
        return self.DATABASE_URL.startswith("sqlite")

    def email_allowed(self, email):
        allowed = self.ALLOWED_EMAILS
        return not allowed or (email or "").strip().lower() in allowed

    def problems(self):
        """Lista de configurações obrigatórias ausentes ou inválidas."""

        issues = []

        if not self.SUPABASE_URL:
            issues.append(
                "SUPABASE_URL — URL do projeto (Supabase → Project Settings → API)."
            )

        if not self.SUPABASE_KEY or self.SUPABASE_KEY.startswith("COLE-AQUI"):
            issues.append(
                "SUPABASE_KEY — chave pública (publishable/anon) do projeto."
            )

        if not self.SECRET_KEY or self.SECRET_KEY.startswith("COLE-AQUI"):
            issues.append(
                "SECRET_KEY — chave Fernet usada para criptografar os prontuários."
            )
        else:
            from cryptography.fernet import Fernet

            try:
                Fernet(self.SECRET_KEY.encode())
            except Exception:
                issues.append(
                    "SECRET_KEY está definida, mas não é uma chave Fernet válida."
                )

        url = self.DATABASE_URL or ""

        if "COLE-AQUI" in url:
            issues.append(
                "DATABASE_URL — URI do Session pooler (Supabase → Connect → Connection String)."
            )

        if ("[YOUR-PASSWORD]" in url or "SUA-SENHA" in url) and not self.DATABASE_PASSWORD:
            issues.append(
                "DATABASE_URL ainda contém o marcador da senha — troque pela senha do banco."
            )

        return issues


settings = Settings()
