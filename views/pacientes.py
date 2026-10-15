from html import escape

import pandas as pd
import streamlit as st

from auth.session import current_user
from components.consultation_dialogs import consultation_dialog, new_consultation_dialog
from components.patient_form import patient_form
from components.ui import empty_state, page_header, payment_badge, slot_row, stat_card, status_badge
from dados.models import PATIENT_STATUSES, STATUS_COLORS
from services.audit_service import register_action
from services.clinical_record_service import (
    consultations_with_record,
    create_record,
    list_records,
    update_record,
)
from services.consultation_service import list_consultations
from services.patient_service import (
    PatientError,
    create_patient,
    delete_patient,
    get_patient,
    list_patients,
    patient_summary,
    update_patient,
)
from services.payment_service import outstanding, patient_payment_summary
from services.report_service import prontuario_pdf
from services.user_service import get_user
from utils.formatting import (
    age,
    fmt_date,
    fmt_date_long,
    fmt_datetime,
    fmt_money,
    fmt_time,
    today,
    whatsapp_link,
)

TABS = ["Visão geral", "Consultas", "Prontuário", "Financeiro", "Editar dados"]


# --------------------------------------------------------------- cadastro


@st.dialog("Novo paciente", width="large")
def new_patient_dialog():
    user = current_user()
    data = patient_form("novo_paciente", submit_label="Cadastrar paciente")

    if data:
        try:
            patient = create_patient(user["id"], data)
        except PatientError as error:
            st.error(str(error))
            return

        register_action(user["id"], "Cadastrou paciente", patient.full_name)
        st.session_state["flash"] = (f"{patient.full_name} cadastrado(a).", "✅")
        st.session_state["patient_id"] = patient.id
        st.rerun()


# ------------------------------------------------------------------ lista


def _patient_list(user):
    head, action = st.columns([4, 1], vertical_alignment="bottom")

    with head:
        page_header("Pacientes", "Busque, cadastre e abra a ficha de cada paciente.", eyebrow="Cadastro")

    if action.button("Novo paciente", type="primary", width="stretch") or st.session_state.pop("open_new_patient", False):
        new_patient_dialog()

    c1, c2 = st.columns([3, 2])
    search = c1.text_input("Buscar", placeholder="Nome, telefone, e-mail ou CPF", label_visibility="collapsed")
    statuses = c2.multiselect(
        "Status", PATIENT_STATUSES, default=["Ativo", "Em pausa"], label_visibility="collapsed",
        placeholder="Todos os status",
    )

    patients = list_patients(user["id"], search=search, status=statuses or None)

    if not patients:
        empty_state(
            "Nenhum paciente encontrado." if (search or statuses) else
            "Nenhum paciente cadastrado ainda. Clique em \"Novo paciente\" para começar."
        )
        return

    frame = pd.DataFrame(
        [
            {
                "Nome": p.full_name,
                "Telefone": p.phone or "",
                "E-mail": p.email or "",
                "Idade": age(p.birth_date),
                "Status": p.status,
                "Desde": p.created_at.date() if p.created_at else None,
            }
            for p in patients
        ]
    )

    frame["Idade"] = frame["Idade"].astype("Int64")

    st.caption(f"{len(patients)} paciente(s). Clique em uma linha para abrir a ficha.")

    event = st.dataframe(
        frame,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="patients_table",
        column_config={
            "Idade": st.column_config.NumberColumn(format="%d anos"),
            "Desde": st.column_config.DateColumn(format="DD/MM/YYYY"),
        },
        placeholder="",
    )

    rows = event.selection.rows if event and event.selection else []

    if rows:
        st.session_state["patient_id"] = patients[rows[0]].id
        st.session_state.pop("patients_table", None)
        st.rerun()


# ------------------------------------------------------------------ ficha


