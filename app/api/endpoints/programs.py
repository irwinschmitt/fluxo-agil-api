from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.db.models import Program
from app.schemas.responses import ProgramResponse

router = APIRouter()


@router.get("/programs", response_model=list[ProgramResponse])
async def read_departments(
    session: AsyncSession = Depends(deps.get_session),
    skip: int = 0,
    limit: int = 100,
):
    """Get all departments"""
    result = await session.execute(select(Program).offset(skip).limit(limit))

    return result.scalars().all()


@router.get("/programs/{program_id}", response_model=ProgramResponse)
async def read_department(
    program_id: int,
    session: AsyncSession = Depends(deps.get_session),
):
    """Get a department"""
    result = await session.execute(select(Program).where(Program.id == program_id))

    program = result.scalars().one_or_none()

    if program is None:
        raise HTTPException(status_code=404, detail="Programa não encontrado")

    return program
