from pages.login import login_screen
import streamlit as st

def main_page():

    if "user" not in st.session_state:
        login_screen()
        return

    user = st.session_state["user"]

    st.sidebar.title("Пользователь")
    st.sidebar.write(f"**{user['username']}** ({user['role']})")

    if st.sidebar.button("Выйти"):
        del st.session_state["user"]
        st.rerun()

    st.title("Главная страница")
    st.write("Выберите нужный раздел в панели навигации (слева).")

    #st.page_link(func, "name") in future
    st.markdown(
        """
        Разделы:
        - Справочники:
            - Группы
            - Предметы
            - Люди
        - Журнал: оценки
        - Отчеты: отчеты
        """
    )