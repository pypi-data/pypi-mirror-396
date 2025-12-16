import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from db.models import ScenarioORM
from api.schemas import ScenarioCreate

class TestDeviceFeatures:
    @pytest.mark.asyncio
    async def test_create_scenario_success(self, mock_db, sample_scenario_data):
        from services.scenario_service import ScenarioService
        from db.repository import ScenarioRepository
        
        mock_db.execute.return_value = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        
        device_data = ScenarioCreate(**sample_scenario_data)
        
        repository = ScenarioRepository(mock_db)
        service = ScenarioService(repository)
        result = await service.add_scenario(device_data)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result.name == sample_scenario_data["name"]
        assert result.trigger_type == sample_scenario_data["trigger"]['trigger_type']

    def test_create_scenario_error(self, mock_db, sample_scenario_data):
        mock_db.execute.return_value = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        with pytest.raises(ValueError) as exc_info:
            sample_wrong_scenario_data = sample_scenario_data
            sample_wrong_scenario_data['trigger']['trigger_type'] = 'skibibi'
            device_data = ScenarioCreate(**sample_wrong_scenario_data)
    
    # def test_create_scenarios_name_error(self, mock_db, sample_scenario_data):
    #     mock_db.execute.return_value = AsyncMock()
    #     mock_db.execute.return_value.scalar_one_or_none.return_value = None
    #     with pytest.raises(ValueError) as exc_info:
    #         device_data = ScenarioCreate(**sample_scenario_data)
    #         device_data_dub = ScenarioCreate(**sample_scenario_data)
    
    def test_create_scenarios_no_actions_error(self, mock_db, sample_scenario_data):
        mock_db.execute.return_value = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        with pytest.raises(ValueError) as exc_info:
            sample_wrong_scenario_data = sample_scenario_data
            sample_wrong_scenario_data['actions'] = []
            device_data = ScenarioCreate(**sample_wrong_scenario_data)
    
    def test_create_scenarios_wrong_trigger(self, mock_db, sample_scenario_data):
        mock_db.execute.return_value = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        with pytest.raises(ValueError) as exc_info:
            sample_wrong_scenario_data = sample_scenario_data
            sample_wrong_scenario_data['trigger']['trigger_type'] = 'skibibi'
            device_data = ScenarioCreate(**sample_wrong_scenario_data)

    def test_create_scenario_endpoint(self, client, mock_db, sample_scenario_data):
        mock_db.execute.return_value = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        response = client.post("/scenarios/create_scenario", json=sample_scenario_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_scenario_data["name"]
        assert "id" in data