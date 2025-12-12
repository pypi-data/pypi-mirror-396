from abc import ABCMeta
from abc import abstractmethod

from django.db.models import Case
from django.db.models import F
from django.db.models import Subquery
from django.db.models import Value
from django.db.models import When
from django.db.models.functions import Coalesce
from django.utils.encoding import force_str
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet

from libaudit.core.types import OperationType
from libaudit.handlers.database_table.proxies import AuditLogViewProxy
from libaudit.handlers.database_table.proxies import model_registry

from .filters import AuditLogFilter
from .serializers import AuditLogDetailSerializer
from .serializers import AuditLogListSerializer


class BaseAuditLogViewSet(ReadOnlyModelViewSet, metaclass=ABCMeta):
    """Базовый Вьюсет для просмотра журнала аудита."""

    queryset = AuditLogViewProxy.objects.all()
    filterset_class = AuditLogFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        """Получить класс сериалайзера для обработки запроса."""
        result = AuditLogDetailSerializer
        if self.action == 'list':
            result = AuditLogListSerializer

        return result

    @abstractmethod
    def _get_user_name_sq(self) -> Subquery:
        """Подзапрос для аннотации имени пользователя.

        Пример:
        .. code-block:: python
        def _get_user_name_sq(self) -> Subquery:
            return Subquery(
                get_user_model().objects.filter(
                    pk=Cast(
                        OuterRef('user_id'), output_field=IntegerField()
                    )
                ).annotate(
                    user_name=Concat(
                        F('last_name'),
                        Value(' '),
                        F('first_name'),
                    ),
                ).values('user_name')[:1]
            )
        """

    @abstractmethod
    def _get_user_unit_name_sq(self) -> Subquery:
        """Подзапрос для аннотации имени организации пользователя.

        Пример:
        .. code-block:: python
        def _get_user_unit_name_sq(self) -> Subquery:
            return Subquery(
                School.objects.filter(
                    pk=Cast(
                        OuterRef('user_unit_id'), output_field=IntegerField()
                    )
                ).values('short_name')[:1]
            )
        """

    def get_queryset(self):
        """Возвращает кверисет записей в журнале."""
        return (
            super()
            .get_queryset()
            .annotate(
                user_name=self._get_user_name_sq(),
                user_unit_name=self._get_user_unit_name_sq(),
                object_id=Coalesce(F('old_data__id'), F('changes__id')),
                operation_name=Case(*(When(operation=op.value, then=Value(op.label)) for op in OperationType)),
                model_verbose_name=Case(
                    *(
                        When(table_name=db_table, then=Value(force_str(model_cls._meta.verbose_name)))
                        for db_table, model_cls in model_registry.table_model.items()
                    ),
                    default=F('table_name'),
                ),
            )
            .order_by('-timestamp')
        )
