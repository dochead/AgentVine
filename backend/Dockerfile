FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency installation
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy project files
COPY pyproject.toml ./
COPY app ./app

# Install dependencies
RUN uv pip install --system -e .

# Create data directory for SQLite
RUN mkdir -p /data

# Expose port
EXPOSE 8000

# Run backend
CMD ["python", "-m", "app.main"]
