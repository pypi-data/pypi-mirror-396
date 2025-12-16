import pytest
from tests.test_performance_base import BasePerformanceTest
from unittest.mock import AsyncMock
import uuid
from datetime import datetime

class TestCreateScenarioPerformance(BasePerformanceTest):
    """Performance тест для создания сценария"""
    
    @property
    def endpoint(self) -> str:
        return "/scenarios/create_scenario"
    
    @property
    def method(self) -> str:
        return "POST"
    
    @property
    def payload(self) -> dict:
        return {
            'name': 'performance_scenario',
            'trigger': {
                'trigger_type': 'none'
            },
            'actions': [
                {
                    'action_type': 'switch',
                    'device_id': str(uuid.uuid4()),
                    'mode': 'on'
                }
            ]
        }
    
    @pytest.mark.benchmark(group="scenarios", min_time=0.1)
    def test_create_scenario_performance(self, client, mock_db, benchmark):
        """Тест производительности создания сценария"""
        mock_db.execute.return_value = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        result = self.run_performance_test(client, benchmark)



@pytest.mark.parametrize("trigger_type", ["none", "time_schedule", "temperature_change"])
def test_scenario_with_different_triggers(benchmark, client, mock_db, trigger_type):
    """Тест производительности с разными типами триггеров"""
    
    mock_db.execute.return_value = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    
    items = {'none': {'trigger_type': 'none'},
             'time_schedule': {'trigger_type': 'time_schedule', 'datetime_str': str(datetime.now().isoformat())},
             'temperature_change': {'trigger_type': 'temperature_change', 'temperature': 22}
    }

    scenario_data = {
        'name': f'scenario_{trigger_type}',
        'trigger': items.get(trigger_type),
        'actions': [
            {
                'action_type': 'switch',
                'device_id': str(uuid.uuid4()),
                'mode': 'on'
            }
        ]
    }
    
    def create_scenario():
        response = client.post("/scenarios/create_scenario", json=scenario_data)
        assert response.status_code == 200
        return response
    
    result = benchmark(create_scenario)
    benchmark.extra_info['trigger_type'] = trigger_type