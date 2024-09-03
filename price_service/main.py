from fastapi import FastAPI

from app.endpoints.price import router as price_router
from app.endpoints.health import router as health_router
from app.settings import settings

# settings = Settings()


app = FastAPI()

app.include_router(price_router, prefix="/price_api/v1")
app.include_router(health_router, prefix="/price_api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.app_port)
