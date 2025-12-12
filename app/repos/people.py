from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db import get_session
from models import Person, Group


def get_all_people() -> list[dict]:
    with get_session() as session:
        stmt = (
            select(Person, Group)
            .select_from(Person)
            .join(Group, Person.group_id == Group.id, isouter=True)
            .order_by(Person.type, Person.last_name, Person.first_name)
        )
        rows = session.execute(stmt).all()

    result: list[dict] = []
    for person, group in rows:
        result.append(
            {
                "id": person.id,
                "first_name": person.first_name,
                "last_name": person.last_name,
                "father_name": person.father_name,
                "type": person.type,
                "group_id": person.group_id,
                "group_name": group.name if group else None,
            }
        )
    return result


def get_students() -> list[dict]:
    with get_session() as session:
        stmt = (
            select(Person, Group)
            .select_from(Person)
            .join(Group, Person.group_id == Group.id, isouter=True)
            .where(Person.type == "S")
            .order_by(Person.last_name, Person.first_name)
        )
        rows = session.execute(stmt).all()

    res: list[dict] = []
    for p, g in rows:
        res.append(
            {
                "id": p.id,
                "first_name": p.first_name,
                "last_name": p.last_name,
                "father_name": p.father_name,
                "group_id": p.group_id,
                "group_name": g.name if g else None,
            }
        )
    return res


def get_teachers() -> list[dict]:
    with get_session() as session:
        stmt = (
            select(Person)
            .where(Person.type == "P")
            .order_by(Person.last_name, Person.first_name)
        )
        teachers = session.scalars(stmt).all()

    return [
        {
            "id": t.id,
            "first_name": t.first_name,
            "last_name": t.last_name,
            "father_name": t.father_name,
        }
        for t in teachers
    ]


def create_person(
    first_name: str,
    last_name: str,
    father_name: Optional[str],
    group_id: Optional[int],
    person_type: str,
):
    with get_session() as session:
        person = Person(
            first_name=first_name,
            last_name=last_name,
            father_name=father_name,
            group_id=group_id,
            type=person_type,
        )
        session.add(person)
        session.commit()


def update_person(
    person_id: int,
    first_name: str,
    last_name: str,
    father_name: Optional[str],
    group_id: Optional[int],
    person_type: str,
):
    with get_session() as session:
        person = session.get(Person, person_id)
        if person is None:
            raise ValueError(f"Человек id={person_id} не найден")

        person.first_name = first_name
        person.last_name = last_name
        person.father_name = father_name
        person.group_id = group_id
        person.type = person_type

        session.commit()


def delete_person(person_id: int):
    with get_session() as session:
        person = session.get(Person, person_id)
        if person is None:
            raise ValueError(f"Человек id={person_id} не найден")
        session.delete(person)
        session.commit()
