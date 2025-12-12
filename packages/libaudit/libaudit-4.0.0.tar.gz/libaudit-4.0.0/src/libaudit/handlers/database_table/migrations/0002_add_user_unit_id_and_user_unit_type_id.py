from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ('libaudit_database_table_handler', '0001_initial'),
    ]

    run_before = [
        ('libaudit', '0002_upgrade_audit_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditlog',
            name='user_unit_id',
            field=models.CharField(db_index=True, max_length=36, null=True, verbose_name='Организация пользователя'),
        ),
        migrations.AddField(
            model_name='auditlog',
            name='user_unit_type_id',
            field=models.IntegerField(db_index=True, null=True, verbose_name='Тип организации пользователя'),
        ),
    ]
