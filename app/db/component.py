from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Component


async def store_or_update_component(session: AsyncSession, component: Component):
    """Store or update a component."""

    expression = Component.sigaa_id == component.sigaa_id
    result = await session.execute(select(Component).where(expression))
    current_component = result.scalars().one_or_none()

    if current_component:
        current_component = component

    else:
        session.add(component)

    await session.commit()

    return current_component
