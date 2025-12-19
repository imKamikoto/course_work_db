from datetime import date
from sqlalchemy import select, func, and_

from db import get_session
from models import Mark, Person, Subject, Group


def avg_marks_analysis(
    date_from: date,
    date_to: date,
    group_id: int | None = None,
    student_id: int | None = None,
    subject_id: int | None = None,
    teacher_id: int | None = None,
    group_by: str = "group",
) -> list[dict]:
    with get_session() as session:
        conditions = [
            Mark.mark_date >= date_from,
            Mark.mark_date <= date_to,
        ]

        if group_id is not None:
            conditions.append(Person.group_id == group_id)
        if student_id is not None:
            conditions.append(Mark.student_id == student_id)
        if subject_id is not None:
            conditions.append(Mark.subject_id == subject_id)
        if teacher_id is not None:
            conditions.append(Mark.teacher_id == teacher_id)

        # student = Person (алиас)
        Student = Person
        Teacher = Person

        # join на student и teacher через алиасы
        from sqlalchemy.orm import aliased
        StudentA = aliased(Person)
        TeacherA = aliased(Person)

        base = (
            select()
            .select_from(Mark)
            .join(StudentA, StudentA.id == Mark.student_id)
            .join(TeacherA, TeacherA.id == Mark.teacher_id)
            .join(Subject, Subject.id == Mark.subject_id)
            .join(Group, Group.id == StudentA.group_id, isouter=True)
            .where(and_(*conditions))
        )

        avg_expr = func.avg(Mark.value).label("avg_value")
        cnt_expr = func.count(Mark.id).label("cnt")

        if group_by == "group":
            stmt = (
                base.with_only_columns(
                    Group.id.label("key_id"),
                    Group.name.label("key_name"),
                    avg_expr,
                    cnt_expr,
                )
                .group_by(Group.id, Group.name)
                .order_by(Group.name)
            )

        elif group_by == "student":
            stmt = (
                base.with_only_columns(
                    StudentA.id.label("key_id"),
                    (StudentA.last_name + " " + StudentA.first_name).label("key_name"),
                    avg_expr,
                    cnt_expr,
                )
                .group_by(StudentA.id, StudentA.last_name, StudentA.first_name)
                .order_by(StudentA.last_name, StudentA.first_name)
            )

        elif group_by == "subject":
            stmt = (
                base.with_only_columns(
                    Subject.id.label("key_id"),
                    Subject.name.label("key_name"),
                    avg_expr,
                    cnt_expr,
                )
                .group_by(Subject.id, Subject.name)
                .order_by(Subject.name)
            )

        elif group_by == "teacher":
            stmt = (
                base.with_only_columns(
                    TeacherA.id.label("key_id"),
                    (TeacherA.last_name + " " + TeacherA.first_name).label("key_name"),
                    avg_expr,
                    cnt_expr,
                )
                .group_by(TeacherA.id, TeacherA.last_name, TeacherA.first_name)
                .order_by(TeacherA.last_name, TeacherA.first_name)
            )

        elif group_by == "year":
            year_expr = func.extract("year", Mark.mark_date).cast(int).label("key_name")
            stmt = (
                base.with_only_columns(
                    year_expr,
                    avg_expr,
                    cnt_expr,
                )
                .group_by(year_expr)
                .order_by(year_expr)
            )
        else:
            raise ValueError("group_by must be one of: group, student, subject, teacher, year")

        rows = session.execute(stmt).all()

    result = []
    for r in rows:
        if group_by == "year":
            key_name, avg_value, cnt = r
            result.append({"key": str(key_name), "avg": float(avg_value), "count": int(cnt)})
        else:
            key_id, key_name, avg_value, cnt = r
            result.append({"id": int(key_id) if key_id is not None else None,
                           "name": key_name if key_name is not None else "—",
                           "avg": float(avg_value) if avg_value is not None else 0.0,
                           "count": int(cnt)})

    return result
