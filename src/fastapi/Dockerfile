# # # # Use the official Debian-hosted Python image
# # # FROM python:3.12-slim-bookworm

# # # # Tell pipenv where the shell is. 
# # # # This allows us to use "pipenv shell" as a container entry point.
# # # ENV PYENV_SHELL=/bin/bash

# # # ENV GOOGLE_APPLICATION_CREDENTIALS=secrets/ai-research-for-good-b6f4173936f9.json

# # # # Ensure we have an up to date baseline, install dependencies 
# # # RUN set -ex; \
# # #     apt-get update && \
# # #     apt-get upgrade -y && \
# # #     apt-get install -y --no-install-recommends build-essential git ffmpeg && \
# # #     pip install --no-cache-dir --upgrade pip && \
# # #     pip install pipenv && \
# # #     pip install fastapi uvicorn requests streamlit && \
# # #     mkdir -p /app

# # # WORKDIR /app

# # # # Add Pipfile, Pipfile.lock
# # # ADD Pipfile Pipfile.lock /app/

# # # RUN pipenv sync

# # # # Source code
# # # ADD . /app
# # # COPY ../../src /app/src
# # # ENV PYTHONPATH=/app/src
# # # # Expose port for FastAPI
# # # EXPOSE 8000

# # # # Expose port for Streamlit
# # # EXPOSE 8501

# # # # Start FastAPI and Streamlit concurrently
# # # CMD ["sh", "-c", "uvicorn src.fastapi.api:app --host 0.0.0.0 --port 8000 & streamlit run src/frontend-ui/app.py"]


# # # Use the official Debian-hosted Python image
# # FROM python:3.12-slim-bookworm

# # # Tell pipenv where the shell is. 
# # # This allows us to use "pipenv shell" as a container entry point.
# # ENV PYENV_SHELL=/bin/bash

# # ENV GOOGLE_APPLICATION_CREDENTIALS=secrets/ai-research-for-good-b6f4173936f9.json

# # # Ensure we have an up-to-date baseline, install dependencies 
# # RUN set -ex; \
# #     apt-get update && \
# #     apt-get upgrade -y && \
# #     apt-get install -y --no-install-recommends build-essential git ffmpeg && \
# #     pip install --no-cache-dir --upgrade pip && \
# #     pip install pipenv && \
# #     pip install fastapi uvicorn requests streamlit && \
# #     mkdir -p /app

# # WORKDIR /app

# # # Add Pipfile, Pipfile.lock from fastapi directory
# # ADD fastapi/Pipfile fastapi/Pipfile.lock /app/

# # RUN pipenv sync

# # # Source code
# # ADD fastapi .  
# # COPY src /app/src

# # ENV PYTHONPATH=/app/src

# # # Expose port for FastAPI
# # EXPOSE 8000

# # # Expose port for Streamlit
# # EXPOSE 8501

# # # Start FastAPI and Streamlit concurrently
# # CMD ["sh", "-c", "uvicorn src.fastapi.api:app --host 0.0.0.0 --port 8000 & streamlit run src/frontend-ui/app.py"]

# # Use the official Debian-hosted Python image
# FROM python:3.12-slim-bookworm

# # Tell pipenv where the shell is. 
# # This allows us to use "pipenv shell" as a container entry point.
# ENV PYENV_SHELL=/bin/bash

# ENV GOOGLE_APPLICATION_CREDENTIALS=secrets/ai-research-for-good-b6f4173936f9.json

# # Ensure we have an up to date baseline, install dependencies 
# RUN set -ex; \
#     apt-get update && \
#     apt-get upgrade -y && \
#     apt-get install -y --no-install-recommends build-essential git ffmpeg && \
#     pip install --no-cache-dir --upgrade pip && \
#     pip install pipenv && \
#     pip install fastapi uvicorn requests streamlit && \
#     mkdir -p /app

# WORKDIR /app

# # Add Pipfile, Pipfile.lock
# ADD ../../Pipfile ../../Pipfile.lock /app/

# RUN pipenv sync

# # Source code
# ADD ../../src /app/src
# COPY ../../src/fastapi /app/src/fastapi
# ENV PYTHONPATH=/app/src

# # Expose port for FastAPI
# EXPOSE 8000

# # Expose port for Streamlit
# EXPOSE 8501

# # Start FastAPI and Streamlit concurrently
# CMD ["sh", "-c", "uvicorn src.fastapi.api:app --host 0.0.0.0 --port 8000 & streamlit run src/frontend-ui/app.py"]

# Use the official Python image
FROM python:3.12-slim-bookworm

# Tell pipenv where the shell is. 
ENV PYENV_SHELL=/bin/bash

# Set Google application credentials for accessing Google services
ENV GOOGLE_APPLICATION_CREDENTIALS=secrets/ai-research-for-good-b6f4173936f9.json

# Ensure we have an up-to-date baseline, install dependencies 
RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential git ffmpeg && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    pip install fastapi uvicorn requests streamlit && \
    mkdir -p /app

WORKDIR /app

# Add Pipfile, Pipfile.lock
# ADD fastapi/Pipfile fastapi/Pipfile.lock /app/
# Add Pipfile, Pipfile.lock from the fastapi directory to /app
ADD src/fastapi/Pipfile src/fastapi/Pipfile.lock /app/

# Install dependencies using pipenv
RUN pipenv sync

# Copy the source code from the correct path
COPY src/ /app/src/

# Set PYTHONPATH to the src directory
ENV PYTHONPATH=/app/src

# Expose FastAPI port
EXPOSE 8000

# Expose Streamlit port
EXPOSE 8501

# Start FastAPI and Streamlit concurrently
CMD ["sh", "-c", "uvicorn src.fastapi.api:app --host 0.0.0.0 --port 8000 & streamlit run src/frontend-ui/app.py"]
