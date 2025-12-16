"""Позволяет сделать возможности репозитория более обширными
Запросы более сложные, разбиваются на несколько запросов к репозиторию"""


from db.repository import ScenarioRepository
from db.models import ScenarioORM
from api.schemas import ScenarioCreate
import uuid
from core.hub import Hub
from automation.scenarios import Scenario, ScenarioFactory
from automation.triggers import TriggerType


class ScenarioService:
    def __init__(self, repository: ScenarioRepository):
        self.repository = repository
        self.hub = Hub()

    async def get_scenario(self, scenario_id: str) -> ScenarioORM | None:
        """Вернуть сценарий по айди"""
        return await self.repository.get_scenario_by_id(scenario_id)

    async def get_all_scenarios(self) -> list[ScenarioORM]:
        """Вернуть все сценарии"""
        return await self.repository.get_all_scenarios()

    async def turn_on_scenario(self, scenario_id: str):
        """Запустить сценарий по айди"""
        scenario = await ScenarioFactory.create_from_id(scenario_id)
        self.repository.change_scenario_mode(scenario_id)
        scenario.execute()
        self.repository.change_scenario_mode(scenario_id)

    
    async def get_status(self, scenario_id: str):
        """Получить статус выполнения сценария"""
        device = await self.repository.get_scenario_by_id(scenario_id)
        return device.is_active
    
    async def add_scenario(self, dev: ScenarioCreate) -> ScenarioORM:
        """Добавить сценарий в БД"""

        scenario_id = str(uuid.uuid4())
        
        items = []
        for item in dev.actions:
            
            if item.action_type == 'switch':
                items.append({'action_type': 'switch', 'device_id': item.device_id, 'mode': item.mode})
            elif item.action_type == 'light':
                items.append({'action_type': 'light', 'device_id': item.device_id, 'brightness': item.brightness})
            elif item.action_type == 'temperature':
                items.append({'action_type': 'temperature', 'device_id': item.device_id, 'degree': item.degree})

        params = {}
        if dev.trigger.trigger_type == TriggerType.TIME_SCHEDULE:
            params = {'time': dev.trigger.datetime}
        elif dev.trigger.trigger_type == TriggerType.TEMPERATURE_CHANGE:
            params = {'temperature': dev.trigger.temperature}


        scenario = ScenarioORM(
            id = scenario_id,
            name = dev.name,
            trigger_type = dev.trigger.trigger_type.value.lower(),
            trigger_config = params,
            actions = items,
            is_active = False,
        )
        scenario_domain = ScenarioFactory.create_from_orm(scenario)
        self.hub.trigger_observer.subscribe_scenario(dev.trigger.trigger_type, params, scenario_domain)

        print(f"Saving to DB: {scenario}")
        result = await self.repository.save_scenario(scenario)
        print(f"Device saved: {result.id}")
        return result