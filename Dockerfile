FROM python:3.11-slim

WORKDIR /app

COPY . /app/


RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev && pip install 'Twisted[tls,http2]'

ARG NODE_MAJOR=18

RUN apt-get update \
    && apt-get install -y ca-certificates curl gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install nodejs -y \
    && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
    && apt-get clean \
    && useradd --create-home python \
    && chown python:python -R /app

RUN SECRET_KEY=nothing python manage.py tailwind install --no-input;
RUN SECRET_KEY=nothing python manage.py tailwind build --no-input;
RUN SECRET_KEY=nothing python manage.py collectstatic --no-input;

CMD python manage.py makemigrations \
    && python manage.py migrate \
    && python manage.py collectstatic --no-input \
    && python manage.py tailwind start \
    && gunicorn --bind 0.0.0.0:8000 core.wsgi:application & \
    daphne -b 0.0.0.0 -p 8001 core.asgi:application & \
    celery -A core worker --loglevel=info