from ._base import set_user_audit_context


class AuditContextAuthenticationMixin:
    """Примесь к классу аутентификации, добавляющая в контекст аудита данные о пользователе.

    Пример использования:
    .. code-block:: python

    class CustomTokenAuthentication(AuditContextAuthenticationMixin, TokenAuthentication):
        ...

    """

    def authenticate(self, request):
        """Добавляет в контекст аудита данные о пользователе."""
        auth = super().authenticate(request)
        return set_user_audit_context(request, auth)
