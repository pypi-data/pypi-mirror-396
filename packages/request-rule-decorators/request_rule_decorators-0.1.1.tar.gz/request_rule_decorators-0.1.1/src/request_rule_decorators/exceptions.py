"""Кастомные исключения для библиотеки."""


class ValidationRuleError(Exception):
    """Базовое исключение для ошибок валидации правил."""
    pass


class ParserError(Exception):
    """Исключение для ошибок парсинга."""
    pass


class RuleExecutionError(Exception):
    """Исключение для ошибок выполнения правил."""
    pass

