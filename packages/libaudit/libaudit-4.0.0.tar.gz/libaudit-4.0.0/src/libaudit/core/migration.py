from typing import Optional

from django.db.migrations.operations.base import Operation

from libaudit.core.install import AuditInstaller


class InstallAuditLog(Operation):
    """Настраивает основную БД."""

    reversible = True

    def __init__(self, version: Optional[int] = None):
        self.installer = AuditInstaller(version)

    def state_forwards(self, app_label, state):
        """Пустая реализация, не меняет состояние моделей."""
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        """Создаёт процедуры и триггеры для журналирования изменений."""
        if schema_editor.connection.alias != 'default':
            return

        for sql, params in self.installer.get_install_sql():
            schema_editor.execute(sql, params)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        """Удаляет процедуры и триггеры."""
        if schema_editor.connection.alias != 'default':
            return

        for sql, params in self.installer.get_uninstall_sql():
            schema_editor.execute(sql, params)
