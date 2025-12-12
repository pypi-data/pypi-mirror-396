-- добавлена поддержка проброса данных об организации
CREATE OR REPLACE FUNCTION process_audit() RETURNS trigger AS $audit_trigger$
    DECLARE
        changes HSTORE;
        old_data HSTORE;
        operation_code SMALLINT;
        changed_values_len INTEGER;
        user_id TEXT;
        user_type_id INTEGER;
        user_unit_type_id INTEGER;
        user_unit_id TEXT;
        request_id TEXT;
        transaction_id TEXT;
        ip_address inet;
    BEGIN
        operation_code := 0;
        user_id := nullif(current_setting('libaudit.user_id', true),'');
        user_type_id := nullif(current_setting('libaudit.user_type_id', true),'');
        user_unit_type_id := nullif(current_setting('libaudit.user_unit_type_id', true),'');
        user_unit_id := nullif(current_setting('libaudit.user_unit_id', true),'');
        request_id := nullif(current_setting('libaudit.request_id', true),'');
        transaction_id := nullif(current_setting('libaudit.transaction_id', true),'');
        ip_address := nullif(current_setting('libaudit.ip_address', true),'');

        changes := NULL;
        old_data := NULL;

        IF (TG_OP = 'INSERT') THEN
            changes := HSTORE(NEW);
            operation_code := 1;
        ELSIF (TG_OP = 'UPDATE') THEN
            old_data := HSTORE(OLD);
            changes := HSTORE(NEW) - old_data;
            changed_values_len := array_length(akeys(changes),1);
            IF changed_values_len IS NOT NULL OR changed_values_len = 0 THEN
                operation_code := 2;
            END IF;
        ELSIF (TG_OP = 'DELETE') THEN
            old_data := HSTORE(OLD);
            operation_code := 3;
        END IF;

        IF operation_code != 0 THEN
            EXECUTE audit_handler(operation_code, TG_TABLE_SCHEMA, TG_TABLE_NAME, old_data, changes, user_type_id, user_id, user_unit_type_id, user_unit_id, request_id, transaction_id, ip_address);
        END IF;
        RETURN NULL;
    END;
$audit_trigger$ LANGUAGE plpgsql;
