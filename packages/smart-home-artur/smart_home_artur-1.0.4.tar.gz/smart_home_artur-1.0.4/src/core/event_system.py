"""
Модуль для правильного прикрепления триггеров к сценариям и наоборот
Также создание и обработка триггеров
"""


from typing import Dict, List, Any, Type
from automation.scenarios import Scenario
from automation.triggers import Trigger, TriggerType, TimeTrigger, TemperatureTrigger, NoneTrigger
from automation.actions import Action
import hashlib


class TriggerRegistry:
    """Реестр для хранения и поиска существующих триггеров"""

    # возможные классы триггера, чтобы по ключу типа вызвать правильный конструктор
    TRIGGER_CLASSES = {
        'time_schedule': TimeTrigger,
        'temperature_change': TemperatureTrigger,
        'none': NoneTrigger,
    }

    def __init__(self):
        self._triggers: Dict[str, Trigger] = {}  # hash -> trigger
        self._type_registry: Dict[TriggerType, Dict[str, Trigger]] = {}
    
    def __get_trigger_hash(self, trigger_type: TriggerType, params: Dict[str, Any]) -> str:
        """Создает уникальный хеш для триггера по типу и параметрам"""
        param_str = str(sorted(params.items()))
        hash_input = f"{trigger_type.value}:{param_str}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def get_or_create_trigger(self, trigger_type: TriggerType, params: Dict[str, Any]) -> Trigger:
        """Находит существующий триггер или создает новый"""
        trigger_hash = self.__get_trigger_hash(trigger_type, params)
        
        if trigger_hash in self._triggers:
            print(f"Найден существующий триггер: {trigger_type.value} с params {params}")
            return self._triggers[trigger_hash]
        try:
            trigger_class = TriggerRegistry.TRIGGER_CLASSES.get(trigger_type.name.lower())
            new_trigger = trigger_class(trigger_hash, params)
            self._triggers[trigger_hash] = new_trigger
            
            if trigger_type not in self._type_registry:
                self._type_registry[trigger_type] = {}
            self._type_registry[trigger_type][trigger_hash] = new_trigger
            
            print(f"Создан новый триггер: {trigger_type.value} с params {params}")
            return new_trigger
        except TypeError as e:
            print('Ошибка создания триггера', e)
    

    def find_triggers_by_type_and_params(self, trigger_type: TriggerType, **filters) -> List[Trigger]:
        """Ищет триггеры по типу и параметрам"""
        result = []
        if trigger_type in self._type_registry:
            for trigger in self._type_registry[trigger_type].values():
                if self.__trigger_matches_filters(trigger, filters):
                    result.append(trigger)
        return result
    
    def __trigger_matches_filters(self, trigger: Trigger, filters: Dict[str, Any]) -> bool:
        """Проверяет соответствует ли триггер фильтрам"""
        for key, value in filters.items():
            if getattr(trigger, key, None) != value:
                return False
        return True


class TriggerObserver:
    """Обзевер - хранит все связи триггеров и сценариев ( а также действий )"""
    def __init__(self):
        self.scenarios: Dict[Trigger, List[Scenario]] = {}
        self.actions: Dict[Trigger, List[Action]] = {}
        self.registry = TriggerRegistry()
    
    def subscribe_scenario(self, trigger_type: TriggerType, params: Dict[str, Any], scenario: Scenario) -> None:
        """Получить триггер по параметрам и подписать с сценарием"""
        trigger = self.registry.get_or_create_trigger(trigger_type, params)
        if trigger not in self.scenarios:
            self.scenarios[trigger] = []
            trigger.attach(self)
        self.scenarios[trigger].append(scenario)
    
    def subscribe_action(self, trigger_type: TriggerType, params: Dict[str, Any], action: Action) -> None:
        """Получить триггер по параметрам и подписать с действием"""
        trigger = self.registry.get_or_create_trigger(trigger_type, params)
        if trigger not in self.actions:
            self.actions[trigger] = []
            trigger.attach(self)
        self.actions[trigger].append(action)
    
    def update(self, trigger: Trigger, **kwargs) -> None:
        """
        Метод, вызываемый при активации триггера
        """
        print(f"\nАктивируем триггер ({trigger.trigger_type.value})")
        
        if trigger in self.actions:
            for action in self.actions[trigger]:
                try:
                    action.execute(**kwargs)
                except Exception as e:
                    print(f"Ошибка выполнения : {e}")
        
        if trigger in self.scenarios:
            for scenario in self.scenarios[trigger]:
                scenario.execute(**kwargs)