# pull official base image
FROM python:3.12.7-slim

# set work directory
WORKDIR /src/ats/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean

# Install Poetry and dependencies
# RUN pip install --upgrade pip
# RUN pip install django psycopg2-binary strawberry-graphql-django django-debug-toolbar pytest pytest-django
COPY pyproject.toml poetry.lock /src/ats/
RUN pip install --upgrade --no-cache-dir pip poetry \
    && poetry --version \
    # Configure to use system instead of virtualenvs
    && poetry config virtualenvs.create false \
    && poetry install --no-root \
    # Remove installer
    && pip uninstall -y poetry virtualenv-clone virtualenv

#COPY pyproject.toml poetry.lock /src/project/

# Copy project files
COPY . /src/ats/

# Run the application (you can adjust the command as needed)
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
