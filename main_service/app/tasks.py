import json
import httpx

from pydantic import BaseModel

from app.config import COORDINATES_SERVICE_URL
from app.config import PRICE_SERVICE_URL
from app.redis_client import redis_client_coordinates, redis_client_price

from app.schemas import CoordinatesBase


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
