from fastapi import APIRouter, Depends
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
