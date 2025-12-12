# Библиотека логирования изменений данных в БД
## Подключение

requirements:

    libaudit>=2.0.0,<3.0

settings:

    INSTALLED_APPS = [
        ...
        'libaudit',
        ...
    ]

    MIDDLEWARE = [
        ...
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'libaudit.middleware.AuditLogMiddleware',
        ...
    ]

    LIBAUDIT = {
        'HANDLER': 'libaudit.handlers.database_table',  # или иной обработчик
        'CONTEXT_RESOLVER_CLS': 'my_app.audit.MyAuditContextResolver',
        'EXCLUDED_TABLES': (),  # опционально
        'SETUP_AUDIT_CONTEXT_FOR_READONLY_REQUESTS': False,  # опционально
	}

Реализовано два обработчика: [хранение в таблице](src/libaudit/handlers/database_table/README.md) и [отправка в стандартный вывод СУБД](src/libaudit/handlers/stdout/README.md).

Дополнения: [contrib](src/libaudit/contrib/README.md)

## Запуск тестов
    $ tox
