import asyncio, os
from playwright.async_api import async_playwright
H = os.path.abspath(os.path.join(os.path.dirname(__file__), "informe.html"))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto("file://" + H); await pg.wait_for_load_state("networkidle")
        await pg.pdf(path=os.path.join(os.path.dirname(H), "TFI_ADM2026_Informe.pdf"), format="A4",
                     margin={"top": "2.2cm", "bottom": "2.2cm", "left": "2.5cm", "right": "2.2cm"},
                     display_header_footer=True, header_template="<span></span>",
                     footer_template='<div style="width:100%;text-align:center;font-size:9px;color:#555"><span class="pageNumber"></span></div>',
                     print_background=True)
        await b.close()
asyncio.run(main())
