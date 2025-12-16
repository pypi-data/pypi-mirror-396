"""DTO классы для валидации и парсинга ответов."""

from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


@dataclass
class ValidationError:
    """Ошибка валидации правила."""
    
    rule_name: str
    error_key: Optional[str] = None
    expected_values: List[Any] = field(default_factory=list)
    received_values: List[Any] = field(default_factory=list)
    attempts: int = 0
    max_attempts: int = 0
    message: str = ""
    
    def __post_init__(self):
        """Генерирует сообщение об ошибке, если оно не задано."""
        if not self.message:
            self.message = self._generate_message()
    
    def _generate_message(self) -> str:
        """Генерирует сообщение об ошибке из компонентов."""
        parts = [
            f"Rule: {self.rule_name}",
            f"Expected: {self.expected_values}",
            f"Received: {self.received_values}",
        ]
        if self.max_attempts > 0:
            parts.append(f"Attempts: {self.attempts}/{self.max_attempts}")
        return " | ".join(parts)


@dataclass
class ValidationData:
    """Данные валидации, прикрепленные к ответу во время выполнения."""
    
    ACTION: Optional[str] = None
    ERRORS: List[ValidationError] = field(default_factory=list)
    PARSED: Dict[str, Any] = field(default_factory=dict)
    ATTEMPTS: int = 0


@dataclass
class WithValid(Generic[T]):
    """Обертка над оригинальным ответом с данными валидации."""
    
    response: T
    valid: ValidationData = field(default_factory=ValidationData)
    
    def is_valid(self) -> bool:
        """
        Проверяет, есть ли ошибки валидации.
        
        Returns:
            True если нет ошибок, False если есть хотя бы одна ошибка
        """
        return len(self.valid.ERRORS) == 0
    
    def has_error(self, error_key: str) -> bool:
        """
        Проверяет наличие конкретной ошибки по ERROR_KEY.
        
        Args:
            error_key: Ключ ошибки для проверки
            
        Returns:
            True если ошибка с таким ключом найдена, False иначе
        """
        return any(error.error_key == error_key for error in self.valid.ERRORS)
    
    def __repr__(self) -> str:
        """Возвращает строковое представление объекта со всеми ошибками."""
        lines = [
            f"WithValid(response={type(self.response).__name__}, "
            f"is_valid={self.is_valid()}, "
            f"errors_count={len(self.valid.ERRORS)})"
        ]
        
        if self.valid.ERRORS:
            lines.append("\nОшибки валидации:")
            for i, error in enumerate(self.valid.ERRORS, 1):
                error_info = [f"  {i}. {error.rule_name}"]
                if error.error_key:
                    error_info.append(f"     ERROR_KEY: {error.error_key}")
                if error.expected_values:
                    error_info.append(f"     Ожидаемые: {error.expected_values}")
                if error.received_values:
                    error_info.append(f"     Полученные: {error.received_values}")
                if error.message:
                    error_info.append(f"     Сообщение: {error.message}")
                lines.append("\n".join(error_info))
        
        if self.valid.PARSED:
            lines.append(f"\nРаспарсенные данные ({len(self.valid.PARSED)} ключей):")
            for key, value in list(self.valid.PARSED.items())[:5]:  # Показываем первые 5
                if isinstance(value, list) and len(value) > 3:
                    lines.append(f"  {key}: {value[:3]} ... (всего {len(value)} элементов)")
                else:
                    lines.append(f"  {key}: {value}")
            if len(self.valid.PARSED) > 5:
                lines.append(f"  ... и еще {len(self.valid.PARSED) - 5} ключей")
        
        return "\n".join(lines)

