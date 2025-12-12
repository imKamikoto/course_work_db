import streamlit as st
import pandas as pd

from .login import ensure_logged_in
from repos.marks import (
    get_all_marks,
    create_mark,
    update_mark,
    delete_mark,
)
from repos.people import get_students, get_teachers
from repos.subjects import get_all_subjects


def grades_page():
    ensure_logged_in()
    user = st.session_state["user"]

    st.title("Журнал: оценки")
    st.sidebar.title("Пользователь")
    st.sidebar.write(f"**{user['username']}** ({user['role']})")

    if st.sidebar.button("Выйти"):
        del st.session_state["user"]
        st.rerun()

    marks = get_all_marks()
    if marks:
        df = pd.DataFrame(marks)
        df_display = df[["id", "student_name", "subject_name", "teacher_name", "value"]]
    else:
        df = pd.DataFrame(columns=["id", "student_name", "subject_name", "teacher_name", "value"])
        df_display = df

    st.subheader("Список оценок")
    st.dataframe(df_display, use_container_width=True)

    is_admin = user["role"] == "admin"
    if not is_admin:
        st.info("У вас нет прав для изменения данных (роль: user)")
        return

    students = get_students()
    teachers = get_teachers()
    subjects = get_all_subjects()

    if not students or not teachers or not subjects:
        st.warning("Для работы журнала нужны студенты, преподаватели и предметы.")
        return

    student_options = [
        (f"{s['last_name']} {s['first_name']} ({s['group_name']})", s["id"])
        for s in students
    ]
    teacher_options = [
        (f"{t['last_name']} {t['first_name']}", t["id"])
        for t in teachers
    ]
    subject_options = [
        (s["name"], s["id"])
        for s in subjects
    ]

    st.subheader("Добавить оценку")
    with st.form("add_mark_form"):
        student_choice = st.selectbox(
            "Студент",
            options=student_options,
            format_func=lambda x: x[0],
        )
        subject_choice = st.selectbox(
            "Предмет",
            options=subject_options,
            format_func=lambda x: x[0],
        )
        teacher_choice = st.selectbox(
            "Преподаватель",
            options=teacher_options,
            format_func=lambda x: x[0],
        )

        value = st.number_input(
            "Оценка",
            min_value=2,
            max_value=5,
            step=1,
            value=5,
        )

        submitted = st.form_submit_button("Добавить")
        if submitted:
            try:
                create_mark(
                    student_id=student_choice[1],
                    subject_id=subject_choice[1],
                    teacher_id=teacher_choice[1],
                    value=int(value),
                )
                st.success("Оценка добавлена")
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка при добавлении: {e}")

    st.subheader("Изменить / удалить оценку")
    if not df.empty:
        selected_id = st.selectbox(
            "Выберите оценку",
            options=df["id"].tolist(),
            format_func=lambda mid: (
                f"{df.loc[df['id'] == mid, 'student_name'].iloc[0]} — "
                f"{df.loc[df['id'] == mid, 'subject_name'].iloc[0]} "
                f"({df.loc[df['id'] == mid, 'value'].iloc[0]})"
            ),
        )

        row = df.loc[df["id"] == selected_id].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            student_idx = 0
            for i, (_, sid) in enumerate(student_options):
                if sid == row["student_id"]:
                    student_idx = i
                    break
            student_edit = st.selectbox(
                "Студент (ред.)",
                options=student_options,
                index=student_idx,
                format_func=lambda x: x[0],
                key="edit_student",
            )

            subject_idx = 0
            for i, (_, sid) in enumerate(subject_options):
                if sid == row["subject_id"]:
                    subject_idx = i
                    break
            subject_edit = st.selectbox(
                "Предмет (ред.)",
                options=subject_options,
                index=subject_idx,
                format_func=lambda x: x[0],
                key="edit_subject",
            )

            teacher_idx = 0
            for i, (_, tid) in enumerate(teacher_options):
                if tid == row["teacher_id"]:
                    teacher_idx = i
                    break
            teacher_edit = st.selectbox(
                "Преподаватель (ред.)",
                options=teacher_options,
                index=teacher_idx,
                format_func=lambda x: x[0],
                key="edit_teacher",
            )

            value_edit = st.number_input(
                "Оценка (ред.)",
                min_value=2,
                max_value=5,
                step=1,
                value=int(row["value"]),
                key="edit_value",
            )

            if st.button("Сохранить изменения"):
                try:
                    update_mark(
                        mark_id=selected_id,
                        student_id=student_edit[1],
                        subject_id=subject_edit[1],
                        teacher_id=teacher_edit[1],
                        value=int(value_edit),
                    )
                    st.success("Оценка обновлена")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка при обновлении: {e}")

        with col2:
            if st.button("Удалить эту оценку"):
                try:
                    delete_mark(selected_id)
                    st.success("Оценка удалена")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка при удалении: {e}")
    else:
        st.write("Оценок пока нет.")
