"""Модуль моделей для ORM SQLAlchemy"""

from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class DeviceORM(Base):
    """
    ORM модель девайса
    Обязательные поля: айди, имя, тип, режим, инфо
    Необязательные: комната, локация, режим, создано и обновлено
    """
    __tablename__ = "devices"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'light', 'sensor', etc.
    location = Column(String, default='unknown')
    room = Column(String, default='unknown')
    is_on = Column(String, default='off')
    info = Column(String, default='')
    state = Column(JSON, default={})  # Для специфичных атрибутов (brightness, motion)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now())

class ScenarioORM(Base):
    """
    ORM модель сценария
    Обязательные поля: айди, имя, тип триггера, настройки триггера, действия
    Необязательные: режим активности
    """
    __tablename__ = "scenarios"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    trigger_type = Column(String, nullable=False)  # 'event', 'time'
    trigger_config = Column(JSON, nullable=False)  # {'event_name': 'motion_detected'}
    actions = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)