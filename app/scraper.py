import asyncio
import re

from pyppeteer import launch
from pyppeteer.browser import Page
from pyppeteer.element_handle import ElementHandle

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
    browser = await launch(headless=False, executablePath="/usr/bin/google-chrome")
    [page] = await browser.pages()

    departments = await get_departments(page)
    programs = await get_programs(page, department_acronym="FGA")

    print(departments)
    print(programs)

    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
