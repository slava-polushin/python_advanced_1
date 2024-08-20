from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.crud import get_car, create_car_in_db
from app.schemas import Car, CarCreate
from app.database import get_db

router = APIRouter()

@router.post("/cars/", response_model=Car)
def create_car(car: CarCreate, db: Session = Depends(get_db)):
    return create_car_in_db(db=db, car=car)


@router.get("/cars/{car_id}", response_model=Car)
def read_user(car_id: int, db: Session = Depends(get_db)):
    db_client = get_car(db, car_id=car_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_client
