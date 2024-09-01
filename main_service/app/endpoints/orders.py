
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.crud import create_order_in_db
# from app.crud import get_order, create_order_in_db
from app.schemas import Order, OrderCreate
from app.database import get_db

router = APIRouter()

@router.post("/orders/", response_model=Order)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    return create_order_in_db(db=db, order=order)
