from django.db import migrations

from libaudit.core.migration import InstallAuditLog


class Migration(migrations.Migration):
    """Обновление системы журналирования изменений."""

    dependencies = [
        ('libaudit', '0001_install_audit_log'),
    ]

    operations = [
        InstallAuditLog(version=2),
    ]
