from supabase import Client, ClientOptions, create_client

from config.settings import settings


def new_supabase_client() -> Client:
    """
    Cria um cliente do Supabase NOVO a cada operação de autenticação.

    Não usamos um cliente compartilhado (st.cache_resource) de propósito:
    o cliente guarda a sessão do último login, e no Streamlit o mesmo
    processo atende todos os visitantes — um cliente compartilhado
    misturaria as sessões de pessoas diferentes.
    """

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_URL/SUPABASE_KEY não configurados. Veja o README."
        )

    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,
        options=ClientOptions(
            persist_session=False,
            auto_refresh_token=False,
        ),
    )
