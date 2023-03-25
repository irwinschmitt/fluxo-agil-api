import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.scraper.departments import get_department_by_acronym


def get_component_department_acronym(component_sigaa_id: str):
    component_match = re.match(r"([A-Z]{3})([0-9]{4})", component_sigaa_id)

    if not component_match:
        raise Exception(f"Invalid component sigaa id ({component_sigaa_id})")

    department_acronym = component_match.group(1)

    return str(department_acronym)


async def get_component_department(component_sigaa_id: str, session: AsyncSession):
    department_acronym = get_component_department_acronym(component_sigaa_id)
    db_department = await get_department_by_acronym(department_acronym, session)

    return db_department


async def get_component(component_sigaa_id: str, session: AsyncSession):
    db_department = await get_component_department(component_sigaa_id, session)

    print(db_department.id, db_department.sigaa_id)
