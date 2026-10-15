from datetime import date

import streamlit as st

from dados.models import PATIENT_STATUSES
from utils.formatting import format_cpf, format_phone, is_valid_cpf, is_valid_email, to_decimal


def patient_form(key, patient=None, submit_label="Salvar"):
    """
    Formulário de cadastro/edição. Retorna o dict de dados quando enviado
    e válido; caso contrário None (erros já exibidos na tela).
    """

    p = patient

    with st.form(key, border=False):
        full_name = st.text_input("Nome completo *", value=p.full_name if p else "")

        c1, c2 = st.columns(2)
        phone = c1.text_input("Telefone / WhatsApp", value=(p.phone or "") if p else "", placeholder="(34) 99999-9999")
        email = c2.text_input("E-mail", value=(p.email or "") if p else "")

        c3, c4, c5 = st.columns(3)
        birth_date = c3.date_input(
            "Data de nascimento",
            value=p.birth_date if p else None,
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY",
        )
        cpf = c4.text_input("CPF", value=(p.cpf or "") if p else "", placeholder="000.000.000-00")
        session_value = c5.number_input(
            "Valor da sessão (R$)",
            min_value=0.0,
            step=10.0,
            value=float(p.session_value) if p and p.session_value is not None else None,
            format="%.2f",
            help="Deixe em branco para usar o valor padrão de Configurações.",
        )

        address = st.text_input("Endereço", value=(p.address or "") if p else "")
        emergency = st.text_input(
            "Contato de emergência",
            value=(p.emergency_contact or "") if p else "",
            placeholder="Nome, parentesco e telefone",
        )

        status = st.selectbox(
            "Status",
            PATIENT_STATUSES,
            index=PATIENT_STATUSES.index(p.status) if p and p.status in PATIENT_STATUSES else 0,
        )

        notes = st.text_area(
            "Observações administrativas",
            value=(p.notes or "") if p else "",
            height=90,
            help="Informações gerais (encaminhamento, convênio, preferências de horário). "
                 "Anotações clínicas vão no prontuário, que é criptografado.",
        )

        submitted = st.form_submit_button(submit_label, type="primary", width="stretch")

    if not submitted:
        return None

    errors = []

    if not full_name.strip():
        errors.append("Informe o nome completo.")

    if cpf.strip() and not is_valid_cpf(cpf):
        errors.append("CPF inválido.")

    if email.strip() and not is_valid_email(email):
        errors.append("E-mail inválido.")

    for message in errors:
        st.error(message)

    if errors:
        return None

    return {
        "full_name": " ".join(full_name.split()),
        "phone": format_phone(phone.strip()) if phone.strip() else None,
        "email": email.strip().lower() or None,
        "birth_date": birth_date,
        "cpf": format_cpf(cpf) if cpf.strip() else None,
        "session_value": to_decimal(session_value),
        "address": address,
        "emergency_contact": emergency,
        "status": status,
        "notes": notes,
    }
