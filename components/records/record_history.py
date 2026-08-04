import streamlit as st



def record_history(records):

    st.subheader("📚 Histórico clínico")

    if not records:

        st.info("Nenhum registro encontrado.")

        return

    for record in records:
        with st.expander(
            str(record.created_at)
        ):
            st.write(record.content)