def _overview(user, patient):
    summary = patient_summary(patient.id, user["id"])
    finance = patient_payment_summary(patient.id, user["id"])

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        stat_card("Sessões realizadas", summary["realizadas"], f"{summary['faltas']} falta(s)", tone="var(--sage)")

    with c2:
        nxt = summary["proxima"]
        stat_card(
            "Próxima sessão",
            fmt_date(nxt.date)[:5] if nxt else "—",
            f"{fmt_time(nxt.start_time)} · {nxt.modality}" if nxt else "nenhuma agendada",
            tone="var(--slate)",
        )

    with c3:
        stat_card("Última sessão", fmt_date(summary["ultima"]) if summary["ultima"] else "—", tone="var(--sky)")

    with c4:
        stat_card(
            "A receber",
            fmt_money(finance["total_pendente"]),
            f"{finance['sessoes_pendentes']} sessão(ões)",
            tone="var(--amber)",
        )

    st.write("")
    left, right = st.columns(2, gap="large")

    with left:
        st.subheader("Contato")
        st.markdown(
            f"**Telefone:** {escape(patient.phone or '-')}  \n"
            f"**E-mail:** {escape(patient.email or '-')}  \n"
            f"**Endereço:** {escape(patient.address or '-')}  \n"
            f"**Emergência:** {escape(patient.emergency_contact or '-')}"
        )

        link = whatsapp_link(patient.phone)

        if link:
            st.link_button("Conversar no WhatsApp", link)

    with right:
        st.subheader("Dados")
        idade = age(patient.birth_date)
        st.markdown(
            f"**Nascimento:** {fmt_date(patient.birth_date)}"
            + (f" ({idade} anos)" if idade is not None else "")
            + f"  \n**CPF:** {escape(patient.cpf or '-')}"
            + f"  \n**Valor da sessão:** {fmt_money(patient.session_value) if patient.session_value else 'padrão'}"
            + f"  \n**Cadastro:** {fmt_date(patient.created_at.date()) if patient.created_at else '-'}"
        )

    if patient.notes:
        st.subheader("Observações")
        st.markdown(escape(patient.notes).replace("\n", "  \n"))


def _consultations(user, patient):
    head, action = st.columns([4, 1], vertical_alignment="bottom")
    head.subheader("Histórico de consultas")

    if action.button("Agendar", type="primary", width="stretch"):
        new_consultation_dialog(patient_id=patient.id)

    items = list_consultations(user["id"], patient_id=patient.id)

    if not items:
        empty_state("Nenhuma consulta registrada.")
        return

    with_record = consultations_with_record(patient.id, user["id"])

    for item in sorted(items, key=lambda c: (c.date, c.start_time), reverse=True):
        paid = bool(item.payment and item.payment.status == "Pago")
        right_html = status_badge(item.status)

        if item.status in ("Realizada", "Falta"):
            right_html += " " + payment_badge(paid)

        meta = f"{fmt_date_long(item.date)} · {item.modality}"

        if item.id in with_record:
            meta += " · com registro no prontuário"

        cols = st.columns([12, 2], vertical_alignment="center")

        with cols[0]:
            slot_row(
                fmt_date(item.date)[:5] + f"/{item.date:%y}",
                fmt_time(item.start_time),
                item.title,
                meta,
                right_html,
                tone=STATUS_COLORS.get(item.status),
            )

        if cols[1].button("Abrir", key=f"pc_{item.id}", width="stretch"):
            consultation_dialog(item.id)


