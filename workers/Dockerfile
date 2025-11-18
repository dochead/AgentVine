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
COPY workers ./workers

# Install dependencies
RUN uv pip install --system -e .

# Create workspace directory
RUN mkdir -p /workspace

# Run worker
CMD ["python", "-m", "workers.main", "--name", "worker"]
