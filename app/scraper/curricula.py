import re

from pyppeteer.browser import Browser, Page
from pyppeteer.element_handle import ElementHandle
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.curriculum import store_or_update_curriculum
from app.db.models import Curriculum
from app.db.program import get_program_by_sigaa_id, get_programs
from app.scraper.constants import ELEMENT_INNER_TEXT, curricula_list_base_url
from app.scraper.utils import get_page


async def get_cell_text_by_header_text(page: Page, th_text: str) -> str:
    expression = f"//th[contains(., '{th_text}')]/following-sibling::td"
    [cell_element, *_] = await page.Jx(expression)

    cell_inner_text: str = await page.evaluate(ELEMENT_INNER_TEXT, cell_element)

    return cell_inner_text


async def get_programs_sigaa_ids(
    session: AsyncSession, program_sigaa_id: int | None = None
) -> set[int]:
    programs_sigaa_ids: set[int] = set()

    if program_sigaa_id:
        programs_sigaa_ids.add(program_sigaa_id)
    else:
        programs = await get_programs(session)
        programs_sigaa_ids.update(program.sigaa_id for program in programs)

    return programs_sigaa_ids


def get_program_curricula_url(program_sigaa_id: int) -> str:
    return f"{curricula_list_base_url}?id={program_sigaa_id}"


async def get_program_curricula_page(browser: Browser, program_sigaa_id: int) -> Page:
    program_curricula_url = get_program_curricula_url(program_sigaa_id)

    page = await get_page(browser, url=program_curricula_url)

    return page


async def get_curricula_tr_elements(
    page: Page, curriculum_sigaa_id: str | None = None
) -> list[ElementHandle]:
    table_xpath_selector = "//table[@id='table_lt']"
    tr_xpath_selector = "//tr[(@class='linha_par' or @class='linha_impar')]"
    xpath_selector = f"{table_xpath_selector}{tr_xpath_selector}"

    if curriculum_sigaa_id:
        td_xpath_selector = f"[descendant::td[contains(., '{curriculum_sigaa_id}')]]"
        xpath_selector += td_xpath_selector

    curricula_tr = await page.xpath(xpath_selector)

    return curricula_tr


async def get_curriculum_status(curriculum_tr: ElementHandle) -> bool:
    active_elements = await curriculum_tr.xpath("td[contains(., 'Ativa')]")

    return bool(active_elements)


async def get_curriculum_page(
    browser: Browser, program_sigaa_id: int, curriculum_sigaa_id: str
) -> Page:
    program_curricula_url = get_program_curricula_url(program_sigaa_id)

    page = await browser.newPage()
    await page.goto(program_curricula_url)

    [curriculum_tr] = await get_curricula_tr_elements(page, curriculum_sigaa_id)
    button = await curriculum_tr.J("a[title='Relatório da Estrutura Curricular']")

    if not button:
        raise Exception("Could not find button to open curriculum page")

    await button.click()
    await page.waitForNavigation()

    return page


async def get_curriculum_sigaa_id_by_tr_element(curriculum_tr: ElementHandle) -> str:
    raw_sigaa_id = await curriculum_tr.Jeval("td:first-child", ELEMENT_INNER_TEXT)

    sigaa_id_pattern = "Detalhes da Estrutura Curricular (.*),"
    sigaa_id_match = re.search(sigaa_id_pattern, raw_sigaa_id)

    if not sigaa_id_match:
        raise Exception("Could not find curriculum sigaa_id")

    sigaa_id = sigaa_id_match.group(1).strip()

    return sigaa_id


async def get_curriculum_sigaa_id(curriculum_page: Page) -> str:
    return await get_cell_text_by_header_text(curriculum_page, "Código")


async def get_curriculum_start_period(curriculum_page: Page) -> tuple[int, int]:
    header_text = "Período Letivo de Entrada em Vigor"
    raw_start_period = await get_cell_text_by_header_text(curriculum_page, header_text)

    [start_year, start_period] = raw_start_period.split(".")
    start_year = int(start_year)
    start_period = int(start_period)

    return start_year, start_period


async def get_curriculum_min_periods(curriculum_page: Page) -> int:
    min_periods = await get_cell_text_by_header_text(curriculum_page, "Mínimo:")
    min_periods = int(min_periods)

    return min_periods


async def get_curriculum_max_periods(curriculum_page: Page) -> int:
    max_periods = await get_cell_text_by_header_text(curriculum_page, "Máximo:")
    max_periods = int(max_periods)

    return max_periods


async def get_curriculum_min_period_workload(curriculum_page: Page) -> int:
    header_text = "Carga Horária Mínima por Período Letivo"
    raw_workload = await get_cell_text_by_header_text(curriculum_page, header_text)

    min_period_workload = format_workload_to_number(raw_workload)

    return min_period_workload


def format_workload_to_number(raw_workload: str) -> int:
    workload = int(raw_workload.replace("h", ""))

    return workload


