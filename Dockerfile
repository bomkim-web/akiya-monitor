# Base image
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y wget gnupg libnss3 libatk-bridge2.0-0 libgtk-3-0 \
    libx11-xcb1 libgbm1 libasound2 libxcomposite1 libxdamage1 \
    libxrandr2 libxss1 libxshmfence1 libxtst6 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the project into the image
ADD . /app

# Set working directory
WORKDIR /app

# Install Playwright and dependencies
RUN uv sync --locked && \
    uv run playwright install chromium

# Run your script
CMD ["uv", "run", "main.py"]