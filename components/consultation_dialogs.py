"""Janelas (diálogos) de nova consulta e de detalhes da consulta."""

from datetime import datetime, time, timedelta

import streamlit as st

from auth.session import current_user
from dados.models import CONSULTATION_STATUSES, MODALITIES, PAYMENT_METHODS
from services.audit_service import register_action
from services.consultation_service import (
    create_consultations,
    delete_consultation,
    get_consultation,
    reschedule_consultation,
    update_consultation,
)
from services.patient_service import list_patients
from services.payment_service import mark_as_paid, mark_as_pending, suggested_amount_for
from services.schedule_service import ScheduleError
from utils.formatting import fmt_date_long, fmt_money, fmt_time, now_local, whatsapp_link

DURATIONS = [30, 40, 45, 50, 60, 75, 90, 120]


def _round_up(moment, minutes=30):
    dt = datetime.combine(datetime.today(), moment)
    extra = (-dt.minute) % minutes
    return (dt + timedelta(minutes=extra)).replace(second=0, microsecond=0).time()


def _close(message=None, icon="✅"):
    if message:
        st.session_state["flash"] = (message, icon)
    st.session_state["calendar_version"] = st.session_state.get("calendar_version", 0) + 1
    st.rerun()


# ------------------------------------------------------------ nova consulta


@st.dialog("Nova consulta", width="large", on_dismiss="rerun")
def new_consultation_dialog(day=None, start=None, duration=None, patient_id=None):
    user = current_user()
    patients = list_patients(user["id"], status=["Ativo", "Em pausa"])

    if not patients:
        st.info("Cadastre um paciente antes de agendar.")
        if st.button("Ir para Pacientes", type="primary"):
            st.session_state["open_new_patient"] = True
            st.switch_page(st.session_state["pages"]["pacientes"])
        return

    ids = [p.id for p in patients]
    names = {p.id: p.full_name for p in patients}

    now = now_local()
    day = day or now.date()
    start = start or _round_up(now.time()) if day == now.date() else (start or time(8, 0))
    default_duration = duration or user.get("default_session_minutes") or 50

    if default_duration not in DURATIONS:
        options = sorted(set(DURATIONS + [default_duration]))
    else:
        options = DURATIONS

    with st.form("nova_consulta", border=False):
        patient = st.selectbox(
            "Paciente",
            ids,
            index=ids.index(patient_id) if patient_id in ids else None,
            format_func=lambda pid: names[pid],
            placeholder="Escolha o paciente",
        )

        c1, c2, c3 = st.columns(3)
        chosen_day = c1.date_input("Data", value=day, format="DD/MM/YYYY")
        chosen_start = c2.time_input("Início", value=start, step=timedelta(minutes=5))
        chosen_duration = c3.selectbox(
            "Duração", options, index=options.index(default_duration),
            format_func=lambda m: f"{m} min",
        )

        c4, c5 = st.columns(2)
        modality = c4.radio("Modalidade", MODALITIES, horizontal=True)
        status = c5.selectbox("Status", ["Agendada", "Confirmada"])

        title = st.text_input("Título", value="Sessão")
        observation = st.text_area("Observações (opcional)", height=80)

        c6, c7 = st.columns([1, 1])
        repeat = c6.checkbox("Repetir semanalmente")
        weeks = c7.number_input(
            "Por quantas semanas (incluindo esta)", min_value=2, max_value=52, value=4,
            disabled=False,
        )

        force = st.checkbox(
            "Permitir fora do horário de atendimento",
            help="Use para encaixes fora dos horários cadastrados em Configurações.",
        )

        submitted = st.form_submit_button("Agendar", type="primary", width="stretch")

    if submitted:
        if not patient:
            st.error("Escolha o paciente.")
            return

        try:
            created = create_consultations(
                user["id"],
                patient,
                chosen_day,
                chosen_start,
                chosen_duration,
                title=title,
                status=status,
                modality=modality,
                observation=observation,
                repeat_weeks=int(weeks) if repeat else 1,
                force=force,
            )
        except ScheduleError as error:
            st.error(str(error))
            if error.soft:
                st.caption("Marque \"Permitir fora do horário de atendimento\" para agendar mesmo assim.")
            return

        total = len(created)
        _close(
            f"Consulta de {names[patient]} agendada."
            if total == 1
            else f"{total} consultas semanais de {names[patient]} agendadas."
        )


# ------------------------------------------------------- detalhes/edição


