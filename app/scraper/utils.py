from pyppeteer.browser import Browser


def raise_exception_if_sigaa_id_is_duplicated(
    elements: list,
):
    for index_a, element_a in enumerate(elements):
        for index_b, element_b in enumerate(elements):
            if element_a["sigaa_id"] == element_b["sigaa_id"] and index_a != index_b:
                raise Exception(f"Duplicated sigaa_id: {element_a and element_b}")


def raise_exception_if_empty_sigaa_id(elements: list):
    for element in elements:
        if not element["sigaa_id"]:
            raise Exception(f"Empty sigaa_id: {element}")


async def get_page(browser: Browser, url: str):
    pages = await browser.pages()

    for page in pages:
        if page.url == url:
            return page

    page = await browser.newPage()

    await page.goto(url)

    return page
