from typing import TYPE_CHECKING
from typing import Any
from typing import Optional
import pathlib

from .settings import get_excluded_tables
from .settings import get_handler_class


if TYPE_CHECKING:
    from typing import Tuple


class AuditInstaller:
    """Установщик процедур и триггеров журналирующих изменения."""

    _version_sql_mapping = {
        1: '0001_apply_triggers.sql',
        2: '0002_apply_triggers.sql',
    }

    def __init__(self, version: Optional[int] = None):
        """Инициализация установщика.

        Args:
            version:
                Версия для установки. По-умолчанию None, что означает установку всех версий последовательно.

        """
        handler_cls = get_handler_class()
        self.version = version
        if self.version:
            assert self.version in self._version_sql_mapping, f'Неизвестная версия {version}'

        self.files_to_apply: tuple[str, ...] = tuple(
            sql_file_name for ver, sql_file_name in self._version_sql_mapping.items() if ver == version or not version
        )

        self.handler = handler_cls(version)

    @staticmethod
    def _read_sql(filename):
        """Чтение sql из файла."""
        sql_file_path = pathlib.Path(__file__).parent / 'sql' / filename
        with sql_file_path.open(mode='r', encoding='utf-8') as sql_file:
            return sql_file.read()

    def get_install_sql(self) -> 'Tuple[tuple[str, Optional[Any]], ...]':
        """Набор запросов с параметрами, выполняющих установку."""
        excluded_tables = set(get_excluded_tables())
        excluded_tables.update(self.handler.excluded_tables)

        return (
            ('CREATE EXTENSION IF NOT EXISTS hstore;', None),
            # установка обработчика
            *((sql, None) for sql in self.handler.get_install_sql()),
            # Установка триггеров в таблицы
            *((self._read_sql(sql_file_name), None) for sql_file_name in self.files_to_apply),
            ('SELECT apply_triggers(%s);', (list(excluded_tables),)),
        )

    def get_uninstall_sql(self) -> 'Tuple[tuple[str, Optional[Any]], ...]':
        """Набор запросов с параметрами, выполняющих удаление."""
        return (
            (self._read_sql('remove_triggers.sql'), None),
            (self.handler.get_uninstall_sql(), None),
        )
