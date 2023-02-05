from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .crud import department
from . import models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.post("/departments/", response_model=schemas.Department)
def create_department(department: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    db_department = department.get_department_by_sigaa_id(
        db, department.sigaa_id)

    if db_department:
        raise HTTPException(
            status_code=400,
            detail="Já existe um departamento com esse id do SIGAA."
        )

    return department.create_department(db, department)


@app.get("/departments/", response_model=list[schemas.Department])
def read_departments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return department.get_departments(db, skip, limit)


@app.get("/departments/{department_id}", response_model=schemas.Department)
def read_department(department_id: int, db: Session = Depends(get_db)):
    return department.get_department(db, department_id)
