"""
Модуль, отвечающий за действия, их различные типы
"""

from abc import ABC, abstractmethod
from typing import Dict
from db.models import DeviceORM
from sqlalchemy import select, update, and_
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db


class Action(ABC):
    """
    Базовый абстрактный класс для действия, обяз.метод Исполнить
    """
    @abstractmethod
    async def execute(self):
        """Выполнить действие."""
        pass

class TurnOnDeviceAction(Action):
    """
    Действие Изменить режим девайса
    """
    def __init__(self, device_id: str, mode: str):
        # mode - новый режим, device_id: айди девайса
        self.device_id = device_id
        self.mode = mode

    async def execute(self, db: AsyncSession = Depends(get_db)):
        # ищем по айди нужный девайс и обновляем режим
        stmt = update(DeviceORM).where(DeviceORM.id == self.device_id).values(is_on=self.mode)
        await db.execute(stmt)
        await db.commit()


class SetLightParamsAction(Action):
    """
    Действие изменить параметры света
    """
    def __init__(self, device_id: str, brightness: int):
        # айди девайса и яркость от 0 до 10
        self.device_id = device_id
        self.brightness = brightness
    
    async def execute(self, db: AsyncSession = Depends(get_db)):
        # найти объект по айди, убедиться что он светильник и обновить яркость
        stmt = update(DeviceORM).where(and_(DeviceORM.id == self.device_id, DeviceORM.type == 'light')).values(state={'brightness': self.brightness})
        await db.execute(stmt)
        await db.commit()

class SetTemperatureAction(Action):
    """
    Действие изменить температуру
    """
    def __init__(self, device_id: str, temperature: float):
        # ID девайса и температура
        self.device_id = device_id
        self.temp = temperature
    
    async def execute(self, db: AsyncSession = Depends(get_db)):
        # найти по айди термометр и обновить температуру
        stmt = update(DeviceORM).where(and_(DeviceORM.id == self.device_id, DeviceORM.type == 'thermometer')).values(state={'temperature': self.temp})
        await db.execute(stmt)
        await db.commit()