def _prontuario(user, patient):
    viewed_key = f"audit_viewed_{patient.id}"

    if not st.session_state.get(viewed_key):
        register_action(user["id"], "Abriu prontuário", patient.full_name)
        st.session_state[viewed_key] = True

    st.markdown(
        '<div class="sigilo">Documento sigiloso. O conteúdo é criptografado antes de ser '
        "gravado e só é exibido para você.</div>",
        unsafe_allow_html=True,
    )

    records = list_records(patient.id, user["id"])

    consultations = [
        c for c in list_consultations(user["id"], patient_id=patient.id)
        if c.status in ("Realizada", "Falta") or c.date <= today()
    ]
    consultations.sort(key=lambda c: (c.date, c.start_time), reverse=True)
    linked = {r.consultation_id for r in records if r.consultation_id}
    options = [None] + [c.id for c in consultations if c.id not in linked]
    labels = {c.id: f"{fmt_date(c.date)} {fmt_time(c.start_time)} · {c.status}" for c in consultations}

    with st.expander("Nova evolução", expanded=not records):
        with st.form(f"novo_registro_{patient.id}", clear_on_submit=True, border=False):
            c1, c2 = st.columns(2)
            consultation_id = c1.selectbox(
                "Sessão relacionada",
                options,
                format_func=lambda cid: "Sem vínculo com consulta" if cid is None else labels[cid],
            )
            session_date = c2.date_input("Data da sessão", value=today(), format="DD/MM/YYYY")
            content = st.text_area(
                "Registro",
                height=220,
                placeholder="Demanda, intervenções, evolução, encaminhamentos...",
            )
            saved = st.form_submit_button("Salvar no prontuário", type="primary", width="stretch")

        if saved:
            if consultation_id and consultation_id in labels:
                chosen = next(c for c in consultations if c.id == consultation_id)
                session_date = chosen.date

            try:
                create_record(user["id"], patient.id, session_date, content, consultation_id)
            except ValueError as error:
                st.error(str(error))
            else:
                register_action(user["id"], "Registrou evolução", patient.full_name)
                st.session_state["flash"] = ("Registro salvo no prontuário.", "✅")
                st.rerun()

    head, download = st.columns([3, 1], vertical_alignment="bottom")
    head.subheader(f"Registros ({len(records)})")

    if records:
        profile = get_user(user["id"]) or user

        download.download_button(
            "Exportar PDF",
            data=lambda: prontuario_pdf(profile, patient, records),
            file_name=f"prontuario-{patient.full_name.lower().replace(' ', '-')}.pdf",
            mime="application/pdf",
            width="stretch",
            on_click=lambda: register_action(user["id"], "Exportou prontuário", patient.full_name),
        )

    if not records:
        empty_state("Nenhum registro no prontuário ainda.")
        return

    query = st.text_input("Buscar nos registros", placeholder="Palavra-chave", key=f"busca_pront_{patient.id}")

    shown = [r for r in records if not query or query.lower() in r.content.lower()]

    if query:
        st.caption(f"{len(shown)} registro(s) com \"{query}\".")

    editing = st.session_state.get("editing_record")

    for record in shown:
        if editing == record.id:
            with st.form(f"edit_{record.id}", border=True):
                new_date = st.date_input("Data da sessão", value=record.session_date, format="DD/MM/YYYY")
                new_content = st.text_area("Registro", value=record.content, height=240)
                c1, c2 = st.columns(2)
                ok = c1.form_submit_button("Salvar alterações", type="primary", width="stretch")
                cancel = c2.form_submit_button("Cancelar", width="stretch")

            if ok:
                try:
                    update_record(record.id, user["id"], new_content, new_date)
                except ValueError as error:
                    st.error(str(error))
                else:
                    register_action(user["id"], "Editou evolução", patient.full_name)
                    st.session_state.pop("editing_record", None)
                    st.rerun()

            if cancel:
                st.session_state.pop("editing_record", None)
                st.rerun()

            continue

        edited = (
            record.updated_at and record.created_at
            and (record.updated_at - record.created_at).total_seconds() > 60
        )
        stamp = f"Registrado em {fmt_datetime(record.created_at)}"

        if edited:
            stamp += f" · editado em {fmt_datetime(record.updated_at)}"

        st.markdown(
            f'<div class="record"><div class="when">{fmt_date_long(record.session_date)} · '
            f"{fmt_date(record.session_date)}</div>"
            f'<div class="body">{escape(record.content)}</div>'
            f'<div class="stamp">{stamp}</div></div>',
            unsafe_allow_html=True,
        )

        if st.button("Editar", key=f"edit_btn_{record.id}", type="tertiary"):
            st.session_state["editing_record"] = record.id
            st.rerun()


