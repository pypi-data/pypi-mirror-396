from django.apps import AppConfig as AppConfigBase


class AppConfig(AppConfigBase):
    name = __package__
    label = 'libaudit_database_table_handler'
