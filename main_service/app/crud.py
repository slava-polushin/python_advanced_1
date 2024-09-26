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
    CarStatusAdd,
    Client,
    Car,
    Driver,
    CarDriver,
    Order,
    OrderStatus,
    Client,
    Car,
    Driver,
    CarStatus,

    CoordinatesBase,
    PayInfo,
)
from app.schemas import orderStatuses
from app.schemas import carStatuses

from app.tasks.tasks import get_coordinates_via_str, get_price_via_coordinates

from app.rabbitmq_client import APP_QUEUE_MAP, rabbitmq_client

from app.config import DEBUG_MODE


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

    # Проверка состояния автомобиля (не сломан ли он), и естановка флага назначения водителя автомобилю
    # Поиск последнего состояния для заказа
    car_status = get_carstatus_in_db(db=db, car_id=cardriver.car_id)
    if car_status is None:
        car_status = CarStatusAdd(
            car_id=cardriver.car_id
        )
    elif car_status.status in (carStatuses["broken"]):
        raise HTTPException(
            status_code=404, detail=f"Car is in status {car_status.status} and can't be assigned to driver")
    else:
        car_status.status = carStatuses["free"]

    car_status = add_new_carstatus_in_db(db=db, new_carstatus=CarStatusAdd(**car_status.model_dump()))

    # Поиск последнего назначенного водителя для автомобиля
    db_cardriver = db.query(CarDriverModel).filter(
        CarDriverModel.car_id == cardriver.car_id).order_by(desc(CarDriverModel.id)).first()

    if db_cardriver is None:
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

def get_orderstatus_in_db(db: Session, order_id: int) -> OrderStatus:
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


def save_payinfo(order_id: int, sum_to_pay: float, db: Session) -> OrderStatus:
    order_status = get_orderstatus_in_db(db,order_id)
    new_orderstatus = OrderStatusAdd(**order_status.model_dump())
    new_orderstatus.unpaid_rest -= sum_to_pay
    if DEBUG_MODE:
        print(f"PAY APPROVED: order_id={order_id}, sum_to_pay={sum_to_pay}, new unpaid rest={new_orderstatus.unpaid_rest}")

    db_orderstatus = add_new_orderstatus_in_db(db, new_orderstatus=new_orderstatus) 
    return db_orderstatus


"""Блок интерфейсов обслуживающих оплату заказа"""


# Заявка на оплату заказа. Сообщение через rabbitMQ от main_service к pay_service
def pay_order_via_queue(pay_info: PayInfo, orderstatus: OrderStatus) -> PayInfo:
    message = {"order_status": orderstatus.model_dump(),
               "pay_sum": pay_info.pay_sum}

    routing_key = APP_QUEUE_MAP["pay_request_queue"]

    if routing_key:
        rabbitmq_client.publish(routing_key, message)

    print('### PAYING MESSAGE SENT!!!')

    return pay_info


def get_all_assigned_or_not_orders_in_db(
        db: Session,
        # Если задано то возвращаются все назначенные на автомобиль заявки,
        # иначе возвращаются все неназначенные заявки
        car_id: int | None
    ) -> list[Order]:
    subquery = db.query(OrderStatusModel).subquery()

    subquery = db.query(
        subquery,
        func.dense_rank().over(
            order_by=subquery.c.id.desc(),
            partition_by=subquery.c.order_id
        ).label('rnk')
    ).subquery()
    
    if car_id is None:
        subquery = db.query(subquery).filter(
            subquery.c.rnk == 1,
            subquery.c.status == orderStatuses["created"]
        ).subquery()
    else:
        subquery = db.query(subquery).filter(
            subquery.c.rnk == 1,
            subquery.c.car_id == car_id,
            subquery.c.status == orderStatuses["trip_started"]
        ).subquery()

    db_found_orders = db.query(OrderModel).join(subquery,OrderModel.order_id==subquery.c.order_id).all()

    return [Order.model_validate(order.__dict__) for order in db_found_orders]