def _financeiro(user, patient):
    summary = patient_payment_summary(patient.id, user["id"])

    c1, c2 = st.columns(2)

    with c1:
        stat_card("Total recebido", fmt_money(summary["total_pago"]), tone="var(--sage)")

    with c2:
        stat_card(
            "A receber",
            fmt_money(summary["total_pendente"]),
            f"{summary['sessoes_pendentes']} sessão(ões) realizadas sem pagamento",
            tone="var(--amber)",
        )

    st.write("")
    pending = outstanding(user["id"], patient_id=patient.id)

    if not pending:
        empty_state("Nenhuma pendência financeira.")
        return

    st.subheader("Sessões a receber")

    for row in pending:
        cols = st.columns([5, 2, 2], vertical_alignment="center")
        cols[0].markdown(f"{fmt_date(row['date'], with_weekday=True)} · {row['status']}")
        cols[1].markdown(f"<span class='money'>{fmt_money(row['amount'])}</span>", unsafe_allow_html=True)

        if cols[2].button("Registrar", key=f"pay_{row['consultation_id']}", width="stretch"):
            consultation_dialog(row["consultation_id"])


def _edit(user, patient):
    data = patient_form(f"editar_{patient.id}", patient=patient, submit_label="Salvar alterações")

    if data:
        try:
            update_patient(patient.id, user["id"], data)
        except PatientError as error:
            st.error(str(error))
        else:
            st.session_state["flash"] = ("Dados atualizados.", "✅")
            st.rerun()

    st.divider()

    with st.expander("Excluir paciente"):
        st.caption(
            "Só é possível excluir pacientes sem consultas e sem prontuário. "
            "Para quem já foi atendido, altere o status para \"Inativo\" ou \"Alta\"."
        )
        confirm = st.text_input("Digite EXCLUIR para confirmar", key=f"confirm_del_{patient.id}")

        if st.button("Excluir definitivamente", disabled=confirm.strip().upper() != "EXCLUIR"):
            try:
                delete_patient(patient.id, user["id"])
            except PatientError as error:
                st.error(str(error))
            else:
                register_action(user["id"], "Excluiu paciente", patient.full_name)
                st.session_state.pop("patient_id", None)
                st.session_state["flash"] = ("Paciente excluído.", "🗑️")
                st.rerun()


def _patient_page(user, patient_id):
    patient = get_patient(patient_id, user["id"])

    if patient is None:
        st.session_state.pop("patient_id", None)
        st.warning("Paciente não encontrado.")
        return

    if st.button("← Todos os pacientes", type="tertiary"):
        st.session_state.pop("patient_id", None)
        st.session_state.pop("editing_record", None)
        st.rerun()

    subtitle = " · ".join(
        part for part in [
            patient.status,
            f"{age(patient.birth_date)} anos" if patient.birth_date else None,
            patient.phone,
        ] if part
    )
    page_header(patient.full_name, subtitle, eyebrow="Ficha do paciente")

    wanted = st.session_state.pop("patient_tab", None)

    if wanted in TABS:
        st.session_state[f"tabs_{patient.id}"] = wanted

    tab_key = f"tabs_{patient.id}"

    section = st.segmented_control(
        "Seção",
        TABS,
        default=None if tab_key in st.session_state else TABS[0],
        key=tab_key,
        label_visibility="collapsed",
        required=True,
    )

    st.write("")

    if section == "Consultas":
        _consultations(user, patient)
    elif section == "Prontuário":
        _prontuario(user, patient)
    elif section == "Financeiro":
        _financeiro(user, patient)
    elif section == "Editar dados":
        _edit(user, patient)
    else:
        _overview(user, patient)


def pacientes():
    user = current_user()
    patient_id = st.session_state.get("patient_id")

    if patient_id:
        _patient_page(user, patient_id)
    else:
        _patient_list(user)
