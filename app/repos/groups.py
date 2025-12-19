from sqlalchemy import select
from sqlalchemy.orm import Session

from db import get_session
from models import Group


def get_all_groups():
    with get_session() as session:
        stmt = select(Group).order_by(Group.name)
        groups = session.scalars(stmt).all()

    return [{"id": g.id, "name": g.name} for g in groups]


def create_group(name: str):
    with get_session() as session:
        group = Group(name=name)
        session.add(group)
        session.commit()


def update_group(group_id: int, new_name: str):
    with get_session() as session:
        group = session.get(Group, group_id)
        if group is None:
            raise ValueError(f"Группа id={group_id} не найдена")
        group.name = new_name
        session.commit()


def delete_group(group_id: int):
    with get_session() as session:
        group = session.get(Group, group_id)
        if group is None:
            raise ValueError(f"Группа id={group_id} не найдена")
        session.delete(group)
        session.commit()
