import asyncio

from pyppeteer import launch
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import async_session
from app.scraper.curricula import create_curricula, get_curricula
from app.scraper.departments import create_departments, get_departments
from app.scraper.programs import create_programs, get_programs

software_engineering_program_sigaa_id = 414924


async def create_sigaa_data(session: AsyncSession):
    browser = await launch(headless=True, executablePath="/usr/bin/google-chrome")

    departments = await get_departments(browser)
    await create_departments(session, departments)

    programs = await get_programs(browser, session)
    await create_programs(session, programs)

    curricula = await get_curricula(
        browser, software_engineering_program_sigaa_id, session
    )
    await create_curricula(session, curricula)

    await browser.close()


async def main():
    async with async_session() as session:
        await create_sigaa_data(session)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
