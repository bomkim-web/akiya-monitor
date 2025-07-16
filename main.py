import os
from playwright.sync_api import sync_playwright
import requests
import time

# Get secrets from environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TARGET_URL = os.environ.get("TARGET_URL")
MOBILE_URL = os.environ.get("MOBILE_URL")
KEYWORD = os.environ.get("KEYWORD")

def send_telegram(msg):
    """
    Send a notification message via Telegram bot.
    This function sends a message to your Telegram chat using your bot.
    """
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        return False

def main():
    max_retries = 3
    retry_delay = 5  # seconds
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt}: Starting Playwright automation...")
            # Start Playwright (browser automation)
            with sync_playwright() as p:
                print("Launching browser...")

                browser = p.chromium.launch(
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
                    ]
                )

                page = browser.new_page()

                print(f"Navigating to the target URL...")
                with page.expect_popup() as search_page_info:
                    page.goto(TARGET_URL)
                    search_page = search_page_info.value

                print("Clicking search button...")
                try:
                    search_button = search_page.get_by_role('link', name='検索する')
                    search_button.first.click()
                except Exception as e:
                    print(f"Search button click error: {e}")
                
                print("Selecting 20 results per page...")
                try:
                    with search_page.expect_navigation():
                        search_page.get_by_role("combobox").select_option("20")
                except Exception as e:
                    print(f"Combobox select error: {e}")

                print("Selecting result table...")
                tables = search_page.query_selector_all('table.cell666666')
                table = tables[1]

                print("Getting table rows...")
                rows = table.query_selector_all('tr')[1:]  # [1:] skips the first tr (header row)

                for idx, row in enumerate(rows, start=1):
                    cells = row.query_selector_all('td')
                    name = cells[1].inner_text().strip()
                    type_ = cells[3].inner_text().strip().replace("\n", "").replace("　", "")
                    madori = cells[5].inner_text().strip()
                    print(f"{idx}")

                    if KEYWORD in name:
                        match_type = type_
                        print(f"Match found.")
                        send_telegram(f"Match found: {name} ({match_type}, {madori}) {MOBILE_URL}")
                        break
                
                browser.close()
                print("Browser closed.")
                return # Exit after successful run
            
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            time.sleep(retry_delay)  # Wait before retrying

    print("All attempts failed. Exiting...")

if __name__ == "__main__":
    # This means: only run main() if this file is run directly (not imported)
    main()
