FROM python:3.11-slim

WORKDIR /app

COPY . /app/

RUN apt-get update && apt-get install -y curl && apt-get clean
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

CMD python manage.py makemigrations \
    && python manage.py migrate \
    && python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='root').exists() or User.objects.create_superuser('root', 'root@example.com', 'root')" \
    && python manage.py collectstatic --no-input \
    && gunicorn --bind 0.0.0.0:8000 core.wsgi:application