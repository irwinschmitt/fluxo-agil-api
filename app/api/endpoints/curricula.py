from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models import Curriculum
from app.schemas.responses import CurriculumResponse

router = APIRouter()


@router.get("/curricula", response_model=list[CurriculumResponse])
async def read_curricula(
    session: AsyncSession = Depends(deps.get_session), skip: int = 0, limit: int = 100
):
    """Get all curricula"""
    result = await session.execute(select(Curriculum).offset(skip).limit(limit))

    return result.scalars().all()


@router.get("/curricula/{curriculum_id}", response_model=CurriculumResponse)
async def read_curriculum(
    curriculum_id: int, session: AsyncSession = Depends(deps.get_session)
):
    """Get a curriculum"""
    result = await session.execute(
        select(Curriculum).where(Curriculum.id == curriculum_id)
    )

    curriculum = result.scalars().one_or_none()

    if curriculum is None:
        raise HTTPException(status_code=404, detail="Currículo não encontrado")

    return curriculum
