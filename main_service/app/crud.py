from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from fastapi.exceptions import HTTPException

from datetime import date

from app.models import (
    Cars as CarModel,
    Clients as ClientModel,
    Drivers as DriverModel,
    CarDrivers as CarDriverModel,
    Orders as OrderModel,
    CarStatus as CarStatusModel,
    OrderStatus as OrderStatusModel,
)
from app.schemas import (
    ClientCreate,
    CarCreate,
    DriverCreate,
    CarDriverAdd,
    OrderCreate,
    OrderStatusAdd,
    Client,
    Car,
    Driver,
    CarDriver,
    Order,
    OrderStatus,
    Client,
    Car,
    Driver,

    CoordinatesBase,
)

from app.tasks.tasks import get_coordinates_via_str, get_price_via_coordinates


def get_client(db: Session, client_id: int):
    return db.query(ClientModel).filter(ClientModel.client_id == client_id).first()


def create_client_in_db(db: Session, client: ClientCreate) -> Client:
    db_client = ClientModel(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return Client.model_validate(db_client)


def get_car(db: Session, car_id: int):
    return db.query(CarModel).filter(CarModel.car_id == car_id).first()


def create_car_in_db(db: Session, car: CarCreate) -> Car:
    db_car = CarModel(**car.model_dump())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return Car.model_validate(db_car)


def get_driver(db: Session, driver_id: int):
    return db.query(DriverModel).filter(DriverModel.driver_id == driver_id).first()


def create_driver_in_db(db: Session, driver: DriverCreate) -> Driver:
    db_driver = DriverModel(**driver.model_dump())
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return Driver.model_validate(db_driver)


# Процедуры для обработки таблицы car_drivers
def create_cardriver_in_db(db: Session, cardriver: CarDriverAdd) -> CarDriver:
    subquery = db.query(CarDriverModel).filter(
        CarDriverModel.fromdate <= cardriver.fromdate).subquery()

    subquery = db.query(
        subquery,
        func.dense_rank().over(
            order_by=subquery.c.fromdate.desc(),
            partition_by=subquery.c.car_id
        ).label('rnk')
    ).subquery()

    busy_driver_fl = db.query(subquery).filter(
        subquery.c.rnk == 1,
        subquery.c.driver_id == cardriver.driver_id,
        subquery.c.car_id != cardriver.car_id
    ).count()

    if busy_driver_fl > 0:
        raise HTTPException(
            status_code=404, detail="Driver is assigned to other car. Please unassign first")

    # Поиск последнего назначенного водителя для автомобиля
    db_cardriver = db.query(CarDriverModel).filter(
        CarDriverModel.car_id == cardriver.car_id).order_by(desc(CarDriverModel.id)).first()

    if db_cardriver == None:
        db_cardriver = CarDriverModel(**cardriver.model_dump())

    # Требуется установка водителя в записи с существующей датой
    elif db_cardriver.fromdate == cardriver.fromdate:
        db_cardriver.driver_id = cardriver.driver_id

    # Требуется установка водителя в записи с новой датой
    elif db_cardriver.driver_id != cardriver.driver_id:
        db_cardriver = CarDriverModel(**cardriver.model_dump())

    db.add(db_cardriver)
    db.commit()
    db.refresh(db_cardriver)
    return CarDriver.model_validate(db_cardriver)


def get_driver_for_car(db: Session, car_id: int, fromdate: date) -> CarDriver:
    return db.query(CarDriverModel).filter(CarDriverModel.car_id == car_id, CarDriverModel.fromdate <= fromdate).order_by(desc(CarDriverModel.fromdate)).first()


def get_car_for_driver(db: Session, driver_id: int, fromdate: date) -> CarDriver:
    subquery = db.query(CarDriverModel).filter(
        CarDriverModel.fromdate <= fromdate).subquery()

    subquery = db.query(
        subquery,
        func.dense_rank().over(
            order_by=subquery.c.fromdate.desc(),
            partition_by=subquery.c.car_id
        ).label('rnk')
    ).subquery()

    result = db.query(subquery).filter(
        subquery.c.rnk == 1,
        subquery.c.driver_id == driver_id
    ).first()

    if result is None:
        return None

    return CarDriver(**result._asdict())


# Процедуры для обработки таблицы orders

# Создание заказа на поездку
def create_order_in_db(db: Session, order: OrderCreate) -> Order:
    client = db.query(ClientModel).filter(
        ClientModel.client_id == order.client_id).first()

    start_coordinates = get_coordinates_via_str(order.start_address)
    finish_coordinates = get_coordinates_via_str(order.finish_address)

    coordinates = CoordinatesBase(
        start_latitude=start_coordinates['latitude'],
        start_longitude=start_coordinates['longitude'],
        finish_latitude=finish_coordinates['latitude'],
        finish_longitude=finish_coordinates['longitude']
    )
    price = get_price_via_coordinates(coordinates=coordinates)

    db_order = OrderModel(
        client=client,
        start_address=order.start_address,
        start_latitude=start_coordinates['latitude'],
        start_longitude=start_coordinates['longitude'],
        finish_address=order.finish_address,
        finish_latitude=finish_coordinates['latitude'],
        finish_longitude=finish_coordinates['longitude'],
        price=price,
        baby_chair_fl=order.baby_chair_fl,
        # status='created',
        comment=order.comment,
    )
    db.add(db_order)

    db_order_status = OrderStatusModel(
        order=db_order,
        status=order.status,
        unpaid_rest=price,
        comment=order.status_comment
    )

    db.add(db_order_status)
    db.commit()
    db.refresh(db_order)
    db.refresh(db_order_status)

    return Order.model_validate(db_order)

# Состояние заказа

def get_orderstatus(db: Session, order_id: int) -> OrderStatus:
    # Поиск последнего состояния для заказа
    db_orderstatus = db.query(OrderStatusModel).filter(
        OrderStatusModel.order_id == order_id).order_by(desc(OrderStatusModel.id)).first()

    return OrderStatus.model_validate(db_orderstatus)


def add_new_orderstatus_in_db(db: Session, new_orderstatus: OrderStatusAdd) -> OrderStatus:
    db_order_status = OrderStatusModel(**new_orderstatus.model_dump())
    db.add(db_order_status)
    db.commit()
    db.refresh(db_order_status)

    return OrderStatus.model_validate(db_order_status)


# Оплата заказа
def pay_order_in_db(db: Session, order_id: int, sum_to_pay: float) -> OrderStatus:
    pass