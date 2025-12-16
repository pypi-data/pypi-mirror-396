import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from db.models import DeviceORM
from api.schemas import DeviceCreate

class TestDeviceFeatures:
    @pytest.mark.asyncio
    async def test_create_device_success(self, mock_db, sample_device_data):
        from services.device_service import DeviceService
        from db.repository import DeviceRepository
        
        mock_db.execute.return_value = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        
        device_data = DeviceCreate(**sample_device_data)
        
        repository = DeviceRepository(mock_db)
        service = DeviceService(repository)
        result = await service.add_device(device_data)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result.name == sample_device_data["name"]
        assert result.type == sample_device_data["type"]
    

    def test_create_device_error_type(self, mock_db, sample_wrong_device_data):
        mock_db.execute.return_value = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        with pytest.raises(ValueError) as exc_info:
            device_data = DeviceCreate(**sample_wrong_device_data)


    # def test_create_device_error_name(self, mock_db, sample_device_data):
    #     mock_db.execute.return_value = AsyncMock()
    #     mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
    #     with pytest.raises(ValueError) as exc_info:
    #         device_data = DeviceCreate(**sample_device_data)
    #         device_data_dub = DeviceCreate(**sample_device_data)

    def test_create_device_endpoint(self, client, mock_db, sample_device_data):
        mock_db.execute.return_value = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        print(f"\nDEBUG: Sending POST to /devices/create_device")
        print(f"DEBUG: Data: {sample_device_data}")
        
        response = client.post("/devices/create_device", json=sample_device_data)
        
        print(f"DEBUG: Status code: {response.status_code}")
        print(f"DEBUG: Headers: {dict(response.headers)}")
        print(f"DEBUG: Response text: {response.text[:200]}...")  # Первые 200 символов
        
        assert response.status_code == 200
        
        # Проверяем, что ответ не пустой
        assert response.text, "Response body is empty"
        
        try:
            data = response.json()
            print(f"DEBUG: Parsed JSON: {data}")
        except Exception as e:
            print(f"DEBUG: JSON parse error: {e}")
            raise
        
        assert data["name"] == sample_device_data["name"]
        assert "id" in data