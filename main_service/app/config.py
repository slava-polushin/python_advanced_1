import os
from dotenv import load_dotenv


load_dotenv()  # Init environment variables by .env file settings

DEBUG_MODE = bool(os.getenv("DEBUG_MODE"))

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://myuser:mypassword@localhost:5432/mydatabase"
)
MAINSERVICE_APP_PORT = int(os.getenv("APP_PORT", 8000))

COORDINATES_SERVICE_URL = os.getenv(
    "COORDINATES_SERVICE_URL", "http://localhost:8001/coordinates_api/v1/get-coordinates"
)
COORDINATES_REDIS_URL = os.getenv("COORDINATES_REDIS_URL", "redis://localhost:6379/1")

PRICE_SERVICE_URL = os.getenv(
    "PRICE_SERVICE_URL", "http://localhost:8002/price_api/v1/get-price"
)
PRICE_REDIS_URL = os.getenv("PRICE_REDIS_URL", "redis://localhost:6379/2")

RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL", "RABBITMQ_URL=amqp://user:password@localhost:5672/"
)
RABBITMQ_RECONNECT_PAUSE = 5
RABBITMQ_RECONNECT_COUNT = 100
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
