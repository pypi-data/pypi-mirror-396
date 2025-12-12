from functools import wraps

from ._base import set_user_audit_context


def with_audit_context(authenticate_method):
    """Декоратор метода ``authenticate`` класса аутентификации DRF, добавляющий в контекст аудита данные о пользователе.

    Пример использования:
    .. code-block:: python

    class CustomDRFAuthentication(BaseAuthentication):
        @with_audit_context
        def authenticate(self, request):
            ...

            return user, None
    """

    @wraps(authenticate_method)
    def wrapper(self, request, *args, **kwargs):
        auth = authenticate_method(self, request, *args, **kwargs)
        return set_user_audit_context(request, auth)

    return wrapper
