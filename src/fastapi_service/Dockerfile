# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Pipfile and Pipfile.lock into the container
COPY Pipfile Pipfile.lock /app/

# Install pipenv and dependencies
RUN pip install pipenv
RUN pipenv install --dev

# Copy the rest of the application code
COPY . /app
WORKDIR /app

# Expose the port the app will run on
EXPOSE 8000

# Set the environment to production (optional)
ENV PYTHONUNBUFFERED=1

# Run the FastAPI application using uvicorn within pipenv
CMD ["pipenv", "run", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
