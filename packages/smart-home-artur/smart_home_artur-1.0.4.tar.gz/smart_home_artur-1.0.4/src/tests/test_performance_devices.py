import pytest
from test_performance_base import BasePerformanceTest
from unittest.mock import AsyncMock

class TestCreateDevicePerformance(BasePerformanceTest):
    """Performance тест для создания устройства"""
    
    @property
    def endpoint(self) -> str:
        return "/devices/create_device"
    
    @property
    def method(self) -> str:
        return "POST"
    
    @property
    def payload(self) -> dict:
        return {
            'name': 'performance_sensor',
            'type': 'teapot',
        }
    
    @pytest.mark.benchmark(group="devices", min_time=0.1)
    def test_create_device_performance(self, client, mock_db, benchmark):
        """Тест производительности создания устройства"""
        # Настраиваем мок
        mock_db.execute.return_value = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        result = self.run_performance_test(client, benchmark)
        

class TestGetDeviceByIdPerformance(BasePerformanceTest):
    """Performance тест для получения устройства по ID"""
    
    def __init__(self):
        self._device_id = "test-id-123"
    
    @property
    def endpoint(self) -> str:
        return f"/devices/{self._device_id}"
    
    @property
    def method(self) -> str:
        return "GET"
    
    @pytest.mark.benchmark(group="devices", min_time=0.1)
    def test_get_device_by_id_performance(self, client, mock_db, benchmark):
        """Тест производительности получения устройства по ID"""
        # Настраиваем мок
        mock_execute_result = AsyncMock()
        mock_execute_result.scalar_one_or_none.return_value = AsyncMock(
            id=self._device_id,
            name='Test Device',
            type='teapot'
        )
        mock_db.execute.return_value = mock_execute_result
        
        result = self.run_performance_test(client, benchmark)


@pytest.mark.benchmark(group="devices-stress", min_time=0.5)
def test_concurrent_device_creation(benchmark, client, mock_db):
    """Тест производительности при конкурентных запросах"""
    mock_db.execute.return_value = AsyncMock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    
    def create_multiple_devices():
        responses = []
        device_data = [
            {'name': f'device_{i}', 'type': 'teapot'}
            for i in range(5)
        ]
        
        for data in device_data:
            response = client.post("/devices/create_device", json=data)
            responses.append(response)
            assert response.status_code == 200
        
        return responses
    
    result = benchmark(create_multiple_devices)
