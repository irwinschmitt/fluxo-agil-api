from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models.orm import Base
from app.models.pydantic import Department, DepartmentCreate
from app.crud import department

Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.post("/departments/", response_model=Department)
def create_department(new_department: DepartmentCreate, db: Session = Depends(get_db)):
    db_department = department.get_department_by_sigaa_id(
        db, new_department.sigaa_id)

    if db_department:
        raise HTTPException(
            status_code=400,
            detail="Já existe um departamento com esse id do SIGAA."
        )

    return department.create_department(db, new_department)


@app.get("/departments/", response_model=list[Department])
def read_departments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return department.get_departments(db, skip, limit)


@app.get("/departments/{department_id}", response_model=Department)
def read_department(department_id: int, db: Session = Depends(get_db)):
    return department.get_department(db, department_id)
