import streamlit as st
from repos.user import check_credentials


def ensure_logged_in():
    if "user" not in st.session_state:
        st.error("Сначала войдите в систему на главной странице.")
        st.stop()


def login_screen():
    st.title("Система деканата — вход")

    username = st.text_input("Логин")
    password = st.text_input("Пароль", type="password")



    if st.button("Войти"):
        user = check_credentials(username, password)
        if user is None:
            st.error("Неверный логин или пароль")
        else:
            st.session_state["user"] = user
            st.success(f"Успешный вход как {user['username']} ({user['role']})")
            st.rerun()
