-- удаляем прошлую версию процедуры
DROP FUNCTION IF EXISTS audit_handler(
    SMALLINT, name, name, HSTORE, HSTORE,
    integer, TEXT, TEXT, TEXT, inet
);
-- добавляем новую
CREATE OR REPLACE FUNCTION audit_handler(
    operation         SMALLINT,
    schema            name,
    table_name        name,
    old_data          HSTORE,
    changes           HSTORE,
    user_type_id      integer,
    user_id           TEXT,
    user_unit_type_id INTEGER,
    user_unit_id      TEXT,
    request_id        TEXT,
    transaction_id    TEXT,
    ip_address        inet
) RETURNS void AS $log_handler$
BEGIN
    RAISE LOG '[AUDIT_LOG] % %.% % % % % % % % old data: (%), changes: (%).', operation, schema, table_name, user_type_id, user_id, user_unit_type_id, user_unit_id, request_id, transaction_id, ip_address, hstore_to_json(old_data), hstore_to_json(changes);
END
$log_handler$
LANGUAGE plpgsql;
