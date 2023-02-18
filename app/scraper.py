import asyncio
import re

from pyppeteer import launch
from pyppeteer.browser import Page
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import async_session
from app.models import Department
from app.schemas.requests import DepartmentCreateRequest

base_url = "https://sig.unb.br/sigaa/public"
graduation_programs_link = base_url + "/curso/lista.jsf?nivel=G&aba=p-graduacao"
graduation_components_link = base_url + "/componentes/busca_componentes.jsf"


def raise_exception_if_sigaa_id_is_duplicated(
    elements: list,
):
    for index_a, element_a in enumerate(elements):
        for index_b, element_b in enumerate(elements):
            if element_a["sigaa_id"] == element_b["sigaa_id"] and index_a != index_b:
                raise Exception(f"Duplicated sigaa_id: {element_a and element_b}")


def raise_exception_if_empty_sigaa_id(elements: list):
    for element in elements:
        if not element["sigaa_id"]:
            raise Exception(f"Empty sigaa_id: {element}")


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


async def get_programs(page: Page, session: AsyncSession):
    programs = []

    await page.goto(graduation_programs_link)
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
