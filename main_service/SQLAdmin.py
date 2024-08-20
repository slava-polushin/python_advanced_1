from sqladmin import Admin, ModelView
from app.models import Clients, Cars

from app.database import engine
from main import app


class ClientAdmin(ModelView, model=Clients):
    column_list = [Clients.client_id, Clients.client_name]
    name = "Client"
    name_plural = "Clients"

class CarAdmin(ModelView, model=Cars):
    column_list = [Cars.car_id, Cars.model, Cars.color, Cars.reg_number, Cars.vin_number]
    name = "Car"
    name_plural = "Cars"


def register_sqlalchemy_admin():
    admin = Admin(app, engine)
    admin.add_view(ClientAdmin)
    admin.add_view(CarAdmin)