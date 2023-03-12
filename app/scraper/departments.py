import re

from pyppeteer.browser import Browser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Department
from app.schemas.requests import DepartmentCreateRequest
from app.scraper.constants import graduation_components_link, graduation_programs_link


async def get_departments(browser: Browser):
    print("Scraping SIGAA departments...")

    programs_page = await browser.newPage()
    components_page = await browser.newPage()

    await programs_page.goto(graduation_programs_link)
    await components_page.goto(graduation_components_link)

    departments: list[DepartmentCreateRequest] = []

    departments_acronym_and_title_elements = await programs_page.querySelectorAll(
        "td.subFormulario"
    )

    departments_sigaa_id_elements = await components_page.querySelectorAll(
        "select[id='form:unidades'] option"
    )

    for acronym_and_title_element in departments_acronym_and_title_elements:
        acronym_and_title: str = await programs_page.evaluate(
            "(element) => element.innerText", acronym_and_title_element
        )

        [acronym, title] = acronym_and_title.split(" - ")

        if not acronym or not title:
            continue

        for sigaa_id_element in departments_sigaa_id_elements:
            inner_text: str = await components_page.evaluate(
                "(element) => element.innerText", sigaa_id_element
            )

            department_title = re.sub(r"\s+", " ", inner_text).split(" - ")[0]

            if title != department_title:
                continue

            sigaa_id: int = await components_page.evaluate(
                "(element) => parseInt(element.getAttribute('value'))",
                sigaa_id_element,
            )

            department = DepartmentCreateRequest(
                acronym=acronym, title=title, sigaa_id=sigaa_id
            )

            departments.append(department)

    return departments


async def create_departments(
    session: AsyncSession, departments: list[DepartmentCreateRequest]
):
    print("Creating departments in the database...")

    new_departments_sigaa_ids = [department.sigaa_id for department in departments]

    new_departments_query_result = await session.execute(
        select(Department).where(Department.sigaa_id.in_(new_departments_sigaa_ids))
    )

    db_departments = new_departments_query_result.scalars().all()

    for department in departments:
        db_department = next(
            (
                db_department
                for db_department in db_departments
                if db_department.sigaa_id == department.sigaa_id
            ),
            None,
        )

        if db_department is None:
            # create new department
            session.add(Department(**department.dict()))

        else:
            # update existent department
            db_department.acronym = department.acronym
            db_department.title = department.title

    await session.commit()

    print("Departments created")
