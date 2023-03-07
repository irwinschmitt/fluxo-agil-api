import asyncio

from pyppeteer import launch

from app.core.session import async_session
from app.scraper.courses import get_programs
from app.scraper.departments import create_departments, get_departments


async def main():
    browser = await launch(headless=True, executablePath="/usr/bin/google-chrome")
    [page] = await browser.pages()

    async with async_session() as session:
        departments = await get_departments(page)
        await create_departments(session, departments)

        programs = await get_programs(page, session)
        print(programs)

    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
