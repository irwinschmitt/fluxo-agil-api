import asyncio

from pyppeteer import launch
from pyppeteer.browser import Page

from app.schemas.requests import DepartmentCreateRequest

base_url = "https://sig.unb.br/sigaa/public"
graduation_programs_link = base_url + "/curso/lista.jsf?nivel=G&aba=p-graduacao"
graduation_components_link = base_url + "/componentes/busca_componentes.jsf"


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

        for index, department in enumerate(departments):
            if department["title"] in department_inner_text:
                id = await page.evaluate(
                    "(element) => element.getAttribute('value')", department_element
                )

                departments[index]["sigaa_id"] = int(id)

    return departments


async def main():
    browser = await launch(headless=False, executablePath="/usr/bin/google-chrome")
    [page] = await browser.pages()

    departments = await get_departments(page)

    print(departments)

    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
