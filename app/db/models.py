"""
SQL Alchemy models declaration.
https://docs.sqlalchemy.org/en/14/orm/declarative_styles.html#example-two-dataclasses-with-declarative-table
Dataclass style for powerful autocompletion support.

https://alembic.sqlalchemy.org/en/latest/tutorial.html
Note, it is used by alembic migrations logic, see `alembic/env.py`

Alembic shortcuts:
# create migration
alembic revision --autogenerate -m "migration_name"

# apply all migrations
alembic upgrade head
"""
import uuid
from typing import Annotated, Literal

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

int_pk = Annotated[int, mapped_column(primary_key=True)]
int_unique_index = Annotated[int, mapped_column(index=True, unique=True)]
str_unique_index = Annotated[str, mapped_column(index=True, unique=True)]


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_model"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda _: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(
        String(254), nullable=False, unique=True, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)


class Department(Base):
    __tablename__ = "department"

    id: Mapped[int_pk]
    sigaa_id: Mapped[int_unique_index]
    acronym: Mapped[str]
    title: Mapped[str]


class Program(Base):
    __tablename__ = "program"

    id: Mapped[int_pk]
    sigaa_id: Mapped[int_unique_index]
    title: Mapped[str]
    degree: Mapped[Literal["BACHELOR", "LICENTIATE"] | None]
    shift: Mapped[Literal["DAY", "NIGHT"] | None]

    department_id: Mapped[int] = mapped_column(ForeignKey("department.id"))


class Curriculum(Base):
    __tablename__ = "curriculum"

    id: Mapped[int_pk]
    sigaa_id: Mapped[str_unique_index]
    active: Mapped[bool]
    start_year: Mapped[int]
    start_period: Mapped[int]
    min_periods: Mapped[int]
    max_periods: Mapped[int]
    min_period_workload: Mapped[int]
    max_period_workload: Mapped[int]
    min_workload: Mapped[int]
    mandatory_components_workload: Mapped[int]
    min_elective_components_workload: Mapped[int]
    max_elective_components_workload: Mapped[int]
    min_complementary_components_workload: Mapped[int]
    max_complementary_components_workload: Mapped[int]

    program_id: Mapped[int] = mapped_column(ForeignKey("program.id"))


class Component(Base):
    __tablename__ = "component"

    id: Mapped[int_pk]
    sigaa_id: Mapped[str_unique_index]
    title: Mapped[str]
    type: Mapped[Literal["COURSE", "ACTIVITY"]]

    department_id: Mapped[int] = mapped_column(ForeignKey("department.id"))


class CurriculumComponent(Base):
    __tablename__ = "curriculum_component"

    id: Mapped[int_pk]
    type: Mapped[Literal["MANDATORY", "ELECTIVE"]]
    percentage_prerequisite: Mapped[int]

    curriculum_id: Mapped[int] = mapped_column(ForeignKey("curriculum.id"))
    component_id: Mapped[int] = mapped_column(ForeignKey("component.id"))


class PrerequisiteOption(Base):
    __tablename__ = "prerequisite_option"

    id: Mapped[int_pk]

    component_id: Mapped[int] = mapped_column(ForeignKey("component.id"))


class PrerequisiteComponent(Base):
    __tablename__ = "prerequisite_component"

    id: Mapped[int_pk]

    component_id: Mapped[int] = mapped_column(ForeignKey("component.id"))
    prerequisite_option_id: Mapped[int] = mapped_column(
        ForeignKey("prerequisite_option.id")
    )


class EquivalenceOption(Base):
    __tablename__ = "equivalence_option"

    id: Mapped[int_pk]

    component_id: Mapped[int] = mapped_column(ForeignKey("component.id"))


class EquivalenceComponent(Base):
    __tablename__ = "equivalence_component"

    id: Mapped[int_pk]

    component_id: Mapped[int] = mapped_column(ForeignKey("component.id"))
    equivalence_option_id: Mapped[int] = mapped_column(
        ForeignKey("equivalence_option.id")
    )


class Corequisite(Base):
    __tablename__ = "corequisite"

    id: Mapped[int_pk]

    component_id: Mapped[int] = mapped_column(ForeignKey("component.id"))
    corequisite_id: Mapped[int] = mapped_column(ForeignKey("component.id"))