# Процедуры для обработки таблицы car_status

def get_carstatus_in_db(db: Session, car_id: int) -> CarStatus | None:
    # Поиск последнего состояния для заказа
    db_carstatus = db.query(CarStatusModel).filter(
        CarStatusModel.car_id == car_id).order_by(desc(CarStatusModel.id)).first()

    if db_carstatus is None:
        return None
    
    return CarStatus.model_validate(db_carstatus)

# Запись нового состояния автомобиля в таблицу car_status
def add_new_carstatus_in_db(db: Session, new_carstatus: CarStatusAdd) -> CarStatus:
    db_car_status = CarStatusModel(**new_carstatus.model_dump())
    db.add(db_car_status)
    db.commit()
    db.refresh(db_car_status)

    return CarStatus.model_validate(db_car_status)

#Проверка, назначен ли на заказ этот же самый (car_id_include) или другой (car_id_exclude) автомобиль
def check_car_assigning_flag(
        db:Session, 
        order_id: int, 
        car_id_include: int = None, 
        car_id_exclude: int = None
    ) -> bool:    
    subquery = db.query(OrderStatusModel).subquery()

    subquery = db.query(
        subquery,
        func.dense_rank().over(
            order_by=(subquery.c.created_at.desc(),subquery.c.id.desc()),
            partition_by=subquery.c.order_id
        ).label('rnk')
    ).subquery()

    #Для повышения производительности созданы два разных подзапроса с ветвлением по if
    if car_id_include is not None and car_id_exclude is None:
        order_already_assigned_fl = db.query(subquery).filter(
            subquery.c.rnk == 1,
            subquery.c.order_id == order_id,
            subquery.c.car_id == car_id_include
        ).count()
    elif car_id_exclude is not None and car_id_include is None:
        order_already_assigned_fl = db.query(subquery).filter(
            subquery.c.rnk == 1,
            subquery.c.order_id == order_id,
            subquery.c.car_id != car_id_exclude
        ).count()
    else:
        raise HTTPException(
            status_code=404, detail="Procedure check_car_assigning_fl is called incorrectly: must be set only car_id_include or only car_id_exclude parameter")

    return bool(order_already_assigned_fl)


def assign_car_to_order_in_db(db:Session, order_id: int, car_id: int) -> CarStatus:
    # Поиск последнего состояния для заказа
    car_status = get_carstatus_in_db(db=db, car_id=car_id)

    # Назначение автомобиля на заказ
    if car_status is None:
        car_status = CarStatusAdd(
            car_id=car_id, 
            order_id=order_id
        )
    elif car_status.status in (carStatuses["broken"], carStatuses["driver_missing"]):
        raise HTTPException(
            status_code=404, detail=f"Car is in status {car_status.status} and can't be assigned to order")
    else:
        car_status.status = carStatuses["busy"]
        car_status.order_id = order_id

    car_status = add_new_carstatus_in_db(db=db, new_carstatus=CarStatusAdd(**car_status.model_dump()))
    return car_status


def change_proceeding_order_for_car_status_in_db(
        db:Session, 
        order_id: int, 
        car_id: int
    ) -> CarStatus:
    # Поиск последнего состояния для заказа
    car_status = get_carstatus_in_db(db=db, car_id=car_id)

    # Назначение автомобиля на заказ
    if car_status is None:
        raise HTTPException(
            status_code=404, detail="Car statuses not exists, and can't be cancelled")
    elif car_status.status not in (carStatuses["busy"]):
        raise HTTPException(
            status_code=404, detail=f"Car is in status {car_status.status} and can't be de-assigned (cancelled) for order {order_id}")
    else:
        car_status.status = carStatuses["free"]
        car_status.order_id = None

    car_status = add_new_carstatus_in_db(db=db, new_carstatus=CarStatusAdd(**car_status.model_dump()))
    return car_status
