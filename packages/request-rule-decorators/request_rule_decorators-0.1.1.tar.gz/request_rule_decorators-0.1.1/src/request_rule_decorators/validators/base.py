"""Базовый класс для валидаторов."""

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from ..dto import ValidationError


class BaseValidator(ABC):
    """Базовый класс для всех валидаторов с поддержкой fluent interface."""
    
    def __init__(self, error_key: Optional[str] = None):
        """
        Инициализация валидатора.
        
        Args:
            error_key: Ключ ошибки для идентификации конкретного правила
        """
        self._rules: List[dict] = []
        self._rule_name: str = self.__class__.__name__
        self._error_key: Optional[str] = error_key
    
    def error_key(self, key: str) -> "BaseValidator":
        """
        Устанавливает ключ ошибки для этого валидатора.
        
        Args:
            key: Ключ ошибки
            
        Returns:
            self для fluent interface
        """
        self._error_key = key
        return self
    
    def _add_rule(self, rule_type: str, **kwargs) -> "BaseValidator":
        """Добавляет правило валидации и возвращает self для fluent interface."""
        self._rules.append({"type": rule_type, **kwargs})
        return self
    
    @abstractmethod
    def validate(self, data: Any) -> tuple[bool, Optional[ValidationError]]:
        """
        Выполняет валидацию данных.
        
        Args:
            data: Данные для валидации
            
        Returns:
            Tuple[bool, Optional[ValidationError]]: (успешность валидации, ошибка если есть)
        """
        pass
    
    def _create_error(
        self,
        rule_type: str,
        expected_values: List[Any],
        received_values: List[Any],
        attempts: int = 0,
        max_attempts: int = 0,
        message: Optional[str] = None,
    ) -> ValidationError:
        """Создает объект ValidationError."""
        return ValidationError(
            rule_name=f"{self._rule_name}.{rule_type}",
            error_key=self._error_key,
            expected_values=expected_values,
            received_values=received_values,
            attempts=attempts,
            max_attempts=max_attempts,
            message=message,
        )

