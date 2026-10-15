from datetime import time, timedelta

import streamlit as st

from auth.session import current_user, update_current_user
from auth.supabase_auth import AuthError, change_password, validate_new_password
from components.ui import empty_state, page_header
from dados.models import WEEKDAYS
from services.audit_service import recent_actions
from services.schedule_service import (
    ScheduleError,
    add_blocked_period,
    add_working_hours,
    delete_blocked_period,
    delete_working_hours,
    list_blocked_periods,
    list_working_hours,
)
from services.user_service import get_user, update_profile
from utils.formatting import fmt_date, fmt_datetime, today, to_decimal


def _profile(user):
    data = get_user(user["id"]) or user

    with st.form("perfil", border=False):
        name = st.text_input("Nome de exibição", value=data.get("name") or "")
        c1, c2 = st.columns(2)
        crp = c1.text_input("CRP", value=data.get("professional_register") or "", placeholder="00/00000")
        phone = c2.text_input("Telefone", value=data.get("phone") or "")

        c3, c4 = st.columns(2)
        minutes = c3.number_input(
            "Duração padrão da sessão (min)", min_value=10, max_value=240, step=5,
            value=int(data.get("default_session_minutes") or 50),
        )
        value = c4.number_input(
            "Valor padrão da sessão (R$)", min_value=0.0, step=10.0, format="%.2f",
            value=float(data.get("default_session_value") or 0),
            help="Usado quando o paciente não tem um valor próprio.",
        )

        st.text_input("E-mail de acesso", value=data.get("email") or "", disabled=True)
        saved = st.form_submit_button("Salvar perfil", type="primary")

    if saved:
        if not name.strip():
            st.error("Informe o nome.")
            return

        updated = update_profile(
            user["id"],
            name=" ".join(name.split()),
            professional_register=crp.strip() or None,
            phone=phone.strip() or None,
            default_session_minutes=int(minutes),
            default_session_value=to_decimal(value),
        )
        update_current_user(**updated)
        st.session_state["flash"] = ("Perfil atualizado.", "✅")
        st.rerun()


def _hours(user):
    st.caption(
        "Os horários aparecem destacados na agenda. Agendamentos fora deles pedem "
        "confirmação. Sem nenhum horário cadastrado, a agenda fica livre."
    )

    items = list_working_hours(user["id"])

    if not items:
        empty_state("Nenhum horário cadastrado.")

    for item in items:
        cols = st.columns([3, 3, 1], vertical_alignment="center")
        cols[0].markdown(f"**{WEEKDAYS[item.weekday]}**")
        cols[1].markdown(f"{item.start_time:%H:%M} às {item.end_time:%H:%M}")

        if cols[2].button("Remover", key=f"wh_{item.id}", type="tertiary"):
            delete_working_hours(item.id, user["id"])
            st.rerun()

    st.subheader("Adicionar horário")

    with st.form("novo_horario", border=False):
        days = st.pills("Dias", WEEKDAYS, selection_mode="multi", default=WEEKDAYS[:5])
        c1, c2 = st.columns(2)
        start = c1.time_input("Início", value=time(8, 0), step=timedelta(minutes=15))
        end = c2.time_input("Fim", value=time(18, 0), step=timedelta(minutes=15))
        added = st.form_submit_button("Adicionar", type="primary")

    if added:
        if not days:
            st.error("Escolha pelo menos um dia.")
            return

        try:
            add_working_hours(user["id"], [WEEKDAYS.index(d) for d in days], start, end)
        except ScheduleError as error:
            st.error(str(error))
        else:
            st.session_state["flash"] = ("Horário adicionado.", "✅")
            st.rerun()


def _blocks(user):
    st.caption("Férias, feriados, congressos: datas bloqueadas não aceitam agendamentos.")

    items = list_blocked_periods(user["id"], from_date=today() - timedelta(days=30))

    if not items:
        empty_state("Nenhum bloqueio futuro.")

    for item in items:
        cols = st.columns([4, 3, 1], vertical_alignment="center")
        period = fmt_date(item.start_date)

        if item.end_date != item.start_date:
            period += f" a {fmt_date(item.end_date)}"

        cols[0].markdown(f"**{period}**")
        cols[1].markdown(item.reason or "")

        if cols[2].button("Remover", key=f"bp_{item.id}", type="tertiary"):
            delete_blocked_period(item.id, user["id"])
            st.rerun()

    st.subheader("Bloquear datas")

    with st.form("novo_bloqueio", border=False, clear_on_submit=True):
        c1, c2 = st.columns(2)
        start = c1.date_input("De", value=today(), format="DD/MM/YYYY")
        end = c2.date_input("Até", value=today(), format="DD/MM/YYYY")
        reason = st.text_input("Motivo (opcional)", placeholder="Férias, feriado, congresso...")
        added = st.form_submit_button("Bloquear", type="primary")

    if added:
        try:
            add_blocked_period(user["id"], start, end, reason)
        except ScheduleError as error:
            st.error(str(error))
        else:
            st.session_state["flash"] = ("Período bloqueado.", "✅")
            st.rerun()


def _security(user):
    with st.form("trocar_senha", border=False, clear_on_submit=True):
        current = st.text_input("Senha atual", type="password", autocomplete="current-password")
        new = st.text_input("Nova senha", type="password", autocomplete="new-password")
        confirmation = st.text_input("Confirmar nova senha", type="password", autocomplete="new-password")
        changed = st.form_submit_button("Alterar senha", type="primary")

    if changed:
        problem = validate_new_password(new, confirmation)

        if problem:
            st.error(problem)
        else:
            try:
                change_password(user["email"], current, new)
            except AuthError as error:
                st.error(str(error))
            else:
                st.success("Senha alterada.")

    st.subheader("Atividade recente")
    st.caption("Registro de acessos e ações sensíveis (prontuários, exclusões).")

    actions = recent_actions(user["id"], limit=30)

    if not actions:
        empty_state("Nada registrado ainda.")
        return

    st.dataframe(
        [
            {"Quando": fmt_datetime(a.created_at), "Ação": a.action, "Detalhe": a.target or ""}
            for a in actions
        ],
        hide_index=True,
        placeholder="",
    )


def configuracoes():
    user = current_user()

    page_header("Configurações", "Perfil, horários de atendimento e segurança.", eyebrow="Conta")

    tabs = st.tabs(["Perfil", "Horários de atendimento", "Bloqueios e férias", "Segurança"])

    with tabs[0]:
        _profile(user)

    with tabs[1]:
        _hours(user)

    with tabs[2]:
        _blocks(user)

    with tabs[3]:
        _security(user)
