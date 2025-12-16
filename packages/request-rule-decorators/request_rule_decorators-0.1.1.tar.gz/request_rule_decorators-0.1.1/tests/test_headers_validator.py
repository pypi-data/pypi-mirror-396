"""Тесты для HeadersValidator."""

import pytest
from request_rule_decorators.validators import HeadersValidator


class TestHeadersValidator:
    """Тесты для HeadersValidator."""
    
    def test_has_key_success(self):
        """Тест успешной валидации has_key."""
        validator = HeadersValidator().has_key("Content-Type")
        headers = {"Content-Type": "application/json"}
        is_valid, error = validator.validate(headers)
        assert is_valid is True
        assert error is None
    
    def test_has_key_failure(self):
        """Тест неудачной валидации has_key."""
        validator = HeadersValidator().has_key("Content-Type")
        headers = {"Accept": "application/json"}
        is_valid, error = validator.validate(headers)
        assert is_valid is False
        assert error is not None
        assert error.rule_name == "HeadersValidator.has_key"
        assert "Content-Type" in error.message
        assert "missing" in error.message.lower()
    
    def test_has_key_case_insensitive(self):
        """Тест has_key - регистронезависимая проверка."""
        validator = HeadersValidator().has_key("Content-Type")
        headers = {"content-type": "application/json"}  # lowercase
        is_valid, error = validator.validate(headers)
        assert is_valid is True
    
    def test_missing_key_success(self):
        """Тест успешной валидации missing_key."""
        validator = HeadersValidator().missing_key("X-Secret-Header")
        headers = {"Content-Type": "application/json"}
        is_valid, error = validator.validate(headers)
        assert is_valid is True
        assert error is None
    
    def test_missing_key_failure(self):
        """Тест неудачной валидации missing_key - ключ присутствует."""
        validator = HeadersValidator().missing_key("Content-Type")
        headers = {"Content-Type": "application/json"}
        is_valid, error = validator.validate(headers)
        assert is_valid is False
        assert error is not None
        assert error.rule_name == "HeadersValidator.missing_key"
        assert "should not be present" in error.message.lower()
    
    def test_blacklist_success(self):
        """Тест успешной валидации blacklist для заголовков."""
        validator = HeadersValidator().blacklist("X-Status", ["error", "failed"])
        headers = {"X-Status": "success"}
        is_valid, error = validator.validate(headers)
        assert is_valid is True
        assert error is None
    
    def test_blacklist_failure(self):
        """Тест неудачной валидации blacklist для заголовков."""
        validator = HeadersValidator().blacklist("X-Status", ["error", "failed"])
        headers = {"X-Status": "error"}
        is_valid, error = validator.validate(headers)
        assert is_valid is False
        assert error is not None
        assert error.rule_name == "HeadersValidator.blacklist"
        assert error.received_values == ["error"]
        assert "blacklist" in error.message.lower()
    
    def test_blacklist_missing_key(self):
        """Тест blacklist - ключ отсутствует."""
        validator = HeadersValidator().blacklist("X-Status", ["error", "failed"])
        headers = {"Content-Type": "application/json"}
        is_valid, error = validator.validate(headers)
        assert is_valid is False
        assert "missing" in error.message.lower()
    
    def test_whitelist_success(self):
        """Тест успешной валидации whitelist для заголовков."""
        validator = HeadersValidator().whitelist("Content-Type", ["application/json", "text/html"])
        headers = {"Content-Type": "application/json"}
        is_valid, error = validator.validate(headers)
        assert is_valid is True
        assert error is None
    
    def test_whitelist_failure(self):
        """Тест неудачной валидации whitelist для заголовков."""
        validator = HeadersValidator().whitelist("Content-Type", ["application/json", "text/html"])
        headers = {"Content-Type": "application/xml"}
        is_valid, error = validator.validate(headers)
        assert is_valid is False
        assert error is not None
        assert error.rule_name == "HeadersValidator.whitelist"
        assert error.expected_values == ["application/json", "text/html"]
        assert error.received_values == ["application/xml"]
        assert "whitelist" in error.message.lower()
    
    def test_regex_success(self):
        """Тест успешной валидации regex для заголовков."""
        validator = HeadersValidator().regex("Content-Type", r"^application/.*$")
        headers = {"Content-Type": "application/json"}
        is_valid, error = validator.validate(headers)
        assert is_valid is True
        assert error is None
    
    def test_regex_failure(self):
        """Тест неудачной валидации regex для заголовков."""
        validator = HeadersValidator().regex("Content-Type", r"^application/.*$")
        headers = {"Content-Type": "text/html"}
        is_valid, error = validator.validate(headers)
        assert is_valid is False
        assert error is not None
        assert error.rule_name == "HeadersValidator.regex"
        assert error.received_values == ["text/html"]
        assert "regex" in error.message.lower()
    
    def test_regex_missing_key(self):
        """Тест regex - ключ отсутствует."""
        validator = HeadersValidator().regex("X-Custom", r"^test.*$")
        headers = {"Content-Type": "application/json"}
        is_valid, error = validator.validate(headers)
        assert is_valid is False
        assert "missing" in error.message.lower()
    
    def test_fluent_interface(self):
        """Тест fluent interface - цепочка методов."""
        validator = (
            HeadersValidator()
            .has_key("Content-Type")
            .whitelist("Content-Type", ["application/json"])
        )
        headers = {"Content-Type": "application/json"}
        is_valid, error = validator.validate(headers)
        assert is_valid is True
    
    def test_fluent_interface_failure(self):
        """Тест fluent interface - первая ошибка в цепочке."""
        validator = (
            HeadersValidator()
            .has_key("Content-Type")
            .whitelist("Content-Type", ["application/json"])
        )
        headers = {"Accept": "application/json"}  # Нет Content-Type
        is_valid, error = validator.validate(headers)
        assert is_valid is False
        assert error.rule_name == "HeadersValidator.has_key"
    
    def test_multiple_headers(self):
        """Тест работы с несколькими заголовками."""
        validator = (
            HeadersValidator()
            .has_key("Content-Type")
            .has_key("Authorization")
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer token123"
        }
        is_valid, error = validator.validate(headers)
        assert is_valid is True

