from fastapi import APIRouter
from pydantic import BaseModel
from random import uniform

router = APIRouter()


class AddressRequest(BaseModel):
    address: str


class CoordinatesResponse(BaseModel):
    latitude: float
    longitude: float


@router.post("/get-coordinates", response_model=CoordinatesResponse)
def get_coordinates(request: AddressRequest):
    # TODO: в тестовой системе координаты генерируются случайным образом
    # 5 знаков после запятой дают точность координат до метра
    latitude = round(uniform(-90, 90), 5)
    longitude = round(uniform(-180, 180), 5)
    return CoordinatesResponse(latitude=latitude, longitude=longitude)
