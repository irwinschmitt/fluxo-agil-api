import re

from pyppeteer.browser import Browser, Page
from pyppeteer.element_handle import ElementHandle
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Department, Program
from app.schemas.requests import ProgramCreateRequest
from app.scraper.constants import graduation_programs_link
from app.scraper.utils import get_page


async def get_programs_tr_elements(page: Page):
    programs_tr_selector = (
        "table.listagem tbody tr.linhaPar, table.listagem tbody tr.linhaImpar"
    )

    return await page.querySelectorAll(programs_tr_selector)


async def get_program_attributes(program_tr_element: ElementHandle):
    [title, _degree, _shift, *_] = await program_tr_element.querySelectorAllEval(
        "td", "tds => tds.map(td => td.innerText)"
    )

    program_link = await program_tr_element.querySelectorEval("a", "a => a.href")

    sigaa_id_match = re.search("id=([0-9]*)&", program_link)

    if not sigaa_id_match:
        raise Exception(f"SIGAA ID not found for program: {title}")

    sigaa_id = int(sigaa_id_match.group(1))

    return sigaa_id, title


async def get_department_id(
    page: Page, program_tr_element: ElementHandle, session: AsyncSession
):
    department_acronym: str
    department_title: str
    [department_acronym, department_title] = await page.evaluate(
        "row => row.previousSiblings()\
                .find(({classList}) => !classList.contains('linhaPar') && !classList.contains('linhaImpar'))\
                .innerText\
                .split(' - ')",
        program_tr_element,
    )

    result = await session.execute(
        select(Department).where(
            Department.acronym == department_acronym
            and Department.title == department_title
        )
    )

    db_department = result.scalars().first()

    if db_department is None:
        raise Exception(
            f"Department not found: {department_acronym} - {department_title}"
        )

    return db_department.id


async def get_programs(browser: Browser, session: AsyncSession):
    print("Scraping SIGAA programs...")

    programs: list[ProgramCreateRequest] = []

    page = await get_page(browser, url=graduation_programs_link)

    programs_tr_elements = await get_programs_tr_elements(page)

    for program_tr_element in programs_tr_elements:
        sigaa_id, title = await get_program_attributes(program_tr_element)

        department_id = await get_department_id(page, program_tr_element, session)

        program = ProgramCreateRequest(
            sigaa_id=sigaa_id, title=title, department_id=department_id
        )

        programs.append(program)

    return programs


async def get_db_program_by_sigaa_id(session: AsyncSession, sigaa_id: int):
    result = await session.execute(select(Program).where(Program.sigaa_id == sigaa_id))

    return result.scalars().one_or_none()


async def create_programs(session: AsyncSession, programs: list[ProgramCreateRequest]):
    print("Creating programs in the database...")

    for program in programs:
        current_db_program = await get_db_program_by_sigaa_id(session, program.sigaa_id)
        new_db_program = Program(**program.dict())

        if current_db_program:
            current_db_program = new_db_program

        else:
            session.add(new_db_program)

    await session.commit()

    print("Programs created")
