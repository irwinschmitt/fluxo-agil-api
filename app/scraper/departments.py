from pyppeteer.browser import Browser, Page

from app.scraper.constants import (
    ELEMENT_INNER_TEXT,
    components_link,
    department_base_components_url,
)
from app.scraper.utils import get_page

department_log_base_prefix = "[Department]"


async def get_departments_sigaa_ids(page: Page) -> set[int]:
    """Get the SIGAA IDs of the departments."""

    options_selector = "select[id='form:unidades'] option"

    options_page_function = "(elements) => elements.map((element) => \
        parseInt(element.getAttribute('value')))\
        .filter((value) => value > 0)"

    sigaa_ids: list[int] = await page.JJeval(options_selector, options_page_function)

    departments_sigaa_ids = set()
    departments_sigaa_ids.update(sigaa_ids)

    return departments_sigaa_ids


async def get_department_components_page(browser: Browser, sigaa_id: int):
    """Get the components page of a department."""

    department_components_url = f"{department_base_components_url}?id={sigaa_id}"

    department_components_page = await get_page(browser, url=department_components_url)

    return department_components_page


async def get_department_header_attributes(page: Page) -> tuple[str, str]:
    header = await page.querySelector("#colDirTop")

    if header is None:
        raise Exception("Department header element not found")

    acronym = await header.Jeval("h1", ELEMENT_INNER_TEXT)
    title = await header.Jeval("h2", ELEMENT_INNER_TEXT)

    return acronym, title


def log_department(sigaa_id: int, acronym: str, title: str):
    """Log the department information."""

    print(f"{department_log_base_prefix}[{sigaa_id}] {acronym} - {title}")


async def get_departments(browser: Browser):
    components_page = await get_page(browser, url=components_link)
    departments_sigaa_ids = await get_departments_sigaa_ids(components_page)

    for sigaa_id in departments_sigaa_ids:
        department_page = await get_department_components_page(browser, sigaa_id)
        acronym, title = await get_department_header_attributes(department_page)

        log_department(sigaa_id, acronym, title)

        await department_page.waitFor(1000)


async def scrape_departments(browser: Browser):
    await get_departments(browser)
