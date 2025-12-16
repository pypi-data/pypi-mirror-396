"""Позволяет сделать возможности репозитория более обширными
Запросы более сложные, разбиваются на несколько запросов к репозиторию"""

from db.repository import DeviceRepository
from db.models import DeviceORM
from sqlalchemy.ext.asyncio import AsyncSession
from api.schemas import DeviceCreate
import uuid

class DeviceService:
    def __init__(self, repository: DeviceRepository):
        self.repository = repository

    async def get_device(self, device_id: str) -> DeviceORM | None:
        """Вернуть девайс по айди"""
        return await self.repository.get_device_by_id(device_id)

    async def get_all_devices(self) -> list[DeviceORM]:
        """Вернуть все девайсы"""
        return await self.repository.get_all_devices()

    async def turn_on_device(self, device_id: str):
        """Включить девайс"""
        device = await self.repository.get_device_by_id(device_id)
        if device:
            device.is_on = True
            await self.repository.save_device(device)
    
    async def get_status(self, device_id: str):
        """Вернуть режим девайса по айди"""
        device = await self.repository.get_device_by_id(device_id)
        return device.state
    
    async def add_device(self, dev: DeviceCreate) -> DeviceORM:
        """Добавить девайс в БД"""
        device_id = str(uuid.uuid4())
        
        # Формируем info строку
        info_parts = []
        if dev.manufacturer:
            info_parts.append(dev.manufacturer)
        if dev.model:
            info_parts.append(dev.model)
        info_str = ' '.join(info_parts) if info_parts else "Unknown device"
        
        device = DeviceORM(
            id=device_id,
            name=dev.name,
            type=dev.type,
            room=dev.room,
            is_on='off',
            info=info_str,
            state={},
        )
        print(f"Saving to DB: {device}")
        result = await self.repository.save_device(device)
        print(f"Device saved: {result.id}")
        return result
