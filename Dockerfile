FROM python:3.11-slim

WORKDIR /app

COPY . /app/


RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev && pip install 'Twisted[tls,http2]'

CMD python manage.py makemigrations \
    && python manage.py migrate \
    && python manage.py collectstatic --no-input \
    && gunicorn --bind 0.0.0.0:8000 core.wsgi:application & \
    daphne -b 0.0.0.0 -p 8001 core.asgi:application & \
    celery -A core worker --loglevel=info