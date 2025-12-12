from sqlalchemy import select
from sqlalchemy.orm import Session

from db import get_session
from models import Subject


def get_all_subjects() -> list[dict]:
    with get_session() as session:
        stmt = select(Subject).order_by(Subject.name)
        subjects = session.scalars(stmt).all()

    return [{"id": s.id, "name": s.name} for s in subjects]


def create_subject(name: str):
    with get_session() as session:
        subj = Subject(name=name)
        session.add(subj)
        session.commit()


def update_subject(subject_id: int, new_name: str):
    with get_session() as session:
        subj = session.get(Subject, subject_id)
        if subj is None:
            raise ValueError(f"Предмет id={subject_id} не найден")

        subj.name = new_name
        session.commit()


def delete_subject(subject_id: int):
    with get_session() as session:
        subj = session.get(Subject, subject_id)
        if subj is None:
            raise ValueError(f"Предмет id={subject_id} не найден")

        session.delete(subj)
        session.commit()
