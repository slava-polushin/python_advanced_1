
from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session
from app.crud import create_order_in_db, get_orderstatus, add_new_orderstatus_in_db, pay_order_via_queue

from app.schemas import Order, OrderCreate, OrderStatus, OrderStatusAdd, PayInfo, orderStatuses
from app.database import get_db

router = APIRouter()

# Создание заявки на поездку в такси
@router.post("/orders/", response_model=Order)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    return create_order_in_db(db=db, order=order)


@router.get("/orders/{order_id}", response_model=OrderStatus)
def read_order_status(order_id: int, db: Session = Depends(get_db)):
    db_orderstatus = get_orderstatus(db=db, order_id=order_id)
    if db_orderstatus is None:
        raise HTTPException(status_code=404, detail="Order status not found")
    return db_orderstatus


@router.post("/cancel_order_from_client/", response_model=OrderStatus)
def cancel_order(order_id: int = Body(..., embed=True), db: Session = Depends(get_db)):
    orderstatus = read_order_status(order_id=order_id, db=db)

    if orderstatus.status in (orderStatuses['trip_started'], orderStatuses['cancelled']):
        raise HTTPException(status_code=404, detail=f"Order {order_id} is in status {
                            orderstatus.status} and can't be cancelled")

    new_orderstatus = OrderStatusAdd(**orderstatus.model_dump())
    new_orderstatus.status = orderStatuses['cancelled']

    orderstatus = add_new_orderstatus_in_db(
        db=db, new_orderstatus=new_orderstatus)
    return orderstatus


@router.post("/pay_order/", response_model=PayInfo)
def pay_order(pay_info: PayInfo, db: Session = Depends(get_db)):

    orderstatus = read_order_status(order_id=pay_info.order_id, db=db)

    if orderstatus.status in (orderStatuses['cancelled']):
        raise HTTPException(status_code=404, detail=f"Order {
                            pay_info.order_id} is in status {orderstatus.status} and can't be payed")

    if pay_info.pay_sum > orderstatus.unpaid_rest:
        raise HTTPException(status_code=404, detail=f"Order {pay_info.order_id} has unpayed rest  {
                            orderstatus.unpaid_rest}, what less then pay sum {pay_info.pay_sum}")

    # Оплата суммы 0 не является ошибкой, но и не требует обработки
    if pay_info.pay_sum in (None, 0):
        return pay_info

    pay_info = pay_order_via_queue(pay_info=pay_info, orderstatus=orderstatus)

    return pay_info
