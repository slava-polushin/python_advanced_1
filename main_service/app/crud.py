from sqlalchemy.orm import Session
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
    Client,
    Car,
#     ServiceCreate,
#     Service,
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
    db_user = ClientModel(
        client_name=client.client_name, 
        comment=client.comment,
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return Client.model_validate(db_user)



def get_car(db: Session, car_id: int):
    return db.query(CarModel).filter(CarModel.car_id == car_id).first()


def create_car_in_db(db: Session, car: CarCreate) -> Car:
    db_user = CarModel(
        model = car.model,
        color = car.color,
        production_date = car.production_date,
        vin_number = car.vin_number,
        reg_number = car.reg_number,
        comment = car.comment,
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return Car.model_validate(db_user)

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
