from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.db.models import Department
from app.schemas.requests import DepartmentCreateRequest, DepartmentUpdateRequest
from app.schemas.responses import DepartmentResponse

router = APIRouter()


@router.post("/departments", response_model=DepartmentResponse, status_code=201)
async def create_department(
    department: DepartmentCreateRequest,
    session: AsyncSession = Depends(deps.get_session),
):
    """Create a department"""
    result = await session.execute(
        select(Department).where(Department.sigaa_id == department.sigaa_id)
    )

    if result.scalars().one_or_none() is not None:
        raise HTTPException(status_code=400, detail="SIGAA ID já cadastrado")

    department = Department(**department.dict())

    session.add(department)
    await session.commit()
    await session.refresh(department)

    return department


@router.post("/departments/bulk", status_code=207)
async def create_departments(
    departments: list[DepartmentCreateRequest],
    session: AsyncSession = Depends(deps.get_session),
):
    """Create or update departments in bulk"""
    result = await session.execute(
        select(Department).where(
            Department.sigaa_id.in_([d.sigaa_id for d in departments])
        )
    )

    db_departments = result.scalars().all()

    for department in departments:
        db_department = next(
            (d for d in db_departments if d.sigaa_id == department.sigaa_id), None
        )

        if db_department is None:
            db_department = Department(**department.dict())
            session.add(db_department)
        else:
            db_department.acronym = department.acronym
            db_department.title = department.title

    await session.commit()


@router.patch("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    department: DepartmentUpdateRequest,
    session: AsyncSession = Depends(deps.get_session),
):
    """Update a department"""
    result = await session.execute(
        select(Department).where(Department.id == department_id)
    )

    db_department = result.scalars().one_or_none()

    if db_department is None:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    if department.acronym is not None:
        db_department.acronym = department.acronym

    if department.title is not None:
        db_department.title = department.title

    await session.commit()
    await session.refresh(db_department)

    return db_department


@router.get("/departments", response_model=list[DepartmentResponse])
async def read_departments(
    session: AsyncSession = Depends(deps.get_session),
    skip: int = 0,
    limit: int = 100,
):
    """Get all departments"""
    result = await session.execute(select(Department).offset(skip).limit(limit))

    return result.scalars().all()


@router.get("/departments/{department_id}", response_model=DepartmentResponse)
async def read_department(
    department_id: int, session: AsyncSession = Depends(deps.get_session)
):
    """Get a department"""
    result = await session.execute(
        select(Department).where(Department.id == department_id)
    )

    department = result.scalars().one_or_none()

    if department is None:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    return department


@router.delete("/departments/{department_id}", status_code=204)
async def delete_department(
    department_id: int, session: AsyncSession = Depends(deps.get_session)
):
    """Delete a department"""
    result = await session.execute(
        select(Department).where(Department.id == department_id)
    )

    department = result.scalars().one_or_none()

    if department is None:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    await session.delete(department)
    await session.commit()
