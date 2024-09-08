from celery import Celery, signals
from app.config import CELERY_BROKER_URL,DEBUG_MODE
from app.rabbitmq_client import rabbitmq_client, APP_QUEUE_MAP
from app.redis_client import redis_client_coordinates, redis_client_price
import logging

logger = logging.getLogger(__name__)
app = Celery(
    "tasks",
    broker=CELERY_BROKER_URL,
    include=["app.tasks.tasks"],
)

# Define queues (no need to specify exchange or routing key)
app.conf.task_queues = {
    "default": {},  # Default queue for general tasks
    APP_QUEUE_MAP["pay_approve_queue"]: {},  # Default queue for accepted payings
    # "cron_tasks": {},  # Queue specifically for cron tasks
}

# Configure task routes
app.conf.task_routes = {
    "app.tasks.tasks.save_payinfo": {"queue": APP_QUEUE_MAP["pay_approve_queue"]},
    # "app.tasks.analyze_job.analyze_incident_status_task": {"queue": "cron_tasks"},
}


def writeLog(message:str):
    if DEBUG_MODE:
        logger.info(message)

@signals.worker_init.connect
def init(**kwargs):
    writeLog("Started init")
    rabbitmq_client.connect()
    redis_client_coordinates.connect()
    redis_client_price.connect()
    writeLog("finished init")


@signals.worker_shutdown.connect
def close(**kwargs):
    writeLog("Started close")
    rabbitmq_client.close()
    redis_client_coordinates.close()
    redis_client_price.close()
    writeLog("finished close")