async def get_curriculum_max_period_workload(curriculum_page: Page) -> int:
    header_text = "Carga Horária Máxima por Período Letivo"
    raw_workload = await get_cell_text_by_header_text(curriculum_page, header_text)

    max_period_workload = format_workload_to_number(raw_workload)

    return max_period_workload


async def get_curriculum_min_workload(curriculum_page: Page) -> int:
    header_text = "Total Mínima"
    raw_workload = await get_cell_text_by_header_text(curriculum_page, header_text)

    min_workload = format_workload_to_number(raw_workload)

    return min_workload


async def get_curriculum_mandatory_components_workload(curriculum_page: Page) -> int:
    header_text = "Total:"
    raw_workload = await get_cell_text_by_header_text(curriculum_page, header_text)

    mandatory_components_workload = format_workload_to_number(raw_workload)

    return mandatory_components_workload


async def get_curriculum_min_elective_components_workload(curriculum_page: Page) -> int:
    header_text = "Carga Horária Optativa Mínima:"
    raw_workload = await get_cell_text_by_header_text(curriculum_page, header_text)

    min_elective_components_workload = format_workload_to_number(raw_workload)

    return min_elective_components_workload


async def get_curriculum_min_complementary_components_workload(
    curriculum_page: Page,
) -> int:
    header_text = "Carga Horária Complementar Mínima:"
    raw_workload = await get_cell_text_by_header_text(curriculum_page, header_text)

    min_complementary_components_workload = format_workload_to_number(raw_workload)

    return min_complementary_components_workload


async def get_curriculum_max_complementary_components_workload(
    curriculum_page: Page,
) -> int:
    header_text = "Carga Horária Máxima de Componentes Eletivos"
    raw_workload = await get_cell_text_by_header_text(curriculum_page, header_text)

    max_complementary_components_workload = format_workload_to_number(raw_workload)

    return max_complementary_components_workload


async def get_curriculum(
    session: AsyncSession, curriculum_page: Page, program_sigaa_id: int, active: bool
) -> Curriculum:
    sigaa_id = await get_curriculum_sigaa_id(curriculum_page)
    start_year, start_period = await get_curriculum_start_period(curriculum_page)
    min_periods = await get_curriculum_min_periods(curriculum_page)
    max_periods = await get_curriculum_max_periods(curriculum_page)
    min_period_workload = await get_curriculum_min_period_workload(curriculum_page)
    max_period_workload = await get_curriculum_max_period_workload(curriculum_page)
    min_workload = await get_curriculum_min_workload(curriculum_page)

    mandatory_components_workload = await get_curriculum_mandatory_components_workload(
        curriculum_page
    )

    min_elective_components_workload = (
        await get_curriculum_min_elective_components_workload(curriculum_page)
    )

    max_elective_components_workload = min_elective_components_workload

    min_complementary_components_workload = (
        await get_curriculum_min_complementary_components_workload(curriculum_page)
    )

    max_complementary_components_workload = (
        await get_curriculum_max_complementary_components_workload(curriculum_page)
    )

    program = await get_program_by_sigaa_id(session, program_sigaa_id)

    if not program:
        raise Exception("Program not found")

    curriculum = Curriculum(
        sigaa_id=sigaa_id,
        active=active,
        start_year=start_year,
        start_period=start_period,
        min_periods=min_periods,
        max_periods=max_periods,
        min_period_workload=min_period_workload,
        max_period_workload=max_period_workload,
        min_workload=min_workload,
        mandatory_components_workload=mandatory_components_workload,
        min_elective_components_workload=min_elective_components_workload,
        max_elective_components_workload=max_elective_components_workload,
        min_complementary_components_workload=min_complementary_components_workload,
        max_complementary_components_workload=max_complementary_components_workload,
        program_id=program.id,
    )

    return curriculum


async def scrape_curricula(
    browser: Browser,
    session: AsyncSession,
    program_sigaa_id: int | None = None,
    only_active: bool = True,
):
    """Scrape and store (or update) curricula."""

    programs_sigaa_ids: set[int]
    programs_sigaa_ids = await get_programs_sigaa_ids(session, program_sigaa_id)

    # There are too many programs (~150) to open all tabs at once
    for p_sigaa_id in programs_sigaa_ids:
        curricula_page = await get_program_curricula_page(browser, p_sigaa_id)
        curricula_tr = await get_curricula_tr_elements(curricula_page)

        for curriculum_tr in curricula_tr:
            active = await get_curriculum_status(curriculum_tr)

            if only_active and not active:
                continue

            sigaa_id = await get_curriculum_sigaa_id_by_tr_element(curriculum_tr)
            curriculum_page = await get_curriculum_page(browser, p_sigaa_id, sigaa_id)

            curriculum = await get_curriculum(
                session, curriculum_page, p_sigaa_id, active
            )

            await store_or_update_curriculum(session, curriculum)

            await curriculum_page.close()

        await curricula_page.waitFor(1000)
        await curricula_page.close()
