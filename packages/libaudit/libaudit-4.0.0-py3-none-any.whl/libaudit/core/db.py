from typing import Any
from typing import Union

from django.db import connection


def set_db_param(key, value):
    """Устанавливает параметры в настройках БД."""
    set_db_params(**{key: value})


def set_db_params(**params):
    """Устанавливает параметры сеанса эффективно, используя одно подключение/курсор."""
    if not params:
        return
    with connection.cursor() as cursor:
        sql = (
            'SELECT set_config(config_key, config_value, FALSE)'
            'FROM unnest(%s::text[], %s::text[]) AS t(config_key, config_value)'
        )
        cursor.execute(sql, (list(params.keys()), list(str(v) if v else None for v in params.values())))


def get_db_param(key) -> Union[Any, None]:
    """Получить параметр сеанса по имени."""
    cursor = connection.cursor()
    cursor.execute('SELECT current_setting(%s, true);', (key,))
    if result := cursor.fetchone():
        return result[0]
