"""Тесты для декоратора ResponseHandler."""

import pytest
from dataclasses import dataclass

from request_rule_decorators import ResponseHandler, Validator, Parser
from request_rule_decorators.dto import ResponseDTO


# Мок объект response для тестирования
@dataclass
class MockResponse:
    status_code: int
    headers: dict
    _json: dict
    _text: str
    
    def json(self):
        return self._json
    
    @property
    def text(self):
        return self._text


class TestResponseHandler:
    """Тесты для декоратора ResponseHandler."""
    
    def test_sync_function_success(self):
        """Тест синхронной функции - успешная валидация."""
        @ResponseHandler.handlers(
            Validator.STATUS_CODE().whitelist([200]),
            Validator.HEADERS().has_key("Content-Type"),
            Validator.JSON("$.status").whitelist(["success"])
        )
        def test_func():
            return MockResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                _json={"status": "success"},
                _text="OK"
            )
        
        result = test_func()
        assert isinstance(result, ResponseDTO)
        assert result.response.status_code == 200
        assert len(result.validation_data.ERRORS) == 0
    
    def test_sync_function_validation_error(self):
        """Тест синхронной функции - ошибка валидации."""
        @ResponseHandler.handlers(
            Validator.STATUS_CODE().whitelist([200]),
            Validator.JSON("$.status").whitelist(["success"])
        )
        def test_func():
            return MockResponse(
                status_code=404,  # Ошибка статус-кода
                headers={},
                _json={"status": "success"},
                _text="Not Found"
            )
        
        result = test_func()
        assert isinstance(result, ResponseDTO)
        assert len(result.validation_data.ERRORS) == 1
        assert result.validation_data.ERRORS[0].rule_name == "StatusCodeValidator.whitelist"
        assert result.validation_data.ERRORS[0].received_values == [404]
    
    def test_async_function_success(self):
        """Тест асинхронной функции - успешная валидация."""
        @ResponseHandler.handlers(
            Validator.STATUS_CODE().whitelist([200]),
            Validator.JSON("$.username").whitelist(["john_doe"])
        )
        async def test_func():
            return MockResponse(
                status_code=200,
                headers={},
                _json={"username": "john_doe"},
                _text="OK"
            )
        
        import asyncio
        result = asyncio.run(test_func())
        assert isinstance(result, ResponseDTO)
        assert len(result.validation_data.ERRORS) == 0
    
    def test_multiple_validation_errors(self):
        """Тест множественных ошибок валидации."""
        @ResponseHandler.handlers(
            Validator.STATUS_CODE().whitelist([200]),
            Validator.JSON("$.age").range(18, 100),
            Validator.JSON("$.status").whitelist(["active"])
        )
        def test_func():
            return MockResponse(
                status_code=404,  # Ошибка 1
                headers={},
                _json={
                    "age": 15,  # Ошибка 2
                    "status": "inactive"  # Ошибка 3
                },
                _text="Not Found"
            )
        
        result = test_func()
        assert len(result.validation_data.ERRORS) == 3
        error_names = [e.rule_name for e in result.validation_data.ERRORS]
        assert "StatusCodeValidator.whitelist" in error_names
        assert "JSONValidator($.age).range" in error_names
        assert "JSONValidator($.status).whitelist" in error_names
    
    def test_parser_success(self):
        """Тест парсера - успешное извлечение данных."""
        @ResponseHandler.handlers(
            Validator.STATUS_CODE().whitelist([200]),
            Parser.JSON("$.age").save_to("parsed_age"),
            Parser.JSON("$.data[*].traffic").extract_field("traffic").sum().save_to("total_traffic")
        )
        def test_func():
            return MockResponse(
                status_code=200,
                headers={},
                _json={
                    "age": 25,
                    "data": [
                        {"traffic": 100},
                        {"traffic": 200}
                    ]
                },
                _text="OK"
            )
        
        result = test_func()
        assert len(result.validation_data.ERRORS) == 0
        assert "parsed_age" in result.validation_data.PARSED
        assert result.validation_data.PARSED["parsed_age"] == 25
        assert "total_traffic" in result.validation_data.PARSED
        assert result.validation_data.PARSED["total_traffic"] == 300
    
    def test_parser_error(self):
        """Тест парсера - ошибка парсинга записывается в ERRORS."""
        @ResponseHandler.handlers(
            Validator.STATUS_CODE().whitelist([200]),
            Parser.JSON("$.nonexistent").save_to("value")
        )
        def test_func():
            return MockResponse(
                status_code=200,
                headers={},
                _json={"age": 25},
                _text="OK"
            )
        
        result = test_func()
        assert len(result.validation_data.ERRORS) == 1
        assert "Parser error" in result.validation_data.ERRORS[0].message
        assert "JSONParser" in result.validation_data.ERRORS[0].rule_name
    
    def test_combined_validator_and_parser(self):
        """Тест комбинации валидаторов и парсеров."""
        @ResponseHandler.handlers(
            Validator.STATUS_CODE().whitelist([200, 201]),
            Validator.HEADERS().has_key("Content-Type"),
            Validator.JSON("$.username").whitelist(["john_doe", "jane_doe"]),
            Validator.JSON("$.age").range(18, 100),
            Parser.JSON("$.age").save_to("parsed_age"),
            Parser.JSON("$.scores[*]").sum().save_to("total_score")
        )
        def test_func():
            return MockResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                _json={
                    "username": "john_doe",
                    "age": 30,
                    "scores": [10, 20, 30]
                },
                _text="OK"
            )
        
        result = test_func()
        assert len(result.validation_data.ERRORS) == 0
        assert result.validation_data.PARSED["parsed_age"] == 30
        assert result.validation_data.PARSED["total_score"] == 60
    
    def test_error_response_structure(self):
        """Тест ошибки - неправильная структура response."""
        @ResponseHandler.handlers(
            Validator.STATUS_CODE().whitelist([200])
        )
        def test_func():
            # Объект без необходимых атрибутов
            class BadResponse:
                pass
            return BadResponse()
        
        with pytest.raises(Exception) as exc_info:
            test_func()
        assert "missing required" in str(exc_info.value).lower()

