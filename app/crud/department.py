from sqlalchemy.orm import Session

from .. import models, schemas


def create_department(db: Session, department: schemas.DepartmentCreate):
    db_department = models.Department(
        sigaa_id=department.sigaa_id,
        title=department.title,
        acronym=department.acronym
    )

    db.add(db_department)
    db.commit()
    db.refresh(db_department)

    return db_department


def get_departments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Department).offset(skip).limit(limit).all()


def get_department(db: Session, department_id):
    return db.query(models.Department).filter(models.Department.id == department_id).one()


def get_department_by_sigaa_id(db: Session, department_sigaa_id: int):
    return db.query(models.Department).filter(models.Department.sigaa_id == department_sigaa_id).first()
