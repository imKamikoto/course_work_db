import streamlit as st
import pandas as pd

from .login import ensure_logged_in
from repos.people import (
    get_all_people,
    create_person,
    update_person,
    delete_person,
)
from repos.groups import get_all_groups


def people_page():
    ensure_logged_in()
    user = st.session_state["user"]

    st.title("Справочник: люди (студенты и преподаватели)")
    st.sidebar.title("Пользователь")
    st.sidebar.write(f"**{user['username']}** ({user['role']})")

    if st.sidebar.button("Выйти"):
        del st.session_state["user"]
        st.rerun()

    people = get_all_people()
    df = pd.DataFrame(people) if people else pd.DataFrame(
        columns=["id", "last_name", "first_name", "father_name", "type", "group_name"]
    )

    if not df.empty:
        df_display = df[["id", "last_name", "first_name", "father_name", "type", "group_name"]]
    else:
        df_display = df

    st.subheader("Список людей")
    st.dataframe(df_display, use_container_width=True)

    is_admin = user["role"] == "admin"
    if not is_admin:
        st.info("У вас нет прав для изменения данных (роль: user)")
        return

    groups = get_all_groups()
    groups_map = {g["id"]: g["name"] for g in groups}

    st.subheader("Добавить человека")
    with st.form("add_person_form"):
        last_name = st.text_input("Фамилия")
        first_name = st.text_input("Имя")
        father_name = st.text_input("Отчество (необязательно)")

        type_choice = st.selectbox(
            "Тип",
            options=[("Студент", "S"), ("Преподаватель", "P")],
            format_func=lambda t: t[0],
        )

        selected_group_id = None
        if type_choice[1] == "S":
            group_options = [("— выберите группу —", None)] + [
                (name, gid) for gid, name in groups_map.items()
            ]
            chosen = st.selectbox(
                "Группа",
                options=group_options,
                format_func=lambda x: x[0],
            )
            selected_group_id = chosen[1]

        submitted = st.form_submit_button("Добавить")
        if submitted:
            if not last_name.strip() or not first_name.strip():
                st.warning("Введите фамилию и имя")
            elif type_choice[1] == "S" and selected_group_id is None:
                st.warning("Выберите группу для студента")
            else:
                try:
                    create_person(
                        first_name=first_name.strip(),
                        last_name=last_name.strip(),
                        father_name=father_name.strip() or None,
                        group_id=selected_group_id if type_choice[1] == "S" else None,
                        person_type=type_choice[1],
                    )
                    st.success("Человек добавлен")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка при добавлении: {e}")

    st.subheader("Изменить / удалить человека")
    if not df.empty:
        selected_id = st.selectbox(
            "Выберите человека",
            options=df["id"].tolist(),
            format_func=lambda pid: (
                f"{df.loc[df['id'] == pid, 'last_name'].iloc[0]} "
                f"{df.loc[df['id'] == pid, 'first_name'].iloc[0]}"
            ),
        )

        row = df.loc[df["id"] == selected_id].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            last_name_edit = st.text_input("Фамилия", value=row["last_name"])
            first_name_edit = st.text_input("Имя", value=row["first_name"])
            father_name_edit = st.text_input(
                "Отчество (необязательно)", value=row.get("father_name") or ""
            )

            type_edit = st.selectbox(
                "Тип",
                options=[("Студент", "S"), ("Преподаватель", "P")],
                index=0 if row["type"] == "S" else 1,
                format_func=lambda t: t[0],
            )

            selected_group_id_edit = None
            if type_edit[1] == "S":
                group_options = [("— нет группы —", None)] + [
                    (name, gid) for gid, name in groups_map.items()
                ]
                current_gid = row.get("group_id")
                default_index = 0
                for i, (_, gid) in enumerate(group_options):
                    if gid == current_gid:
                        default_index = i
                        break

                chosen_edit = st.selectbox(
                    "Группа",
                    options=group_options,
                    index=default_index,
                    format_func=lambda x: x[0],
                )
                selected_group_id_edit = chosen_edit[1]

            if st.button("Сохранить изменения"):
                if not last_name_edit.strip() or not first_name_edit.strip():
                    st.warning("Введите фамилию и имя")
                elif type_edit[1] == "S" and selected_group_id_edit is None:
                    st.warning("Выберите группу для студента")
                else:
                    try:
                        update_person(
                            person_id=selected_id,
                            first_name=first_name_edit.strip(),
                            last_name=last_name_edit.strip(),
                            father_name=father_name_edit.strip() or None,
                            group_id=selected_group_id_edit if type_edit[1] == "S" else None,
                            person_type=type_edit[1],
                        )
                        st.success("Данные обновлены")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка при обновлении: {e}")

        with col2:
            if st.button("Удалить этого человека"):
                try:
                    delete_person(selected_id)
                    st.success("Человек удалён")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка при удалении: {e}")
    else:
        st.write("Людей пока нет.")
