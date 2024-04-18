# Taxi API
API for taxi drivers, enabling them to join a queue and accept orders.

Key methods:

- Registration and authentication
- Queue order management
- Order retrieval and tracking

# Quickstart
    git clone https://github.com/polatbeknazarov/taxi_api.git
    cd taxi_api

    python3 -m venv venv
    source venv/bin/activate

    # Install poetry
    pip install poetry

    # Install packages
    poetry install


This project uses environment variables for configuration. Before running the application, you need to create a .env file based on .env.template and fill it with values.

### Creating the .env file

1. Copy the contents of the .env.template file.
2. Create a new file named .env.
3. Paste the copied values into the .env file.
4. Fill in the values in the .env file with corresponding values for your environment.

Example content of the .env.template file:

    SECRET_KEY="your_secret_key"

    DB_NAME=your_database_name
    DB_USER=your_database_user
    DB_PASSWORD=your_database_password
    DB_HOST=your_database_host
    DB_PORT=your_database_port

    CELERY_BROKER_URL=redis://<HOST>:<PORT>
    CELERY_RESULT_BACKEND=redis://<HOST>:<PORT>

### Run the app locally:
    python manage.py runserver 0.0.0.0:8000