from datetime import date, timedelta

import streamlit as st
import io
import pandas as pd
import matplotlib.pyplot as plt

from .login import ensure_logged_in
from repos.reports import avg_marks_analysis
from repos.groups import get_all_groups
from repos.people import get_students, get_teachers
from repos.subjects import get_all_subjects


def reports_page():
    ensure_logged_in()
    user = st.session_state["user"]

    st.title("Отчёты: анализ среднего балла по интервалу дат")
    st.sidebar.title("Пользователь")
    st.sidebar.write(f"**{user['username']}** ({user['role']})")

    if st.sidebar.button("Выйти"):
        del st.session_state["user"]
        st.rerun()

    st.subheader("Параметры анализа")

    today = date.today()
    default_from = today - timedelta(days=30)

    col_a, col_b = st.columns(2)
    with col_a:
        d_from = st.date_input("Дата с", value=default_from)
    with col_b:
        d_to = st.date_input("Дата по", value=today)

    if d_from > d_to:
        st.error("Дата 'с' не может быть позже даты 'по'.")
        st.stop()

    groups = get_all_groups()
    students = get_students()
    teachers = get_teachers()
    subjects = get_all_subjects()

    group_opts = [("Все группы", None)] + [(g["name"], g["id"]) for g in groups]
    subj_opts = [("Все предметы", None)] + [(s["name"], s["id"]) for s in subjects]
    teacher_opts = [("Все преподаватели", None)] + [
        (f'{t["last_name"]} {t["first_name"]}', t["id"]) for t in teachers
    ]
    student_opts = [("Все студенты", None)] + [
        (f'{s["last_name"]} {s["first_name"]} ({s["group_name"]})', s["id"]) for s in students
    ]

    col1, col2 = st.columns(2)
    with col1:
        group_choice = st.selectbox("Группа", options=group_opts, format_func=lambda x: x[0])
        subject_choice = st.selectbox("Предмет", options=subj_opts, format_func=lambda x: x[0])
    with col2:
        teacher_choice = st.selectbox("Преподаватель", options=teacher_opts, format_func=lambda x: x[0])
        student_choice = st.selectbox("Студент", options=student_opts, format_func=lambda x: x[0])

    group_id = group_choice[1]
    subject_id = subject_choice[1]
    teacher_id = teacher_choice[1]
    student_id = student_choice[1]

    group_by = st.selectbox(
        "Разрез (по чему считать средний балл)",
        options=[
            ("Группы", "group"),
            ("Студенты", "student"),
            ("Предметы", "subject"),
            ("Преподаватели", "teacher"),
            ("Года (по датам оценок)", "year"),
        ],
        format_func=lambda x: x[0],
    )[1]

    view_mode = st.radio("Показать результат", options=["Таблица", "График", "Таблица + график"], horizontal=True)

    if st.button("Рассчитать"):
        try:
            data = avg_marks_analysis(
                date_from=d_from,
                date_to=d_to,
                group_id=group_id,
                student_id=student_id,
                subject_id=subject_id,
                teacher_id=teacher_id,
                group_by=group_by,
            )
        except Exception as e:
            st.error(f"Ошибка расчёта: {e}")
            st.stop()

        if not data:
            st.info("Нет данных для выбранных фильтров/интервала.")
            st.stop()

        df = pd.DataFrame(data)

        st.subheader("Экспорт")

        col_e1, col_e2 = st.columns(2)

        with col_e1:
            txt = df.to_string(index=False)
            st.download_button(
                label="Скачать TXT",
                data=txt.encode("utf-8"),
                file_name="report.txt",
                mime="text/plain; charset=utf-8",
            )

        with col_e2:
            csv = df.to_csv(index=False, sep=";")
            st.download_button(
                label="Скачать CSV",
                data=csv.encode("utf-8"),
                file_name="report.csv",
                mime="text/csv; charset=utf-8",
            )

        if view_mode in ("Таблица", "Таблица + график"):
            st.subheader("Результат (таблица)")
            st.dataframe(df, use_container_width=True)

        if view_mode in ("График", "Таблица + график"):
            st.subheader("Результат (график)")

            fig = plt.figure()
            ax = fig.add_subplot(111)

            if group_by == "year":
                x = df["key"].astype(str).tolist()
            else:
                x = df["name"].astype(str).tolist()

            y = df["avg"].astype(float).tolist()

            ax.plot(x, y, marker="o")
            ax.set_ylabel("Средний балл")
            ax.set_xlabel("Категория")
            ax.set_title(f"Средний балл за период {d_from} — {d_to}")
            ax.grid(True)
            plt.xticks(rotation=45, ha="right")

            st.pyplot(fig)
