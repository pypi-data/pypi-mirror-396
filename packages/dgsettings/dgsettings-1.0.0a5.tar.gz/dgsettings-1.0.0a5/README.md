# dgsettings

Универсальный менеджер конфигураций Python-приложений  
- ✔️ Чтение и авто-перезагрузка YAML/JSON-файлов с поддержкой переменных среды и .env  
- ✔️ Хранение и обновление конфигов из различных источников: файлов, PostgreSQL, Redis  
- ✔️ Плагинная архитектура — легко расширяется под ваши нужды  
- ✔️ Работа с несколькими сервисами (service_name)
- ✔️ Легкая интеграция c любой средой (FastAPI, Celery, классические сервисы, микросервисы)

---

## Возможности

- **Settings**: Основной класс для работы с деревом конфигурации.
- **FileConfigStorage**: Файловое хранение с автоматическим обновлением при изменении.
- **DBConfigStorage**: Встроенная поддержка PostgreSQL и других СУБД через SQLAlchemy, автоматическое создание таблицы.
- **RedisConfigStorage**: Быстрый конфиг через Redis (опционально).
- **check_reload()**: Позволяет легко реализовать "hot reload" настроек сервиса, если источник изменился.

---

## Установка

```bash
pip install dgsettings  # если в PyPI (или копируйте repo)
pip install dgsettings[redis] # для Redis-хранилища
pip install dgsettings[db]  # для работы с БД (Postgres)
```

---

## Пример использования

#### Самый простой вариант: использование файлового слоя

```python
from dgsettings import Settings

settings = Settings(file_="config.yaml", env_file=".env")

db = settings.get("db")
print(db["user"])   # поддерживаются переменные окружения и .env-файлов: db_user: "%PGUSER%"

# Авто-перезагрузка (например, в цикле сервиса)
if settings.check_reload():
    print("Конфиг-файл изменился! Нужно обновить состояние приложения")
```

---

#### Использование с PostgreSQL (DBConfigStorage)

```python
from dgsettings import Settings, DBConfigStorage
from sqlalchemy import create_engine, Table, MetaData

engine = create_engine("postgresql://user:pass@localhost:5432/mydb")

# Автоматически создаём таблицу для хранения конфигов (разделение по service_name)
DBConfigStorage.create_table_if_needed(engine)

metadata = MetaData(bind=engine)
table = Table("app_configs", metadata, autoload_with=engine)

storage = DBConfigStorage(
    session_factory=lambda: engine.connect(),  # или sessionmaker()
    table=table,
    key_column='service_name',
    value_column='config_data',
    service_name='my_service',
    auto_reload=True,     # авто-перезагрузка при обновлении, если есть поле updated_at
    engine=engine
)

settings = Settings(storage=storage)
```

---

#### Использование с Redis (RedisConfigStorage)

```python
from dgsettings import Settings, RedisConfigStorage
import redis

client = redis.Redis(host="localhost")
# Для hot reload желательно указать ts_key
storage = RedisConfigStorage(client, "config:myservice", auto_reload=True, ts_key="config:myservice:ts")
settings = Settings(storage=storage)
```

---

## API кратко

- `Settings(file_="...", env_file="...")` — создание и авто-парсинг конфига.
- `parse(file_)` — парсинг файла (JSON/YAML).
- `save(file_)` — сохранить текущий конфиг в файл.
- `get(key, default=None)` — получить значение по ключу.
- `set(obj)` — установить словарь настроек.
- `check_reload()` — если источник изменился, перезагружает, возвращает True.
- `convert("config.yaml", "config.json", use_yaml=False)` — переводит между форматами JSON/YAML.

---

## Переменные среды и .env

Любая строка вида `$VARNAME$` или `${VARNAME}` в конфиге подменяется на значение переменной среды или из файла .env

**.env:**
```
PGUSER=postgres
PGPASSWORD=secret
```

**config.yaml:**
```yaml
db_user: "$PGUSER$"
db_pass: "${PGPASSWORD}"
```

---

## Автосоздание таблицы PostgreSQL

- Таблица создаётся автоматически при первом запуске через `DBConfigStorage.create_table_if_needed(engine)`.
- В таблице выделяются поля `service_name` (имя сервиса), `config_data` (JSON), `updated_at` (авто-метка времени).

---

## Необязательные зависимости

- Для работы с файлами (`FileConfigStorage`) — только PyYAML/JSON.
- Для работы с БД — SQLAlchemy и psycopg2/asyncpg и т.п.
- Для работы с Redis — пакет redis.

Если зависимости не установлены, соответствующий storage будет недоступен, но Settings и файловая работа будут работать всегда.

---

## Пример сервисной интеграции

```python
# В потоке/таймере/worker-e проверяем:
if settings.check_reload():
    my_service.reload_settings()
```

---

## Расширяемость

Вы можете реализовать свой storage (например, через S3, Consul, etcd).
Просто реализуйте абстрактный класс ConfigStorageBase (`load`, `save`, `has_changed`, `supports_auto_reload`).

---

## Contributing

Пулреквесты, багрепорты и обсуждения приветствуются!

---

## Лицензия

MIT

---

**Авторы:**  
["Roman Rasputin"]

---

**Пример быстрого старта, документация по методам и архитектуре — см. исходный код либо открывайте issues!**