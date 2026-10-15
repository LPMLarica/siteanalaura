from datetime import date, timedelta
from decimal import Decimal

import pandas as pd
import streamlit as st

from auth.session import current_user
from components.consultation_dialogs import consultation_dialog
from components.ui import empty_state, page_header, stat_card
from services.payment_service import financial_rows, outstanding, received_between
from utils.formatting import add_months, fmt_date, fmt_money, month_label, today


def financeiro():
    user = current_user()

    page_header("Financeiro", "Recebimentos e pendências por mês.", eyebrow="Pagamentos")

    current = today()
    months = [add_months(date(current.year, current.month, 1), -i) for i in range(0, 24)]

    c1, c2 = st.columns([2, 3])
    month_start = c1.selectbox(
        "Mês",
        months,
        format_func=lambda d: month_label(d.year, d.month),
        label_visibility="collapsed",
    )
    month_end = add_months(month_start, 1) - timedelta(days=1)

    rows = financial_rows(user["id"], month_start, month_end)
    received = received_between(user["id"], month_start, month_end)

    billable = [r for r in rows if r["billable"]]
    to_receive = sum((r["amount"] for r in billable if not r["paid"]), Decimal("0"))
    expected = sum((r["amount"] for r in rows if r["status"] in ("Agendada", "Confirmada")), Decimal("0"))
    sessions_done = sum(1 for r in rows if r["status"] == "Realizada")
    absences = sum(1 for r in rows if r["status"] == "Falta")

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        stat_card("Recebido no mês", fmt_money(received), "por data de pagamento", tone="var(--sage)")

    with k2:
        stat_card("A receber do mês", fmt_money(to_receive), "sessões realizadas/faltas sem pagamento", tone="var(--amber)")

    with k3:
        stat_card("Previsto (agendadas)", fmt_money(expected), "sessões ainda por acontecer", tone="var(--slate)")

    with k4:
        stat_card("Sessões realizadas", sessions_done, f"{absences} falta(s)", tone="var(--berry)")

    st.write("")

    if not rows:
        empty_state(f"Nenhuma consulta em {month_label(month_start.year, month_start.month).lower()}.")
    else:
        frame = pd.DataFrame(
            [
                {
                    "Data": r["date"],
                    "Hora": r["start_time"].strftime("%H:%M"),
                    "Paciente": r["patient"],
                    "Status": r["status"],
                    "Valor": fmt_money(r["amount"]),
                    "Pagamento": "Pago" if r["paid"] else ("A receber" if r["billable"] else "—"),
                    "Forma": r["payment_method"] or "",
                    "Pago em": r["payment_date"],
                }
                for r in rows
            ]
        )

        st.caption("Clique em uma linha para registrar ou alterar o pagamento.")

        # A seleção de linha fica guardada no navegador; se a tabela não
        # for recriada, cada recarga reabriria o diálogo sem parar. Por isso
        # o clique só registra qual consulta abrir e troca a chave da
        # tabela, que volta sem nenhuma linha selecionada.
        version = st.session_state.get("fin_table_version", 0)
        table_key = f"fin_table_{month_start}_{version}"
        consultation_ids = [r["consultation_id"] for r in rows]

        def _on_select():
            state = st.session_state.get(table_key)
            picked = state.selection.rows if state and state.selection else []

            if picked:
                st.session_state["fin_open_consultation"] = consultation_ids[picked[0]]
                st.session_state["fin_table_version"] = version + 1

        st.dataframe(
            frame,
            hide_index=True,
            on_select=_on_select,
            selection_mode="single-row",
            key=table_key,
            column_config={
                "Data": st.column_config.DateColumn(format="DD/MM/YYYY"),
                "Pago em": st.column_config.DateColumn(format="DD/MM/YYYY"),
                "Valor": st.column_config.TextColumn(),
            },
            placeholder="",
        )

        to_open = st.session_state.pop("fin_open_consultation", None)

        if to_open:
            consultation_dialog(to_open)

        export = frame.copy()
        export["Data"] = export["Data"].map(fmt_date)
        export["Pago em"] = export["Pago em"].map(lambda d: fmt_date(d) if d else "")

        st.download_button(
            "Baixar planilha (CSV)",
            data=export.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
            file_name=f"financeiro-{month_start:%Y-%m}.csv",
            mime="text/csv",
        )

    pending = outstanding(user["id"])
    older = [p for p in pending if p["date"] < month_start]

    if older:
        st.subheader("Pendências de meses anteriores")
        total = sum((p["amount"] for p in older), Decimal("0"))
        st.caption(f"{len(older)} sessão(ões) · {fmt_money(total)}")

        for row in older:
            cols = st.columns([5, 2, 2], vertical_alignment="center")
            cols[0].markdown(f"{fmt_date(row['date'])} · **{row['patient']}**")
            cols[1].markdown(f"<span class='money'>{fmt_money(row['amount'])}</span>", unsafe_allow_html=True)

            if cols[2].button("Registrar", key=f"old_{row['consultation_id']}", width="stretch"):
                consultation_dialog(row["consultation_id"])
