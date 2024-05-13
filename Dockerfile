# Stage 1: Build Python dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        gnupg \
        && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Install Python dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Stage 2: Production image
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy the rest of the application
COPY . .

# Install Node.js
ARG NODE_MAJOR=18

RUN apt-get update \
    && apt-get install -y ca-certificates curl gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install nodejs -y \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean

# Install Tailwind CSS and build assets
RUN SECRET_KEY=nothing python manage.py tailwind install --no-input \
    && SECRET_KEY=nothing python manage.py tailwind build --no-input \
    && SECRET_KEY=nothing python manage.py collectstatic --no-input

# Switch to a non-root user
RUN useradd --create-home python \
    && chown -R python:python /app
USER python

# Define command to run the application
CMD python manage.py makemigrations \
    && python manage.py migrate \
    && python manage.py collectstatic --no-input \
    && python manage.py tailwind start \
    && gunicorn --bind 0.0.0.0:8000 core.wsgi:application & \
    daphne -b 0.0.0.0 -p 8001 core.asgi:application & \
    celery -A core worker --loglevel=info
