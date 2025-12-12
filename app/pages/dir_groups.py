import streamlit as st
import pandas as pd

from .login import ensure_logged_in
from repos.groups import (
    get_all_groups,
    create_group,
    update_group,
    delete_group,
)


def groups_page():
    ensure_logged_in()
    user = st.session_state["user"]

    st.title("Справочник: группы")
    st.sidebar.title("Пользователь")
    st.sidebar.write(f"**{user['username']}** ({user['role']})")

    if st.sidebar.button("Выйти"):
        del st.session_state["user"]
        st.rerun()

    # чтение
    rows = get_all_groups()
    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["id", "name"])

    st.subheader("Список групп")
    st.dataframe(df, use_container_width=True)

    is_admin = user["role"] == "admin"
    if not is_admin:
        st.info("У вас нет прав для изменения данных (роль: user)")
        return

    # добавление
    st.subheader("Добавить группу")
    with st.form("add_group_form"):
        new_name = st.text_input("Наименование группы")
        submitted = st.form_submit_button("Добавить")
        if submitted:
            name = new_name.strip()
            if not name:
                st.warning("Введите наименование группы")
            else:
                try:
                    create_group(name)
                    st.success("Группа добавлена")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка при добавлении: {e}")

    # редактирование / удаление
    st.subheader("Изменить / удалить группу")
    if not df.empty:
        selected_id = st.selectbox(
            "Выберите группу",
            options=df["id"].tolist(),
            format_func=lambda gid: df.loc[df["id"] == gid, "name"].iloc[0],
        )

        col1, col2 = st.columns(2)

        with col1:
            default_name = df.loc[df["id"] == selected_id, "name"].iloc[0]
            new_name = st.text_input(
                "Новое имя группы",
                value=default_name,
                key="edit_group_name",
            )
            if st.button("Сохранить изменения"):
                name = new_name.strip()
                if not name:
                    st.warning("Имя не может быть пустым")
                else:
                    try:
                        update_group(selected_id, name)
                        st.success("Группа обновлена")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка при изменении: {e}")

        with col2:
            if st.button("Удалить выбранную группу"):
                try:
                    delete_group(selected_id)
                    st.success("Группа удалена")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка при удалении: {e}")
    else:
        st.write("Групп в базе пока нет.")
