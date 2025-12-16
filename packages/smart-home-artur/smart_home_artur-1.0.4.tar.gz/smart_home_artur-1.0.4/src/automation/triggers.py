"""
Модуль для триггеров, полный контроль какой когда запускается
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List


# возможные виды триггера
class TriggerType(Enum):
    TEMPERATURE_CHANGE = "temperature_change"
    TIME_SCHEDULE = "time_schedule"
    NONE = 'none'


class Trigger(ABC):
    """
    Класс триггера, подключается к обзерверу
    """
    def __init__(self, trigger_hash: str, trigger_type: TriggerType):
        self.trigger_hash: str = trigger_hash
        self.trigger_type: TriggerType = trigger_type
        self._observers: List[Any] = []
    
    def attach(self, observer: Any) -> None:
        self._observers.append(observer)
    
    def detach(self, observer: Any) -> None:
        self._observers.remove(observer)
    
    def notify(self, **kwargs) -> None:
        for observer in self._observers:
            observer.update(self, **kwargs)

class TimeTrigger(Trigger):
    '''
    Триггер для времени
    '''
    def __init__(self, trigger_hash: str, params: Dict[str, Any]):
        super().__init__(trigger_hash, TriggerType.TIME_SCHEDULE)
        self.time = params.get('time')

    
class TemperatureTrigger(Trigger):
    """
    Триггер для температуры
    """
    def __init__(self, trigger_hash: str, params: Dict[str, Any]):
        super().__init__(trigger_hash, TriggerType.TEMPERATURE_CHANGE)
        self.temperature = params.get('temperature')


class NoneTrigger(Trigger):
    """
    Триггер пустышка, только по коллу
    """
    def __init__(self, trigger_hash: str, params: Dict[str, Any]):
        super().__init__(trigger_hash, TriggerType.TIME_SCHEDULE)
