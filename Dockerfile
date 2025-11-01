# Use Python 3.12 slim as the base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Install additional dependencies used in app.py
RUN pip install --no-cache-dir httpx python-dotenv

# Copy the application code
COPY app/ ./app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
