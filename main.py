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
            page.goto(TARGET_URL, timeout=10000)
            page.wait_for_load_state("networkidle", timeout=5000)

            # If a new tab (search form) is opened, switch to it
            pages = browser.contexts[0].pages
            search_page = pages[-1] if len(pages) > 1 else page

            # Tick the checkbox for 間取り "2K ～ 2LDK"
            try:
                search_page.get_by_role('cell', name='2K ～ 2LDK', exact=True).get_by_role('checkbox').click()
            except Exception:
                pass

            # Select "一般申込" in 優先募集種別 dropdown
            try:
                search_page.locator('select[name="akiyaInitRM.akiyaRefM.yusenBoshu"]').select_option(['一般申込'])
            except Exception:
                pass

            # Click the search button
            try:
                search_button = search_page.get_by_role('link', name='検索する').first
                search_button.click()
            except Exception:
                pass
                
            search_page.wait_for_load_state("networkidle", timeout=5000)

            # Look through all table rows on the results page
            rows = search_page.query_selector_all('tr')
            for row in rows:
                text = row.inner_text()
                if KEYWORD in text:
                    send_telegram(f"Match found: {KEYWORD} {MOBILE_URL}")
                    break
            
            browser.close()
            
    except Exception as e:
        raise

if __name__ == "__main__":
    # This means: only run main() if this file is run directly (not imported)
    main()
