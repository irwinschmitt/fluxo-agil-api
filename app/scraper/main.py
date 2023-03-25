import asyncio

from pyppeteer import launch
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import async_session
from app.scraper.curricula import (
    create_curricula,
    get_curricula,
    get_curricula_pages,
    get_curriculum_elective_components_sigaa_ids,
    get_curriculum_mandatory_components_sigaa_ids,
)
from app.scraper.departments import create_departments, get_departments
from app.scraper.programs import create_programs, get_programs

swe_program_sigaa_id = 414924


async def create_sigaa_data(session: AsyncSession):
    browser = await launch(headless=True, executablePath="/usr/bin/google-chrome")

    departments = await get_departments(browser)
    await create_departments(session, departments)

    programs = await get_programs(browser, session)
    await create_programs(session, programs)

    curricula_pages = await get_curricula_pages(browser, swe_program_sigaa_id)

    curricula = await get_curricula(curricula_pages, swe_program_sigaa_id, session)
    await create_curricula(session, curricula)

    for curriculum_page in curricula_pages:
        elective_components_sigaa_ids = (
            await get_curriculum_elective_components_sigaa_ids(curriculum_page)
        )
        mandatory_components_sigaa_ids = (
            await get_curriculum_mandatory_components_sigaa_ids(curriculum_page)
        )

        print(elective_components_sigaa_ids)
        print(mandatory_components_sigaa_ids)


async def main():
    async with async_session() as session:
        await create_sigaa_data(session)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
