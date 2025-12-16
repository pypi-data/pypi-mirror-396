"""Тесты для StatusCodeValidator."""

import pytest
from request_rule_decorators.validators import StatusCodeValidator


class TestStatusCodeValidator:
    """Тесты для StatusCodeValidator."""
    
    def test_whitelist_success(self):
        """Тест успешной валидации whitelist для статус-кода."""
        validator = StatusCodeValidator().whitelist([200, 201, 204])
        is_valid, error = validator.validate(200)
        assert is_valid is True
        assert error is None
    
    def test_whitelist_failure(self):
        """Тест неудачной валидации whitelist для статус-кода."""
        validator = StatusCodeValidator().whitelist([200, 201, 204])
        is_valid, error = validator.validate(404)
        assert is_valid is False
        assert error is not None
        assert error.rule_name == "StatusCodeValidator.whitelist"
        assert error.expected_values == [200, 201, 204]
        assert error.received_values == [404]
        assert "whitelist" in error.message.lower()
        assert "404" in error.message
    
    def test_blacklist_success(self):
        """Тест успешной валидации blacklist для статус-кода."""
        validator = StatusCodeValidator().blacklist([400, 401, 403, 404, 500])
        is_valid, error = validator.validate(200)
        assert is_valid is True
        assert error is None
    
    def test_blacklist_failure(self):
        """Тест неудачной валидации blacklist для статус-кода."""
        validator = StatusCodeValidator().blacklist([400, 401, 403, 404, 500])
        is_valid, error = validator.validate(404)
        assert is_valid is False
        assert error is not None
        assert error.rule_name == "StatusCodeValidator.blacklist"
        assert error.received_values == [404]
        assert "blacklist" in error.message.lower()
        assert "404" in error.message
    
    def test_fluent_interface(self):
        """Тест fluent interface - цепочка методов."""
        validator = (
            StatusCodeValidator()
            .whitelist([200, 201, 204])
            .blacklist([500])
        )
        # whitelist проверяется первым, если проходит - blacklist не проверяется
        is_valid, error = validator.validate(200)
        assert is_valid is True
    
    def test_multiple_rules_whitelist_first(self):
        """Тест множественных правил - whitelist проверяется первым."""
        validator = (
            StatusCodeValidator()
            .whitelist([200, 201])
            .blacklist([500])
        )
        # 200 в whitelist - проходит
        is_valid, error = validator.validate(200)
        assert is_valid is True
        
        # 404 не в whitelist - ошибка
        is_valid, error = validator.validate(404)
        assert is_valid is False
        assert error.rule_name == "StatusCodeValidator.whitelist"
    
    def test_success_codes(self):
        """Тест успешных кодов."""
        validator = StatusCodeValidator().whitelist([200, 201, 202, 204])
        for code in [200, 201, 202, 204]:
            is_valid, error = validator.validate(code)
            assert is_valid is True, f"Code {code} should be valid"
    
    def test_client_error_codes(self):
        """Тест кодов ошибок клиента."""
        validator = StatusCodeValidator().blacklist([400, 401, 403, 404])
        for code in [400, 401, 403, 404]:
            is_valid, error = validator.validate(code)
            assert is_valid is False, f"Code {code} should be invalid"
            assert error.rule_name == "StatusCodeValidator.blacklist"
    
    def test_server_error_codes(self):
        """Тест кодов ошибок сервера."""
        validator = StatusCodeValidator().blacklist([500, 502, 503, 504])
        for code in [500, 502, 503, 504]:
            is_valid, error = validator.validate(code)
            assert is_valid is False, f"Code {code} should be invalid"
    
    def test_empty_rules(self):
        """Тест без правил - всегда успешно."""
        validator = StatusCodeValidator()
        is_valid, error = validator.validate(200)
        assert is_valid is True
        assert error is None

