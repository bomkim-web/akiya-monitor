import os
import json
import requests
import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get secrets from environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TARGET_URL = os.environ.get("TARGET_URL")
MOBILE_URL = os.environ.get("MOBILE_URL")
KEYWORDS = json.loads(os.environ.get("KEYWORDS", "[]"))  # Default to empty list if not set
MADORIS = json.loads(os.environ.get("MADORIS", "[]"))  # Default to empty list if not set

def send_telegram(msg: str) -> bool:
    """
    Send a notification message via Telegram bot.
    """
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False

async def run_once():
    """
    Single attempt of Playwright automation (async version).
    """
    print("Starting Playwright automation (async)...")

    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(
            headless=True,  # Run in headless mode
            args=[
                "--disable-background-networking",
                "--disable-background-timer-throttling",
                "--disable-breakpad",
                "--disable-client-side-phishing-detection",
                "--disable-component-update",
                "--disable-default-apps",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-features=site-per-process",
                "--disable-hang-monitor",
                "--disable-ipc-flooding-protection",
                "--disable-popup-blocking",
                "--disable-prompt-on-repost",
                "--disable-renderer-backgrounding",
                "--disable-sync",
                "--force-color-profile=srgb",
                "--metrics-recording-only",
                "--no-sandbox",
                "--no-zygote",
                "--headless=new",
                "--single-process",
                "--enable-automation",
                "--hide-scrollbars",
                "--mute-audio",
                "--no-first-run",
                "--disable-gpu",
            ],
        )

        page = await browser.new_page()

        print("Navigating to the target URL...")
        async with page.expect_popup() as search_page_info:
            await page.goto(TARGET_URL)
        search_page = await search_page_info.value

        print("Clicking search button...")
        try:
            search_button = search_page.get_by_role("link", name="検索する")
            await search_button.first.click()
        except Exception as e:
            print(f"Search button click error: {e}")

        print("Selecting 50 results per page...")
        try:
            async with search_page.expect_navigation():
                await search_page.get_by_role("combobox").select_option("50")
        except Exception as e:
            print(f"Combobox select error: {e}")

        print("Selecting result table...")
        try:
            tables = await search_page.query_selector_all("table.cell666666")
            print(len(tables), "tables found with class 'cell666666'")
            if len(tables) != 2:
                error_msg = f"Expected exactly 2 tables with class 'cell666666', but found {len(tables)}."
                send_telegram(error_msg)
                raise ValueError(error_msg)
            table = tables[1]
        except Exception as e:
            print(f"Error selecting result table: {e}")
            await browser.close()
            return

        print("Getting table rows...")
        rows = await table.query_selector_all("tr")
        rows = rows[1:]  # skip header row

        for idx, row in enumerate(rows, start=1):
            cells = await row.query_selector_all("td")
            name = (await cells[1].inner_text()).strip().replace("\n", "")
            type_ = (
                (await cells[3].inner_text())
                .strip()
                .replace("\n", "")
                .replace("　", "")
            )
            madori = (await cells[5].inner_text()).strip()
            print(f"{idx}")

            if any(keyword in name for keyword in KEYWORDS) and (
                not MADORIS or madori in MADORIS
            ):
                match_type = type_
                print("Match found.")
                send_telegram(
                    f"Match found: {name} ({match_type}, {madori}) {MOBILE_URL}"
                )
                break

        await browser.close()
        print("Browser closed.")


async def main_async():
    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt}: Starting Playwright automation...")
        try:
            await run_once()
            print("Run succeeded. Exiting...")
            return
        except Exception as e:
            error_msg = f"Attempt {attempt} failed: {e}"
            print(error_msg)
            send_telegram(error_msg)
            if attempt < max_retries:
                print(f"Waiting {retry_delay} seconds before retry...")
                await asyncio.sleep(retry_delay)

    print("All attempts failed. Exiting...")

if __name__ == "__main__":
    asyncio.run(main_async())