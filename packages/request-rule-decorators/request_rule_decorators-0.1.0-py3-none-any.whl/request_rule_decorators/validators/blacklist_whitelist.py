"""Классы для blacklist и whitelist правил."""

from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from .base import BaseValidator


class Blacklist:
    """Класс для создания правил черного списка."""
    
    def __init__(self, validator: "BaseValidator"):
        """
        Инициализация Blacklist.
        
        Args:
            validator: Валидатор, к которому применяется правило
        """
        self._validator = validator
        self._rule_type = "blacklist"
    
    def values(self, values: List[Any]) -> "BaseValidator":  # type: ignore
        """Проверка, что значение не в черном списке значений."""
        return self._validator._add_rule(f"{self._rule_type}_values", values=values)
    
    def words(self, words: List[str]) -> "BaseValidator":  # type: ignore
        """Проверка, что строка не содержит ни одного слова из черного списка."""
        return self._validator._add_rule(f"{self._rule_type}_words", words=words)
    
    def regex(self, pattern: str) -> "BaseValidator":  # type: ignore
        """Проверка, что значение не соответствует регулярному выражению."""
        return self._validator._add_rule(f"{self._rule_type}_regex", pattern=pattern)


class Whitelist:
    """Класс для создания правил белого списка."""
    
    def __init__(self, validator: "BaseValidator"):  # type: ignore
        """
        Инициализация Whitelist.
        
        Args:
            validator: Валидатор, к которому применяется правило
        """
        self._validator = validator
        self._rule_type = "whitelist"
    
    def values(self, values: List[Any]) -> "BaseValidator":  # type: ignore
        """Проверка, что значение в белом списке значений."""
        return self._validator._add_rule(f"{self._rule_type}_values", values=values)
    
    def words(self, words: List[str]) -> "BaseValidator":  # type: ignore
        """Проверка, что строка содержит хотя бы одно слово из белого списка."""
        return self._validator._add_rule(f"{self._rule_type}_words", words=words)
    
    def regex(self, pattern: str) -> "BaseValidator":  # type: ignore
        """Проверка, что значение соответствует регулярному выражению."""
        return self._validator._add_rule(f"{self._rule_type}_regex", pattern=pattern)

