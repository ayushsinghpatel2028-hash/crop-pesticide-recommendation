# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /code

# Copy requirements file and install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy all backend application code
COPY . /code

# Create an empty database file to initialize SQLite cleanly if not present
RUN touch /code/database.db

# Hugging Face Spaces runs on port 7860 by default
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
