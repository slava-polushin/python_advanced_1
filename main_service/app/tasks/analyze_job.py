from datetime import datetime

from app.tasks.celery_config import celery_app
from app.database import get_db
from app.models import OrderStatus
from app.aws_client import aws_service_client
from app.config import S3_BUCKET_NAME


@celery_app.task(queue="cron_tasks")
def analyze_order_status_task():
    db = next(get_db())
    try:
        analyze_order_status(db)
    finally:
        db.close()


def analyze_order_status(db):
    aws_service_client.connect_to_s3_client()
    try:
        data = get_average_times(db)
        # Generate the report filename based on the current date
        report_date = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"order_status_average_report_{report_date}.json"
        aws_service_client.put_to_s3(data, filename, S3_BUCKET_NAME)
    except Exception as exc:
        print(exc)
        raise
    finally:
        aws_service_client.close_clients()

from sqlalchemy import func
def get_average_times(db) -> list[dict]:
    # Dictionary to store total time and count for each transition
    transition_data = {}

    order_statuses = (
        db.query(OrderStatus)
        .order_by(OrderStatus.order_id, OrderStatus.modified_at, OrderStatus.id)
        .all()
    )

    for i in range(len(order_statuses) - 1):
        current_order_status = order_statuses[i]
        next_order_status = order_statuses[i + 1]

        # Обработка проводится в рамках одного заказа на поездку
        if current_order_status.order_id == next_order_status.order_id:
            from_status = current_order_status.status
            to_status = next_order_status.status
            time_taken = (
                next_order_status.modified_at - current_order_status.modified_at
            ).total_seconds()

            transition_key = f"{from_status} -> {to_status}"

            if transition_key not in transition_data:
                transition_data[transition_key] = {"total_time": 0, "count": 0}

            transition_data[transition_key]["total_time"] += time_taken
            transition_data[transition_key]["count"] += 1

    # Calculate average times
    average_times = []
    for transition, data in transition_data.items():
        average_time = data["total_time"] / data["count"]
        average_times.append(
            {"transition": transition, "count": f"{data["count"]}", "average_time": f"{average_time:.2f}"}
        )
    return average_times
