# Use official Python slim image for smaller size
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (Docker layer caching — faster rebuilds)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose app port
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