@st.dialog("Consulta", width="large", on_dismiss="rerun")
def consultation_dialog(consultation_id):
    user = current_user()
    consultation = get_consultation(consultation_id, user["id"])

    if consultation is None:
        st.warning("Esta consulta não existe mais.")
        return

    patient = consultation.patient

    st.markdown(f"### {patient.full_name}")
    st.caption(
        f"{fmt_date_long(consultation.date).capitalize()} · "
        f"{fmt_time(consultation.start_time)}–{fmt_time(consultation.end_time)} · "
        f"{consultation.modality}"
    )

    link = whatsapp_link(
        patient.phone,
        f"Olá, {patient.full_name.split()[0]}! Passando para confirmar sua sessão de "
        f"{consultation.date:%d/%m} às {consultation.start_time:%H:%M}.",
    )

    tab_status, tab_payment, tab_move = st.tabs(["Status", "Pagamento", "Remarcar / excluir"])

    with tab_status:
        with st.form(f"status_{consultation.id}", border=False):
            status = st.segmented_control(
                "Status",
                CONSULTATION_STATUSES,
                default=consultation.status,
                selection_mode="single",
            )
            modality = st.radio(
                "Modalidade", MODALITIES, horizontal=True,
                index=MODALITIES.index(consultation.modality) if consultation.modality in MODALITIES else 0,
            )
            title = st.text_input("Título", value=consultation.title)
            observation = st.text_area("Observações", value=consultation.observation or "", height=90)
            saved = st.form_submit_button("Salvar", type="primary", width="stretch")

        if saved:
            update_consultation(
                consultation.id,
                user["id"],
                {
                    "status": status or consultation.status,
                    "modality": modality,
                    "title": title,
                    "observation": observation,
                },
            )
            _close("Consulta atualizada.")

        c1, c2 = st.columns(2)

        if link:
            c1.link_button("Confirmar pelo WhatsApp", link, width="stretch")

        if c2.button("Abrir ficha do paciente", width="stretch"):
            st.session_state["patient_id"] = patient.id
            st.session_state["patient_tab"] = "Prontuário"
            st.switch_page(st.session_state["pages"]["pacientes"])

    with tab_payment:
        payment = consultation.payment
        paid = bool(payment and payment.status == "Pago")

        if paid:
            st.success(
                f"Pago — {fmt_money(payment.amount)}"
                + (f" via {payment.payment_method}" if payment.payment_method else "")
                + (f" em {payment.payment_date:%d/%m/%Y}" if payment.payment_date else "")
            )
        else:
            st.info("Pagamento ainda não registrado.")

        amount_default = float(suggested_amount_for(consultation.id, user["id"]))

        with st.form(f"pagamento_{consultation.id}", border=False):
            c1, c2, c3 = st.columns(3)
            amount = c1.number_input("Valor (R$)", min_value=0.0, step=10.0, value=amount_default, format="%.2f")
            method = c2.selectbox(
                "Forma",
                PAYMENT_METHODS,
                index=PAYMENT_METHODS.index(payment.payment_method)
                if payment and payment.payment_method in PAYMENT_METHODS else 0,
            )
            paid_on = c3.date_input(
                "Data do pagamento",
                value=(payment.payment_date if payment and payment.payment_date else now_local().date()),
                format="DD/MM/YYYY",
            )
            notes = st.text_input("Observação (opcional)", value=(payment.notes or "") if payment else "")

            b1, b2 = st.columns(2)
            pay = b1.form_submit_button("Registrar como pago", type="primary", width="stretch")
            pending = b2.form_submit_button("Marcar como pendente", width="stretch")

        if pay:
            mark_as_paid(consultation.id, user["id"], amount, method, payment_date=paid_on, notes=notes)
            _close("Pagamento registrado.")

        if pending:
            mark_as_pending(consultation.id, user["id"], amount=amount)
            _close("Pagamento marcado como pendente.", icon="🕒")

    with tab_move:
        with st.form(f"remarcar_{consultation.id}", border=False):
            c1, c2, c3 = st.columns(3)
            new_day = c1.date_input("Nova data", value=consultation.date, format="DD/MM/YYYY")
            new_start = c2.time_input("Início", value=consultation.start_time, step=timedelta(minutes=5))
            minutes = int(
                (datetime.combine(consultation.date, consultation.end_time)
                 - datetime.combine(consultation.date, consultation.start_time)).total_seconds() // 60
            )
            new_duration = c3.number_input("Duração (min)", min_value=10, max_value=240, value=minutes, step=5)
            force = st.checkbox("Permitir fora do horário de atendimento", key=f"force_{consultation.id}")
            moved = st.form_submit_button("Remarcar", type="primary", width="stretch")

        if moved:
            new_end = (datetime.combine(new_day, new_start) + timedelta(minutes=int(new_duration))).time()

            try:
                reschedule_consultation(consultation.id, user["id"], new_day, new_start, new_end, force=force)
            except ScheduleError as error:
                st.error(str(error))
            else:
                _close("Consulta remarcada.")

        st.divider()

        confirm = st.checkbox("Quero excluir esta consulta definitivamente", key=f"del_{consultation.id}")
        st.caption("Se o paciente desmarcou, prefira o status \"Cancelada\" para manter o histórico.")

        if st.button("Excluir consulta", disabled=not confirm, key=f"delbtn_{consultation.id}"):
            delete_consultation(consultation.id, user["id"])
            register_action(user["id"], "Excluiu consulta", f"{patient.full_name} {consultation.date}")
            _close("Consulta excluída.", icon="🗑️")
