import re

from pyppeteer.browser import Browser, Page
from pyppeteer.element_handle import ElementHandle
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.department import get_department_by_acronym_and_title
from app.db.models import Program
from app.db.program import store_or_update_program
from app.scraper.constants import (
    ELEMENT_INNER_TEXT,
    ELEMENT_PREVIOUS_SIBLINGS,
    FIND_ELEMENT_WITHOUT_CLASS,
    TABLE_CONTENT_ROW_SELECTOR,
    graduation_programs_url,
    program_degree_map,
    program_shift_map,
)
from app.scraper.utils import get_page


async def get_content_tr_elements(container: Page | ElementHandle):
    """Get tr.linhaPar and tr.linhaImpar elements from a page or element."""

    return await container.querySelectorAll(TABLE_CONTENT_ROW_SELECTOR)


async def get_program_sigaa_id(program_tr_element: ElementHandle) -> int:
    """Get the SIGAA ID of a program from its tr element."""

    program_url = await program_tr_element.Jeval("a", "a => a.href")

    sigaa_id_match = re.search("id=([0-9]+)", program_url)

    if not sigaa_id_match:
        raise Exception(f"SIGAA ID not found on program URL: {program_url}")

    sigaa_id = int(sigaa_id_match.group(1))

    return sigaa_id


async def get_program_title(program_tr_element: ElementHandle) -> str:
    """Get the title of a program from its tr element."""

    title_selector = "td:nth-child(1)"
    program_title = await program_tr_element.Jeval(title_selector, ELEMENT_INNER_TEXT)

    return program_title


async def get_program_degree(program_tr_element: ElementHandle) -> str | None:
    """Get the degree (BACHELOR or LICENTIATE) of a program from its tr element."""

    degree_selector = "td:nth-child(2)"

    raw_degree: str
    raw_degree = await program_tr_element.Jeval(degree_selector, ELEMENT_INNER_TEXT)
    raw_degree = raw_degree.strip().upper()

    if raw_degree not in program_degree_map:
        return None

    degree = program_degree_map[raw_degree]

    return degree


async def get_program_shift(program_tr_element: ElementHandle) -> str | None:
    """Get the shift (DAY or NIGHT) of a program from its tr element."""
    shift_selector = "td:nth-child(3)"

    raw_shift: str
    raw_shift = await program_tr_element.Jeval(shift_selector, ELEMENT_INNER_TEXT)
    raw_shift = raw_shift.strip().upper()

    if raw_shift not in program_shift_map:
        return None

    shift = program_shift_map[raw_shift]

    return shift


async def get_program_department_attributes(page: Page, program_tr: ElementHandle):
    """Get the department acronym and title from the program's tr element."""

    page_function = f"{ELEMENT_PREVIOUS_SIBLINGS}{FIND_ELEMENT_WITHOUT_CLASS}"
    department_tr_js = await page.evaluateHandle(page_function, program_tr)

    department_tr = department_tr_js.asElement()

    department_attributes: str = await page.evaluate(ELEMENT_INNER_TEXT, department_tr)

    [department_acronym, department_title] = department_attributes.split(" - ")

    return department_acronym.strip(), department_title.strip()


async def get_program_department_id(
    page: Page, program_tr: ElementHandle, session: AsyncSession
):
    """Get the department ID from the program's tr element."""

    acronym, title = await get_program_department_attributes(page, program_tr)

    department = await get_department_by_acronym_and_title(session, acronym, title)

    return department.id


async def scrape_programs(browser: Browser, session: AsyncSession):
    """Scrape and store (or update) the graduation programs"""

    graduation_programs_page = await get_page(browser, graduation_programs_url)
    programs_tr_elements = await get_content_tr_elements(graduation_programs_page)

    for program_tr_element in programs_tr_elements:
        sigaa_id = await get_program_sigaa_id(program_tr_element)
        title = await get_program_title(program_tr_element)
        degree = await get_program_degree(program_tr_element)
        shift = await get_program_shift(program_tr_element)

        department_id = await get_program_department_id(
            graduation_programs_page, program_tr_element, session
        )

        program = Program(
            sigaa_id=sigaa_id,
            title=title,
            degree=degree,
            shift=shift,
            department_id=department_id,
        )

        await store_or_update_program(session, program)

    await graduation_programs_page.close()
