# Akiya Monitor

This project automatically monitors vacant house listings (空き家, akiya) and sends a Telegram notification when a match is found.

## Features

- Uses [Playwright](https://playwright.dev/python/) for browser automation
- Searches for properties matching your criteria
- Sends a Telegram message when a match is detected
- Designed for scheduled automation via GitHub Actions

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/akiya-monitor.git
cd akiya-monitor
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 3. Set environment variables

Set the following environment variables (locally or in your workflow):

- `TELEGRAM_TOKEN` – Your Telegram bot token
- `TELEGRAM_CHAT_ID` – Your Telegram chat ID
- `TARGET_URL` – The URL of the property search page
- `MOBILE_URL` – The mobile URL for notifications
- `KEYWORD` – The keyword to search for (e.g., property name)

### 4. Run the script

```bash
python main.py
```

## GitHub Actions Workflow

This project includes a workflow file at `.github/workflows/auto-check.yml` to run the monitor automatically.

### Secrets to set in GitHub

- `TELEGRAM_TOKEN`
- `TELEGRAM_CHAT_ID`
- `TARGET_URL`
- `MOBILE_URL`
- `KEYWORD`

Go to your repository’s **Settings > Secrets and variables > Actions** to add these.

### Workflow schedule

The workflow runs every 5 minutes between 00:00 and 10:55 UTC (09:00–19:55 JST).

## How it works

1. The script launches a headless browser and navigates to the target site.
2. It fills out the search form with your criteria.
3. It scans the results for your keyword.
4. If a match is found, it sends a Telegram notification.

## License

MIT License

---

**Note:**  
You must have a Telegram bot and chat ID.  
See [Telegram Bot API documentation](https://core.telegram.org/bots) for setup instructions.