from pyppeteer.browser import Browser


async def get_page(browser: Browser, url: str):
    pages = await browser.pages()

    for page in pages:
        if page.url == url:
            return page

    page = await browser.newPage()

    await page.goto(url)

    return page
