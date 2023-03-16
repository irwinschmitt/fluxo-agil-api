import re

from pyppeteer.browser import Browser, Page
from pyppeteer.element_handle import ElementHandle

from app.scraper.utils import get_graduation_program_curricula_link, get_page


async def get_curriculum_attributes(curriculum_tr_element: ElementHandle):
    raw_sigaa_id_and_start_year: str
    raw_active: str
    [
        raw_sigaa_id_and_start_year,
        raw_active,
        *_,
    ] = await curriculum_tr_element.querySelectorAllEval(
        "td", "tds => tds.map(td => td.innerText)"
    )

    sigaa_id_and_start_year_match = re.search(
        "Detalhes da Estrutura Curricular (.*), Criado em (.*)",
        raw_sigaa_id_and_start_year,
    )

    if not sigaa_id_and_start_year_match:
        raise Exception(
            f"SIGAA ID and start year not found for curriculum: {raw_sigaa_id_and_start_year}"
        )

    sigaa_id = sigaa_id_and_start_year_match.group(1)
    start_year = int(sigaa_id_and_start_year_match.group(2))
    active = raw_active == "Ativa"

    return sigaa_id, start_year, active


async def get_curricula_tr_elements(page: Page):
    curricula_tr_selector = "table#table_lt tr.linha_par, tr.linha_impar"

    return await page.querySelectorAll(curricula_tr_selector)


async def get_curricula(browser: Browser, program_sigaa_id: int):
    print("Scraping SIGAA curricula...")

    curricula_link = get_graduation_program_curricula_link(program_sigaa_id)

    page = await get_page(browser, url=curricula_link)

    curricula = []

    curricula_tr_elements = await get_curricula_tr_elements(page)

    for curricula_tr_element in curricula_tr_elements:
        sigaa_id, start_year, active = await get_curriculum_attributes(
            curricula_tr_element
        )

        curricula.append(
            {
                "sigaa_id": sigaa_id,
                "start_year": start_year,
                "active": active,
            }
        )

    return curricula
