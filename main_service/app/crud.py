from sqlalchemy.orm import Session
from sqlalchemy import desc
from sqlalchemy.sql import text

from fastapi.exceptions import HTTPException

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
    Client,
    Car,
    Driver,
    CarDriver,
    Order,
    Client,
    Car,
    Driver,
)
# from datetime import datetime

# incident_service_mapping = {
#     "Murder": [1],  # Assuming 1 is the ID for police service
#     "Gas Blow": [1, 2],  # Assuming 1 is police and 2 is ambulance
#     "Fire": [1, 3],  # Assuming 3 is the ID for fire brigade
#     "Theft": [1],  # Assuming 1 is police
#     "Medical Emergency": [2],  # Assuming 2 is ambulance
#     "Traffic Accident": [1, 2],  # Assuming 1 is police and 2 is ambulance
#     # Add more mappings as needed
# }


def get_client(db: Session, client_id: int):
    return db.query(ClientModel).filter(ClientModel.client_id == client_id).first()


def create_client_in_db(db: Session, client: ClientCreate) -> Client:
    db_client = ClientModel(
        client_name=client.client_name,
        comment=client.comment,
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return Client.model_validate(db_client)


def get_car(db: Session, car_id: int):
    return db.query(CarModel).filter(CarModel.car_id == car_id).first()


def create_car_in_db(db: Session, car: CarCreate) -> Car:
    db_car = CarModel(
        model=car.model,
        color=car.color,
        production_date=car.production_date,
        vin_number=car.vin_number,
        reg_number=car.reg_number,
        comment=car.comment,
    )
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return Car.model_validate(db_car)


def get_driver(db: Session, driver_id: int):
    return db.query(DriverModel).filter(DriverModel.driver_id == driver_id).first()


def create_driver_in_db(db: Session, driver: DriverCreate) -> Driver:
    db_driver = DriverModel(
        driver_name=driver.driver_name,
        driver_license=driver.driver_license,
        comment=driver.comment,
    )
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return Driver.model_validate(db_driver)


# Процедуры для обработки таблицы car_drivers
# TODO: Процедура не завершена, требует отладки. Сложена в виде чернового варианта
def create_cardriver_in_db(db: Session, cardriver: CarDriverAdd) -> CarDriver:

    stmt = text("""
select count(1)
  from (
select cd.car_id, 
       cd.driver_id, 
	   cd.fromdate,
	   cd.id,
	   last_value(cd.id) over(order by cd.created_at, cd.id) last_id 
  from car_drivers cd 
       ) x
 where id = last_id
   and ( (x.car_id = :car_id and x.driver_id != :driver_id) -- Машина уже назначена другому водителю
         or 
         (x.car_id != :car_id and x.driver_id = :driver_id) -- Водитель назначен другой машине
       )
        """)
    error_fl = db.execute(stmt, bind_arguments={
                          "car_id": cardriver.car_id,
                          "driver_id": cardriver.driver_id}
                          ).first()

    if error_fl > 0:
        raise HTTPException(
            status_code=404, detail="Driver is assigned to car. Please unassign first")

    # Поиск последнего назначенного водителя для автомобиля
    cardriver = db.query(CarDriverModel).filter(
        CarDriverModel.car_id == cardriver.car_id).order_by(desc(CarDriverModel.id)).first()

    # Поиск - назначен ли водитель на автомобиль
    cardriver = db.query(CarDriverModel).filter(
        CarDriverModel.driver_id == cardriver.driver_id).order_by(desc(CarDriverModel.id)).first()

# Процедуры для обработки таблицы orders


def create_order_in_db(db: Session, order: OrderCreate) -> Order:
    client = db.query(ClientModel).filter(
        ClientModel.client_id == order.client_id).first()

    db_order = OrderModel(
        client=client,
        start_address=order.start_address,
        finish_address=order.finish_address,
        baby_chair_fl=order.baby_chair_fl,
        comment=order.comment,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    db_order_status = OrderStatusModel(
        order=db_order,
        status=order.status,

        comment=order.status_comment
    )

    db.add(db_order_status)
    db.commit()
    db.refresh(db_order_status)

    return Order.model_validate(db_order)


def get_driver(db: Session, driver_id: int):
    return db.query(DriverModel).filter(DriverModel.driver_id == driver_id).first()


def create_driver_in_db(db: Session, driver: DriverCreate) -> Driver:
    db_user = DriverModel(
        driver_name=driver.driver_name,
        driver_license=driver.driver_license,
        comment=driver.comment,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return Driver.model_validate(db_user)


# def get_incident(db: Session, incident_id: int):
#     return db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()


# def create_incident_in_db(db: Session, incident: IncidentCreate) -> Incident:
#     db_incident = IncidentModel(**incident.model_dump())
#     db.add(db_incident)
#     db.commit()
#     db.refresh(db_incident)

#     # Automatically fill the incident_status table
#     service_ids = incident_service_mapping.get(db_incident.name, [])
#     for service_id in service_ids:
#         db_status = IncidentStatusModel(
#             incident_id=db_incident.id,
#             service_id=service_id,
#             status="required",
#             created_at=datetime.now(),
#         )
#         db.add(db_status)
#     db.commit()

#     return Incident.model_validate(db_incident)


# def create_service(db: Session, service: ServiceCreate) -> Service:
#     db_service = ServiceModel(**service.model_dump())
#     db.add(db_service)
#     db.commit()
#     db.refresh(db_service)
#     return Service.model_validate(db_service)


# def get_all_cars(db: Session) -> list[Car]:
#     cars = db.query(CarModel).all()
#     return [Car.model_validate(car) for car in cars]
