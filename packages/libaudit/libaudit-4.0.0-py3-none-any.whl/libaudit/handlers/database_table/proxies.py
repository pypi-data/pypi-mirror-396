from collections.abc import KeysView
from functools import cached_property
from functools import partial
from typing import Optional
from typing import TypeVar

from django.apps import apps
from django.db import models
from django.db.models.fields.related import RelatedField
from django.utils.dateparse import parse_date
from django.utils.dateparse import parse_datetime
from django.utils.dateparse import parse_time
from django.utils.encoding import force_str

from libaudit.core.types import OperationType

from .models import AuditLog


ModelT = TypeVar('ModelT', bound=models.Model)


class ModelRegistry:
    """Реестр моделей в системе."""

    @cached_property
    def table_model(self):
        """Сопоставление имён таблиц с моделями."""
        return {
            model._meta.db_table: model
            for model in apps.get_models(include_auto_created=True)
            if not (model._meta.proxy)
        }

    def get_model(self, table_name: str):
        """Возвращает класс модели по имени таблицы."""
        return self.table_model.get(table_name)


model_registry = ModelRegistry()


class FieldValueParser:
    """Парсер значений из JSON."""

    @classmethod
    def parse_value(cls, fields: Optional[dict], column_name: str, value):
        """Конвертирует значение поля в строковое представление."""
        if value is None:
            return ''

        if not fields:
            return force_str(value)

        field = fields.get(column_name)
        if not field:
            return force_str(value)

        try:
            return cls._get_parsed_value(field, value)
        except (ValueError, TypeError):
            return force_str(value)

    @classmethod
    def _get_parsed_value(cls, field, value):
        """Возвращает отображаемое значение в зависимости от типа поля."""
        if isinstance(field, RelatedField):
            parser = partial(cls._convert_related_field, field)
        elif isinstance(field, models.BooleanField):
            parser = cls._convert_boolean_field
        elif isinstance(field, models.IntegerField) and field.choices:
            parser = partial(cls._convert_choice_field, field.choices)
        else:
            parser = force_str

        return parser(value)

    @staticmethod
    def _convert_related_field(field: models.Field, value):
        if not value:
            return ''
        related = field.remote_field
        model = related.model
        field_name = related.field_name
        qs = model._default_manager.filter(**{field_name: value})[:1]
        if qs:
            return '{{{}}} {}'.format(qs[0].id, str(qs[0]))

        return value

    @staticmethod
    def _convert_boolean_field(value):
        value_map = {'t': True, 'f': False}

        return value_map.get(value, value)

    @staticmethod
    def _convert_choice_field(choices, choice_id):
        if choice_id:
            choice_id = int(choice_id)

        return dict(choices).get(choice_id, choice_id)


class DiffBuilder:
    """Построитель diff'а между исходным и новым состоянием объекта модели."""

    _value_parser: callable

    def __init__(self, value_parser: callable):
        self._value_parser = value_parser

    def get_diff(
        self,
        model_cls: Optional[type[ModelT]],
        operation_type: OperationType,
        changes: Optional[dict],
        old_data: Optional[dict],
    ) -> list[dict]:
        """Возвращает список различий между старыми и новыми данными объекта модели.

        Returns:
            list[dict]: Список словарей с различиями. Пример:
            [
                {
                    'name': 'field_name',
                    'verbose_name': 'Название поля',
                    'old': 'старое значение',
                    'new': 'новое значение'
                }
            ]

        """
        changes = changes or {}
        old_data = old_data or {}

        # поля модели
        fields = {field.get_attname_column()[1]: field for field in model_cls._meta.fields} if model_cls else {}

        keys, data, new_data = self._get_operation_data(operation_type, changes, old_data)

        result = (
            {
                'name': key,
                'verbose_name': self._get_field_verbose_name(fields, key),
                'old': self._value_parser(fields, key, data.get(key, '')),
                'new': self._value_parser(fields, key, new_data.get(key, '')),
            }
            for key in keys
        )
        return sorted(result, key=lambda x: x['name'])

    def _get_operation_data(
        self, operation_type: OperationType, changes: dict, old_data: dict
    ) -> tuple[KeysView, dict, dict]:
        empty = {}
        keys, data, new_data = empty.keys(), empty, empty
        if operation_type == OperationType.INSERT:
            keys, data, new_data = changes.keys(), empty, changes
        elif operation_type == OperationType.UPDATE:
            keys, data, new_data = changes.keys(), old_data, changes
        elif operation_type == OperationType.DELETE:
            keys, data, new_data = old_data.keys(), old_data, empty

        return keys, data, new_data

    @staticmethod
    def _get_field_verbose_name(fields, column_name: str) -> str:
        """Возвращает отображаемое имя поля модели."""
        name = column_name
        field = fields.get(column_name)
        if field and field.verbose_name:
            name = force_str(field.verbose_name)
        return name


def get_object_string_representation(instance: Optional[ModelT]):
    """Возвращает строковое представление объекта."""
    if hasattr(instance, 'log_display'):
        try:
            return instance.log_display()
        except Exception:  # noqa: S110
            pass
    elif hasattr(instance, 'display'):
        try:
            return instance.display()
        except Exception:  # noqa: S110
            pass
    return str(instance)


class ModelSnapshotFactory:
    """Восстановитель экземпляра модели."""

    @classmethod
    def create(
        cls,
        model_cls: Optional[type[ModelT]],
        data: Optional[dict],
        changes: Optional[dict],
    ) -> Optional[ModelT]:
        """Восстанавливает экземпляр модели из сохраненных данных.

        Если объект был удалён, то возвращает состояние до удаления.
        """
        if not model_cls:
            return None

        data = data or {}
        changes = changes or {}

        instance = model_cls()
        fields_dict = {field.name: field for field in model_cls._meta.fields}

        for key, value in (data | changes).items():
            field = fields_dict.get(key)
            converted_value = cls._convert_field_value(field, value)
            setattr(instance, key, converted_value)

        return instance

    @classmethod
    def _convert_field_value(cls, field, value):
        if not field:
            return value

        try:
            if isinstance(field, models.DateTimeField):
                return parse_datetime(value)
            elif isinstance(field, models.DateField):
                return parse_date(value)
            elif isinstance(field, models.TimeField):
                return parse_time(value)
            elif isinstance(field, models.IntegerField):
                return int(value)
            elif isinstance(field, models.FloatField):
                return float(value)
            elif isinstance(field, models.FileField):
                return cls._handle_file_field(field, value)
        except (ValueError, TypeError):
            pass
        return value

    @staticmethod
    def _handle_file_field(field, value):
        storage = field.storage
        if storage.exists(value):
            return storage.path(value)
        return None


class AuditLogViewProxy(AuditLog):
    """Прокси-модель для отображения."""

    class Meta:  # noqa: D106
        proxy = True

    @property
    def model_cls(self) -> Optional[type[models.Model]]:
        """Класс измененной модели."""
        return model_registry.get_model(self.table_name)

    @property
    def operation_type(self) -> OperationType:
        """Тип операции."""
        return OperationType(self.operation)

    @property
    def diff(self):
        """Возвращает diff для объекта."""
        return DiffBuilder(value_parser=FieldValueParser.parse_value).get_diff(
            self.model_cls, self.operation_type, self.changes, self.old_data
        )

    @property
    def object_display(self) -> str:
        """Строковое представление экземпляра модели."""
        return get_object_string_representation(self.object_snapshot)

    @property
    def object_snapshot(self) -> ModelT:
        """Снимок экземпляра модели."""
        return ModelSnapshotFactory.create(self.model_cls, self.old_data, self.changes)
