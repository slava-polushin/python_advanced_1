### Описание моделей данных для организации доступа по HTTP ###

from pydantic import BaseModel, ConfigDict
from datetime import datetime, date

# from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, ForeignKeyConstraint, Index, Numeric, PrimaryKeyConstraint, String, Text

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

