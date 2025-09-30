# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
# We install psycopg2 dependencies first
RUN apt-get update && apt-get install -y libpq-dev gcc
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Command to run the application
# This will be overridden by docker-compose for development
CMD ["uvicorn", "src.itinerary_planner.main:app", "--host", "0.0.0.0", "--port", "8000"]
