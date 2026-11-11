
# Pinterest Clone

A Pinterest-inspired web application built using Django. Users can create, edit, delete, explore, and search Pins. The application uses Elasticsearch for fuzzy search and Celery for asynchronous background tasks.

## Features

- User authentication (Signup and Login).
- Create, edit, and delete Pins.
- Upload and manage images using Cloudinary.
- Create and manage Boards.
- Like and explore Pins.
- Fuzzy search using Elasticsearch.
- Asynchronous background tasks using Celery.
- Redis as a Celery message broker.
- Automatic synchronization between PostgreSQL and Elasticsearch.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web framework |
| PostgreSQL | Primary database |
| Elasticsearch | Search engine |
| Redis | Message broker |
| Celery | Background task processing |
| Cloudinary | Image storage |
| HTML, CSS, JavaScript | Frontend |

## Prerequisites

Make sure you have installed:

- Python 3.9+
- PostgreSQL
- Docker
- Git

## 1. Clone the Repository

```bash
git clone <repository-url>
cd django_pinterest_copy_fixing
```

## 2. Create and Activate Virtual Environment

```bash
python3 -m venv .venv
```

Activate the environment:

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Create a `.env` file in the project root.

Add the required configuration:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True

ELASTICSEARCH_HOST=http://localhost:9200

# Add your PostgreSQL database credentials
# Add your Cloudinary credentials
```

Configure the PostgreSQL and Cloudinary variables according to your `settings.py`.

**Important:** Never commit your `.env` file or expose your secret credentials.

## 5. Start PostgreSQL

Make sure your PostgreSQL server is running and create the database configured in your Django settings.

## 6. Start Redis

Run Redis using Docker:

```bash
docker run -d \
  --name pinterest-redis \
  -p 6379:6379 \
  redis:7-alpine
```

If the container already exists, start it:

```bash
docker start pinterest-redis
```

Verify Redis:

```bash
docker exec -it pinterest-redis redis-cli ping
```

Expected output:

```text
PONG
```

## 7. Start Elasticsearch

Run Elasticsearch using Docker:

```bash
docker run -d \
  --name pinterest-elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  docker.elastic.co/elasticsearch/elasticsearch:8.17.0
```

If the container already exists:

```bash
docker start pinterest-elasticsearch
```

Verify Elasticsearch:

```bash
curl http://localhost:9200
```

## 8. Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## 9. Initialize Elasticsearch Index

Create the Pins index:

```bash
python manage.py shell
```

Inside the Django shell:

```python
from pinterest_config.elasticsearch_indexes import create_pins_index

create_pins_index()
```

To index existing Pins from PostgreSQL:

```python
from pinterest_config.elasticsearch_indexes import index_existing_pins

index_existing_pins()
```

This step is required when initializing Elasticsearch with existing database records.

## 10. Run the Django Application

Open a terminal in the project root:

```bash
python manage.py runserver
```

Application URL:

```text
http://127.0.0.1:8000/
```

## 11. Start Celery Worker

Open a separate terminal in the project root.

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Start the Celery worker:

```bash
celery -A pinterest_config worker --loglevel=info
```

The Celery worker processes background tasks such as:

- Uploading Pin images to Cloudinary.
- Deleting temporary images.
- Deleting Pin images from Cloudinary.
- Synchronizing Pins with Elasticsearch.

## Running Services

During development, the following services should be running:

| Service | Command |
|---|---|
| Django | `python manage.py runserver` |
| Celery | `celery -A pinterest_config worker --loglevel=info` |
| Redis | Docker container |
| Elasticsearch | Docker container |
| PostgreSQL | PostgreSQL server |



## Stopping Docker Containers

```bash
docker stop pinterest-redis
docker stop pinterest-elasticsearch
```

## Useful Commands

```bash
# Run Django server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Start Celery worker
celery -A pinterest_config worker --loglevel=info

# List all containers
docker ps -a

# View running containers
docker ps

# View Docker logs
docker logs pinterest-redis
docker logs pinterest-elasticsearch
```
