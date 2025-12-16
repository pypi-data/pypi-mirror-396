"""Парсер для JSON данных с использованием jsonpath."""

import re
from typing import Any, Dict, List, Optional

from jsonpath_ng import parse as parse_jsonpath

from ..exceptions import ParserError
from .base import BaseParser


class JSONParser(BaseParser):
    """Парсер для извлечения и обработки JSON данных по jsonpath."""
    
    def __init__(self, json_path: str):
        """
        Инициализация JSON парсера.
        
        Args:
            json_path: JSONPath выражение для извлечения значения
        """
        super().__init__()
        self.json_path = json_path
        self._extracted_field: Optional[str] = None
    
    def regex(self, pattern: str) -> "JSONParser":
        """Применить regex к значению."""
        return self._add_operation("regex", pattern=pattern)
    
    def sum(self) -> "JSONParser":
        """Суммировать числовые значения (для списков чисел и списков словарей)."""
        return self._add_operation("sum")
    
    def average(self) -> "JSONParser":
        """Вычислить среднее значение (для списков чисел и списков словарей)."""
        return self._add_operation("average")
    
    def max(self) -> "JSONParser":
        """Найти максимальное значение (для списков чисел и списков словарей)."""
        return self._add_operation("max")
    
    def min(self) -> "JSONParser":
        """Найти минимальное значение (для списков чисел и списков словарей)."""
        return self._add_operation("min")
    
    def count(self) -> "JSONParser":
        """Подсчитать количество элементов (для списков)."""
        return self._add_operation("count")
    
    def extract_field(self, field: str) -> "JSONParser":
        """Извлечь поле из списка словарей."""
        self._extracted_field = field
        return self._add_operation("extract_field", field=field)
    
    def parse(self, json_data: dict | list) -> Any:
        """
        Выполняет парсинг JSON данных.
        
        Args:
            json_data: JSON данные для парсинга
            
        Returns:
            Распарсенные данные
        """
        # Извлекаем значения по jsonpath
        try:
            jsonpath_expr = parse_jsonpath(self.json_path)
            matches = [match.value for match in jsonpath_expr.find(json_data)]
        except Exception as e:
            raise ParserError(f"Failed to parse jsonpath '{self.json_path}': {str(e)}") from e
        
        if not matches:
            raise ParserError(f"No values found for jsonpath '{self.json_path}'")
        
        # Если найдено одно значение, работаем с ним, иначе со списком
        if len(matches) == 1:
            value = matches[0]
        else:
            value = matches
        
        # Применяем операции в порядке добавления
        result = value
        
        for operation in self._operations:
            op_type = operation["type"]
            
            if op_type == "extract_field":
                # Извлекаем поле из списка словарей
                field = operation["field"]
                if not isinstance(result, list):
                    raise ParserError(f"extract_field can only be applied to lists, got {type(result).__name__}")
                
                extracted = []
                for item in result:
                    if not isinstance(item, dict):
                        raise ParserError(f"extract_field can only be applied to list of dicts, got list of {type(item).__name__}")
                    if field not in item:
                        raise ParserError(f"Field '{field}' not found in dict: {item}")
                    extracted.append(item[field])
                
                result = extracted
            
            elif op_type == "regex":
                pattern = operation["pattern"]
                if isinstance(result, list):
                    result = [re.match(pattern, str(v)).group(0) if re.match(pattern, str(v)) else None for v in result]
                    result = [v for v in result if v is not None]
                    if len(result) == 1:
                        result = result[0]
                else:
                    match = re.match(pattern, str(result))
                    if match:
                        result = match.group(0)
                    else:
                        raise ParserError(f"Value '{result}' does not match regex pattern '{pattern}'")
            
            elif op_type == "sum":
                result = self._apply_numeric_operation(result, "sum")
            
            elif op_type == "average":
                result = self._apply_numeric_operation(result, "average")
            
            elif op_type == "max":
                result = self._apply_numeric_operation(result, "max")
            
            elif op_type == "min":
                result = self._apply_numeric_operation(result, "min")
            
            elif op_type == "count":
                if isinstance(result, list):
                    result = len(result)
                else:
                    result = 1
        
        return result
    
    def _apply_numeric_operation(self, value: Any, operation: str) -> float:
        """
        Применяет числовую операцию к значению.
        
        Args:
            value: Значение для обработки (список чисел или список словарей)
            operation: Тип операции (sum, average, max, min)
            
        Returns:
            Результат операции
        """
        # Преобразуем значение в список чисел
        if isinstance(value, list):
            if not value:
                raise ParserError(f"Cannot apply {operation} to empty list")
            
            # Если это список словарей и было вызвано extract_field, извлекаем поле
            if isinstance(value[0], dict):
                if not self._extracted_field:
                    raise ParserError(f"{operation} requires extract_field() to be called first when working with list of dicts")
                numbers = []
                for item in value:
                    if self._extracted_field not in item:
                        raise ParserError(f"Field '{self._extracted_field}' not found in dict: {item}")
                    numbers.append(self._to_number(item[self._extracted_field]))
            else:
                # Это уже список чисел (возможно после extract_field или исходный список чисел)
                numbers = [self._to_number(v) for v in value]
        else:
            # Одиночное значение
            numbers = [self._to_number(value)]
        
        if not numbers:
            raise ParserError(f"Cannot apply {operation} to empty list")
        
        if operation == "sum":
            return sum(numbers)
        elif operation == "average":
            return sum(numbers) / len(numbers)
        elif operation == "max":
            return max(numbers)
        elif operation == "min":
            return min(numbers)
        else:
            raise ParserError(f"Unknown operation: {operation}")
    
    def _to_number(self, value: Any) -> float:
        """Преобразует значение в число."""
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(value)
        except (ValueError, TypeError) as e:
            raise ParserError(f"Cannot convert '{value}' to number: {str(e)}") from e

