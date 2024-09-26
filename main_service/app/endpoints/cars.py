""" Интерфейсы REST-api для работы с автомобилями
"""

from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session

from app.crud import get_car, create_car_in_db, get_carstatus_in_db, add_new_carstatus_in_db 
from app.database import get_db
from app.schemas import Car, CarCreate, CarStatus, CarStatusAdd
from app.schemas import carStatuses

router = APIRouter()

@router.post("/cars/", response_model=Car)
def create_car(car: CarCreate, db: Session = Depends(get_db)):
    db_car = create_car_in_db(db=db, car=car)

    new_carstatus = CarStatusAdd(car_id=db_car.car_id)
    new_carstatus.status = carStatuses["driver_missing"]
    car = add_new_carstatus_in_db(db=db, new_carstatus=new_carstatus)

    return car


@router.get("/cars/{car_id}", response_model=Car)
def read_car(car_id: int, db: Session = Depends(get_db)):
    db_client = get_car(db, car_id=car_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_client


# Запрос №9 в схеме "Architecture.drawio" : POST http://localhost:8000/mainservice_api/v1/set_car_coordinates
@router.post("/set_car_coordinates/", response_model=CarStatus)
def set_car_coordinates(car_status: CarStatusAdd, db: Session = Depends(get_db)):
    
    current_car_status = get_carstatus_in_db(db=db, car_id=car_status.car_id)
    if current_car_status is None:
        new_carstatus = CarStatusAdd(**car_status.model_dump())
        new_carstatus.car_id = car_status.car_id
    else:
        new_carstatus = CarStatusAdd(**current_car_status.model_dump())

    new_carstatus.current_latitude = car_status.current_latitude
    new_carstatus.current_longitude = car_status.current_longitude
    

    return add_new_carstatus_in_db(db=db, new_carstatus=new_carstatus)
