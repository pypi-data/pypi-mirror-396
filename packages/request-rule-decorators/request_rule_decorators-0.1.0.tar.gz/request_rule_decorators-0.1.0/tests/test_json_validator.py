"""Тесты для JSONValidator."""

import pytest
from request_rule_decorators.validators import JSONValidator


class TestJSONValidator:
    """Тесты для JSONValidator."""
    
    def test_blacklist_success(self):
        """Тест успешной валидации blacklist."""
        validator = JSONValidator("$.age").blacklist([10, 20, 30])
        json_data = {"age": 25}
        is_valid, error = validator.validate(json_data)
        assert is_valid is True
        assert error is None
    
    def test_blacklist_failure(self):
        """Тест неудачной валидации blacklist."""
        validator = JSONValidator("$.age").blacklist([10, 20, 30])
        json_data = {"age": 20}
        is_valid, error = validator.validate(json_data)
        assert is_valid is False
        assert error is not None
        assert error.rule_name == "JSONValidator($.age).blacklist"
        assert error.received_values == [20]
        assert "blacklist" in error.message.lower()
    
    def test_whitelist_success(self):
        """Тест успешной валидации whitelist."""
        validator = JSONValidator("$.status").whitelist(["active", "pending"])
        json_data = {"status": "active"}
        is_valid, error = validator.validate(json_data)
        assert is_valid is True
        assert error is None
    
    def test_whitelist_failure(self):
        """Тест неудачной валидации whitelist."""
        validator = JSONValidator("$.status").whitelist(["active", "pending"])
        json_data = {"status": "inactive"}
        is_valid, error = validator.validate(json_data)
        assert is_valid is False
        assert error is not None
        assert error.rule_name == "JSONValidator($.status).whitelist"
        assert error.expected_values == ["active", "pending"]
        assert error.received_values == ["inactive"]
        assert "whitelist" in error.message.lower()
    
    def test_range_success(self):
        """Тест успешной валидации range."""
        validator = JSONValidator("$.age").range(18, 100)
        json_data = {"age": 25}
        is_valid, error = validator.validate(json_data)
        assert is_valid is True
        assert error is None
    
    def test_range_failure_below_min(self):
        """Тест неудачной валидации range - значение ниже минимума."""
        validator = JSONValidator("$.age").range(18, 100)
        json_data = {"age": 15}
        is_valid, error = validator.validate(json_data)
        assert is_valid is False
        assert error is not None
        assert error.rule_name == "JSONValidator($.age).range"
        assert error.received_values == [15]
        assert "range" in error.message.lower()
        assert "18" in error.message
        assert "100" in error.message
    
    def test_range_failure_above_max(self):
        """Тест неудачной валидации range - значение выше максимума."""
        validator = JSONValidator("$.age").range(18, 100)
        json_data = {"age": 150}
        is_valid, error = validator.validate(json_data)
        assert is_valid is False
        assert error is not None
        assert error.received_values == [150]
    
    def test_range_failure_not_number(self):
        """Тест неудачной валидации range - значение не число."""
        validator = JSONValidator("$.age").range(18, 100)
        json_data = {"age": "twenty"}
        is_valid, error = validator.validate(json_data)
        assert is_valid is False
        assert error is not None
        assert "number" in error.message.lower()
    
    def test_regex_success(self):
        """Тест успешной валидации regex."""
        validator = JSONValidator("$.email").regex(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        json_data = {"email": "test@example.com"}
        is_valid, error = validator.validate(json_data)
        assert is_valid is True
        assert error is None
    
    def test_regex_failure(self):
        """Тест неудачной валидации regex."""
        validator = JSONValidator("$.email").regex(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        json_data = {"email": "invalid-email"}
        is_valid, error = validator.validate(json_data)
        assert is_valid is False
        assert error is not None
        assert error.rule_name == "JSONValidator($.email).regex"
        assert error.received_values == ["invalid-email"]
        assert "regex" in error.message.lower()
    
    def test_exists_success(self):
        """Тест успешной валидации exists."""
        validator = JSONValidator("$.name").exists()
        json_data = {"name": "John"}
        is_valid, error = validator.validate(json_data)
        assert is_valid is True
        assert error is None
    
    def test_exists_failure(self):
        """Тест неудачной валидации exists."""
        validator = JSONValidator("$.name").exists()
        json_data = {"age": 25}
        is_valid, error = validator.validate(json_data)
        assert is_valid is False
        assert error is not None
        assert error.rule_name == "JSONValidator($.name).exists"
        assert "does not exist" in error.message.lower()
    
    def test_type_success(self):
        """Тест успешной валидации type."""
        validator = JSONValidator("$.age").type(int)
        json_data = {"age": 25}
        is_valid, error = validator.validate(json_data)
        assert is_valid is True
        assert error is None
    
    def test_type_failure(self):
        """Тест неудачной валидации type."""
        validator = JSONValidator("$.age").type(int)
        json_data = {"age": "25"}
        is_valid, error = validator.validate(json_data)
        assert is_valid is False
        assert error is not None
        assert error.rule_name == "JSONValidator($.age).type"
        assert "int" in error.message.lower()
        assert "str" in error.message.lower()
    
    def test_fluent_interface(self):
        """Тест fluent interface - цепочка методов."""
        validator = (
            JSONValidator("$.age")
            .range(18, 100)
            .whitelist([25, 30, 35])
        )
        json_data = {"age": 25}
        is_valid, error = validator.validate(json_data)
        assert is_valid is True
    
    def test_fluent_interface_failure(self):
        """Тест fluent interface - первая ошибка в цепочке."""
        validator = (
            JSONValidator("$.age")
            .range(18, 100)
            .whitelist([25, 30, 35])
        )
        json_data = {"age": 15}  # Не проходит range
        is_valid, error = validator.validate(json_data)
        assert is_valid is False
        assert error.rule_name == "JSONValidator($.age).range"
    
    def test_nested_json_path(self):
        """Тест работы с вложенными путями."""
        validator = JSONValidator("$.user.age").range(18, 100)
        json_data = {"user": {"age": 25}}
        is_valid, error = validator.validate(json_data)
        assert is_valid is True
    
    def test_array_json_path(self):
        """Тест работы с массивами в jsonpath."""
        validator = JSONValidator("$.users[*].age").range(18, 100)
        json_data = {"users": [{"age": 25}, {"age": 30}, {"age": 20}]}
        is_valid, error = validator.validate(json_data)
        assert is_valid is True
    
    def test_array_json_path_failure(self):
        """Тест работы с массивами - один элемент не проходит валидацию."""
        validator = JSONValidator("$.users[*].age").range(18, 100)
        json_data = {"users": [{"age": 25}, {"age": 15}, {"age": 30}]}  # 15 не проходит
        is_valid, error = validator.validate(json_data)
        assert is_valid is False
        assert error.received_values == [15]

