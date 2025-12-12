from django.db import migrations

from libaudit.core.migration import InstallAuditLog


class Migration(migrations.Migration):
    """Инициализация системы журналирования изменений."""

    operations = [
        InstallAuditLog(version=1),
    ]
