# Use official Python slim image for smaller size
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (for SQLite, etc.)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create directories for persistent storage
RUN mkdir -p /app/uploads /app/instance

# Set permissions for uploads and instance folders (non-root user)
RUN chown -R 1000:1000 /app/uploads /app/instance && \
    chmod -R 755 /app/uploads /app/instance

# Run as non-root user for security
USER 1000:1000

# Expose port (Northflank sets $PORT dynamically)
EXPOSE $PORT

# Run Gunicorn with dynamic port binding
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "main:app"]