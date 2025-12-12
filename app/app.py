import sys
import streamlit as st
from db import init_db

if not sys.argv[1].endswith(".ini"):
    st.error("Не удалось подключиться к базе данных.")
    st.code("Запуск приложения возможен только из командной строки с указанием файла конфигурации.")
    st.stop()

try:
    init_db(sys.argv[1])
except Exception as e:
    st.set_page_config(page_title="Система деканата", layout="wide")
    st.error("Не удалось подключиться к базе данных.")
    st.code(str(e))
    st.stop()

from pages.login import login_screen
from pages.main import main_page
from pages.dir_groups import groups_page
from pages.dir_of_subjects import subjects_page
from pages.dir_people import people_page
from pages.grade_book import grades_page
from pages.reports import reports_page


st.set_page_config(page_title="Система деканата", layout="wide")

login = st.Page(login_screen, title="Вход", icon="🔐", url_path="login")
main = st.Page(main_page, title="Главная", icon="🏠", url_path="home")
groups = st.Page(groups_page, title="Группы", icon="👥", url_path="groups")
subjects = st.Page(subjects_page, title="Предметы", icon="📚", url_path="subjects")
people = st.Page(people_page, title="Люди", icon="🧑‍🎓", url_path="people")
grades = st.Page(grades_page, title="Оценки", icon="📝", url_path="grades")
reports = st.Page(reports_page, title="Отчеты", icon="📊", url_path="reports")

pg = st.navigation({
    "Общее": [
        main,
    ],
    "Справочники": [
        groups,
        subjects,
        people,
    ],
    "Журнал": [
        grades,
    ],
    "Отчёты": [
        reports,
    ],
})

pg.run()
