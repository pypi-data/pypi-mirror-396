from typing import Type

from django.utils.deprecation import MiddlewareMixin

from libaudit.core import db
from libaudit.core.requests import AbstractAuditContextResolver
from libaudit.core.settings import get_context_resolver
from libaudit.core.settings import get_setup_context_in_readonly_requests


class AuditLogMiddleware(MiddlewareMixin):
    """Извлекает из запроса и передаёт в контекст аудита дополнительную информацию."""

    _safe_methods = ('GET', 'HEAD', 'OPTIONS')

    @property
    def _audit_context_resolver(self) -> Type[AbstractAuditContextResolver]:
        return get_context_resolver()

    def _should_set_context(self, request) -> bool:
        setup_in_readonly = get_setup_context_in_readonly_requests()
        is_safe = getattr(request, 'method', '').upper() in self._safe_methods
        return setup_in_readonly or not is_safe

    def process_request(self, request):
        """Добавляет в контекст аудита данные о запросе."""
        if self._should_set_context(request):
            request._audit_context = self._audit_context_resolver.get_audit_context(request)
            db.set_db_params(**request._audit_context.dict())

    def process_response(self, request, response):
        """Обнуляет данные контекста аудита после обработки запроса."""
        if self._should_set_context(request):
            request._audit_context = self._audit_context_resolver.get_audit_context()
            db.set_db_params(**request._audit_context.dict())

        return response
