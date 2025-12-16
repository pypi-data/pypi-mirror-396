"""Декоратор для обработки HTTP-ответов с валидацией и парсингом."""

import inspect
from functools import wraps
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar, overload

from .dto import ValidationData, ValidationError, WithValid
from .exceptions import ParserError, RuleExecutionError
from .parsers.base import BaseParser
from .validators.base import BaseValidator

P = ParamSpec("P")
T = TypeVar("T")


class ResponseHandler:
    """Класс для обработки HTTP-ответов с валидацией и парсингом."""
    
    @staticmethod
    @overload
    def handlers(
        *rules: BaseValidator | BaseParser
    ) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[WithValid[T]]]]:
        ...
    
    @staticmethod
    @overload
    def handlers(
        *rules: BaseValidator | BaseParser
    ) -> Callable[[Callable[P, T]], Callable[P, WithValid[T]]]:
        ...
    
    @staticmethod
    def handlers(*rules: BaseValidator | BaseParser):
        """
        Декоратор для обработки HTTP-ответов с применением правил валидации и парсинга.
        
        Args:
            *rules: Правила валидации и парсинга
            
        Returns:
            Декорированная функция, возвращающая WithValid[T]
        """
        def decorator(func: Callable[P, T] | Callable[P, Awaitable[T]]) -> Callable[P, WithValid[T]] | Callable[P, Awaitable[WithValid[T]]]:
            is_async = inspect.iscoroutinefunction(func)
            
            if is_async:
                @wraps(func)
                async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> WithValid[T]:
                    try:
                        response = await func(*args, **kwargs)  # type: ignore
                    except Exception as e:
                        raise RuleExecutionError(f"Function execution failed: {str(e)}") from e
                    
                    return ResponseHandler._process_response(response, rules)
                
                return async_wrapper  # type: ignore
            else:
                @wraps(func)
                def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> WithValid[T]:
                    try:
                        response = func(*args, **kwargs)
                    except Exception as e:
                        raise RuleExecutionError(f"Function execution failed: {str(e)}") from e
                    
                    return ResponseHandler._process_response(response, rules)
                
                return sync_wrapper  # type: ignore
        
        return decorator  # type: ignore
    
    @staticmethod
    def _process_response(response: Any, rules: tuple[BaseValidator | BaseParser, ...]) -> WithValid[Any]:
        """
        Обрабатывает response объект, применяя правила валидации и парсинга.
        
        Args:
            response: Response объект
            rules: Правила валидации и парсинга
            
        Returns:
            WithValid с результатами валидации и парсинга
        """
        validation_data = ValidationData()
        
        # Проверяем наличие необходимых атрибутов/методов
        ResponseHandler._validate_response_structure(response)
        
        # Извлекаем данные из response
        json_data = ResponseHandler._get_json(response)
        html_data = ResponseHandler._get_html(response)
        headers = ResponseHandler._get_headers(response)
        status_code = ResponseHandler._get_status_code(response)
        
        # Импортируем конкретные классы для проверки типов
        from .validators import (
            ContentTypeValidator,
            HTMLValidator,
            JSONValidator,
            HeadersValidator,
            StatusCodeValidator,
        )
        from .parsers import HTMLParser, JSONParser
        
        # Применяем правила
        for rule in rules:
            try:
                if isinstance(rule, BaseValidator):
                    # Применяем валидатор
                    if isinstance(rule, JSONValidator):
                        is_valid, error = rule.validate(json_data)
                        if not is_valid and error:
                            validation_data.ERRORS.append(error)
                    elif isinstance(rule, HTMLValidator):
                        is_valid, error = rule.validate(html_data)
                        if not is_valid and error:
                            validation_data.ERRORS.append(error)
                    elif isinstance(rule, HeadersValidator):
                        is_valid, error = rule.validate(headers)
                        if not is_valid and error:
                            validation_data.ERRORS.append(error)
                    elif isinstance(rule, ContentTypeValidator):
                        is_valid, error = rule.validate(headers)
                        if not is_valid and error:
                            validation_data.ERRORS.append(error)
                    elif isinstance(rule, StatusCodeValidator):
                        is_valid, error = rule.validate(status_code)
                        if not is_valid and error:
                            validation_data.ERRORS.append(error)
                    else:
                        raise RuleExecutionError(f"Unknown validator type: {rule.__class__.__name__}")
                
                elif isinstance(rule, BaseParser):
                    # Применяем парсер
                    if isinstance(rule, JSONParser):
                        parsed_value = rule.parse(json_data)
                        # Сохраняем результат в PARSED словарь
                        save_key = rule._save_key or f"parsed_{len(validation_data.PARSED)}"
                        validation_data.PARSED[save_key] = parsed_value
                    elif isinstance(rule, HTMLParser):
                        parsed_value = rule.parse(html_data)
                        # Сохраняем результат в PARSED словарь
                        save_key = rule._save_key or f"parsed_{len(validation_data.PARSED)}"
                        validation_data.PARSED[save_key] = parsed_value
                    else:
                        raise RuleExecutionError(f"Unknown parser type: {rule.__class__.__name__}")
                
            except ParserError as e:
                validation_data.ERRORS.append(
                    ValidationError(
                        rule_name=rule.__class__.__name__,
                        expected_values=[],
                        received_values=[],
                        message=f"Parser error: {str(e)}",
                    )
                )
            except Exception as e:
                validation_data.ERRORS.append(
                    ValidationError(
                        rule_name=rule.__class__.__name__,
                        expected_values=[],
                        received_values=[],
                        message=f"Rule execution error: {str(e)}",
                    )
                )
        
        return WithValid(response=response, valid=validation_data)
    
    @staticmethod
    def _validate_response_structure(response: Any) -> None:
        """Проверяет наличие необходимых атрибутов/методов в response объекте."""
        required_attrs = ["status_code", "headers"]
        required_methods = ["json", "text"]
        
        for attr in required_attrs:
            if not hasattr(response, attr):
                raise RuleExecutionError(f"Response object missing required attribute: {attr}")
        
        for method in required_methods:
            if not (hasattr(response, method) and callable(getattr(response, method, None))):
                # Проверяем, может быть это свойство
                if not hasattr(response, method):
                    raise RuleExecutionError(f"Response object missing required method/property: {method}")
    
    @staticmethod
    def _get_json(response: Any) -> dict | list:
        """Извлекает JSON данные из response объекта."""
        json_method = getattr(response, "json", None)
        if callable(json_method):
            json_data = json_method()
        else:
            json_data = json_method
        
        if json_data is None:
            return {}
        
        # Поддерживаем как dict, так и list
        if not isinstance(json_data, (dict, list)):
            raise RuleExecutionError(f"Response.json() must return dict or list, got {type(json_data).__name__}")
        
        return json_data
    
    @staticmethod
    def _get_headers(response: Any) -> dict:
        """Извлекает заголовки из response объекта."""
        headers = getattr(response, "headers", None)
        
        if headers is None:
            return {}
        
        # Если headers - это объект с методами (как в httpx), преобразуем в dict
        if hasattr(headers, "items"):
            return dict(headers.items())
        
        if isinstance(headers, dict):
            return headers
        
        raise RuleExecutionError(f"Response.headers must be dict or dict-like, got {type(headers).__name__}")
    
    @staticmethod
    def _get_status_code(response: Any) -> int:
        """Извлекает статус-код из response объекта."""
        status_code = getattr(response, "status_code", None)
        
        if status_code is None:
            raise RuleExecutionError("Response.status_code is missing")
        
        if not isinstance(status_code, int):
            raise RuleExecutionError(f"Response.status_code must be int, got {type(status_code).__name__}")
        
        return status_code
    
    @staticmethod
    def _get_html(response: Any) -> str | bytes:
        """Извлекает HTML данные из response объекта."""
        text_method = getattr(response, "text", None)
        if callable(text_method):
            html_data = text_method()
        else:
            html_data = text_method
        
        if html_data is None:
            return ""
        
        # Поддерживаем как str, так и bytes
        if isinstance(html_data, (str, bytes)):
            return html_data
        
        # Пытаемся преобразовать в строку
        try:
            return str(html_data)
        except Exception as e:
            raise RuleExecutionError(f"Response.text must return str or bytes, got {type(html_data).__name__}: {str(e)}")

