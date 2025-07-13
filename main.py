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
    try:
        # Start Playwright (browser automation)
        with sync_playwright() as p:
            # Launch a headless (invisible) browser for production
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Go to the target URL
            with page.expect_popup() as search_page:
                page.goto(TARGET_URL, timeout=10000)
                page.wait_for_load_state("networkidle", timeout=5000)
                search_page = search_page.value

            # Tick the checkbox for 間取り "2K ～ 2LDK"
            try:
                search_page.get_by_role('cell', name='2K ～ 2LDK', exact=True).get_by_role('checkbox').click()
            except Exception:
                pass

            # Click the search button
            try:
                search_button = search_page.get_by_role('link', name='検索する').nth(1)
                search_button.click()
            except Exception:
                pass
                
            search_page.wait_for_load_state("networkidle", timeout=5000)

            # Select the table with class 'cell666666' 
            tables = search_page.query_selector_all('table.cell666666')

            # Select the second table (index 1) which contains the search results
            table = tables[1]

            # Get all the rows (tr) of this table
            rows = table.query_selector_all('tr')[1:]  # [1:] skips the first tr (header row)

            for row in rows:
                # For each row, you can get the values of each column (td)
                cells = row.query_selector_all('td')
                print(row)
                # Example: 2nd td (building name), 4th td (category)
                if not cells or len(cells) < 4:
                    continue  # Safety: skip rows with not enough columns
                name = cells[1].inner_text().strip()
                type_ = cells[3].inner_text().strip()
                if name == KEYWORD and (type_ == "一般" or type_ == "応援"):
                    match_type = type_
                    send_telegram(f"Match found: {name} ({match_type}) {MOBILE_URL}")
                    break
            
            browser.close()
            
    except Exception as e:
        raise

if __name__ == "__main__":
    # This means: only run main() if this file is run directly (not imported)
    main()
