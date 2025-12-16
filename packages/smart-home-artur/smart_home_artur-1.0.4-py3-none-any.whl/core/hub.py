"""Модуль Хаб синглтон для хранения информации, общей и используемой по всему проекту"""

from .event_system import TriggerObserver
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import DeviceORM

class Hub:
    '''
    Hub - Singleton
    '''
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance


    def __init__(self):
        if not self._initialized:
            self.trigger_observer = TriggerObserver()
            self.db_session: AsyncSession = None
            self._initialized = True
