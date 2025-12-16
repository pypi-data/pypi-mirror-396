'''
Модуль для эндпоинтов запросов, связанных со сценариями
'''


from typing import Dict
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from services.scenario_service import ScenarioService
from db.repository import ScenarioRepository
from api.schemas import ScenarioCreate, ScenarioSchema

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get("/test")
async def test_route():
    """
    Тестовый эндпоинт
    """
    return {"message": "Scenarios router is working!"}


@router.get("/", response_model=list[ScenarioSchema])
async def get_scenarios(db: AsyncSession = Depends(get_db)):
    """
    Вывести все существующие сценарии
    """
    repository = ScenarioRepository(db)
    service = ScenarioService(repository)
    result = await service.get_all_scenarios()
    print(f"Found {len(result)} scenarios")
    return result


@router.post("/create_scenario")
async def add_scenario(dev: ScenarioCreate, db: AsyncSession = Depends(get_db)):
    """
    Добавить сценарий
    """
    repository = ScenarioRepository(db)
    service = ScenarioService(repository)
    result = await service.add_scenario(dev)
    return result


@router.post('/execute_scenario')
async def execute_scenario(raw_json: Dict = Body(...), db: AsyncSession = Depends(get_db)):
    """
    Включить, исполнить (пока не до конца реализовано)
    """
    scenario_id = raw_json.get('id')
    repository = ScenarioRepository(db)
    service = ScenarioService(repository)
    service.turn_on_scenario(scenario_id)
    print('Executing scenario successfully')
    