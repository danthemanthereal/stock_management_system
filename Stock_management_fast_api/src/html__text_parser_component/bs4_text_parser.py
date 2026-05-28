import urllib.request
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

class BS4TextParser:
    def __init__(self):
        pass

    async def get_website_text(self, url: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, wait_until="networkidle")

            html = await page.content()

            await browser.close()

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        lines = [line.strip() for line in text.splitlines() if line.strip()]

        return "\n".join(lines)