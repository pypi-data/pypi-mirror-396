"""Базовый класс для парсеров."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseParser(ABC):
    """Базовый класс для всех парсеров с поддержкой fluent interface."""
    
    def __init__(self):
        """Инициализация парсера."""
        self._operations: List[dict] = []
        self._save_key: Optional[str] = None
    
    def save_to(self, key: str) -> "BaseParser":
        """Указывает ключ для сохранения результата в PARSED словарь."""
        self._save_key = key
        return self
    
    @abstractmethod
    def parse(self, data: Any) -> Any:
        """
        Выполняет парсинг данных.
        
        Args:
            data: Данные для парсинга
            
        Returns:
            Распарсенные данные
        """
        pass
    
    def _add_operation(self, operation_type: str, **kwargs) -> "BaseParser":
        """Добавляет операцию парсинга и возвращает self для fluent interface."""
        self._operations.append({"type": operation_type, **kwargs})
        return self

