"""
Запуск API, подключение всех эндпоинтов
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.session import async_engine
from db.models import Base
from api.routes import devices_routes, scenarios_routes
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()

app = FastAPI(title="Smart Home Hub API", lifespan=lifespan)

app.include_router(devices_routes.router)
app.include_router(scenarios_routes.router)

@app.get("/")
async def root():
    return {"message": "Smart Home Hub API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)