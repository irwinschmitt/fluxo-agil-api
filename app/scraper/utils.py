from pyppeteer.browser import Browser

from app.scraper.constants import default_language, graduation_curricula_link


async def get_page(browser: Browser, url: str):
    pages = await browser.pages()

    for page in pages:
        if page.url == url:
            return page

    page = await browser.newPage()

    await page.goto(url)

    return page


def get_graduation_program_curricula_link(program_sigaa_id: int) -> str:
    return f"{graduation_curricula_link}?lc={default_language}&id={program_sigaa_id}"
