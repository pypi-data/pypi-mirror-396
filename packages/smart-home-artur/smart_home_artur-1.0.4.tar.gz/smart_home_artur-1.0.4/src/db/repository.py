"""
Модель для репозиториев - позволяет легко делает сложные запросы к БД через методы и AsyncSession
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from .models import DeviceORM, ScenarioORM


class DeviceRepository:
    """Все инструменты для обращения к таблице с девайсами"""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_device_by_id(self, device_id: str) -> DeviceORM | None:
        """Обратиться по айди к девайсу"""
        result = await self.session.execute(
            select(DeviceORM).where(DeviceORM.id == device_id)
        )
        return result.scalar_one_or_none()

    async def get_all_devices(self) -> list[DeviceORM]:
        """Вернуть все девайсы"""
        result = await self.session.execute(select(DeviceORM))
        return result.scalars().all()

    async def save_device(self, dev: DeviceORM) -> DeviceORM:
        """Сохранить девайс"""
        self.session.add(dev)
        await self.session.commit()
        await self.session.refresh(dev)
        return dev
    

class ScenarioRepository:
    """Все инструменты для обращения к таблице с сценариями"""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_scenario_by_id(self, scenario_id: str) -> ScenarioORM | None:
        """обратиться к сценарию по айди"""
        result = await self.session.execute(
            select(ScenarioORM).where(ScenarioORM.id == scenario_id)
        )
        return result.scalar_one_or_none()

    async def change_scenario_mode(self, scenario_id: str) -> None:
        scenario = self.session.query(ScenarioORM).filter_by(id=scenario_id).first()
        scenario.is_active = not scenario.is_active
        self.session.commit()

    async def get_all_scenarios(self) -> list[ScenarioORM]:
        """вернуть все сценарии"""
        result = await self.session.execute(select(ScenarioORM))
        return result.scalars().all()

    async def save_scenario(self, dev: ScenarioORM) -> ScenarioORM:
        """Сохранить сценарий"""
        self.session.add(dev)
        await self.session.commit()
        await self.session.refresh(dev)
        return dev