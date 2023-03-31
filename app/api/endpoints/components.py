from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.db.models import Component
from app.schemas.responses import ComponentResponse

# create the read endpoints for components
router = APIRouter()


@router.get("/components", response_model=list[ComponentResponse])
async def read_components(
    session: AsyncSession = Depends(deps.get_session),
    skip: int = 0,
    limit: int = 100,
):
    """Get all components"""
    result = await session.execute(select(Component).offset(skip).limit(limit))

    return result.scalars().all()


@router.get("/components/{component_id}", response_model=ComponentResponse)
async def read_component(
    component_id: int, session: AsyncSession = Depends(deps.get_session)
):
    """Get a component"""
    result = await session.execute(
        select(Component).where(Component.id == component_id)
    )

    component = result.scalars().one_or_none()

    if component is None:
        raise HTTPException(status_code=404, detail="Componente não encontrado")

    return component
