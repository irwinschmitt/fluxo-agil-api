from sqlalchemy.orm import Session

from ..models import orm

from ..models import pydantic


def create_department(db: Session, department: pydantic.DepartmentCreate):
    db_department = orm.Department(
        sigaa_id=department.sigaa_id,
        title=department.title,
        acronym=department.acronym
    )

    db.add(db_department)
    db.commit()
    db.refresh(db_department)

    return db_department


def get_departments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(orm.Department).offset(skip).limit(limit).all()


def get_department(db: Session, department_id):
    return db.query(orm.Department).filter(orm.Department.id == department_id).one()


def get_department_by_sigaa_id(db: Session, department_sigaa_id: int):
    return db.query(orm.Department).filter(orm.Department.sigaa_id == department_sigaa_id).first()
