import streamlit as st

from services.consultation_service import (
    update_consultation,
    delete_consultation
)
from services.payment_service import (
    PAYMENT_METHODS,
    STATUS_PAGO,
    STATUS_PENDENTE,
    get_payment_for_consultation,
    mark_as_paid,
    mark_as_pending,
)


def consultation_details(
        consultation,
        user_id
):

    st.subheader(
        "Detalhes da Consulta"
    )

    st.write(
        f"Paciente: {consultation.patient.full_name}"
    )

    st.write(
        f"Data: {consultation.date}"
    )

    st.write(
        f"Horário: {consultation.start_time}"
    )

    st.write(
        f"Observação: {consultation.observation}"
    )

    status = st.selectbox(

        "Status",

        [
            "Agendada",
            "Confirmada",
            "Cancelada",
            "Remarcada"
        ],

        index=[
            "Agendada",
            "Confirmada",
            "Cancelada",
            "Remarcada"
        ].index(
            consultation.status
        ),

        key=f"consulta_status_{consultation.id}"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Salvar",
            key=f"consulta_salvar_{consultation.id}"
        ):

            update_consultation(
                consultation.id,
                user_id,
                {
                    "status": status
                }
            )

            st.success(
                "Atualizado"
            )

            st.rerun()

    with col2:

        if st.button(
            "Excluir",
            key=f"consulta_excluir_{consultation.id}"
        ):

            delete_consultation(
                consultation.id,
                user_id
            )

            st.warning(
                "Removido"
            )

            st.rerun()

    st.divider()

    _payment_section(consultation, user_id)


def _payment_section(consultation, user_id):

    st.markdown("**💰 Pagamento**")

    payment = get_payment_for_consultation(
        consultation.id,
        user_id
    )

    is_paid = bool(payment) and payment.status == STATUS_PAGO

    if is_paid:
        st.success(
            f"Pago — R$ {payment.amount:.2f} via {payment.payment_method or '-'}"
            + (f" em {payment.payment_date}" if payment.payment_date else "")
        )
    else:
        st.warning("Pendente")

    with st.form(f"pagamento_form_{consultation.id}"):

        amount = st.number_input(
            "Valor (R$)",
            min_value=0.0,
            step=10.0,
            value=float(payment.amount) if payment and payment.amount else 0.0,
            key=f"pagamento_valor_{consultation.id}"
        )

        method = st.selectbox(
            "Forma de pagamento",
            PAYMENT_METHODS,
            index=(
                PAYMENT_METHODS.index(payment.payment_method)
                if payment and payment.payment_method in PAYMENT_METHODS
                else 0
            ),
            key=f"pagamento_metodo_{consultation.id}"
        )

        col_pago, col_pendente = st.columns(2)

        with col_pago:
            marcar_pago = st.form_submit_button(
                "Marcar como pago",
                use_container_width=True
            )

        with col_pendente:
            marcar_pendente = st.form_submit_button(
                "Marcar como pendente",
                use_container_width=True
            )

    if marcar_pago:
        mark_as_paid(
            consultation_id=consultation.id,
            patient_id=consultation.patient_id,
            user_id=user_id,
            amount=amount,
            payment_method=method
        )
        st.success("Pagamento registrado.")
        st.rerun()

    if marcar_pendente:
        mark_as_pending(
            consultation_id=consultation.id,
            patient_id=consultation.patient_id,
            user_id=user_id
        )
        st.info("Pagamento marcado como pendente.")
        st.rerun()
