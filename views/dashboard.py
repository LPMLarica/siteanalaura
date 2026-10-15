import streamlit as st

from auth.session import current_user
from components.consultation_dialogs import consultation_dialog, new_consultation_dialog
from components.ui import empty_state, page_header, payment_badge, slot_row, stat_card, status_badge
from dados.models import STATUS_COLORS
from services.dashboard_service import get_dashboard_stats
from utils.formatting import fmt_date, fmt_date_long, fmt_money, fmt_time, now_local, whatsapp_link


def _greeting():
    hour = now_local().hour

    if hour < 12:
        return "Bom dia"

    if hour < 18:
        return "Boa tarde"

    return "Boa noite"


def dashboard():
    user = current_user()
    stats = get_dashboard_stats(user["id"])
    first_name = (user.get("name") or "").split(" ")[0]

    page_header(
        f"{_greeting()}, {first_name}",
        fmt_date_long(now_local().date()).capitalize(),
        eyebrow="Início",
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        stat_card("Sessões hoje", len(stats["today"]), "sem contar canceladas", tone="var(--berry)")

    with c2:
        stat_card("Sessões na semana", stats["week_count"], "segunda a domingo", tone="var(--slate)")

    with c3:
        stat_card("Pacientes ativos", stats["active_patients"], "em acompanhamento", tone="var(--sky)")

    with c4:
        stat_card(
            "Recebido no mês",
            fmt_money(stats["received_month"]),
            f"a receber: {fmt_money(stats['pending_total'])}",
            tone="var(--sage)",
        )

    st.write("")

    left, right = st.columns([3, 2], gap="large")

    with left:
        head, action = st.columns([3, 1])
        head.subheader("Hoje")

        if action.button("Nova consulta", type="primary", width="stretch"):
            new_consultation_dialog()

        if not stats["today"]:
            empty_state("Nenhuma sessão hoje.")

        for item in stats["today"]:
            paid = bool(item.payment and item.payment.status == "Pago")
            right_html = status_badge(item.status)

            if item.status in ("Realizada", "Falta"):
                right_html += " " + payment_badge(paid)

            slot_row(
                fmt_time(item.start_time),
                fmt_time(item.end_time),
                item.patient.full_name,
                f"{item.title} · {item.modality}",
                right_html,
                tone=STATUS_COLORS.get(item.status),
            )

        today_ids = [item.id for item in stats["today"]]

        if today_ids:
            labels = {
                item.id: f"{fmt_time(item.start_time)} · {item.patient.full_name}"
                for item in stats["today"]
            }
            def _pick():
                st.session_state["open_consultation"] = st.session_state.get("dashboard_open_today")
                st.session_state["dashboard_open_today"] = None

            st.selectbox(
                "Abrir sessão de hoje",
                today_ids,
                index=None,
                format_func=labels.get,
                placeholder="Escolha para registrar status ou pagamento",
                key="dashboard_open_today",
                on_change=_pick,
            )

            chosen = st.session_state.pop("open_consultation", None)

            if chosen:
                consultation_dialog(chosen)

        st.subheader("Próximos 14 dias")

        if not stats["upcoming"]:
            empty_state("Nenhuma sessão marcada para os próximos dias.")

        for item in stats["upcoming"]:
            slot_row(
                fmt_date(item.date)[:5],
                fmt_time(item.start_time),
                item.patient.full_name,
                f"{fmt_date_long(item.date)} · {item.modality}",
                status_badge(item.status, soft=True),
                tone=STATUS_COLORS.get(item.status),
            )

    with right:
        st.subheader("Confirmar para amanhã")

        if not stats["unconfirmed_tomorrow"]:
            empty_state("Tudo confirmado para amanhã.")

        for item in stats["unconfirmed_tomorrow"]:
            link = whatsapp_link(
                item.patient.phone,
                f"Olá, {item.patient.full_name.split()[0]}! Confirmando nossa sessão de amanhã, "
                f"{item.date:%d/%m}, às {item.start_time:%H:%M}. Posso contar com você?",
            )

            with st.container(border=True):
                st.markdown(f"**{item.patient.full_name}** · {fmt_time(item.start_time)}")

                if link:
                    st.link_button("Enviar confirmação no WhatsApp", link, width="stretch")
                else:
                    st.caption("Sem telefone cadastrado.")

        st.subheader("A receber")

        pending = stats["pending"]

        if not pending:
            empty_state("Nenhum pagamento pendente.")
        else:
            for row in pending[:6]:
                st.markdown(
                    f"{fmt_date(row['date'])} · **{row['patient']}** — "
                    f"<span class='money'>{fmt_money(row['amount'])}</span>",
                    unsafe_allow_html=True,
                )

            if len(pending) > 6:
                st.caption(f"e mais {len(pending) - 6}. Veja tudo em Financeiro.")
