# Use Python 3.11 slim image for smaller footprint
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal for free tier)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with optimization for free tier
RUN pip install --no-cache-dir --no-compile -r requirements.txt \
    && pip cache purge

# Copy application code
COPY . .

# Create directories for logs and reports
RUN mkdir -p logs reports data

# Expose port for Streamlit dashboard
EXPOSE 8501

# Health check (simplified for free tier)
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command optimized for low memory
CMD ["python", "-u", "launch_dashboard.py"]
