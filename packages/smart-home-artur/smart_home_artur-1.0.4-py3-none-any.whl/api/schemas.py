"""
Модуль, отвечающий за основные классы, используемые для эндпоинтов API.
Прием форм для создание через Create модели, возврат через Schema модели.
"""


from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, timedelta
from typing import List
from automation.triggers import TriggerType

# возможные типы действий
class ActionType(str, Enum):
    SWITCH = 'switch'
    LIGHT = 'light'
    TEMPERATURE = 'temperature'

# конфиг для создания действия Включение
class TurnOnActionConfig(BaseModel):
    action_type: ActionType = ActionType.SWITCH
    device_id: str = Field(...)
    mode: str = Field(...)


# конфиг для создания действия Установление света
class SetLightActionConfig(BaseModel):
    action_type: ActionType = ActionType.LIGHT
    device_id: str = Field(...)
    brightness: int = Field(..., ge=0, le=10)


# конфиг для создания действия Установление температуры
class SetTempActionConfig(BaseModel):
    action_type: ActionType = ActionType.TEMPERATURE
    device_id: str = Field(...)
    degree: float = Field(..., ge=18, le=28)


# возможные типы девайса
class DeviceType(str, Enum):
    LIGHT = "light"
    THERMOMETER = "thermometer"
    CAR = 'car'
    SOCKET = 'socket'
    VACUUM_CLEANER = 'vacuum'
    TEAPOT = 'teapot'


# возможные режимы девайса
class DeviceStatus(str, Enum):
    ON = "on"
    OFF = "off"
    ERROR = "error"


class DeviceSchema(BaseModel):
    """
    Модель для девайса для эндпоинта
    Из обязательных: ID, имя, тип, режим, время создания и последнего обновления
    Необязательные: локация, комната, модель, производитель
    """
    id: str
    name: str = Field(..., min_length=1, max_length=100)
    type: str
    status: str = Field(default=DeviceStatus.OFF)
    location: Optional[str] = Field(None, max_length=100)
    room: Optional[str] = Field(None, description="Комната расположения")
    manufacturer: Optional[str] = Field(None)
    model: Optional[str] = Field(None)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DeviceCreate(BaseModel):
    """
    Модель для создания девайса из эндпоинта
    Из обязательных: имя и тип
    Необязательные: локация, комната, производитель, модель
    """
    name: str = Field(..., min_length=1, max_length=100)
    type: str
    location: Optional[str] = Field(None, max_length=100)
    room: Optional[str] = Field(None, description="Комната расположения")
    manufacturer: Optional[str] = Field(None)
    model: Optional[str] = Field(None)


    # Проверка что тип из поддерживаемых
    @field_validator('type')
    def validate_type(cls, v: str) -> str:
        if v.upper() not in DeviceType.__members__:
            raise ValueError('Тип не поддерживается системой')
        return v


ActionConfig = Union[
    TurnOnActionConfig,
    SetLightActionConfig,
    SetTempActionConfig
]

# базовый тип для задания модели триггера
class BaseTriggerConfig(BaseModel):
    trigger_type: TriggerType

# тип для триггера, который активируется только по коллу
class NoneTriggerConfig(BaseTriggerConfig):
    trigger_type: TriggerType = TriggerType.NONE


# тип для триггера Временной
class TimeTriggerConfig(BaseTriggerConfig):
    trigger_type: TriggerType = TriggerType.TIME_SCHEDULE
    datetime_str: str
    
    @property
    def datetime(self) -> datetime:
        """Конвертируем строку в datetime при обращении"""
        return datetime.fromisoformat(self.datetime_str)


# тип для триггера Температурный
class TemperatureTriggerConfig(BaseTriggerConfig):
    trigger_type: TriggerType = TriggerType.TEMPERATURE_CHANGE
    temperature: float = 10


TriggerConfig = Union[
    NoneTriggerConfig,
    TimeTriggerConfig,
    TemperatureTriggerConfig
]

class ScenarioCreate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    """
    Модель для сохранения Сценария
    Обяз. сигнатура: имя, триггер, список действий
    """
    name: str = Field(..., min_length=1, max_length=100)
    trigger: TriggerConfig
    actions: List[ActionConfig] = Field(..., min_items=1, description="Список действий")


    # проверка Действий >=1
    @field_validator('actions')
    def validate_actions(cls, v):
        if not v:
            raise ValueError("Сценарий должен содержать хотя бы одно действие")
        return v

class ScenarioSchema(BaseModel):
    """
    Модель для хранения сценария
    """
    id: str
    name: str = Field(..., min_length=1, max_length=100)
    actions: List[ActionConfig] = Field(..., min_items=1, description="Список действий")
