### Описание моделей данных для организации доступа по HTTP ###

from pydantic import BaseModel, ConfigDict
from datetime import datetime, date

# Схема таблицы 'clients'
class ClientBase(BaseModel):
    client_name: str
    comment: str

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
    comment: str

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
    comment: str

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
    comment: str = ""

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
    status: str = "created"
    comment: str = ""

class OrderCreate(OrderBase):
    status_comment: str
    # status:str = 'created'

class Order(OrderBase):
    order_id: int
    client: Client
    start_latitude: float
    start_longitude: float
    finish_latitude: float
    finish_longitude: float
    price: float

    created_at: datetime
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Схема для обмена данными с coordinates_service
class CoordinatesBase(BaseModel):
    start_latitude: float
    start_longitude: float
    finish_latitude: float
    finish_longitude: float