import streamlit as st

def login_page():
    if not st.user.is_logged_in:
        if st.button("Log in"):
            st.login()
    else:
        if st.button("Log out"):
            st.logout()
        st.write(f"Hello, {st.user.name}!")