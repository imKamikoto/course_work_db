import streamlit as st
import pandas as pd

from .login import ensure_logged_in
from repos.subjects import (
    get_all_subjects,
    create_subject,
    update_subject,
    delete_subject,
)


def subjects_page():
    ensure_logged_in()
    user = st.session_state["user"]

    st.title("Справочник: предметы")
    st.sidebar.title("Пользователь")
    st.sidebar.write(f"**{user['username']}** ({user['role']})")

    if st.sidebar.button("Выйти"):
        del st.session_state["user"]
        st.rerun()

    rows = get_all_subjects()
    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["id", "name"])

    st.subheader("Список предметов")
    st.dataframe(df, use_container_width=True)

    is_admin = user["role"] == "admin"
    if not is_admin:
        st.info("У вас нет прав для изменения данных (роль: user)")
        return

    st.subheader("Добавить предмет")
    with st.form("add_subject_form"):
        new_name = st.text_input("Наименование предмета")
        submitted = st.form_submit_button("Добавить")
        if submitted:
            name = new_name.strip()
            if not name:
                st.warning("Введите название предмета")
            else:
                try:
                    create_subject(name)
                    st.success("Предмет добавлен")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка при добавлении: {e}")

    st.subheader("Изменить / удалить предмет")
    if not df.empty:
        selected_id = st.selectbox(
            "Выберите предмет",
            options=df["id"].tolist(),
            format_func=lambda sid: df.loc[df["id"] == sid, "name"].iloc[0],
        )

        col1, col2 = st.columns(2)

        with col1:
            default_name = df.loc[df["id"] == selected_id, "name"].iloc[0]
            new_name = st.text_input(
                "Новое имя предмета",
                value=default_name,
                key="edit_subject_name",
            )
            if st.button("Сохранить изменения"):
                name = new_name.strip()
                if not name:
                    st.warning("Имя не может быть пустым")
                else:
                    try:
                        update_subject(selected_id, name)
                        st.success("Предмет обновлён")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка при изменении: {e}")

        with col2:
            if st.button("Удалить выбранный предмет"):
                try:
                    delete_subject(selected_id)
                    st.success("Предмет удалён")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка при удалении: {e}")
    else:
        st.write("Предметов пока нет.")
