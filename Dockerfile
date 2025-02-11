FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Copy the locust file and environment files
COPY locustfile.py ./

# Install dependencies using uv
RUN uv sync --frozen

EXPOSE 8080

# Set the entrypoint to run Locust
ENTRYPOINT ["uv", "run", "locust", "-f", "locustfile.py", "--web-port", "8080", "--users", "1000", "--spawn-rate", "1", "--host", "https://localhost:8080"] 