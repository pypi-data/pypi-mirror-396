## Расширения для аутентификации DRF

### AuditContextAuthenticationMixin

Примесь к классам аутентификации DRF, дополняющая контекст данными о пользователе DRF.
Использование:
```python
from rest_framework.authentication import TokenAuthentication 
from libaudit.contrib.rest_framework.auth import AuditContextAuthenticationMixin


class AuditContextTokenAuthentication(AuditContextAuthenticationMixin, TokenAuthentication):
    # Реализация authenticate() наследуется
    ...
```

### with_audit_context
Декоратор для метода `authenticate`
Пример:
```python
from rest_framework.authentication import BaseAuthentication
from libaudit.contrib.rest_framework.auth import with_audit_context


class CustomDRFAuthentication(BaseAuthentication):
    @with_audit_context
    def authenticate(self, request):
        # Реализация authenticate
        user = ... # 
        return user, None
```
