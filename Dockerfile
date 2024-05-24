# Use the official Python 3.8 image.
# https://hub.docker.com/_/python
FROM python:3.8-slim

# Set environment variables to reduce Python's output buffering and enable it to run directly within Docker
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the Docker container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Command to run when starting the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]