# Use official Python image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies (just in case)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Make sure the script is executable
RUN chmod +x main.py

# Run the bot
CMD ["python", "main.py"]