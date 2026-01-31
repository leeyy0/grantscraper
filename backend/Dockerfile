# 1. Use the official Playwright image (Ubuntu 24.04 + Python 3.12)
# This matches the Python version (3.12) seen in your logs.
FROM mcr.microsoft.com/playwright/python:v1.49.1-noble

# 2. Install uv (copying the binary is faster/cleaner than pip install)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Set working directory
WORKDIR /app

# 4. Copy configuration files first (for better caching)
COPY pyproject.toml uv.lock ./

# 5. Install dependencies
# --frozen: ensures we use exactly what is in uv.lock
# --no-dev: skips development dependencies (optional, remove if you need dev tools)
RUN uv sync --frozen --no-dev

# 6. Copy the rest of your application code
COPY . .

# 7. Ensure the Playwright browsers match the installed Python package version
# The base image has browsers, but if your uv.lock has a newer Playwright version,
# this command updates the browser binaries to match.
ENV PATH="/app/.venv/bin:$PATH"
RUN uv run playwright install

# 8. Run the app using the virtual environment
# Adjust "app.main:app" if your entry point is different
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]