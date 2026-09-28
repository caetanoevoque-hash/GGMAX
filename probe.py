import asyncio, json, re, sys
from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "https://ggmax.com.br/busca/gemini"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = await b.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
            locale="pt-BR", viewport={"width": 1366, "height": 900},
        )
        page = await ctx.new_page()
        api_hits = []
        async def on_resp(r):
            ct = r.headers.get("content-type", "")
            if "json" in ct and "ggmax" in r.url:
                try:
                    body = await r.text()
                    api_hits.append((r.url, body[:600]))
                except Exception:
                    pass
        page.on("response", on_resp)
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(9000)
        title = await page.title()
        html = await page.content()
        print("TITLE:", title, "| HTML len:", len(html))
        print("API JSON responses:", len(api_hits))
        for u, bdy in api_hits[:15]:
            print("\n==", u, "\n", bdy)
        text = await page.inner_text("body")
        print("\nBODY TEXT (first 3000):\n", text[:3000])
        open("/home/user/webapp/probe.html", "w").write(html)
        await b.close()

asyncio.run(main())
