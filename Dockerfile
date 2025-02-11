FROM python:3.13-slim
RUN apt-get update && apt-get install -y chromium-driver
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory and create necessary directories with proper permissions
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./
COPY locustfile.py ./
RUN uv sync --frozen

# Set the entrypoint to run Locust
ENTRYPOINT ["uv", "run", "locust", "-f", "locustfile.py", "--headless", "--users", "1000", "--spawn-rate", "1", "--host", "https://localhost:8080", "--run-time", "5m"] 