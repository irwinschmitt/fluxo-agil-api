import asyncio

from pyppeteer import launch
from pyppeteer.browser import Browser
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


async def scrape_all_departments(browser: Browser, session: AsyncSession):
    departments = await get_departments(browser)
    await create_departments(session, departments)


async def scrape_all_programs(browser: Browser, session: AsyncSession):
    programs = await get_programs(browser, session)
    await create_programs(session, programs)


async def scrape_curricula_by_program_id(
    browser: Browser, program_sigaa_id: int, session: AsyncSession
):
    curricula_pages = await get_curricula_pages(browser, program_sigaa_id)

    curricula = await get_curricula(curricula_pages, program_sigaa_id, session)
    await create_curricula(session, curricula)

    return curricula_pages


async def create_sigaa_data(session: AsyncSession, program_sigaa_id: int):
    browser = await launch(headless=True, executablePath="/usr/bin/google-chrome")

    await scrape_all_departments(browser, session)
    await scrape_all_programs(browser, session)

    curricula_pages = await scrape_curricula_by_program_id(
        browser, program_sigaa_id, session
    )

    for curriculum_page in curricula_pages:
        elective_components_sigaa_ids = (
            await get_curriculum_elective_components_sigaa_ids(curriculum_page)
        )
        mandatory_components_sigaa_ids = (
            await get_curriculum_mandatory_components_sigaa_ids(curriculum_page)
        )

        print(elective_components_sigaa_ids)
        print(mandatory_components_sigaa_ids)

    await browser.close()


async def main():
    async with async_session() as session:
        await create_sigaa_data(session, swe_program_sigaa_id)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
