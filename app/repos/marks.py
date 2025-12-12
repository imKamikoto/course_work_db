from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from db import get_session
from models import Mark, Person, Subject


def get_all_marks() -> list[dict]:
    with get_session() as session:
        stmt = (
            select(Mark)
            .options(
                joinedload(Mark.student),
                joinedload(Mark.teacher),
                joinedload(Mark.subject),
            )
            .order_by(Mark.id)
        )
        marks = session.scalars(stmt).all()

    result: list[dict] = []
    for m in marks:
        st = m.student
        th = m.teacher
        sb = m.subject

        student_name = " ".join(
            filter(None, [st.last_name if st else None,
                          st.first_name if st else None,
                          st.father_name if st else None])
        ) if st else None

        teacher_name = " ".join(
            filter(None, [th.last_name if th else None,
                          th.first_name if th else None,
                          th.father_name if th else None])
        ) if th else None

        result.append(
            {
                "id": m.id,
                "value": m.value,
                "student_id": m.student_id,
                "teacher_id": m.teacher_id,
                "subject_id": m.subject_id,
                "student_name": student_name,
                "teacher_name": teacher_name,
                "subject_name": sb.name if sb else None,
            }
        )
    return result


def create_mark(student_id: int, subject_id: int, teacher_id: int, value: int):
    with get_session() as session:
        mark = Mark(
            student_id=student_id,
            subject_id=subject_id,
            teacher_id=teacher_id,
            value=value,
        )
        session.add(mark)
        session.commit()


def update_mark(
    mark_id: int,
    student_id: int,
    subject_id: int,
    teacher_id: int,
    value: int,
):
    with get_session() as session:
        mark = session.get(Mark, mark_id)
        if mark is None:
            raise ValueError(f"Оценка id={mark_id} не найдена")

        mark.student_id = student_id
        mark.subject_id = subject_id
        mark.teacher_id = teacher_id
        mark.value = value

        session.commit()


def delete_mark(mark_id: int):
    with get_session() as session:
        mark = session.get(Mark, mark_id)
        if mark is None:
            raise ValueError(f"Оценка id={mark_id} не найдена")

        session.delete(mark)
        session.commit()
