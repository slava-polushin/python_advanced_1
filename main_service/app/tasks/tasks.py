import json
import httpx

from sqlalchemy.orm import Session


# from pydantic import BaseModel

from app.tasks.celery_config import celery_app
from app.database import get_db


from app.config import COORDINATES_SERVICE_URL
from app.config import PRICE_SERVICE_URL
from app.redis_client import redis_client_coordinates, redis_client_price

from app.rabbitmq_client import APP_QUEUE_MAP, rabbitmq_client

from app.schemas import *

def get_coordinates_via_str(address: str):
    address_key = f"address:{address}"
    cached_coordinates = redis_client_coordinates.get(address_key)
    if cached_coordinates:
        # Найденные в кеше значения преобразуются в dict
        return json.loads(cached_coordinates)

    response = httpx.post(
        COORDINATES_SERVICE_URL, json={"address": address}, timeout=10
    )
    response.raise_for_status()
    coordinates = response.json()

    # Срок жизни значения в кеше - 1 час
    redis_client_coordinates.set(address_key, coordinates, ex=3600)
    return coordinates


def get_price_via_coordinates(coordinates: CoordinatesBase):
    coordinates_key = f"coordinates:{coordinates.start_latitude}:{
        coordinates.start_longitude}:{coordinates.finish_latitude}:{coordinates.finish_longitude}"
    cached_coordinates = redis_client_price.get(coordinates_key)
    if cached_coordinates:
        # Найденные в кеше значения преобразуются в dict
        return json.loads(cached_coordinates)

    response = httpx.post(
        PRICE_SERVICE_URL, json={
            "start_latitude": coordinates.start_latitude,
            "start_longitude": coordinates.start_longitude,
            "finish_latitude": coordinates.finish_latitude,
            "finish_longitude": coordinates.finish_longitude
        },
        timeout=10
    )
    response.raise_for_status()
    price = response.json()

    # Срок жизни значения в кеше - 1 час
    redis_client_price.set(coordinates_key, price, ex=3600)
    return price


# Обработка уведомления о корректной оплате заказа
def pay_order_in_db(db: Session, order_id: int, sum_to_pay: float) -> OrderStatus:
    print(f"### order_id={order_id}, sum_to_pay={sum_to_pay}")
    pass

    return None

# Было проведено несколько разных попыток интеграции двух сервисов через CELERY,
# Но ни один из нх не сработал

# 1.
# @celery_app.task()
# Изначально было сделано так, и во внешнем сервисе попытка вызова - такая:
            # app = Celery(
            #     "tasks",
            #     broker_url=CELERY_BROKER_URL
            # )
            # app.send_task(
            #     name='app.tasks.tasks.save_payinfo',
            #     args=(pay_sum, order_status) 
            # )
# С одной стороны это не падало, но и ничего не происходило.


# 2.
# С таким вариантом объявления точки обработки - падает при старте сервиса
# Судя по всему shared_task может выступать как отдельный декоратор, но подойдет ли он, непонятно; пробовал методом "наугад"
# from celery import shared_task
# @shared_task(name='save_payinfo_queue',bind=True,)


# 3.
# Вариант предыдущего случая, с адресом 'app.tasks.tasks.save_payinfo'

# from celery import shared_task
# @shared_task()

#4.
# Пока что оставлен первоначальный вариант
@celery_app.task()
def save_payinfo(order_id: int, sum_to_pay: float):

    print(f"PAY APPROVE is Recieved: order_id={order_id}, sum_to_pay={sum_to_pay}")

    db = next(get_db())
    try:
        pay_order_in_db(db, order_id, sum_to_pay)
    finally:
        db.close()
    return order_id
    