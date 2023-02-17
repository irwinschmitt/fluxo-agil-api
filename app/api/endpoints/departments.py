from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models import Department
from app.schemas.responses import DepartmentResponse

router = APIRouter()


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

    department = result.scalars().first()

    if department is None:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    return department
