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


# Документация библиотеки request-rule-decorators

## Содержание

1. [Введение](#введение)
2. [Быстрый старт](#быстрый-старт)
3. [Валидаторы](#валидаторы)
   - [JSONValidator](#jsonvalidator)
   - [HeadersValidator](#headersvalidator)
   - [StatusCodeValidator](#statuscodevalidator)
   - [ContentTypeValidator](#contenttypevalidator)
   - [HTMLValidator](#htmlvalidator)
4. [Парсеры](#парсеры)
   - [JSONParser](#jsonparser)
   - [HTMLParser](#htmlparser)
5. [Blacklist и Whitelist](#blacklist-и-whitelist)
6. [Примеры использования](#примеры-использования)

---

## Введение

Библиотека `request-rule-decorators` предназначена для валидации и парсинга HTTP-ответов с использованием декораторов. Она позволяет легко проверять различные части ответа (JSON, заголовки, статус-код, Content-Type, HTML) и извлекать данные с помощью простого и понятного API.

---

## Быстрый старт

```python
from request_rule_decorators import ResponseHandler, Validator, Parser

@ResponseHandler.handlers(
    Validator.STATUS_CODE().whitelist([200, 201]),
    Validator.CONTENT_TYPE().equals("application/json"),
    Validator.JSON("$.username").whitelist().values(["john_doe", "jane_doe"]),
    Parser.JSON("$.age").save_to("parsed_age"),
)
async def my_function():
    # Ваша функция, возвращающая response объект
    return response

result = await my_function()
print(result.is_valid())  # True/False
print(result.valid.ERRORS)  # Список ошибок
print(result.valid.PARSED)  # Распарсенные данные
```

---

## Валидаторы

### JSONValidator

Валидатор для проверки JSON данных с использованием JSONPath выражений.

**Создание:**
```python
Validator.JSON(json_path: str, error_key: str | None = None) -> JSONValidator
```

**Параметры:**
- `json_path` - JSONPath выражение для извлечения значения (например, `"$.username"`, `"$[*].id"`)
- `error_key` - Опциональный ключ ошибки для идентификации конкретного правила

#### Методы валидации

##### `blacklist() -> Blacklist`
Возвращает объект `Blacklist` для создания правил черного списка.

**Пример:**
```python
Validator.JSON("$.status").blacklist().values(["error", "failed"])
```

##### `whitelist() -> Whitelist`
Возвращает объект `Whitelist` для создания правил белого списка.

**Пример:**
```python
Validator.JSON("$.status").whitelist().values(["active", "pending"])
```

##### `range(min_val: Union[int, float], max_val: Union[int, float]) -> JSONValidator`
Проверяет, что значение находится в заданном диапазоне.

**Параметры:**
- `min_val` - Минимальное значение
- `max_val` - Максимальное значение

**Пример:**
```python
Validator.JSON("$.age").range(18, 100)
```

##### `regex(pattern: str) -> JSONValidator`
Проверяет значение по регулярному выражению.

**Параметры:**
- `pattern` - Регулярное выражение

**Пример:**
```python
Validator.JSON("$.email").regex(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
```

##### `exists() -> JSONValidator`
Проверяет существование пути в JSON.

**Пример:**
```python
Validator.JSON("$.username").exists()
```

##### `type(expected_type: Type) -> JSONValidator`
Проверяет тип значения.

**Параметры:**
- `expected_type` - Ожидаемый тип (например, `int`, `str`, `dict`)

**Пример:**
```python
Validator.JSON("$.age").type(int)
```

#### Примеры использования

```python
# Проверка нескольких правил
Validator.JSON("$.user.age").range(18, 100).type(int)

# Проверка массива
Validator.JSON("$[*].id").type(int).range(1, 100)

# Проверка с ERROR_KEY
Validator.JSON("$.status", error_key="BAN").whitelist().values(["active"])
```

---

### HeadersValidator

Валидатор для проверки HTTP заголовков.

**Создание:**
```python
Validator.HEADERS(error_key: str | None = None) -> HeadersValidator
```

**Параметры:**
- `error_key` - Опциональный ключ ошибки для идентификации конкретного правила

#### Методы валидации

##### `has_key(key: str) -> HeadersValidator`
Проверяет наличие ключа в заголовках.

**Параметры:**
- `key` - Имя заголовка для проверки

**Пример:**
```python
Validator.HEADERS().has_key("Content-Type")
```

##### `missing_key(key: str) -> HeadersValidator`
Проверяет отсутствие ключа в заголовках.

**Параметры:**
- `key` - Имя заголовка, который должен отсутствовать

**Пример:**
```python
Validator.HEADERS().missing_key("X-Secret-Header")
```

##### `blacklist(key: str, values: List[str]) -> HeadersValidator`
Проверяет, что значение ключа не в черном списке.

**Параметры:**
- `key` - Имя заголовка
- `values` - Список запрещенных значений

**Пример:**
```python
Validator.HEADERS().blacklist("X-Status", ["error", "failed"])
```

##### `whitelist(key: str, values: List[str]) -> HeadersValidator`
Проверяет, что значение ключа в белом списке.

**Параметры:**
- `key` - Имя заголовка
- `values` - Список разрешенных значений

**Пример:**
```python
Validator.HEADERS().whitelist("Content-Type", ["application/json", "text/html"])
```

##### `regex(key: str, pattern: str) -> HeadersValidator`
Проверяет значение ключа по регулярному выражению.

**Параметры:**
- `key` - Имя заголовка
- `pattern` - Регулярное выражение

**Пример:**
```python
Validator.HEADERS().regex("Content-Type", r"^application/.*$")
```

#### Примеры использования

```python
# Проверка наличия нескольких заголовков
Validator.HEADERS().has_key("Content-Type").has_key("Authorization")

# Комбинация проверок
Validator.HEADERS().has_key("Content-Type").whitelist("Content-Type", ["application/json"])
```

---

### StatusCodeValidator

Валидатор для проверки HTTP статус-кода.

**Создание:**
```python
Validator.STATUS_CODE(error_key: str | None = None) -> StatusCodeValidator
```

**Параметры:**
- `error_key` - Опциональный ключ ошибки для идентификации конкретного правила

#### Методы валидации

##### `blacklist(codes: List[int]) -> StatusCodeValidator`
Проверяет, что статус-код не в черном списке.

**Параметры:**
- `codes` - Список запрещенных статус-кодов

**Пример:**
```python
Validator.STATUS_CODE().blacklist([400, 401, 403, 404, 500])
```

##### `whitelist(codes: List[int]) -> StatusCodeValidator`
Проверяет, что статус-код в белом списке.

**Параметры:**
- `codes` - Список разрешенных статус-кодов

**Пример:**
```python
Validator.STATUS_CODE().whitelist([200, 201, 204])
```

#### Примеры использования

```python
# Только успешные коды
Validator.STATUS_CODE().whitelist([200, 201, 202, 204])

# Запрет ошибок клиента и сервера
Validator.STATUS_CODE().blacklist([400, 401, 403, 404, 500, 502, 503, 504])
```

---

### ContentTypeValidator

Валидатор для проверки заголовка Content-Type с поддержкой Literal типов для автодополнения в IDE.

**Создание:**
```python
Validator.CONTENT_TYPE(error_key: str | None = None) -> ContentTypeValidator
```

**Параметры:**
- `error_key` - Опциональный ключ ошибки для идентификации конкретного правила

#### Методы валидации

##### `blacklist() -> Blacklist`
Возвращает объект `Blacklist` для создания правил черного списка типов контента.

**Пример:**
```python
Validator.CONTENT_TYPE().blacklist().values(["text/plain", "application/xml"])
```

##### `whitelist() -> Whitelist`
Возвращает объект `Whitelist` для создания правил белого списка типов контента.

**Пример:**
```python
Validator.CONTENT_TYPE().whitelist().values(["application/json", "text/html"])
```

##### `equals(content_type: Union[ContentType, str]) -> ContentTypeValidator`
Проверяет, что Content-Type точно равен указанному значению.

**Параметры:**
- `content_type` - Тип контента (с автодополнением в IDE: `"application/json"`, `"text/html"` и т.д.)

**Пример:**
```python
Validator.CONTENT_TYPE().equals("application/json")
```

#### Поддерживаемые типы контента

Библиотека поддерживает следующие типы контента с автодополнением в IDE:

**Application:**
- `application/json`, `application/xml`, `application/pdf`, `application/zip`, `application/javascript` и др.

**Text:**
- `text/plain`, `text/html`, `text/css`, `text/javascript`, `text/csv`, `text/markdown` и др.

**Image:**
- `image/jpeg`, `image/png`, `image/gif`, `image/svg+xml`, `image/webp` и др.

**Audio/Video:**
- `audio/mpeg`, `video/mp4`, `video/webm` и др.

**Font:**
- `font/woff`, `font/woff2`, `font/ttf` и др.

**Multipart:**
- `multipart/form-data`, `multipart/byteranges`

#### Примеры использования

```python
# Точное совпадение (с автодополнением)
Validator.CONTENT_TYPE().equals("application/json")

# Белый список типов
Validator.CONTENT_TYPE().whitelist().values(["application/json", "text/html"])

# Черный список типов
Validator.CONTENT_TYPE().blacklist().values(["text/plain"])
```

---

### HTMLValidator

Валидатор для проверки HTML данных с использованием XPath выражений.

**Создание:**
```python
Validator.HTML(xpath: str, error_key: str | None = None) -> HTMLValidator
```

**Параметры:**
- `xpath` - XPath выражение для извлечения значения (например, `"//div[@class='content']"`, `"//a/@href"`)
- `error_key` - Опциональный ключ ошибки для идентификации конкретного правила

#### Методы валидации

Все методы аналогичны `JSONValidator`:

- `blacklist() -> Blacklist` - Черный список значений
- `whitelist() -> Whitelist` - Белый список значений
- `range(min_val, max_val)` - Проверка диапазона
- `regex(pattern)` - Проверка по регулярному выражению
- `exists()` - Проверка существования элемента
- `type(expected_type)` - Проверка типа

#### Примеры использования

```python
# Проверка текста элемента
Validator.HTML("//div[@class='status']/text()").whitelist().values(["active", "pending"])

# Проверка атрибута
Validator.HTML("//a/@href").regex(r"^https?://.*$")

# Проверка количества элементов
Validator.HTML("//div[@class='item']").exists()
```

---

## Парсеры

### JSONParser

Парсер для извлечения и обработки JSON данных с использованием JSONPath выражений.

**Создание:**
```python
Parser.JSON(json_path: str) -> JSONParser
```

**Параметры:**
- `json_path` - JSONPath выражение для извлечения значения

#### Методы парсинга

##### `save_to(key: str) -> JSONParser`
Указывает ключ для сохранения результата в словарь `PARSED`.

**Параметры:**
- `key` - Ключ для сохранения результата

**Пример:**
```python
Parser.JSON("$.age").save_to("parsed_age")
```

##### `regex(pattern: str) -> JSONParser`
Применяет регулярное выражение к значению.

**Параметры:**
- `pattern` - Регулярное выражение

**Пример:**
```python
Parser.JSON("$.email").regex(r"^([a-zA-Z0-9._%+-]+)@")
```

##### `sum() -> JSONParser`
Суммирует числовые значения (для списков чисел и списков словарей).

**Пример:**
```python
Parser.JSON("$.numbers").sum()
Parser.JSON("$.data[*]").extract_field("traffic").sum()
```

##### `average() -> JSONParser`
Вычисляет среднее значение (для списков чисел и списков словарей).

**Пример:**
```python
Parser.JSON("$.scores").average()
```

##### `max() -> JSONParser`
Находит максимальное значение (для списков чисел и списков словарей).

**Пример:**
```python
Parser.JSON("$.prices").max()
```

##### `min() -> JSONParser`
Находит минимальное значение (для списков чисел и списков словарей).

**Пример:**
```python
Parser.JSON("$.prices").min()
```

##### `count() -> JSONParser`
Подсчитывает количество элементов (для списков).

**Пример:**
```python
Parser.JSON("$[*].id").count()
```

##### `extract_field(field: str) -> JSONParser`
Извлекает поле из списка словарей.

**Параметры:**
- `field` - Имя поля для извлечения

**Пример:**
```python
Parser.JSON("$.data[*]").extract_field("traffic")
```

#### Примеры использования

```python
# Простое извлечение
Parser.JSON("$.username").save_to("username")

# Извлечение и суммирование
Parser.JSON("$.data[*].traffic").extract_field("traffic").sum().save_to("total_traffic")

# Подсчет элементов
Parser.JSON("$[*].id").count().save_to("user_count")

# Комбинация операций
Parser.JSON("$.items[*].price").max().save_to("max_price")
```

---

### HTMLParser

Парсер для извлечения и обработки HTML данных с использованием XPath выражений.

**Создание:**
```python
Parser.HTML(xpath: str) -> HTMLParser
```

**Параметры:**
- `xpath` - XPath выражение для извлечения значения

#### Методы парсинга

Все методы аналогичны `JSONParser`:

- `save_to(key)` - Сохранение результата
- `regex(pattern)` - Применение regex
- `sum()` - Суммирование
- `average()` - Среднее значение
- `max()` - Максимум
- `min()` - Минимум
- `count()` - Подсчет элементов
- `extract_field(field)` - Извлечение поля из словарей

#### Примеры использования

```python
# Извлечение текста
Parser.HTML("//div[@class='title']/text()").save_to("title")

# Извлечение всех ссылок
Parser.HTML("//a/@href").save_to("links")

# Подсчет элементов
Parser.HTML("//div[@class='item']").count().save_to("item_count")
```

---

## Blacklist и Whitelist

Объекты `Blacklist` и `Whitelist` используются для создания правил валидации с различными типами проверок.

### Blacklist

Объект для создания правил черного списка.

#### Методы

##### `values(values: List[Any]) -> BaseValidator`
Проверяет, что значение не в черном списке значений.

**Параметры:**
- `values` - Список запрещенных значений

**Пример:**
```python
Validator.JSON("$.status").blacklist().values(["error", "failed"])
```

##### `words(words: List[str]) -> BaseValidator`
Проверяет, что строка не содержит ни одного слова из черного списка.

**Параметры:**
- `words` - Список запрещенных слов

**Пример:**
```python
Validator.JSON("$.description").blacklist().words(["spam", "forbidden"])
```

##### `regex(pattern: str) -> BaseValidator`
Проверяет, что значение не соответствует регулярному выражению.

**Параметры:**
- `pattern` - Запрещенный regex паттерн

**Пример:**
```python
Validator.JSON("$.url").blacklist().regex(r".*spam.*")
```

### Whitelist

Объект для создания правил белого списка.

#### Методы

##### `values(values: List[Any]) -> BaseValidator`
Проверяет, что значение в белом списке значений.

**Параметры:**
- `values` - Список разрешенных значений

**Пример:**
```python
Validator.JSON("$.status").whitelist().values(["active", "pending"])
```

##### `words(words: List[str]) -> BaseValidator`
Проверяет, что строка содержит хотя бы одно слово из белого списка.

**Параметры:**
- `words` - Список разрешенных слов

**Пример:**
```python
Validator.JSON("$.category").whitelist().words(["tech", "science"])
```

##### `regex(pattern: str) -> BaseValidator`
Проверяет, что значение соответствует регулярному выражению.

**Параметры:**
- `pattern` - Требуемый regex паттерн

**Пример:**
```python
Validator.JSON("$.email").whitelist().regex(r"^.*@example\.com$")
```

---

## Примеры использования

### Пример 1: Валидация API ответа

```python
@ResponseHandler.handlers(
    Validator.STATUS_CODE().whitelist([200, 201]),
    Validator.CONTENT_TYPE().equals("application/json"),
    Validator.JSON("$.status").whitelist().values(["success"]),
    Validator.JSON("$.data[*].id").type(int).range(1, 1000),
    Validator.JSON("$.data[*].email").regex(r"^[^@]+@[^@]+\.[^@]+$"),
)
async def fetch_users():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/users")
        return response

result = await fetch_users()
if result.is_valid():
    print("Валидация пройдена!")
else:
    for error in result.valid.ERRORS:
        print(f"Ошибка: {error.message}")
```

### Пример 2: Парсинг данных

```python
@ResponseHandler.handlers(
    Validator.STATUS_CODE().whitelist([200]),
    Parser.JSON("$[*].id").count().save_to("total_users"),
    Parser.JSON("$[*].age").average().save_to("avg_age"),
    Parser.JSON("$[*].salary").max().save_to("max_salary"),
    Parser.JSON("$[*].transactions[*]").extract_field("amount").sum().save_to("total_amount"),
)
async def analyze_data():
    # Ваша функция
    return response

result = await analyze_data()
print(f"Всего пользователей: {result.valid.PARSED['total_users']}")
print(f"Средний возраст: {result.valid.PARSED['avg_age']}")
print(f"Максимальная зарплата: {result.valid.PARSED['max_salary']}")
print(f"Общая сумма транзакций: {result.valid.PARSED['total_amount']}")
```

### Пример 3: Использование ERROR_KEY

```python
@ResponseHandler.handlers(
    Validator.STATUS_CODE().whitelist([200]),
    Validator.JSON("$.status", error_key="BAN").whitelist().values(["active"]),
    Validator.JSON("$.age", error_key="AGE_ERROR").range(18, 100),
)
async def check_user():
    return response

result = await check_user()

# Проверка конкретной ошибки
if result.has_error("BAN"):
    print("Пользователь забанен!")
if result.has_error("AGE_ERROR"):
    print("Ошибка возраста!")
```

### Пример 4: Комплексная валидация

```python
@ResponseHandler.handlers(
    # Статус и заголовки
    Validator.STATUS_CODE().whitelist([200, 201]),
    Validator.CONTENT_TYPE().equals("application/json"),
    Validator.HEADERS().has_key("X-Request-ID"),
    
    # Валидация JSON структуры
    Validator.JSON("$.data").exists(),
    Validator.JSON("$.data[*].id").type(int),
    Validator.JSON("$.data[*].name").exists(),
    Validator.JSON("$.data[*].email").regex(r"^[^@]+@[^@]+\.[^@]+$"),
    
    # Проверка на запрещенные слова
    Validator.JSON("$.data[*].description").blacklist().words(["spam", "forbidden"]),
    
    # Парсинг данных
    Parser.JSON("$.data[*].id").count().save_to("count"),
    Parser.JSON("$.data[*].score").average().save_to("avg_score"),
)
async def complex_validation():
    return response
```

---

## Дополнительная информация

### WithValid объект

Декоратор возвращает объект `WithValid[T]`, который содержит:

- `response: T` - Оригинальный response объект
- `valid: ValidationData` - Данные валидации с ошибками и распарсенными данными

#### Методы

- `is_valid() -> bool` - Проверяет, есть ли ошибки валидации
- `has_error(error_key: str) -> bool` - Проверяет наличие конкретной ошибки по ERROR_KEY
- `__repr__()` - Возвращает строковое представление со всеми ошибками

### ValidationData

Объект содержит:

- `ACTION: Optional[str]` - Действие (опционально)
- `ERRORS: List[ValidationError]` - Список ошибок валидации
- `PARSED: Dict[str, Any]` - Распарсенные данные
- `ATTEMPTS: int` - Счетчик попыток

### ValidationError

Каждая ошибка содержит:

- `rule_name: str` - Имя правила, на котором произошла ошибка
- `error_key: Optional[str]` - Ключ ошибки для идентификации
- `expected_values: List[Any]` - Ожидаемые значения
- `received_values: List[Any]` - Полученные значения
- `attempts: int` - Количество попыток
- `max_attempts: int` - Максимальное количество попыток
- `message: str` - Сообщение об ошибке

---

## Поддержка

Для вопросов и предложений создайте issue в репозитории проекта.


