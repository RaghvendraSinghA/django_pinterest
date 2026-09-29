# Django Pinterest

A Django-based Pinterest clone project.

## Setup

### 1. Clone the repository

    git clone <repository-url>
    cd django_pinterest

### 2. Create a virtual environment

    python3 -m venv .venv

### 3. Activate the virtual environment

    source .venv/bin/activate

### 4. Install dependencies

    pip install -r requirements.txt

### 5. Configure environment variables

Create a `.env` file in the project root.

    SECRET_KEY=your-secret-key
    DEBUG=True
    DATABASE_URL=postgresql://postgres:your_password@localhost:5432/pinterest_db

Do not commit `.env` to Git.

### 6. Run migrations

    python manage.py migrate

### 7. Start the development server

    python manage.py runserver

Open:

    http://127.0.0.1:8000/

## App

`home_app` contains the homepage functionality.

`pinterest_config` contains the main Django project configuration.

## Production

`build.sh` is used for the deployment build process.

It installs dependencies, collects static files, and runs migrations.

Gunicorn is used as the production web server.

    gunicorn pinterest_config.wsgi:application


### Live link: (https://django-pinterest.onrender.com)