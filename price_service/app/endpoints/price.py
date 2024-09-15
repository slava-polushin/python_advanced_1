from fastapi import APIRouter
from pydantic import BaseModel
# from random import uniform

from geopy.distance import great_circle as GC

from app.settings import settings


router = APIRouter()


class CoordinatesPairRequest(BaseModel):
    start_latitude: float
    start_longitude: float
    finish_latitude: float
    finish_longitude: float


# Запрос №6 в схеме "Architecture.drawio" : POST localhost:8001/price_api/v1/get-price/
@router.post("/get-price", response_model=float)
def get_price(request: CoordinatesPairRequest):
    # TODO: для тестового использования, принимается сферическая модель Земли
    # Также в качестве допущения принимается что расстояние в 1 км пути стоит 1 рубль (вне зависимости от времени суток, дня недели и ни от чего другого), и что все расстояния являются прямыми линиями на сфере.

    price_per_km = settings.price_per_km

    distance = GC((request.start_latitude, request.finish_latitude),
                  (request.finish_latitude, request.finish_longitude)
                  ).km

    price = round(distance*price_per_km, 2)
    return price
