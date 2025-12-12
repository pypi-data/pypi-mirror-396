from typing import Optional
import pathlib

from ..base import AbstractAuditLogHandler
from .constants import AUDIT_LOG_TABLE_NAME


class AuditLogHandler(AbstractAuditLogHandler):
    """Обработчик с выводом изменений в таблицу."""

    _version_sql_mapping = {
        1: '0001_handler.sql',
        2: '0002_handler.sql',
    }

    def __init__(self, version: Optional[int] = None):
        super().__init__(version)
        if self.version:
            assert self.version in self._version_sql_mapping, f'Неизвестная версия {version}'

        self.files_to_apply: tuple[str, ...] = tuple(
            sql_file_name for ver, sql_file_name in self._version_sql_mapping.items() if ver == version or not version
        )

    @staticmethod
    def _read_sql(filename):
        """Чтение sql из файла."""
        sql_file_path = pathlib.Path(__file__).parent / 'sql' / filename
        with sql_file_path.open(mode='r', encoding='utf-8') as sql_file:
            return sql_file.read()

    @property
    def excluded_tables(self) -> tuple[str, ...]:
        """Вешать триггеры на таблицу с журналом операций не нужно."""
        return (AUDIT_LOG_TABLE_NAME,)

    def get_install_sql(self) -> tuple[str, ...]:
        """Набор запросов, выполняющих установку."""
        return tuple(
            self._read_sql(sql_file_name).replace('%AUDIT_LOG_TABLE_NAME%', AUDIT_LOG_TABLE_NAME)
            for sql_file_name in self.files_to_apply
        )

    def get_uninstall_sql(self) -> str:
        """Возвращает SQL запрос удаления функции обработчика логирования изменений."""
        return 'DROP FUNCTION IF EXISTS audit_handler;'
