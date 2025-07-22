FROM python:3.11-slim

# Install system packages needed by Playwright
RUN apt-get update && apt-get install -y \
    wget gnupg libnss3 libatk-bridge2.0-0 libgtk-3-0 \
    libx11-xcb1 libgbm1 libasound2 libxcomposite1 libxdamage1 \
    libxrandr2 libxss1 libxshmfence1 libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and Python deps
RUN pip install --no-cache-dir playwright \
    && playwright install --with-deps chromium

WORKDIR /app
COPY . .

CMD ["python", "main.py"]