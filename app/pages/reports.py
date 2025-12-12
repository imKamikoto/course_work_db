import streamlit as st
from pages.login import ensure_logged_in

def reports_page():
    ensure_logged_in()
    user = st.session_state["user"]

    st.title("Отчёты")

    st.sidebar.title("Пользователь")
    st.sidebar.write(f"**{user['username']}** ({user['role']})")

    if st.sidebar.button("Выйти"):
        del st.session_state["user"]
        st.switch_page("app.py")

    st.info("Здесь будем вызывать хранимые процедуры, строить таблицы и графики успеваемости.")
