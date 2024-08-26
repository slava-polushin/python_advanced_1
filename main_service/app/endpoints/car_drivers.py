""" Интерфейсы REST-api для назначение водителей автомобилям
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.crud import create_cardriver_in_db
from app.schemas import CarDriver, CarDriverAdd, Car, Driver
from app.database import get_db

router = APIRouter()



@router.post("/cardrivers/", response_model=CarDriver)
def create_cardriver(cardriver: CarDriverAdd, db: Session = Depends(get_db)):
    return create_cardriver_in_db(db=db, cardriver=cardriver)


# @router.get("/driver_via_car/{car_id}", response_model=Driver)
# def read_car(car_id: int, db: Session = Depends(get_db)):
#     db_client = get_driver_via_car(db, car_id=car_id)
#     if db_client is None:
#         raise HTTPException(status_code=404, detail="Car not found")
#     return db_client

# @router.get("/car_via_driver/{driver_id}", response_model=Car)
# def read_car(driver_id: int, db: Session = Depends(get_db)):
#     db_client = get_car_via_driver(db, driver_id=driver_id)
#     if db_client is None:
#         raise HTTPException(status_code=404, detail="Car not found")
#     return db_client