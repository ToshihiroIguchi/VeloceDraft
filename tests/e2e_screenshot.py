import asyncio
from playwright.async_api import async_playwright
import os

async def capture_screenshots():
    # Ensure screenshot dir exists
    out_dir = os.path.join(os.path.dirname(__file__), "..", "production_artifacts", "browser_screenshots")
    os.makedirs(out_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 720})

        print("Navigating to frontend...")
        # Increase timeout and retry once
        try:
            await page.goto("http://localhost:5173/", timeout=60000)
        except Exception:
            await asyncio.sleep(5)
            await page.goto("http://localhost:5173/", timeout=60000)

        await asyncio.sleep(3) # Wait for canvas init
        await page.screenshot(path=os.path.join(out_dir, "01_home.png"))
        
        # Rounded Rect
        await page.click("button:has-text('Rounded Rect')")
        await page.mouse.move(300, 300)
        await page.mouse.down()
        await page.mouse.move(400, 400)
        await page.mouse.up()
        await asyncio.sleep(0.5)

        # Line tool
        await page.click("button:has-text('Line')")
        await page.mouse.move(500, 200)
        await page.mouse.down()
        await page.mouse.move(600, 300)
        await page.mouse.up()
        await asyncio.sleep(0.5)
        await page.screenshot(path=os.path.join(out_dir, "03_entities.png"))

        # Select & Array
        await page.click("button:has-text('Select')")
        await page.mouse.click(350, 350)
        await asyncio.sleep(0.5)
        await page.click("button:has-text('Create Array')")
        await asyncio.sleep(1)
        await page.screenshot(path=os.path.join(out_dir, "04_electrode_array.png"))

        # PDF Export (handle dialog)
        page.on("dialog", lambda dialog: dialog.accept())
        await page.click("button:has-text('PDF')")
        await asyncio.sleep(2)
        await page.screenshot(path=os.path.join(out_dir, "09_export_pdf.png"))

        # Layer Toggle
        await page.click("text=Layer 1")
        await asyncio.sleep(0.5)
        await page.screenshot(path=os.path.join(out_dir, "07_layer_toggle.png"))

        # Area Calc
        await page.click("text=Calculate Area")
        await asyncio.sleep(1)
        await page.screenshot(path=os.path.join(out_dir, "06_closed_region_area.png"))

        await browser.close()
        print("Screenshots captured successfully!")

if __name__ == "__main__":
    asyncio.run(capture_screenshots())
