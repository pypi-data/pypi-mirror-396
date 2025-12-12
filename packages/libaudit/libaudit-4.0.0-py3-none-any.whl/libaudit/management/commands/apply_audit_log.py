from django.core.management.base import BaseCommand
from django.db import ProgrammingError
from django.db import connections

from libaudit.core.install import AuditInstaller


class Command(BaseCommand):
    """Выпоняет настройку логирования изменений системы."""

    help = 'Настройка БД для логирования изменений объектов.'

    def handle(self, *args, **options):
        """Настроить логирование изменений объектов."""
        installer = AuditInstaller()
        with connections['default'].cursor() as cursor:
            try:
                for sql, params in installer.get_install_sql():
                    cursor.execute(sql, params)
            except ProgrammingError as exc:
                raise exc
            else:
                self.stdout.write('Настройка логирования изменений прошла успешно.')
