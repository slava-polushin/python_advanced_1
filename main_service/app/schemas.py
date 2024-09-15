### Описание моделей данных для организации доступа по HTTP ###

from pydantic import BaseModel, ConfigDict
from datetime import datetime, date

from app.models import orderStatuses

# Схема таблицы 'clients'


class ClientBase(BaseModel):
    client_name: str
    comment: str | None = None


class ClientCreate(ClientBase):
    pass


class Client(ClientBase):
    client_id: int
    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Схема таблицы 'cars'


class CarBase(BaseModel):
    model: str
    color: str
    production_date: date
    vin_number: str
    reg_number: str
    comment: str | None = None


class CarCreate(CarBase):
    pass


class Car(CarBase):
    car_id: int
    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Схема таблицы 'drivers'


class DriverBase(BaseModel):
    driver_name: str
    driver_license: str
    comment: str | None = None


class DriverCreate(DriverBase):
    pass


class Driver(DriverBase):
    driver_id: int
    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Схема таблицы 'car_drivers'
class CarDriverBase(BaseModel):
    car_id: int
    driver_id: int
    fromdate: date
    comment: str | None = None


class CarDriverAdd(CarDriverBase):
    pass


class CarDriver(CarDriverBase):
    id: int
    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Схемы таблиц 'orders', 'order_status'


class OrderBase(BaseModel):
    # client: Client
    client_id: int
    start_address: str
    finish_address: str
    baby_chair_fl: bool = False
    status: str = orderStatuses['created']
    comment: str | None = None


class OrderCreate(OrderBase):
    status_comment: str | None = None


class Order(OrderBase):
    order_id: int
    # client: Client 
    start_latitude: float
    start_longitude: float
    finish_latitude: float
    finish_longitude: float
    price: float

    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderStatusBase(BaseModel):
    order_id: int
    status: str
    car_id: int | None = None
    comment: str | None = None
    start_at: datetime | None = None
    finish_at: datetime | None = None
    unpaid_rest: float
    created_at: datetime


class OrderStatusAdd(OrderStatusBase):
    pass

class OrderStatus(OrderStatusBase):
    id: int
    car: Car | None = None
    order: Order

    model_config = ConfigDict(from_attributes=True)


# Схема таблицы 'car_status'
class CarStatusBase(BaseModel):
    car_id: int
    #Статус автомобиля, может быть равен: {free, busy, broken, driver_missing}
    status: str = "free"
    current_latitude: float | None = None
    current_longitude: float | None = None
    order_id: int | None = None
    comment: str | None = None

class CarStatusAdd(CarStatusBase):
    pass


class CarStatus(CarStatusBase):
    id: int
    created_at: datetime | None = None
    car: Car
    order: Order | None = None

    model_config = ConfigDict(from_attributes=True)


# Схема для обмена данными с coordinates_service
class CoordinatesBase(BaseModel):
    start_latitude: float
    start_longitude: float
    finish_latitude: float
    finish_longitude: float

# Схема для получения информации о платеже клиента
class PayInfo(BaseModel):
    order_id: int
    pay_sum: float
