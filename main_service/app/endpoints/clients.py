from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.crud import get_client, create_client_in_db
from app.schemas import Client, ClientCreate
from app.database import get_db

router = APIRouter()

@router.post("/clients/", response_model=Client)
def create_user(client: ClientCreate, db: Session = Depends(get_db)):
    return create_client_in_db(db=db, client=client)


@router.get("/clients/{client_id}", response_model=Client)
def read_user(client_id: int, db: Session = Depends(get_db)):
    db_client = get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client
