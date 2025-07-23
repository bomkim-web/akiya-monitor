# Base image
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
ADD . /app

# Set working directory
WORKDIR /app

# Install Playwright and dependencies
RUN uv sync --locked && \
    uv run playwright install --with-deps chromium

# Run your script
CMD ["uv", "run", "main.py"]