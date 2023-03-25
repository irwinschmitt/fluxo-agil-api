import re

from pyppeteer.browser import Browser, Page
from pyppeteer.element_handle import ElementHandle
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Curriculum
from app.schemas.requests import CurriculumCreateRequest
from app.scraper.programs import get_db_program_by_sigaa_id
from app.scraper.utils import get_graduation_program_curricula_link, get_page


def format_workload(workload: str) -> int:
    return int(workload.replace("h", ""))


async def get_start_period_curriculum(page: Page) -> tuple[int, int]:
    raw_start_year_and_period = await get_cell_text_by_header_text(
        page, "Período Letivo de Entrada em Vigor"
    )
    [raw_start_year, raw_start_period] = raw_start_year_and_period.split(".")
    start_year = int(raw_start_year)
    start_period = int(raw_start_period)

    return start_year, start_period


async def get_cell_text_by_header_text(page: Page, th_text: str) -> str:
    [cell_element, *_] = await page.Jx(
        f"//th[contains(., '{th_text}')]/following-sibling::td"
    )

    cell_inner_text: str = await page.evaluate(
        "(element) => element.textContent", cell_element
    )

    return cell_inner_text


async def get_program_id_by_sigaa_id(session: AsyncSession, sigaa_id: int) -> int:
    db_program = await get_db_program_by_sigaa_id(session, sigaa_id)

    if not db_program:
        raise Exception(f"Program with SIGAA ID {sigaa_id} not found")

    return db_program.id


async def get_curriculum(
    session: AsyncSession, page: Page, program_sigaa_id: int
) -> CurriculumCreateRequest:
    # Geral
    sigaa_id = await get_cell_text_by_header_text(page, "Código")
    start_year, start_period = await get_start_period_curriculum(page)

    min_periods = await get_cell_text_by_header_text(page, "Mínimo:")
    max_periods = await get_cell_text_by_header_text(page, "Máximo:")

    min_period_workload = await get_cell_text_by_header_text(
        page, "Carga Horária Mínima por Período Letivo"
    )
    max_period_workload = await get_cell_text_by_header_text(
        page, "Carga Horária Máxima por Período Letivo"
    )

    # Total
    min_workload = await get_cell_text_by_header_text(page, "Total Mínima")

    # Obrigatórias
    mandatory_components_workload = await get_cell_text_by_header_text(page, "Total:")

    # Optativas
    min_elective_components_workload = await get_cell_text_by_header_text(
        page, "Carga Horária Optativa Mínima"
    )
    max_elective_components_workload = min_elective_components_workload

    # Complementares
    min_complementary_components_workload = await get_cell_text_by_header_text(
        page, "Carga Horária Complementar Mínima"
    )
    max_complementary_components_workload = await get_cell_text_by_header_text(
        page, "Carga Horária Máxima de Componentes Eletivos"
    )

    program_id = await get_program_id_by_sigaa_id(session, program_sigaa_id)

    curriculum = CurriculumCreateRequest(
        sigaa_id=sigaa_id,
        active=True,
        start_year=start_year,
        start_period=start_period,
        min_periods=int(min_periods),
        max_periods=int(max_periods),
        min_period_workload=format_workload(min_period_workload),
        max_period_workload=format_workload(max_period_workload),
        min_workload=format_workload(min_workload),
        mandatory_components_workload=format_workload(mandatory_components_workload),
        min_elective_components_workload=format_workload(
            min_elective_components_workload
        ),
        max_elective_components_workload=format_workload(
            max_elective_components_workload
        ),
        min_complementary_components_workload=format_workload(
            min_complementary_components_workload
        ),
        max_complementary_components_workload=format_workload(
            max_complementary_components_workload
        ),
        program_id=program_id,
    )

    return curriculum


async def get_curriculum_anchor_element(page: Page, curriculum_sigaa_id: str):
    [element] = await page.Jx(f"//tr[contains(., '{curriculum_sigaa_id}')]")

    anchor = await element.querySelector("a[title='Relatório da Estrutura Curricular']")

    return anchor


async def open_curriculum_in_new_tab(
    browser: Browser, program_sigaa_id: int, curriculum_sigaa_id: str
):
    # there is no url for a curriculum
    curricula_link = get_graduation_program_curricula_link(program_sigaa_id)

    page = await browser.newPage()
    await page.goto(curricula_link)

    a_element = await get_curriculum_anchor_element(page, curriculum_sigaa_id)

    if not a_element:
        raise Exception(f"Curriculum {curriculum_sigaa_id} link not found")

    await a_element.click()
    await page.waitForNavigation()

    return page


async def get_main_curriculum_attributes(curriculum_tr_element: ElementHandle):
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


async def get_curricula(
    curricula_pages: list[Page], program_sigaa_id: int, session: AsyncSession
):
    print("Scraping SIGAA curricula...")

    curricula: list[CurriculumCreateRequest] = []

    for page in curricula_pages:
        curriculum = await get_curriculum(session, page, program_sigaa_id)
        curricula.append(curriculum)

    return curricula


async def get_curricula_pages(browser: Browser, program_sigaa_id: int) -> list[Page]:
    curricula_link = get_graduation_program_curricula_link(program_sigaa_id)

    page = await get_page(browser, url=curricula_link)

    curricula_tr_elements = await get_curricula_tr_elements(page)

    curricula_pages: list[Page] = []

    for curricula_tr_element in curricula_tr_elements:
        sigaa_id, *_ = await get_main_curriculum_attributes(curricula_tr_element)

        curriculum_page = await open_curriculum_in_new_tab(
            browser, program_sigaa_id, sigaa_id
        )

        curricula_pages.append(curriculum_page)

    return curricula_pages


async def get_db_curriculum_by_sigaa_id(session: AsyncSession, sigaa_id: str):
    result = await session.execute(
        select(Curriculum).where(Curriculum.sigaa_id == sigaa_id)
    )

    return result.scalars().one_or_none()


async def create_curricula(
    session: AsyncSession, curricula: list[CurriculumCreateRequest]
):
    print("Creating curricula in the database...")

    for curriculum in curricula:
        current_db_curriculum = await get_db_curriculum_by_sigaa_id(
            session, curriculum.sigaa_id
        )
        new_db_curriculum = Curriculum(**curriculum.dict())

        if current_db_curriculum:
            current_db_curriculum = new_db_curriculum

        else:
            session.add(new_db_curriculum)

    await session.commit()

    print("Curricula created")


async def get_table_by_title(page: Page, title: str):
    [table_element] = await page.xpath(
        f"//table[descendant::tr[1][contains(., '{title}')]]"
    )

    return table_element


async def get_components_tr_elements(element: ElementHandle | Page):
    return await element.querySelectorAll("tr.componentes")


async def get_components_sigaa_ids(tr_elements: list[ElementHandle]):
    sigaa_ids: list[str] = []

    for tr_element in tr_elements:
        sigaa_id: str = await tr_element.Jeval("td", "td => td.innerText.split(' ')[0]")

        sigaa_ids.append(sigaa_id)

    return sigaa_ids


async def get_curriculum_components_sigaa_ids(curriculum_page: Page):
    components_tr = await get_components_tr_elements(curriculum_page)
    components_sigaa_ids = await get_components_sigaa_ids(components_tr)
    unique_components_sigaa_ids = set(components_sigaa_ids)

    return unique_components_sigaa_ids
