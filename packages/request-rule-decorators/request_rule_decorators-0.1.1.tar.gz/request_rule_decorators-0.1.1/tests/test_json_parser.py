"""Тесты для JSONParser."""

import pytest
from request_rule_decorators.parsers import JSONParser
from request_rule_decorators.exceptions import ParserError


class TestJSONParser:
    """Тесты для JSONParser."""
    
    def test_simple_extraction(self):
        """Тест простого извлечения значения."""
        parser = JSONParser("$.age")
        json_data = {"age": 25}
        result = parser.parse(json_data)
        assert result == 25
    
    def test_save_to(self):
        """Тест сохранения результата в ключ."""
        parser = JSONParser("$.age").save_to("parsed_age")
        json_data = {"age": 25}
        result = parser.parse(json_data)
        assert result == 25
        assert parser._save_key == "parsed_age"
    
    def test_regex(self):
        """Тест применения regex."""
        parser = JSONParser("$.email").regex(r"^([a-zA-Z0-9._%+-]+)@")
        json_data = {"email": "test@example.com"}
        result = parser.parse(json_data)
        assert result == "test"
    
    def test_sum_list(self):
        """Тест суммирования списка чисел."""
        parser = JSONParser("$.numbers").sum()
        json_data = {"numbers": [1, 2, 3, 4, 5]}
        result = parser.parse(json_data)
        assert result == 15
    
    def test_average_list(self):
        """Тест вычисления среднего списка чисел."""
        parser = JSONParser("$.numbers").average()
        json_data = {"numbers": [10, 20, 30]}
        result = parser.parse(json_data)
        assert result == 20.0
    
    def test_max_list(self):
        """Тест поиска максимума в списке чисел."""
        parser = JSONParser("$.numbers").max()
        json_data = {"numbers": [10, 20, 30, 5]}
        result = parser.parse(json_data)
        assert result == 30
    
    def test_min_list(self):
        """Тест поиска минимума в списке чисел."""
        parser = JSONParser("$.numbers").min()
        json_data = {"numbers": [10, 20, 30, 5]}
        result = parser.parse(json_data)
        assert result == 5
    
    def test_extract_field(self):
        """Тест извлечения поля из списка словарей."""
        parser = JSONParser("$.data[*]").extract_field("traffic")
        json_data = {
            "data": [
                {"traffic": 100},
                {"traffic": 200},
                {"traffic": 300}
            ]
        }
        result = parser.parse(json_data)
        assert result == [100, 200, 300]
    
    def test_extract_field_sum(self):
        """Тест извлечения поля и суммирования."""
        parser = JSONParser("$.data[*]").extract_field("traffic").sum()
        json_data = {
            "data": [
                {"traffic": 100},
                {"traffic": 200},
                {"traffic": 300}
            ]
        }
        result = parser.parse(json_data)
        assert result == 600
    
    def test_extract_field_average(self):
        """Тест извлечения поля и вычисления среднего."""
        parser = JSONParser("$.data[*]").extract_field("traffic").average()
        json_data = {
            "data": [
                {"traffic": 100},
                {"traffic": 200},
                {"traffic": 300}
            ]
        }
        result = parser.parse(json_data)
        assert result == 200.0
    
    def test_extract_field_max(self):
        """Тест извлечения поля и поиска максимума."""
        parser = JSONParser("$.data[*]").extract_field("traffic").max()
        json_data = {
            "data": [
                {"traffic": 100},
                {"traffic": 200},
                {"traffic": 300}
            ]
        }
        result = parser.parse(json_data)
        assert result == 300
    
    def test_fluent_interface(self):
        """Тест fluent interface - цепочка операций."""
        parser = (
            JSONParser("$.data[*]")
            .extract_field("traffic")
            .sum()
            .save_to("total_traffic")
        )
        json_data = {
            "data": [
                {"traffic": 100},
                {"traffic": 200}
            ]
        }
        result = parser.parse(json_data)
        assert result == 300
        assert parser._save_key == "total_traffic"
    
    def test_nested_path(self):
        """Тест работы с вложенными путями."""
        parser = JSONParser("$.user.profile.age")
        json_data = {"user": {"profile": {"age": 25}}}
        result = parser.parse(json_data)
        assert result == 25
    
    def test_array_path_single(self):
        """Тест работы с массивом - одно значение."""
        parser = JSONParser("$.users[0].age")
        json_data = {"users": [{"age": 25}, {"age": 30}]}
        result = parser.parse(json_data)
        assert result == 25
    
    def test_array_path_all(self):
        """Тест работы с массивом - все значения."""
        parser = JSONParser("$.users[*].age").sum()
        json_data = {"users": [{"age": 25}, {"age": 30}, {"age": 20}]}
        result = parser.parse(json_data)
        assert result == 75
    
    def test_error_missing_path(self):
        """Тест ошибки - путь не найден."""
        parser = JSONParser("$.nonexistent")
        json_data = {"age": 25}
        with pytest.raises(ParserError) as exc_info:
            parser.parse(json_data)
        assert "No values found" in str(exc_info.value)
    
    def test_error_extract_field_not_list(self):
        """Тест ошибки - extract_field применен не к списку."""
        parser = JSONParser("$.age").extract_field("value")
        json_data = {"age": 25}
        with pytest.raises(ParserError) as exc_info:
            parser.parse(json_data)
        assert "can only be applied to lists" in str(exc_info.value)
    
    def test_error_extract_field_missing_field(self):
        """Тест ошибки - поле отсутствует в словаре."""
        parser = JSONParser("$.data[*]").extract_field("nonexistent")
        json_data = {"data": [{"traffic": 100}]}
        with pytest.raises(ParserError) as exc_info:
            parser.parse(json_data)
        assert "not found" in str(exc_info.value)

