# Use an official Python base image
FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.8.2

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl build-essential git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set working directory
WORKDIR /app

# Add this line to fix import issues
ENV PYTHONPATH=/app

# Configure Poetry to not use virtualenvs
RUN --mount=type=bind,source=src,target=src \
    --mount=type=bind,source=dist,target=dist \
    --mount=type=bind,source=README.md,target=README.md \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=poetry.lock,target=poetry.lock \
    poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Install Chromium and the driver
RUN apt-get update && apt-get install -y \
    chromium chromium-driver \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["poetry", "run", "python3", "-m", "src.main"]