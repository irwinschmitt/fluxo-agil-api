from enum import Enum
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM

from .database import Base


class Department(Base):
    __tablename__ = "Department"

    id = Column(Integer, primary_key=True, index=True)
    sigaa_id = Column(Integer, index=True)
    acronym = Column(String)
    title = Column(String)


class ProgramDegree(Enum):
    BACHELOR = "BACHELOR"
    LICENTIATE = "LICENTIATE"


class ProgramShift(Enum):
    DAY = "DAY"
    NIGHT = "NIGHT"


class Program(Base):
    __tablename__ = "Program"

    id = Column(Integer, primary_key=True, index=True)
    sigaa_id = Column(Integer, index=True)
    title = Column(String)
    degree = Column(ENUM(ProgramDegree, name="ProgramDegree"))
    shift = Column(ENUM(ProgramShift, name="ProgramShift"))

    department_id = Column(Integer, ForeignKey("Department.id"))


class Curriculum(Base):
    __tablename__ = "Curriculum"

    id = Column(Integer, primary_key=True, index=True)
    sigaa_id = Column(Integer, index=True)
    active = Column(Boolean)
    start_year = Column(Integer)
    star_period = Column(Integer)
    min_periods = Column(Integer)
    max_periods = Column(Integer)
    min_period_workload = Column(Integer)
    max_period_workload = Column(Integer)
    min_workload = Column(Integer)
    mandatory_components_workload = Column(Integer)
    min_elective_components_workload = Column(Integer)
    max_elective_components_workload = Column(Integer)
    min_complementary_components_workload = Column(Integer)
    max_complementary_components_workload = Column(Integer)

    program_id = Column(Integer, ForeignKey("Program.id"))


class ComponentType(Enum):
    COURSE = "COURSE"
    ACTIVITY = "ACTIVITY"


class Component(Base):
    __tablename__ = "Component"

    id = Column(Integer, primary_key=True, index=True)
    sigaa_id = Column(String, index=True)
    title = Column(String)
    type = Column(ENUM(ComponentType, name="ComponentType"))

    department_id = Column(Integer, ForeignKey("Department.id"))


class CurriculumComponentType(Enum):
    MANDATORY = "MANDATORY"
    ELECTIVE = "ELECTIVE"


class CurriculumComponent(Base):
    __tablename__ = "CurriculumComponent"

    id = Column(Integer, primary_key=True, index=True)

    curriculum_id = Column(Integer, ForeignKey("Curriculum.id"))
    component_id = Column(Integer, ForeignKey("Component.id"))
    type = Column(ENUM(CurriculumComponentType, name="CurriculumComponentType"))
    percentage_prerequisite = Column(Integer)


class PrerequisiteOption(Base):
    __tablename__ = "PrerequisiteOption"

    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(Integer, ForeignKey("Component.id"))


class PrerequisiteComponent(Base):
    __tablename__ = "PrerequisiteComponent"

    id = Column(Integer, primary_key=True, index=True)
    prerequisite_option_id = Column(
        Integer, ForeignKey("PrerequisiteOption.id"))
    component_id = Column(Integer, ForeignKey("Component.id"))


class EquivalenceOption(Base):
    __tablename__ = "EquivalenceOption"

    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(Integer, ForeignKey("Component.id"))


class EquivalenceComponent(Base):
    __tablename__ = "EquivalenceComponent"

    id = Column(Integer, primary_key=True, index=True)
    prerequisite_option_id = Column(
        Integer, ForeignKey("EquivalenceOption.id"))
    component_id = Column(Integer, ForeignKey("Component.id"))


class Corequisite(Base):
    __tablename__ = "Corequisite"

    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(Integer, ForeignKey("Component.id"))
    corequisite_id = Column(Integer, ForeignKey("Component.id"))
