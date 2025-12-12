import os
import sys
import logging
from typing import Union, Optional
from copy import deepcopy
from datetime import datetime


try:
    from dotenv import load_dotenv, dotenv_values
    _dotenv_available = True
except ImportError:
    _dotenv_available = False


# импорт хранилищ
from .storage import ConfigStorageBase
from .file_storage import FileConfigStorage

class Settings:
    """
    Класс-конфигуратор с поддержкой разных слоёв хранения,
    авто-отслеживанием изменений файлового слоя и подстановкой переменных среды/.env.
    """

    parse_settings_cnt = 0

    def __init__(self,
                 file_: Optional[str] = None,
                 encoding: str = 'utf-8',
                 use_yaml: bool = True,
                 storage: Optional[ConfigStorageBase] = None,
                 env_file: Optional[str] = None,
                 logger: Optional[logging.Logger] = None,
                 **kwargs):
        """
        :param file_: путь к файлу с конфигом (если не указан storage)
        :param use_yaml: формат файла (True - yaml, False - json)
        :param storage: объект класса ConfigStorageBase
        :param env_file: имя .env-файла (будут применены значения переменных)
        :param logger: использовать свой логгер
        """
        self.logger = logger or logging.getLogger('dgsettings')
        self.settings: dict = {}
        self.env_vars = {}

        if storage is not None:
            self.storage = storage
        elif file_:
            self.storage = FileConfigStorage(file_, use_yaml=use_yaml, encoding=encoding)
        else:
            raise ValueError("Either file_ or storage must be specified!")

        # Если .env-файл — подгружаем (требует python-dotenv)
        if env_file and _dotenv_available:
            load_dotenv(env_file)
            self.env_vars = dotenv_values(env_file)
            self.logger.debug(f"Loaded env vars from {env_file}")

        self.reload()

    def _substitute_env_vars(self, value: str) -> str:
        import re

        if not isinstance(value, str) or ('$' not in value and 'getenv' not in value):
            return value
        pattern = re.compile(
            r'\$(\w+)\$|'  # $VAR$
            r'\$\{(\w+)\}|'  # ${VAR}
            r'\s*getenv\s+[\'"]?([\w\d_]+)[\'"]?\s*',  # [[ getenv "VAR" ]]
            re.IGNORECASE,
        )

        def replace_var(match):
            env_key = match.group(1) or match.group(2) or match.group(3)
            return (
                    self.env_vars.get(env_key)
                    or os.environ.get(env_key)
                    or match.group(0)
            )

        return pattern.sub(replace_var, value)

    def _substitute_env_in_settings(self, d: dict):
        for k, v in d.items():
            if isinstance(v, dict):
                self._substitute_env_in_settings(v)
            elif isinstance(v, list):
                if (
                        len(v) == 1 and
                        isinstance(v[0], list) and
                        len(v[0]) == 1 and
                        isinstance(v[0][0], str) and
                        'getenv' in v[0][0]
                ):
                    # Преобразовать двумерный массив из одного значения в строку
                    d[k] = v[0][0]
                    d[k] = self._substitute_env_vars(d[k])
            elif isinstance(v, str):
                d[k] = self._substitute_env_vars(v)

    def reload(self):
        """Перезагружает конфиг из storage."""
        data = self.storage.load()
        self.settings = deepcopy(data)
        self._substitute_env_in_settings(self.settings)

    def check_reload(self) -> bool:
        """
        Проверить, изменился ли источник конфигов (файл и др).
        Если изменился — перезагрузить, возвратить True.
        """
        if hasattr(self.storage, 'supports_auto_reload') and self.storage.supports_auto_reload():
            if self.storage.has_changed():
                self.logger.info("Config source changed, reloading config.")
                self.reload()
                return True
        return False

    def get(self, param: str = None, default: Union[str, list, dict, bool] = None):
        """Получить либо весь конфиг-словарь, либо значение по ключу."""
        if param:
            return self.settings.get(param, default)
        return self.settings

    def set(self, data: dict):
        """Установить дикт конфигурации (инжекция, тесты, редактирование)."""
        self.settings_raw = deepcopy(data)
        self.settings = deepcopy(data)
        self._substitute_env_in_settings(self.settings)

    def parse(self, file_: str, encoding: str = 'utf-8', use_yaml: bool = True):
        """(Однократный) парсинг файла - полезно при первичной инициализации."""
        file_storage = FileConfigStorage(file_, use_yaml=use_yaml, encoding=encoding)
        data = file_storage.load()
        self.set(data)

    def save(self, file_: Optional[str] = None, encoding: str = 'utf-8', use_yaml: Optional[bool] = None):
        """Сохраняет настройки в файл, по умолчанию в тот, что был задан при инициализации (если подходит)."""
        import json, yaml
        if file_ is None and isinstance(self.storage, FileConfigStorage):
            file_ = self.storage.filename
            use_yaml = self.storage.use_yaml if use_yaml is None else use_yaml
        elif file_ is None:
            raise ValueError("file_ must be specified for saving if non-file storage is used.")
        else:
            use_yaml = True if use_yaml is None else use_yaml
        with open(file_, 'w', encoding=encoding) as f:
            if use_yaml:
                yaml.dump(self.settings, f, allow_unicode=True, sort_keys=False)
            else:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)

    @staticmethod
    def get_version(fname=None):
        if not fname:
            fname = sys.argv[0]
        filename = os.path.join(os.path.dirname(fname), os.path.basename(fname))
        version = datetime.fromtimestamp(os.path.getmtime(filename))
        return datetime.strftime(version, '%y%m%d')

    @staticmethod
    def convert(file_from: str, file_to: str, encoding='utf-8', use_yaml=True):
        """Конвертация yaml <-> json."""
        import json, yaml
        with open(file_from, encoding=encoding) as f:
            if use_yaml:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        with open(file_to, 'w', encoding=encoding) as fout:
            if use_yaml:
                yaml.dump(data, fout, allow_unicode=True, sort_keys=False)
            else:
                json.dump(data, fout, ensure_ascii=False, indent=2)

    # ALIASES
    get_settings = get
    set_settings = set
    parse_settings = parse
    save_settings = save
    convert_config = convert


# __all__ for import *
__all__ = ['Settings']
