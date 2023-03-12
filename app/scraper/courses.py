import re

from pyppeteer.browser import Browser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Department
from app.scraper.constants import graduation_programs_link
from app.scraper.utils import (
    get_page,
    raise_exception_if_empty_sigaa_id,
    raise_exception_if_sigaa_id_is_duplicated,
)


async def get_programs(browser: Browser, session: AsyncSession):
    print("Scraping SIGAA programs...")

    programs = []

    page = await get_page(browser, url=graduation_programs_link)

    programs_rows_elements = await page.querySelectorAll(
        "table.listagem tbody tr.linhaPar, table.listagem tbody tr.linhaImpar",
    )

    # for each program_row_element, get the previous tr element that does not have class
    for program_row_element in programs_rows_elements:
        program_attributes: list[str] = await program_row_element.querySelectorAllEval(
            "td", "tds => tds.map(td => td.innerText)"
        )

        program_link = await page.evaluate(
            '(element) => element.querySelector("a").href', program_row_element
        )

        sigaa_id = re.search("id=([0-9]*)&", program_link).group(1)

        department_inner_text: str = await page.evaluate(
            "row => row.previousSiblings()\
                .find(({classList}) => !classList.contains('linhaPar') && !classList.contains('linhaImpar'))\
                .innerText",
            program_row_element,
        )

        department_acronym = department_inner_text.split(" - ")[0]

        result = await session.execute(
            select(Department).where(Department.acronym == department_acronym)
        )

        db_department = result.scalars().first()

        if db_department is None:
            raise Exception(f"Department not found: {department_acronym}")

        db_department.id

        programs.append(
            {
                "sigaa_id": int(sigaa_id),
                "title": program_attributes[0],
                "degree": program_attributes[1].upper(),
                "shift": program_attributes[2],
                "department_id": db_department.id,
            }
        )

    raise_exception_if_empty_sigaa_id(programs)
    raise_exception_if_sigaa_id_is_duplicated(programs)

    return programs
