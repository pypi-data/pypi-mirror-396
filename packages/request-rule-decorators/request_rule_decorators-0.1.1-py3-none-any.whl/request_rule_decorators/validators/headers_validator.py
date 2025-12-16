"""Валидатор для HTTP заголовков."""

import re
from typing import Any, List, Optional

from ..dto import ValidationError
from .base import BaseValidator
from .blacklist_whitelist import Blacklist, Whitelist


class HeadersValidator(BaseValidator):
    """Валидатор для проверки HTTP заголовков."""
    
    def __init__(self, error_key: str | None = None):
        """
        Инициализация валидатора заголовков.
        
        Args:
            error_key: Ключ ошибки для идентификации конкретного правила
        """
        super().__init__(error_key=error_key)
        self._rule_name = "HeadersValidator"
    
    def has_key(self, key: str) -> "HeadersValidator":
        """Проверка наличия ключа в заголовках."""
        return self._add_rule("has_key", key=key)
    
    def missing_key(self, key: str) -> "HeadersValidator":
        """Проверка отсутствия ключа в заголовках."""
        return self._add_rule("missing_key", key=key)
    
    def blacklist(self, key: str, values: List[str]) -> "HeadersValidator":
        """Проверка, что значение ключа не в черном списке."""
        return self._add_rule("blacklist", key=key, values=values)
    
    def whitelist(self, key: str, values: List[str]) -> "HeadersValidator":
        """Проверка, что значение ключа в белом списке."""
        return self._add_rule("whitelist", key=key, values=values)
    
    def regex(self, key: str, pattern: str) -> "HeadersValidator":
        """Проверка значения ключа по регулярному выражению."""
        return self._add_rule("regex", key=key, pattern=pattern)
    
    def validate(self, headers: dict) -> tuple[bool, Optional[ValidationError]]:
        """
        Выполняет валидацию заголовков.
        
        Args:
            headers: Словарь заголовков для валидации
            
        Returns:
            Tuple[bool, Optional[ValidationError]]: (успешность валидации, ошибка если есть)
        """
        if not self._rules:
            return True, None
        
        # Нормализуем заголовки: приводим ключи к нижнему регистру для сравнения
        normalized_headers = {k.lower(): v for k, v in headers.items()}
        
        for rule in self._rules:
            rule_type = rule["type"]
            key = rule.get("key", "").lower()
            
            if rule_type == "has_key":
                if key not in normalized_headers:
                    return False, self._create_error(
                        rule_type="has_key",
                        expected_values=[f"key '{rule['key']}'"],
                        received_values=list(headers.keys()),
                        message=f"Header key '{rule['key']}' is missing",
                    )
            
            elif rule_type == "missing_key":
                if key in normalized_headers:
                    return False, self._create_error(
                        rule_type="missing_key",
                        expected_values=[f"key '{rule['key']}' should not exist"],
                        received_values=[f"key '{rule['key']}' exists"],
                        message=f"Header key '{rule['key']}' should not be present",
                    )
            
            elif rule_type == "blacklist":
                if key not in normalized_headers:
                    return False, self._create_error(
                        rule_type="blacklist",
                        expected_values=[f"key '{rule['key']}'"],
                        received_values=list(headers.keys()),
                        message=f"Header key '{rule['key']}' is missing",
                    )
                value = normalized_headers[key]
                # Заголовки могут быть строками или списками строк
                header_values = [value] if isinstance(value, str) else value
                for header_value in header_values:
                    if header_value in rule["values"]:
                        return False, self._create_error(
                            rule_type="blacklist",
                            expected_values=[f"not in {rule['values']}"],
                            received_values=[header_value],
                            message=f"Header '{rule['key']}' value '{header_value}' is in blacklist {rule['values']}",
                        )
            
            elif rule_type == "whitelist":
                if key not in normalized_headers:
                    return False, self._create_error(
                        rule_type="whitelist",
                        expected_values=[f"key '{rule['key']}'"],
                        received_values=list(headers.keys()),
                        message=f"Header key '{rule['key']}' is missing",
                    )
                value = normalized_headers[key]
                # Заголовки могут быть строками или списками строк
                header_values = [value] if isinstance(value, str) else value
                for header_value in header_values:
                    if header_value not in rule["values"]:
                        return False, self._create_error(
                            rule_type="whitelist",
                            expected_values=rule["values"],
                            received_values=[header_value],
                            message=f"Header '{rule['key']}' value '{header_value}' is not in whitelist {rule['values']}",
                        )
            
            elif rule_type == "regex":
                if key not in normalized_headers:
                    return False, self._create_error(
                        rule_type="regex",
                        expected_values=[f"key '{rule['key']}'"],
                        received_values=list(headers.keys()),
                        message=f"Header key '{rule['key']}' is missing",
                    )
                value = normalized_headers[key]
                # Заголовки могут быть строками или списками строк
                header_values = [value] if isinstance(value, str) else value
                pattern = rule["pattern"]
                for header_value in header_values:
                    if not re.match(pattern, str(header_value)):
                        return False, self._create_error(
                            rule_type="regex",
                            expected_values=[f"match pattern '{pattern}'"],
                            received_values=[header_value],
                            message=f"Header '{rule['key']}' value '{header_value}' does not match regex pattern '{pattern}'",
                        )
        
        return True, None

