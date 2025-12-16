"""Парсер для HTML данных с использованием xpath."""

import re
from typing import Any, Dict, List, Optional

from lxml import html

from ..exceptions import ParserError
from .base import BaseParser


class HTMLParser(BaseParser):
    """Парсер для извлечения и обработки HTML данных по xpath."""
    
    def __init__(self, xpath: str):
        """
        Инициализация HTML парсера.
        
        Args:
            xpath: XPath выражение для извлечения значения
        """
        super().__init__()
        self.xpath = xpath
        self._extracted_field: Optional[str] = None
    
    def regex(self, pattern: str) -> "HTMLParser":
        """Применить regex к значению."""
        return self._add_operation("regex", pattern=pattern)
    
    def sum(self) -> "HTMLParser":
        """Суммировать числовые значения (для списков чисел и списков словарей)."""
        return self._add_operation("sum")
    
    def average(self) -> "HTMLParser":
        """Вычислить среднее значение (для списков чисел и списков словарей)."""
        return self._add_operation("average")
    
    def max(self) -> "HTMLParser":
        """Найти максимальное значение (для списков чисел и списков словарей)."""
        return self._add_operation("max")
    
    def min(self) -> "HTMLParser":
        """Найти минимальное значение (для списков чисел и списков словарей)."""
        return self._add_operation("min")
    
    def count(self) -> "HTMLParser":
        """Подсчитать количество элементов (для списков)."""
        return self._add_operation("count")
    
    def extract_field(self, field: str) -> "HTMLParser":
        """Извлечь поле из списка словарей."""
        self._extracted_field = field
        return self._add_operation("extract_field", field=field)
    
    def parse(self, html_data: str | bytes) -> Any:
        """
        Выполняет парсинг HTML данных.
        
        Args:
            html_data: HTML данные для парсинга (строка или bytes)
            
        Returns:
            Распарсенные данные
        """
        # Парсим HTML
        try:
            if isinstance(html_data, bytes):
                tree = html.fromstring(html_data)
            else:
                tree = html.fromstring(html_data.encode('utf-8') if isinstance(html_data, str) else html_data)
        except Exception as e:
            raise ParserError(f"Failed to parse HTML: {str(e)}") from e
        
        # Извлекаем значения по xpath
        try:
            matches = tree.xpath(self.xpath)
            # Преобразуем элементы в строки или текстовое содержимое
            matches = [elem.text if hasattr(elem, 'text') and elem.text else str(elem) for elem in matches]
        except Exception as e:
            raise ParserError(f"Failed to parse xpath '{self.xpath}': {str(e)}") from e
        
        if not matches:
            raise ParserError(f"No values found for xpath '{self.xpath}'")
        
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

