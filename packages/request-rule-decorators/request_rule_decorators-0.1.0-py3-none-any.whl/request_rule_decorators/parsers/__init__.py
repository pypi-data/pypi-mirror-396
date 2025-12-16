"""Парсеры для извлечения и обработки данных из HTTP-ответов."""

from .json_parser import JSONParser
from .html_parser import HTMLParser

__all__ = [
    "JSONParser",
    "HTMLParser",
]

