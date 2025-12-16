"""Валидатор для JSON данных с использованием jsonpath."""

import re
from typing import Any, List, Optional, Type, Union

from jsonpath_ng import parse as parse_jsonpath

from ..dto import ValidationError
from .base import BaseValidator
from .blacklist_whitelist import Blacklist, Whitelist


class JSONValidator(BaseValidator):
    """Валидатор для проверки JSON данных по jsonpath."""
    
    def __init__(self, json_path: str, error_key: str | None = None):
        """
        Инициализация JSON валидатора.
        
        Args:
            json_path: JSONPath выражение для извлечения значения
            error_key: Ключ ошибки для идентификации конкретного правила
        """
        super().__init__(error_key=error_key)
        self.json_path = json_path
        self._rule_name = f"JSONValidator({json_path})"
    
    def blacklist(self) -> Blacklist:
        """Возвращает объект Blacklist для создания правил черного списка."""
        return Blacklist(self)
    
    def whitelist(self) -> Whitelist:
        """Возвращает объект Whitelist для создания правил белого списка."""
        return Whitelist(self)
    
    def range(self, min_val: Union[int, float], max_val: Union[int, float]) -> "JSONValidator":
        """Проверка, что значение в заданном диапазоне."""
        return self._add_rule("range", min_val=min_val, max_val=max_val)
    
    def regex(self, pattern: str) -> "JSONValidator":
        """Проверка значения по регулярному выражению."""
        return self._add_rule("regex", pattern=pattern)
    
    def exists(self) -> "JSONValidator":
        """Проверка существования пути."""
        return self._add_rule("exists")
    
    def type(self, expected_type: Type) -> "JSONValidator":
        """Проверка типа значения."""
        return self._add_rule("type", expected_type=expected_type)
    
    def validate(self, json_data: dict | list) -> tuple[bool, Optional[ValidationError]]:
        """
        Выполняет валидацию JSON данных.
        
        Args:
            json_data: JSON данные для валидации
            
        Returns:
            Tuple[bool, Optional[ValidationError]]: (успешность валидации, ошибка если есть)
        """
        if not self._rules:
            return True, None
        
        # Извлекаем значения по jsonpath
        try:
            jsonpath_expr = parse_jsonpath(self.json_path)
            matches = [match.value for match in jsonpath_expr.find(json_data)]
        except Exception as e:
            return False, self._create_error(
                rule_type="exists",
                expected_values=[self.json_path],
                received_values=[],
                message=f"Failed to parse jsonpath '{self.json_path}': {str(e)}",
            )
        
        # Если нет совпадений и требуется exists, это ошибка
        if not matches:
            for rule in self._rules:
                if rule["type"] == "exists":
                    return False, self._create_error(
                        rule_type="exists",
                        expected_values=[self.json_path],
                        received_values=[],
                        message=f"Path '{self.json_path}' does not exist",
                    )
            # Если нет правила exists, но нет значений - пропускаем
            return True, None
        
        # Применяем все правила к каждому найденному значению
        for value in matches:
            for rule in self._rules:
                rule_type = rule["type"]
                
                if rule_type == "exists":
                    continue  # Уже проверили выше
                
                elif rule_type == "blacklist_values":
                    if value in rule["values"]:
                        return False, self._create_error(
                            rule_type="blacklist.values",
                            expected_values=[f"not in {rule['values']}"],
                            received_values=[value],
                            message=f"Value {value} is in blacklist {rule['values']}",
                        )
                
                elif rule_type == "whitelist_values":
                    if value not in rule["values"]:
                        return False, self._create_error(
                            rule_type="whitelist.values",
                            expected_values=rule["values"],
                            received_values=[value],
                            message=f"Value {value} is not in whitelist {rule['values']}",
                        )
                
                elif rule_type == "blacklist_words":
                    if not isinstance(value, str):
                        return False, self._create_error(
                            rule_type="blacklist.words",
                            expected_values=["string"],
                            received_values=[type(value).__name__],
                            message=f"Value {value} is not a string, cannot check words",
                        )
                    value_lower = value.lower()
                    found_words = [word for word in rule["words"] if word.lower() in value_lower]
                    if found_words:
                        return False, self._create_error(
                            rule_type="blacklist.words",
                            expected_values=[f"not contain words: {rule['words']}"],
                            received_values=[f"contains: {found_words}"],
                            message=f"Value '{value}' contains forbidden words: {found_words}",
                        )
                
                elif rule_type == "whitelist_words":
                    if not isinstance(value, str):
                        return False, self._create_error(
                            rule_type="whitelist.words",
                            expected_values=["string"],
                            received_values=[type(value).__name__],
                            message=f"Value {value} is not a string, cannot check words",
                        )
                    value_lower = value.lower()
                    found_words = [word for word in rule["words"] if word.lower() in value_lower]
                    if not found_words:
                        return False, self._create_error(
                            rule_type="whitelist.words",
                            expected_values=[f"contain at least one word from: {rule['words']}"],
                            received_values=[value],
                            message=f"Value '{value}' does not contain any allowed words from {rule['words']}",
                        )
                
                elif rule_type == "blacklist_regex":
                    pattern = rule["pattern"]
                    value_str = str(value)
                    if re.match(pattern, value_str):
                        return False, self._create_error(
                            rule_type="blacklist.regex",
                            expected_values=[f"not match pattern '{pattern}'"],
                            received_values=[value],
                            message=f"Value {value} matches forbidden regex pattern '{pattern}'",
                        )
                
                elif rule_type == "whitelist_regex":
                    pattern = rule["pattern"]
                    value_str = str(value)
                    if not re.match(pattern, value_str):
                        return False, self._create_error(
                            rule_type="whitelist.regex",
                            expected_values=[f"match pattern '{pattern}'"],
                            received_values=[value],
                            message=f"Value {value} does not match required regex pattern '{pattern}'",
                        )
                
                elif rule_type == "range":
                    min_val = rule["min_val"]
                    max_val = rule["max_val"]
                    if not isinstance(value, (int, float)):
                        return False, self._create_error(
                            rule_type="range",
                            expected_values=[f"number in range [{min_val}, {max_val}]"],
                            received_values=[value],
                            message=f"Value {value} is not a number",
                        )
                    if not (min_val <= value <= max_val):
                        return False, self._create_error(
                            rule_type="range",
                            expected_values=[f"number in range [{min_val}, {max_val}]"],
                            received_values=[value],
                            message=f"Value {value} is not in range [{min_val}, {max_val}]",
                        )
                
                elif rule_type == "regex":
                    pattern = rule["pattern"]
                    value_str = str(value)
                    if not re.match(pattern, value_str):
                        return False, self._create_error(
                            rule_type="regex",
                            expected_values=[f"match pattern '{pattern}'"],
                            received_values=[value],
                            message=f"Value {value} does not match regex pattern '{pattern}'",
                        )
                
                elif rule_type == "type":
                    expected_type = rule["expected_type"]
                    if not isinstance(value, expected_type):
                        return False, self._create_error(
                            rule_type="type",
                            expected_values=[expected_type.__name__],
                            received_values=[type(value).__name__],
                            message=f"Value {value} is of type {type(value).__name__}, expected {expected_type.__name__}",
                        )
                
                elif rule_type == "blacklist_words":
                    if not isinstance(value, str):
                        return False, self._create_error(
                            rule_type="blacklist_words",
                            expected_values=["string"],
                            received_values=[type(value).__name__],
                            message=f"Value {value} is not a string, cannot check words",
                        )
                    value_lower = value.lower()
                    found_words = [word for word in rule["words"] if word.lower() in value_lower]
                    if found_words:
                        return False, self._create_error(
                            rule_type="blacklist_words",
                            expected_values=[f"not contain words: {rule['words']}"],
                            received_values=[f"contains: {found_words}"],
                            message=f"Value '{value}' contains forbidden words: {found_words}",
                        )
                
                elif rule_type == "whitelist_words":
                    if not isinstance(value, str):
                        return False, self._create_error(
                            rule_type="whitelist_words",
                            expected_values=["string"],
                            received_values=[type(value).__name__],
                            message=f"Value {value} is not a string, cannot check words",
                        )
                    value_lower = value.lower()
                    found_words = [word for word in rule["words"] if word.lower() in value_lower]
                    if not found_words:
                        return False, self._create_error(
                            rule_type="whitelist_words",
                            expected_values=[f"contain at least one word from: {rule['words']}"],
                            received_values=[value],
                            message=f"Value '{value}' does not contain any allowed words from {rule['words']}",
                        )
        
        return True, None

