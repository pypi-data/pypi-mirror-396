from dataclasses import dataclass
from enum import Enum
from typing import Optional

from libaudit.core.constants import IP_ADDRESS_KEY
from libaudit.core.constants import REQUEST_ID_KEY
from libaudit.core.constants import TRANSACTION_ID_KEY
from libaudit.core.constants import USER_ID_KEY
from libaudit.core.constants import USER_TYPE_ID_KEY
from libaudit.core.constants import USER_UNIT_ID_KEY
from libaudit.core.constants import USER_UNIT_TYPE_ID_KEY


class NamedIntEnum(int, Enum):
    """Базовый класс для набора пар число + строка."""

    def __new__(cls, value: int, label: str) -> 'NamedIntEnum':
        """Создаёт экземпляр перечисления."""
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label

        return obj

    def __str__(self) -> str:
        """строковое представление экземпляра перечисления."""
        return str(self.value)

    @classmethod
    def choices(cls) -> tuple[tuple[int, str], ...]:
        """Варианты выбора на основе перечисления."""
        return tuple((member.value, member.label) for member in cls)


class OperationType(NamedIntEnum):
    """Перечисление возможных операций."""

    INSERT = (1, 'Создание')
    UPDATE = (2, 'Изменение')
    DELETE = (3, 'Удаление')


@dataclass
class AuditRequestContext:
    """Контекст запроса для передачи в журнал."""

    user_type_id: Optional[int] = None  # Идентификатор ContentType модели пользователя
    user_id: Optional[str] = None  # Идентификатор пользователя;
    user_unit_type_id: Optional[int] = None  # Идентификатор ContentType модели организации пользователя
    user_unit_id: Optional[str] = None  # Идентификатор организации пользователя
    request_id: Optional[str] = None  # Идентификатор запроса
    transaction_id: Optional[str] = None  # Идентификатор транзакции
    ip_address: Optional[str] = None  # IP адрес пользователя

    def dict(self):
        """Возвращает параметры контекста, пригодные для передачи в СУБД."""
        return {
            USER_TYPE_ID_KEY: self.user_type_id,
            USER_ID_KEY: self.user_id,
            USER_UNIT_ID_KEY: self.user_unit_id,
            USER_UNIT_TYPE_ID_KEY: self.user_unit_type_id,
            REQUEST_ID_KEY: self.request_id,
            TRANSACTION_ID_KEY: self.transaction_id,
            IP_ADDRESS_KEY: self.ip_address,
        }
