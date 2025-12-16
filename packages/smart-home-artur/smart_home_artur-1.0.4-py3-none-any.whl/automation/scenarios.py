"""
Модуль, отвечающий за сценарии ( питоновская часть )
"""


from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy import select
from .actions import Action, TurnOnDeviceAction, SetLightParamsAction, SetTemperatureAction
from typing import List, Dict, Any
import time
import hashlib
from db.models import ScenarioORM
from db.session import get_db
from typing import Optional
from datetime import datetime


class ActionFactory:
    """
    Класс для создания и хранения действий
    Чтобы действия с одинаковыми параметрами были одним объектом.
    Сама фабрика - синглтон
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(self):
        self._action_cache: Dict[str, Action] = {}  # hash -> Action
    
    def __get_action_hash(self, action_type: str, device_id: str, params: Dict[str, Any]) -> str:
        """Создает уникальный хеш для действия"""
        param_str = str(sorted(params.items()))
        return hashlib.md5(f"{action_type}:{device_id}:{param_str}".encode()).hexdigest()
    
    def get_or_create_action(self, action_type: str, device_id: str, params: Dict[str, Any]) -> Action:
        """Создает или возвращает существующее действие"""
        action_hash = self.__get_action_hash(action_type, device_id, params)
        
        if action_hash in self._action_cache:
            print(f"Возвращаем кешированное действие: {action_type}")
            return self._action_cache[action_hash]
        
        # Создаем новое действие
        if action_type == "switch":
            action = TurnOnDeviceAction(device_id, params.get('mode'))
        elif action_type == "light":
            action = SetLightParamsAction(device_id, params.get('brightness'))
        elif action_type == "temperature":
            action = SetTemperatureAction(device_id, params.get('degree'))
        else:
            raise ValueError(f"неверное действие {action_type}")
        
        self._action_cache[action_hash] = action
        print(f"Создано новое действие: {action_type}")
        return action
    
    def clear_cache(self):
        """Очищает кеш (например при перезагрузке)"""
        self._action_cache.clear()


class Scenario:
    """
    Сценарии - класс, ответственный за связку триггера и последовательности триггера, 
    а также за последовательный запуск всех действий
    """
    def __init__(self, id: str, name: str):
        # айди и имя даны, фабрика синглтон, действий изначально нет
        self.id = id
        self.name = name
        self.action_factory = ActionFactory()
        self.actions: List[Action] = []
    
    def add_action(self, action_type: str, device_id: str, params: Dict[str, Any]) -> None:
        # добавляем действие по параметрам
        action = self.action_factory.get_or_create_action(action_type, device_id, params)
        self.actions.append(action)
    
    def execute(self, **kwargs) -> None:
        # исполняем сценарий = последовательно исполняем действия
        print(f"Выполняю сценарий {self.name}")
        for action in self.actions:
            try:
                action.execute(**kwargs)
                time.sleep(0.1)  # небольшая задержка между действиями
            except Exception as e:
                print(f"Ошибка от действия : {e}")


class ScenarioFactory:
    @staticmethod
    async def create_from_id(scenario_id: str, session: AsyncSession = Depends(get_db)) -> Optional[Scenario]:
        result = await session.execute(
            select(ScenarioORM).where(ScenarioORM.id == scenario_id)
        )
        orm_obj = result.scalar_one_or_none()
        
        if not orm_obj:
            return None
        
        return ScenarioFactory.create_from_orm(orm_obj)
    
    @staticmethod
    def create_from_orm(dev: ScenarioORM) -> Scenario:
        scenario_domain = Scenario(
            id = dev.id,
            name = dev.name,
        )
        for item in dev.actions:
            if item.get('action_type') == 'switch':
                scenario_domain.add_action(item.get('action_type'), item.get('device_id'), {'mode': item.get('mode')})
            elif item.get('action_type') == 'light':
                scenario_domain.add_action(item.get('action_type'), item.get('device_id'), {'brigtness': item.get('brightness')})
            elif item.get('action_type') == 'temperature':
                scenario_domain.add_action(item.get('action_type'), item.get('device_id'), {'degree': item.get('degree')})
        return scenario_domain

