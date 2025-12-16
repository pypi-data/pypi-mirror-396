"""Фабрика для создания правил валидации и парсинга."""

from .parsers import HTMLParser, JSONParser
from .validators import (
    ContentTypeValidator,
    HeadersValidator,
    HTMLValidator,
    JSONValidator,
    StatusCodeValidator,
)


class Validator:
    """Фабрика для создания валидаторов."""
    
    @staticmethod
    def JSON(json_path: str, error_key: str | None = None) -> JSONValidator:
        """
        Создает JSON валидатор.
        
        Args:
            json_path: JSONPath выражение для извлечения значения
            error_key: Ключ ошибки для идентификации конкретного правила
            
        Returns:
            JSONValidator экземпляр
        """
        return JSONValidator(json_path, error_key=error_key)
    
    @staticmethod
    def HEADERS(error_key: str | None = None) -> HeadersValidator:
        """
        Создает валидатор заголовков.
        
        Args:
            error_key: Ключ ошибки для идентификации конкретного правила
        
        Returns:
            HeadersValidator экземпляр
        """
        return HeadersValidator(error_key=error_key)
    
    @staticmethod
    def STATUS_CODE(error_key: str | None = None) -> StatusCodeValidator:
        """
        Создает валидатор статус-кода.
        
        Args:
            error_key: Ключ ошибки для идентификации конкретного правила
        
        Returns:
            StatusCodeValidator экземпляр
        """
        return StatusCodeValidator(error_key=error_key)
    
    @staticmethod
    def CONTENT_TYPE(error_key: str | None = None) -> ContentTypeValidator:
        """
        Создает валидатор Content-Type заголовка.
        
        Args:
            error_key: Ключ ошибки для идентификации конкретного правила
        
        Returns:
            ContentTypeValidator экземпляр
        """
        return ContentTypeValidator(error_key=error_key)
    
    @staticmethod
    def HTML(xpath: str, error_key: str | None = None) -> HTMLValidator:
        """
        Создает HTML валидатор.
        
        Args:
            xpath: XPath выражение для извлечения значения
            error_key: Ключ ошибки для идентификации конкретного правила
            
        Returns:
            HTMLValidator экземпляр
        """
        return HTMLValidator(xpath, error_key=error_key)


class Parser:
    """Фабрика для создания парсеров."""
    
    @staticmethod
    def JSON(json_path: str) -> JSONParser:
        """
        Создает JSON парсер.
        
        Args:
            json_path: JSONPath выражение для извлечения значения
            
        Returns:
            JSONParser экземпляр
        """
        return JSONParser(json_path)
    
    @staticmethod
    def HTML(xpath: str) -> HTMLParser:
        """
        Создает HTML парсер.
        
        Args:
            xpath: XPath выражение для извлечения значения
            
        Returns:
            HTMLParser экземпляр
        """
        return HTMLParser(xpath)

