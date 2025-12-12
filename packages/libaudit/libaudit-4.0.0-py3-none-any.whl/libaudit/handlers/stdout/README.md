## Обработчик логирования стандартный вывод СУБД. Далее стандартный вывод может быть обработан с помощью fluentbit.
Подключение:
```python
# settings.py
LIBAUDIT = {
    'HANDLER': 'libaudit.handlers.stdout',
    ...
}
```
