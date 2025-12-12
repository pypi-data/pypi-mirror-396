from typing import TYPE_CHECKING

from django.utils.module_loading import import_string

from libaudit.core.requests import AbstractAuditContextResolver
from libaudit.handlers.base import AbstractAuditLogHandler


if TYPE_CHECKING:
    from typing import Tuple
    from typing import Type


def _get_settings_value(key: str):
    """Возвращает значение настроек libaudit.

    Если в настройках django значение не указано — возвращает значение по-умолчанию.
    """
    from django.conf import settings as django_settings

    from libaudit import settings as default_settings

    assert key in dir(default_settings)
    django_settings_libaudit = getattr(django_settings, 'LIBAUDIT', {})

    return django_settings_libaudit.get(key, getattr(default_settings, key, None))


def get_context_resolver() -> 'Type[AbstractAuditContextResolver]':
    """Возвращает класс извлекающий контекст из запроса."""
    return import_string(_get_settings_value('CONTEXT_RESOLVER_CLS'))


def get_excluded_tables() -> 'Tuple[str]':
    """Возвращает кортеж таблиц, в которые не будут установлены триггеры."""
    return _get_settings_value('EXCLUDED_TABLES')


def get_handler_class() -> 'Type[AbstractAuditLogHandler]':
    """Возвращает класс обработчика изменений в наблюдаемых таблицах."""
    return import_string(f'{_get_settings_value("HANDLER")}.handler.AuditLogHandler')


def get_setup_context_in_readonly_requests() -> bool:
    """Если False — не устанавливать контекст аудита для readonly-запросов (GET/HEAD/OPTIONS)."""
    return bool(_get_settings_value('SETUP_AUDIT_CONTEXT_FOR_READONLY_REQUESTS'))
