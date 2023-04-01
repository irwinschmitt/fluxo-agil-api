from pyppeteer.browser import Browser
from pyppeteer.page import Page
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.component import store_or_update_component
from app.db.department import get_department_by_title
from app.db.models import Component
from app.scraper.constants import ELEMENT_INNER_TEXT
from app.scraper.curricula import get_curriculum_page


async def get_elective_tr_components(curriculum_page: Page):
    electives_table_xpath = "//td[contains(text(), 'Optativas')]/ancestor::table[1]"

    [electives_table] = await curriculum_page.xpath(electives_table_xpath)

    elective_tr_components = await electives_table.JJ("tr.componentes")

    return elective_tr_components


async def get_component_page(
    browser: Browser,
    program_sigaa_id: int,
    curriculum_sigaa_id: str,
    component_sigaa_id: str,
) -> Page:
    page = await get_curriculum_page(browser, program_sigaa_id, curriculum_sigaa_id)

    tr_selector = f"//td[contains(text(), '{component_sigaa_id}')]/ancestor::tr[1]"
    anchor_selector = f"{tr_selector}//a[contains(@title, 'Visualizar Detalhes do Componente Curricular')]"

    [component_anchor, *_] = await page.xpath(anchor_selector)

    await component_anchor.click()
    await page.waitForNavigation()

    return page


async def get_elective_components_ids(curriculum_page: Page) -> set[str]:
    elective_tr_components = await get_elective_tr_components(curriculum_page)

    elective_components_ids = set()

    for tr_component in elective_tr_components:
        raw: str = await tr_component.Jeval("td:first-child", ELEMENT_INNER_TEXT)

        component_sigaa_id = raw.split(" - ")[0]

        elective_components_ids.add(component_sigaa_id)

    return elective_components_ids


async def get_cell_text_by_header_text(page: Page, th_text: str) -> str:
    expression = f"//th[contains(., '{th_text}')]/following-sibling::td"
    [cell_element, *_] = await page.Jx(expression)

    cell_inner_text: str = await page.evaluate(ELEMENT_INNER_TEXT, cell_element)

    return cell_inner_text


async def get_component_sigaa_id(component_page: Page) -> str:
    header_text = "Código"

    sigaa_id = await get_cell_text_by_header_text(component_page, header_text)

    return sigaa_id


async def get_component_title(component_page: Page) -> str:
    header_text = "Nome"

    title = await get_cell_text_by_header_text(component_page, header_text)

    return title


async def get_component_type(component_page: Page) -> str:
    header_text = "Tipo do Componente Curricular"

    raw_type = await get_cell_text_by_header_text(component_page, header_text)

    type: str
    if raw_type == "DISCIPLINA":
        type = "COURSE"
    elif raw_type == "ATIVIDADE":
        type = "ACTIVITY"
    else:
        raise Exception(f"Invalid component type ({raw_type})")

    return type


async def get_component_department_title(component_page: Page) -> str:
    header_text = "Unidade Responsável"
    department = await get_cell_text_by_header_text(component_page, header_text)

    department_title = department.split(" - ")[0]

    return department_title


async def get_component_department_id(
    component_page: Page, session: AsyncSession
) -> int:
    department_title = await get_component_department_title(component_page)
    db_department = await get_department_by_title(session, department_title)

    return db_department.id


async def get_component(component_page: Page, session: AsyncSession) -> Component:
    sigaa_id = await get_component_sigaa_id(component_page)
    title = await get_component_title(component_page)
    type = await get_component_type(component_page)
    department_id = await get_component_department_id(component_page, session)

    return Component(
        sigaa_id=sigaa_id,
        title=title,
        type=type,
        department_id=department_id,
    )


async def scrape_components(
    browser,
    session: AsyncSession,
    program_sigaa_id: int | None = None,
    curriculum_sigaa_id: str | None = None,
):
    if not program_sigaa_id or not curriculum_sigaa_id:
        return

    curriculum_page = await get_curriculum_page(
        browser, program_sigaa_id, curriculum_sigaa_id
    )

    elective_components_ids = await get_elective_components_ids(curriculum_page)

    for component_sigaa_id in elective_components_ids:
        component_page = await get_component_page(
            browser, program_sigaa_id, curriculum_sigaa_id, component_sigaa_id
        )

        component = await get_component(component_page, session)

        await store_or_update_component(session, component)

        await component_page.close()
