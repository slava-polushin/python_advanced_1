""" Интерфейсы REST-api для назначение водителей автомобилям
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.crud import create_cardriver_in_db, get_driver_for_car, get_car_for_driver
from app.schemas import CarDriver, CarDriverAdd, Car, Driver
from app.database import get_db

from datetime import date

router = APIRouter()



@router.post("/cardrivers/", response_model=CarDriver)
def create_cardriver(cardriver: CarDriverAdd, db: Session = Depends(get_db)):
    return create_cardriver_in_db(db=db, cardriver=cardriver)


@router.get("/cardriver_via_car/{car_id}", response_model=CarDriver)
def read_driver_via_car(car_id: int, db: Session = Depends(get_db)):
    fromdate=date.today()
    db_cardriver = get_driver_for_car(db, car_id=car_id, fromdate=fromdate)
    if db_cardriver is None:
        raise HTTPException(status_code=404, detail=f"Driver for car {car_id} on date {fromdate} not found")
    return db_cardriver

@router.get("/cardriver_via_driver/{driver_id}", response_model=CarDriver)
def read_car_via_driver(driver_id: int, db: Session = Depends(get_db)):
    fromdate=date.today()
    db_cardriver = get_car_for_driver(db, driver_id=driver_id,fromdate=fromdate)
    if db_cardriver is None:
        raise HTTPException(status_code=404, detail=f"Car for driver {driver_id} on date {fromdate} not found")
    return db_cardriver