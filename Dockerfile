# Base image
FROM python:3.12-slim-bookworm

# Add uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy project files into image
COPY . /app

# Install dependencies and playwright
RUN uv sync --locked && \
    uv run playwright install --with-deps chromium

# Run script
CMD ["uv", "run", "main.py"]