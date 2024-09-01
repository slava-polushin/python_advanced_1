""" Интерфейсы REST-api для работы с водителями
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.crud import get_driver, create_driver_in_db
from app.schemas import Driver, DriverCreate
from app.database import get_db

router = APIRouter()

@router.post("/drivers/", response_model=Driver)
def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
    return create_driver_in_db(db=db, driver=driver)


@router.get("/drivers/{driver_id}", response_model=Driver)
def read_driver(driver_id: int, db: Session = Depends(get_db)):
    db_driver = get_driver(db, driver_id=driver_id)
    if db_driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    return db_driver
