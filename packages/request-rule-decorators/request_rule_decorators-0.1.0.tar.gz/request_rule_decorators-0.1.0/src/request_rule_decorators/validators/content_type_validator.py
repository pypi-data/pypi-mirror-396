"""Валидатор для Content-Type заголовка."""

from typing import Literal, Optional, Union

from ..dto import ValidationError
from .base import BaseValidator
from .blacklist_whitelist import Blacklist, Whitelist

# Типы контента для подсказок в IDE
ContentType = Literal[
    # Application types
    "application/json",
    "application/xml",
    "application/xhtml+xml",
    "application/pdf",
    "application/zip",
    "application/gzip",
    "application/x-www-form-urlencoded",
    "application/octet-stream",
    "application/javascript",
    "application/ld+json",
    "application/rss+xml",
    "application/atom+xml",
    "application/x-shockwave-flash",
    "application/vnd.api+json",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.ms-word",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    # Text types
    "text/plain",
    "text/html",
    "text/css",
    "text/javascript",
    "text/csv",
    "text/xml",
    "text/markdown",
    "text/yaml",
    "text/event-stream",
    # Image types
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/svg+xml",
    "image/webp",
    "image/x-icon",
    "image/bmp",
    "image/tiff",
    # Audio types
    "audio/mpeg",
    "audio/ogg",
    "audio/wav",
    "audio/webm",
    "audio/aac",
    # Video types
    "video/mp4",
    "video/webm",
    "video/ogg",
    "video/quicktime",
    "video/x-msvideo",
    # Font types
    "font/woff",
    "font/woff2",
    "font/ttf",
    "font/otf",
    "font/eot",
    # Multipart types
    "multipart/form-data",
    "multipart/byteranges",
    # Other
    "message/http",
    "message/rfc822",
]


class ContentTypeValidator(BaseValidator):
    """Валидатор для проверки Content-Type заголовка."""
    
    def __init__(self, error_key: str | None = None):
        """
        Инициализация валидатора Content-Type.
        
        Args:
            error_key: Ключ ошибки для идентификации конкретного правила
        """
        super().__init__(error_key=error_key)
        self._rule_name = "ContentTypeValidator"
    
    def blacklist(self) -> Blacklist:
        """Возвращает объект Blacklist для создания правил черного списка."""
        return Blacklist(self)
    
    def whitelist(self) -> Whitelist:
        """Возвращает объект Whitelist для создания правил белого списка."""
        return Whitelist(self)
    
    def equals(self, content_type: Union[ContentType, str]) -> "ContentTypeValidator":
        """Проверка, что Content-Type точно равен указанному значению."""
        return self._add_rule("equals", content_type=content_type)
    
    def validate(self, headers: dict) -> tuple[bool, Optional[ValidationError]]:
        """
        Выполняет валидацию Content-Type заголовка.
        
        Args:
            headers: Словарь заголовков для валидации
            
        Returns:
            Tuple[bool, Optional[ValidationError]]: (успешность валидации, ошибка если есть)
        """
        if not self._rules:
            return True, None
        
        # Нормализуем заголовки: приводим ключи к нижнему регистру для сравнения
        normalized_headers = {k.lower(): v for k, v in headers.items()}
        
        # Извлекаем Content-Type
        content_type_key = "content-type"
        if content_type_key not in normalized_headers:
            return False, self._create_error(
                rule_type="exists",
                expected_values=["Content-Type header"],
                received_values=[],
                message="Content-Type header is missing",
            )
        
        content_type = normalized_headers[content_type_key]
        # Content-Type может быть строкой или списком строк
        content_type_value = content_type if isinstance(content_type, str) else (content_type[0] if isinstance(content_type, list) and content_type else "")
        
        # Убираем параметры после точки с запятой (например, charset=utf-8)
        content_type_base = content_type_value.split(";")[0].strip()
        
        for rule in self._rules:
            rule_type = rule["type"]
            
            if rule_type == "blacklist_values":
                if content_type_base in rule["values"]:
                    return False, self._create_error(
                        rule_type="blacklist.values",
                        expected_values=[f"not in {rule['values']}"],
                        received_values=[content_type_base],
                        message=f"Content-Type '{content_type_base}' is in blacklist {rule['values']}",
                    )
            
            elif rule_type == "whitelist_values":
                if content_type_base not in rule["values"]:
                    return False, self._create_error(
                        rule_type="whitelist.values",
                        expected_values=rule["values"],
                        received_values=[content_type_base],
                        message=f"Content-Type '{content_type_base}' is not in whitelist {rule['values']}",
                    )
            
            elif rule_type == "blacklist_words":
                found_words = [word for word in rule["words"] if word.lower() in content_type_base.lower()]
                if found_words:
                    return False, self._create_error(
                        rule_type="blacklist.words",
                        expected_values=[f"not contain words: {rule['words']}"],
                        received_values=[f"contains: {found_words}"],
                        message=f"Content-Type '{content_type_base}' contains forbidden words: {found_words}",
                    )
            
            elif rule_type == "whitelist_words":
                found_words = [word for word in rule["words"] if word.lower() in content_type_base.lower()]
                if not found_words:
                    return False, self._create_error(
                        rule_type="whitelist.words",
                        expected_values=[f"contain at least one word from: {rule['words']}"],
                        received_values=[content_type_base],
                        message=f"Content-Type '{content_type_base}' does not contain any allowed words from {rule['words']}",
                    )
            
            elif rule_type == "blacklist_regex":
                import re
                pattern = rule["pattern"]
                if re.match(pattern, content_type_base):
                    return False, self._create_error(
                        rule_type="blacklist.regex",
                        expected_values=[f"not match pattern '{pattern}'"],
                        received_values=[content_type_base],
                        message=f"Content-Type '{content_type_base}' matches forbidden regex pattern '{pattern}'",
                    )
            
            elif rule_type == "whitelist_regex":
                import re
                pattern = rule["pattern"]
                if not re.match(pattern, content_type_base):
                    return False, self._create_error(
                        rule_type="whitelist.regex",
                        expected_values=[f"match pattern '{pattern}'"],
                        received_values=[content_type_base],
                        message=f"Content-Type '{content_type_base}' does not match required regex pattern '{pattern}'",
                    )
            
            elif rule_type == "equals":
                expected_type = rule["content_type"]
                if content_type_base != expected_type:
                    return False, self._create_error(
                        rule_type="equals",
                        expected_values=[expected_type],
                        received_values=[content_type_base],
                        message=f"Content-Type '{content_type_base}' does not equal '{expected_type}'",
                    )
        
        return True, None

