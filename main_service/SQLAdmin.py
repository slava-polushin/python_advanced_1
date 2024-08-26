""" Создание структуры администрирования данных посредством sqladmin
"""

from sqladmin import Admin, ModelView
from app.models import Clients, Cars, Drivers, CarDrivers, Orders, CarStatus, OrderStatus

from app.database import engine
from main import app


class ClientAdmin(ModelView, model=Clients):
    column_list = [Clients.client_id, Clients.client_name]
    name = "Client"
    name_plural = "Clients"


class CarAdmin(ModelView, model=Cars):
    column_list = [Cars.car_id, Cars.model,
                   Cars.color, Cars.reg_number, Cars.vin_number,
                   ]
    name = "Car"
    name_plural = "Cars"


class DriverAdmin(ModelView, model=Drivers):
    column_list = [Drivers.driver_id,
                   Drivers.driver_name, Drivers.driver_license,
                   ]
    name = "Driver"
    name_plural = "Drivers"


class CarDriversAdmin(ModelView, model=CarDrivers):
    column_list = [CarDrivers.id,
                   CarDrivers.car_id,  CarDrivers.car,  # (reg_number),
                   CarDrivers.driver_id,  CarDrivers.driver  # .driver_name,
                   ]
    name = "Car driver"
    name_plural = "Car drivers"


class OrdersAdmin(ModelView, model=Orders):
    column_list = [Orders.order_id, Orders.client_id, Orders.price
                   ]
    name = "Order"
    name_plural = "Orders"


class CarStatusAdmin(ModelView, model=CarStatus):
    column_list = [CarStatus.id, CarStatus.car_id,
                   CarStatus.order_id, CarStatus.status
                   ]
    name = "Car status"
    name_plural = "Car statuses"


class OrderStatusAdmin(ModelView, model=OrderStatus):
    column_list = [OrderStatus.id, OrderStatus.order_id, OrderStatus.car_id, OrderStatus.status, OrderStatus.unpaid_rest
                   ]
    name = "Order status"
    name_plural = "Order statuses"


adminClasses = (
    ClientAdmin,
    CarAdmin,
    DriverAdmin,
    CarDriversAdmin,
    OrdersAdmin,
    CarStatusAdmin,
    OrderStatusAdmin,
)


def register_sqlalchemy_admin():
    admin = Admin(app, engine)
    for adminClass in adminClasses:
        admin.add_view(adminClass)
