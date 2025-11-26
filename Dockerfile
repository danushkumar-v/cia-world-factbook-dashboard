FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create cache directory
RUN mkdir -p .cache

# Expose port
EXPOSE 8050

# Set environment variables
ENV APP_ENV=production
ENV PYTHONUNBUFFERED=1

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "--workers", "4", "--timeout", "120", "wsgi:server"]
