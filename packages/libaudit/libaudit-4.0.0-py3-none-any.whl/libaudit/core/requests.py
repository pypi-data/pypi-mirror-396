from abc import ABCMeta
from abc import abstractmethod
from typing import TYPE_CHECKING

from django.contrib.admin.options import get_content_type_for_model
from django.http.request import HttpRequest

from libaudit.core.types import AuditRequestContext


if TYPE_CHECKING:
    from typing import Optional


class AbstractAuditContextResolver(metaclass=ABCMeta):
    """Абстрактный извлекатель контекста аудита из запроса."""

    @classmethod
    @abstractmethod
    def _get_user_id(cls, request: HttpRequest) -> 'Optional[str]':
        """Возвращает идентификатор пользователя."""

    @classmethod
    @abstractmethod
    def _get_user_type_id(cls, request: HttpRequest) -> 'Optional[int]':
        """Возвращает идентификатор ContentType модели пользователя."""

    @classmethod
    @abstractmethod
    def _get_user_unit_id(cls, request: HttpRequest) -> 'Optional[str]':
        """Возвращает идентификатор организации пользователя."""

    @classmethod
    @abstractmethod
    def _get_user_unit_type_id(cls, request: HttpRequest) -> 'Optional[int]':
        """Возвращает идентификатор ContentType модели организации пользователя."""

    @classmethod
    @abstractmethod
    def _get_request_id(cls, request: HttpRequest) -> 'Optional[str]':
        """Возвращает идентификатор запроса."""

    @classmethod
    @abstractmethod
    def _get_transaction_id(cls, request: HttpRequest) -> 'Optional[str]':
        """Возвращает идентификатор транзакции."""

    @classmethod
    def _get_ip_address(cls, request: HttpRequest) -> 'Optional[str]':
        """Возвращает ip источника запроса.

        :param request: запрос
        :type django.http.HttpRequest

        :return IP адрес
        :rtype str or None
        """
        # Берем ip из X-Real-IP, если параметр установлен.
        # Вернет адрес первого недоверенного прокси.
        http_x_real_ip = request.META.get('HTTP_X_REAL_IP', None)
        if http_x_real_ip is not None:
            return http_x_real_ip

        # Берем первый ip из X-Forwarded-For, если параметр установлен.
        # Вернет первый адрес в цепочке прокси.
        x_forward_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
        if x_forward_for is not None:
            x_forward_ip, _, _ = x_forward_for.partition(',')
            return x_forward_ip.strip()

        return request.META.get('REMOTE_ADDR', None)

    @classmethod
    def get_audit_context(cls, request: 'Optional[HttpRequest]' = None) -> AuditRequestContext:
        """Возвращает контекст для логирования изменений.

        Если передан запрос, то контекст извлекается из запроса.
        """
        context = AuditRequestContext()

        if request is None:
            return context

        assert isinstance(request, HttpRequest), type(request)

        if request.user and request.user.is_authenticated:
            context.user_id = cls._get_user_id(request)
            context.user_type_id = cls._get_user_type_id(request)
            context.user_unit_id = cls._get_user_unit_id(request)
            context.user_unit_type_id = cls._get_user_unit_type_id(request)

        context.request_id = cls._get_request_id(request)
        context.transaction_id = cls._get_transaction_id(request)
        context.ip_address = cls._get_ip_address(request)

        return context


class DefaultAuditContextResolver(AbstractAuditContextResolver):
    """Минимально функциональная реализация извлекателя контекста аудита.

    Поддерживает извлечение ip_address, user_id и user_type_id для стандартного пользователя Django.
    """

    @classmethod
    def _get_user_id(cls, request: HttpRequest) -> 'Optional[str]':
        return str(request.user.pk)

    @classmethod
    def _get_user_type_id(cls, request: HttpRequest) -> 'Optional[int]':
        return get_content_type_for_model(request.user).id

    @classmethod
    @abstractmethod
    def _get_user_unit_id(cls, request: HttpRequest) -> 'Optional[str]':
        """Возвращает идентификатор организации пользователя."""
        return None

    @classmethod
    @abstractmethod
    def _get_user_unit_type_id(cls, request: HttpRequest) -> 'Optional[int]':
        """Возвращает идентификатор ContentType модели организации пользователя."""
        return None

    @classmethod
    def _get_request_id(cls, request: HttpRequest) -> 'Optional[str]':
        return None

    @classmethod
    def _get_transaction_id(cls, request: HttpRequest) -> 'Optional[str]':
        return None
