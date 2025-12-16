"""Request Rule Decorators - библиотека для валидации и парсинга HTTP-ответов."""

# Core classes
from .decorator import ResponseHandler
from .dto import WithValid, ValidationData, ValidationError
from .exceptions import ParserError, RuleExecutionError, ValidationRuleError
from .rules import Parser, Validator

# Validators
from .validators import (
    Blacklist,
    ContentType,
    ContentTypeValidator,
    HeadersValidator,
    HTMLValidator,
    JSONValidator,
    StatusCodeValidator,
    Whitelist,
)

# Parsers
from .parsers import HTMLParser, JSONParser

__version__ = "0.1.0"

__all__ = [
    # Core
    "ResponseHandler",
    "Validator",
    "Parser",
    "WithValid",
    "ValidationData",
    "ValidationError",
    # Exceptions
    "ParserError",
    "RuleExecutionError",
    "ValidationRuleError",
    # Validators
    "JSONValidator",
    "HeadersValidator",
    "StatusCodeValidator",
    "ContentTypeValidator",
    "ContentType",
    "HTMLValidator",
    "Blacklist",
    "Whitelist",
    # Parsers
    "JSONParser",
    "HTMLParser",
]

