from django.db import models
from django.db.models import JSONField

from libaudit.core.types import OperationType

from .constants import AUDIT_LOG_TABLE_NAME


class AuditLog(models.Model):
    """Журнал изменений."""

    user_id = models.CharField(
        null=True,
        max_length=36,
        db_index=True,
        verbose_name='Пользователь',
    )
    user_type_id = models.IntegerField(
        null=True,
        db_index=True,
        verbose_name='Тип пользователя',
    )
    user_unit_id = models.CharField(
        null=True,
        max_length=36,
        db_index=True,
        verbose_name='Организация пользователя',
    )
    user_unit_type_id = models.IntegerField(
        null=True,
        db_index=True,
        verbose_name='Тип организации пользователя',
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата, время')
    table_name = models.CharField(max_length=255)
    old_data = JSONField(
        null=True,
        verbose_name='Объект',
    )
    changes = JSONField(null=True, verbose_name='Изменения')
    operation = models.SmallIntegerField(choices=OperationType.choices(), verbose_name='Действие')
    request_id = models.CharField(
        null=True,
        max_length=36,
        verbose_name='Идентификатор запроса',
    )
    transaction_id = models.CharField(
        null=True,
        max_length=36,
        verbose_name='Идентификатор транзакции',
    )
    ip_address = models.GenericIPAddressField(null=True, verbose_name='IP адрес')

    class Meta:  # noqa: D106
        db_table = AUDIT_LOG_TABLE_NAME
