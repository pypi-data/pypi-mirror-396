FROM python:3.14-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt update && apt install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY ./pyproject.toml ./uv.lock* /app/

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY ./vantage_agent /app/vantage_agent

# Run the vantage agent
CMD ["uv", "run", "--no-dev", "vtg-run"]