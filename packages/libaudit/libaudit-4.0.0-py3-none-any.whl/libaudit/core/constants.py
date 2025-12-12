import os


# Папка с sql файлами
SQL_FILES_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        'sql',
    )
)


USER_ID_KEY = 'libaudit.user_id'
USER_TYPE_ID_KEY = 'libaudit.user_type_id'
USER_UNIT_ID_KEY = 'libaudit.user_unit_id'
USER_UNIT_TYPE_ID_KEY = 'libaudit.user_unit_type_id'
REQUEST_ID_KEY = 'libaudit.request_id'
TRANSACTION_ID_KEY = 'libaudit.transaction_id'
IP_ADDRESS_KEY = 'libaudit.ip_address'
