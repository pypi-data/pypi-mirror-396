# Request Rule Decorators

Библиотека для валидации и парсинга HTTP-ответов с использованием декораторов.

## Установка

```bash
pip install -e .
```

Для разработки с тестами:

```bash
pip install -e ".[dev]"
```

## Быстрый старт

```python
from request_rule_decorators import ResponseHandler, Validator, Parser

@ResponseHandler.handlers(
    Validator.STATUS_CODE().whitelist([200, 201]),
    Validator.CONTENT_TYPE().equals("application/json"),
    Validator.JSON("$.username").whitelist().values(["john_doe"]),
    Validator.JSON("$.age").range(18, 100),
    Parser.JSON("$.age").save_to("parsed_age"),
)
async def my_function():
    # Ваша функция, возвращающая response объект
    return response

result = await my_function()
# result.response - оригинальный response
# result.valid.ERRORS - список ошибок валидации
# result.valid.PARSED - распарсенные данные
# result.is_valid() - проверка валидации
```

## Документация

Подробная документация доступна в файле [DOCS.md](DOCS.md)

## Запуск тестов

```bash
pytest tests/
```

## Запуск демонстрационного примера

```bash
python demo.py
```

## Структура проекта

- `request_rule_decorators/` - основной пакет библиотеки
  - `dto.py` - DTO классы (ValidationError, ValidationData, WithValid)
  - `decorator.py` - декоратор ResponseHandler
  - `rules.py` - фабрика правил (Validator, Parser)
  - `exceptions.py` - кастомные исключения
  - `validators/` - валидаторы (JSON, Headers, StatusCode, ContentType, HTML)
  - `parsers/` - парсеры (JSON, HTML)
- `tests/` - тесты
- `demo.py` - демонстрационный файл
- `DOCS.md` - подробная документация

