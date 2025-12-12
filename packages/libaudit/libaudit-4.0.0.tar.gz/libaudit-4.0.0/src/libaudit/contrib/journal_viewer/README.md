## Базовый вьюсет реализующий просмотр журнала
Предназначен для совместного использования с `libaudit.handlers.database_table`

Использование:
```python
# views.py
from django.db.models import F
from django.db.models import IntegerField
from django.db.models import OuterRef
from django.db.models import Subquery
from django.db.models import Value
from django.db.models.functions import Cast
from django.db.models.functions import Concat
from django.contrib.auth import get_user_model
from rest_framework.pagination import LimitOffsetPagination

from libaudit.contrib.journal_viewer.views import (
    BaseAuditLogViewSet,
)


class AuditLogViewSet(BaseAuditLogViewSet):
    pagination_class = LimitOffsetPagination

    def _get_user_name_sq(self) -> Subquery:
        """Подзапрос для аннотации имени пользователя."""
        return Subquery(
            get_user_model()
            .objects.filter(pk=Cast(OuterRef('user_id'), output_field=IntegerField()))
            .annotate(
                user_name=Concat(
                    F('last_name'),
                    Value(' '),
                    F('first_name'),
                ),
            )
            .values('user_name')[:1]
        )

    def _get_user_unit_name_sq(self) -> Subquery:
        return Subquery(
            School.objects.filter(
                pk=Cast(
                    OuterRef('user_unit_id'), output_field=IntegerField()
                )
            ).values('short_name')[:1]
        )
```

```python
# urls.py
from .views import AuditLogViewSet
from rest_framework.routers import SimpleRouter

router = SimpleRouter()

router.register('auditlog', AuditLogViewSet, basename='libaudit_log')
```
