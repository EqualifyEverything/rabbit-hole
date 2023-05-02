# Use an official Python runtime as a parent image
# Use alpine with Python pre-installed
FROM python:3.9-alpine

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY src /app/src

# Env Variables
ENV APP_PORT 8084

# Logging Level
ENV LOG_LEVEL INFO

EXPOSE $APP_PORT

# Run main.py when the container launches
CMD ["python", "src/main.py"]