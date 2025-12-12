from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Text, String, CheckConstraint, ForeignKey, CHAR
from db import Base


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    students: Mapped[list["Person"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(Text, nullable=False)
    last_name: Mapped[str] = mapped_column(Text, nullable=False)
    father_name: Mapped[str | None] = mapped_column(Text, nullable=True)

    group_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("groups.id", ondelete="SET NULL"),
        nullable=True,
    )

    type: Mapped[str] = mapped_column(
        CHAR(1),
        CheckConstraint("type IN ('S','P')"),
        nullable=False,
    )

    group: Mapped[Group | None] = relationship(back_populates="students")

    student_marks: Mapped[list["Mark"]] = relationship(
        back_populates="student",
        foreign_keys="Mark.student_id",
    )
    teacher_marks: Mapped[list["Mark"]] = relationship(
        back_populates="teacher",
        foreign_keys="Mark.teacher_id",
    )


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    marks: Mapped[list["Mark"]] = relationship(back_populates="subject")


class Mark(Base):
    __tablename__ = "marks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("people.id", ondelete="CASCADE"),
        nullable=False,
    )
    subject_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
    )
    teacher_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("people.id", ondelete="CASCADE"),
        nullable=False,
    )

    value: Mapped[int] = mapped_column(Integer, nullable=False)

    student: Mapped[Person] = relationship(
        back_populates="student_marks",
        foreign_keys=[student_id],
    )
    teacher: Mapped[Person] = relationship(
        back_populates="teacher_marks",
        foreign_keys=[teacher_id],
    )
    subject: Mapped[Subject] = relationship(back_populates="marks")


class AppUser(Base):
    __tablename__ = "app_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(
        String(10),
        CheckConstraint("role IN ('admin','user')"),
        nullable=False,
    )
