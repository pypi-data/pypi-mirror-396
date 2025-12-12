## Обработчик логирования в таблицу основной БД.
Подключение:
```python
# settings.py
LIBAUDIT = {
    'HANDLER': 'libaudit.handlers.database_table',
    ...
}

```
