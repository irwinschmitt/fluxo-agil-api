import asyncio

from pyppeteer import launch

# from pyppeteer.browser import Browser
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import async_session
from app.scraper.components import scrape_components
from app.scraper.curricula import scrape_curricula
from app.scraper.departments import scrape_departments
from app.scraper.programs import scrape_programs

# from app.scraper.components import get_component
# from app.scraper.curricula import (
#     create_curricula,
#     get_curricula,
#     get_curricula_pages,
# )


swe_program_sigaa_id = 414924
swe_curriculum_sigaa_id = "6360/1"


# async def scrape_curricula_by_program__sigaa_id(
#     browser: Browser, program_sigaa_id: int, session: AsyncSession
# ):
#     curricula_pages = await get_curricula_pages(browser, program_sigaa_id)

#     curricula = await get_curricula(curricula_pages, program_sigaa_id, session)
#     await create_curricula(session, curricula)

#     return curricula_pages


# async def scrape_components_by_sigaa_ids(sigaa_ids: set[str], session: AsyncSession):
#     for sigaa_id in sigaa_ids:
#         await get_component(sigaa_id, session)


async def create_sigaa_data(
    session: AsyncSession,
    program_sigaa_id: int | None = None,
    curriculum_sigaa_id: str | None = None,
):
    browser = await launch(headless=False, executablePath="/usr/bin/google-chrome")

    await scrape_departments(browser, session)
    await scrape_programs(browser, session)
    await scrape_curricula(browser, session, program_sigaa_id)
    await scrape_components(browser, session, program_sigaa_id, curriculum_sigaa_id)

    # curricula_pages = await scrape_curricula_by_program__sigaa_id(
    #     browser, program_sigaa_id, session
    # )

    # program_components_sigaa_ids: set[str] = set()

    # for curriculum_page in curricula_pages:
    #     curriculum_components_sigaa_ids = await get_curriculum_components_sigaa_ids(
    #         curriculum_page
    #     )

    #     program_components_sigaa_ids.update(curriculum_components_sigaa_ids)

    # await scrape_components_by_sigaa_ids(program_components_sigaa_ids, session)

    await browser.close()


async def main():
    async with async_session() as session:
        await create_sigaa_data(session, swe_program_sigaa_id, swe_curriculum_sigaa_id)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
