"""
Cria as tabelas que ainda não existem (sem apagar nada).

Uso:  python -m dados.migrations

Em produção o schema já é criado pelo arquivo ``sql/001_schema.sql``
(aplicado no Supabase). Este script é útil para desenvolvimento local
com SQLite ou para conferir se a connection string está correta.
"""

from dados.database import check_connection, init_db


def migrate():
    error = check_connection()

    if error:
        raise SystemExit(f"Não foi possível conectar ao banco: {error}")

    init_db()
    print("Tabelas verificadas/criadas com sucesso.")


if __name__ == "__main__":
    migrate()
