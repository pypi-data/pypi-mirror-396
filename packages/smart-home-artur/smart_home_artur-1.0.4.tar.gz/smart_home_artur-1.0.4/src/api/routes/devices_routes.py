'''
Модуль предоставляет эндпоинты для работы с девайсами для умного дома
'''


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from services.device_service import DeviceService
from db.repository import DeviceRepository
from api.schemas import DeviceCreate, DeviceSchema
from db.models import DeviceORM

router = APIRouter(prefix="/devices", tags=["devices"])

@router.get("/", response_model=list[DeviceSchema])
async def get_devices(db: AsyncSession = Depends(get_db)):
    '''Вернуть все девайсы'''
    repository = DeviceRepository(db)
    service = DeviceService(repository)
    devices = await service.get_all_devices()
    return devices

@router.post("/create_device")
async def add_device(dev: DeviceCreate, db: AsyncSession = Depends(get_db)):
    '''
    Создать новый девайс и добавить в БД
    '''
    repository = DeviceRepository(db)
    service = DeviceService(repository)
    result = await service.add_device(dev)
    return result



@router.get('/{device_id}/status')
async def get_status(device_id: str, db: AsyncSession = Depends(get_db)):
    '''
    Узнать статус определенного девайса
    '''
    repository = DeviceRepository(db)
    service = DeviceService(repository)
    status = await service.get_status(device_id)
    return status

@router.post("/{device_id}/turn_on")
async def turn_on_device(device_id: str, db: AsyncSession = Depends(get_db)):
    '''Включить девайс по ID'''
    repository = DeviceRepository(db)
    service = DeviceService(repository)
    await service.turn_on_device(device_id)
    return {"status": "ok", "message": f"Device {device_id} turned on"}