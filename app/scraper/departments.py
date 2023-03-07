import re

from pyppeteer.browser import Page
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Department
from app.schemas.requests import DepartmentCreateRequest
from app.scraper.constants import graduation_components_link, graduation_programs_link
from app.scraper.utils import (
    raise_exception_if_empty_sigaa_id,
    raise_exception_if_sigaa_id_is_duplicated,
)


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
