from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.endpoints.clients import router as clients_router
from app.endpoints.cars import router as cars_router
from app.endpoints.drivers import router as drivers_router
from app.endpoints.car_drivers import router as cardrivers_router

from app.endpoints.orders import router as orders_router

from app.endpoints.health import router as health_router

from app.config import DEBUG_MODE
from app.config import MAINSERVICE_APP_PORT, COORDINATES_REDIS_URL, PRICE_REDIS_URL
from app.redis_client import redis_client_coordinates
from app.redis_client import redis_client_price
from app.rabbitmq_client import rabbitmq_client



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    redis_client_coordinates.connect(urlStr=COORDINATES_REDIS_URL)
    redis_client_price.connect(urlStr=PRICE_REDIS_URL)
    rabbitmq_client.connect()
    yield
    # Shutdown event
    redis_client_coordinates.close()
    redis_client_price.close()
    rabbitmq_client.close()


app = FastAPI(lifespan=lifespan, debug=DEBUG_MODE)

app.include_router(clients_router, prefix="/mainservice_api/v1")
app.include_router(cars_router, prefix="/mainservice_api/v1")
app.include_router(drivers_router, prefix="/mainservice_api/v1")
app.include_router(cardrivers_router, prefix="/mainservice_api/v1")
app.include_router(orders_router, prefix="/mainservice_api/v1")

app.include_router(health_router, prefix="/mainservice_api/v1")

if DEBUG_MODE:
    from SQLAdmin import register_sqlalchemy_admin
    register_sqlalchemy_admin()


@app.get("/", response_class=FileResponse)
async def root():
    return 'README.md'

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=MAINSERVICE_APP_PORT)
