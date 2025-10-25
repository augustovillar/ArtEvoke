# Use official Python image
FROM python:3.13

# Set the working directory in the container
WORKDIR /app

RUN apt-get update

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy pyproject.toml first for dependency caching
COPY pyproject.toml ./

# Install dependencies using UV (creates lockfile if missing)
RUN uv sync

# Copy the rest of the application
COPY . .

# Expose the backend port
EXPOSE 5001

# Command to run the FastAPI app with reload using UV
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001", "--reload"]
