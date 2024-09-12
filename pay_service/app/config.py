import os
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file

RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL", "RABBITMQ_URL=amqp://user:password@localhost:5672/"
)

CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL", "redis://localhost:6379/0"
)