import asyncio
import re

from pyppeteer import launch
from pyppeteer.browser import Page
from pyppeteer.element_handle import ElementHandle
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import async_session
from app.models import Department
from app.schemas.requests import DepartmentCreateRequest

base_url = "https://sig.unb.br/sigaa/public"
graduation_programs_link = base_url + "/curso/lista.jsf?nivel=G&aba=p-graduacao"
graduation_components_link = base_url + "/componentes/busca_componentes.jsf"


def raise_exception_if_sigaa_id_is_duplicated(
    departments: list[DepartmentCreateRequest],
):
    for index_a, department_a in enumerate(departments):
        for index_b, department_b in enumerate(departments):
            if (
                department_a["sigaa_id"] == department_b["sigaa_id"]
                and index_a != index_b
            ):
                raise Exception(f"Duplicated sigaa_id: {department_a and department_b}")


def raise_exception_if_empty_sigaa_id(departments: list[DepartmentCreateRequest]):
    for department in departments:
        if not department["sigaa_id"]:
            raise Exception(f"Empty sigaa_id: {department}")


async def get_departments(page: Page):
    departments: list[DepartmentCreateRequest] = []

    await page.goto(graduation_programs_link)
    departments_elements = await page.querySelectorAll("td.subFormulario")

    for department_element in departments_elements:
        department_inner_text: str = await page.evaluate(
            "(element) => element.innerText", department_element
        )

        [acronym, title] = department_inner_text.split(" - ")

        if not acronym or not title:
            continue

        departments.append({"acronym": acronym, "title": title})

    await page.goto(graduation_components_link)

    departments_elements = await page.querySelectorAll(
        "select[id='form:unidades'] option"
    )

    for department_element in departments_elements:
        department_inner_text: str = await page.evaluate(
            "(element) => element.innerText", department_element
        )

        department_inner_text = re.sub(r"\s+", " ", department_inner_text)

        for index, department in enumerate(departments):
            department["title"] = re.sub(r"\s+", " ", department["title"])

            if department["title"] == department_inner_text.split(" - ")[0]:
                sigaa_id = await page.evaluate(
                    "(element) => element.getAttribute('value')", department_element
                )

                departments[index]["sigaa_id"] = int(sigaa_id)

    raise_exception_if_sigaa_id_is_duplicated(departments)
    raise_exception_if_empty_sigaa_id(departments)

    return departments


async def create_departments(
    session: AsyncSession, departments: list[DepartmentCreateRequest]
):
    result = await session.execute(
        select(Department).where(
            Department.sigaa_id.in_([d["sigaa_id"] for d in departments])
        )
    )

    db_departments = result.scalars().all()

    for department in departments:
        db_department = next(
            (d for d in db_departments if d.sigaa_id == department["sigaa_id"]), None
        )

        if db_department is None:
            db_department = Department(**department)
            session.add(db_department)
        else:
            db_department.acronym = department["acronym"]
            db_department.title = department["title"]

    await session.commit()

    print("Departments created")


async def get_programs(page: Page, department_acronym: str = None):
    programs = []

    await page.goto(graduation_programs_link)
    programs_table_rows_elements = await page.querySelectorAll(
        "table.listagem tbody tr"
    )
    programs_start_index = 0
    programs_end_index = len(programs_table_rows_elements) + 1

    if department_acronym:
        department_xpath = (
            f"//td[contains(text(), '{department_acronym} -')]/ancestor::tr"
        )
        previous_departments = f"{department_xpath}/preceding-sibling::tr"
        next_department_xpath = f"{department_xpath}/following-sibling::tr[not(@class)][1]/preceding-sibling::tr"

        programs_start_index = len(await page.xpath(previous_departments)) + 1
        programs_end_index = len(await page.xpath(next_department_xpath)) + 1

    programs_rows_elements: list[ElementHandle] = await page.xpath(
        f"//tbody/tr \
            [position() > {programs_start_index} and position() < {programs_end_index}] \
            [@class='linhaPar' or @class='linhaImpar']"
    )

    for program_row_element in programs_rows_elements:
        program: list[str] = await program_row_element.querySelectorAllEval(
            "td", "(elements) => elements.map((element) => element.innerText)"
        )

        program_link_page_function = '(element) => element.querySelector("a").href'
        program_link = await page.evaluate(
            program_link_page_function, program_row_element
        )
        sigaa_id = re.search("id=([0-9]*)&", program_link).group(1)

        programs.append(
            {
                "sigaa_id": int(sigaa_id),
                "title": program[0],
                "degree": program[1].upper(),
                "shift": program[2],
            }
        )

    return programs


async def main():
    browser = await launch(headless=True, executablePath="/usr/bin/google-chrome")
    [page] = await browser.pages()

    async with async_session() as session:
        departments = await get_departments(page)
        await create_departments(session, departments)

        programs = await get_programs(page, department_acronym="FGA")
        print(f"{len(programs)} programs to be created")

    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
