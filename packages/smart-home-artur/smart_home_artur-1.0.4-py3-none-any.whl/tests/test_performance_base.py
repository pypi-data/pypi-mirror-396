import pytest
from typing import Dict, Any, Callable, List
from abc import ABC, abstractmethod
from fastapi.testclient import TestClient
import statistics

class BasePerformanceTest(ABC):
    """Базовый класс для всех performance тестов"""
    
    @property
    @abstractmethod
    def endpoint(self) -> str:
        """URL эндпоинта"""
        pass
    
    @property
    @abstractmethod
    def method(self) -> str:
        """HTTP метод (GET, POST, PUT, DELETE)"""
        pass
    
    @property
    def headers(self) -> Dict[str, str]:
        """Заголовки запроса"""
        return {}
    
    @property
    def payload(self) -> Any:
        """Тело запроса (для POST/PUT)"""
        return None
    
    @property
    def params(self) -> Dict[str, Any]:
        """Query параметры (для GET)"""
        return {}
    
    @property
    def expected_status(self) -> int:
        """Ожидаемый статус код"""
        return 200
    
    def make_request(self, client: TestClient) -> Any:
        """Выполняет запрос с текущей конфигурацией"""
        if self.method.upper() == "GET":
            return client.get(
                self.endpoint, 
                params=self.params, 
                headers=self.headers
            )
        elif self.method.upper() == "POST":
            return client.post(
                self.endpoint, 
                json=self.payload, 
                headers=self.headers
            )
        else:
            raise ValueError(f"Unsupported method: {self.method}")
    
    def validate_response(self, response):
        """Валидация ответа (можно переопределить)"""
        assert response.status_code == self.expected_status
    
    def run_performance_test(self, client: TestClient, benchmark):
        """Основной метод для запуска performance теста"""
        def request_func():
            response = self.make_request(client)
            self.validate_response(response)
            return response
        
        result = benchmark(request_func)
                
        return result