import django_filters as filters

from libaudit.core.types import OperationType


class AuditLogFilter(filters.FilterSet):
    """Фильтр записей журнала изменений."""

    timestamp_from = filters.IsoDateTimeFilter(field_name='timestamp', lookup_expr='gte', label='Дата, время с')
    timestamp_to = filters.IsoDateTimeFilter(field_name='timestamp', lookup_expr='lte', label='Дата, время по')
    operation = filters.ChoiceFilter(choices=OperationType.choices(), label='Операция')
    user_name = filters.CharFilter(lookup_expr='icontains', label='Имя пользователя')
    table_name = filters.CharFilter(lookup_expr='icontains', label='Таблица')
    model_verbose_name = filters.CharFilter(lookup_expr='icontains', label='Модель объекта')
    object_id = filters.CharFilter(lookup_expr='exact', label='Идентификатор объекта')
    request_id = filters.CharFilter(lookup_expr='icontains', label='Идентификатор запроса')
    transaction_id = filters.CharFilter(lookup_expr='icontains', label='Идентификатор транзакции')
    ip_address = filters.CharFilter(lookup_expr='icontains', label='IP Адрес пользователя')

    ordering = filters.OrderingFilter(
        fields=(
            ('timestamp', 'timestamp'),
            ('operation', 'operation'),
            ('operation_name', 'operation_name'),
            ('user_name', 'user_name'),
            ('table_name', 'table_name'),
            ('model_verbose_name', 'model_verbose_name'),
            ('object_id', 'object_id'),
            ('ip_address', 'ip_address'),
        ),
        field_labels={
            'timestamp': 'Дата, время',
            'operation': 'Операция',
            'operation_name': 'Наименование операции',
            'user_name': 'Имя пользователя',
            'table_name': 'Таблица',
            'model_verbose_name': 'Модель объекта',
            'object_id': 'Идентификатор объекта',
            'ip_address': 'IP Адрес пользователя',
        },
    )
