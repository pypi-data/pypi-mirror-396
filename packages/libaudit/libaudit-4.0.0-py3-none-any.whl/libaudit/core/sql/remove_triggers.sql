CREATE OR REPLACE FUNCTION remove_triggers() RETURNS void AS $body$
DECLARE
    target_table RECORD;
BEGIN
    FOR target_table IN
        SELECT table_name, table_schema
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    LOOP
        EXECUTE
           'DROP TRIGGER IF EXISTS audit_trigger ON ' ||
           target_table.table_schema || '.' || target_table.table_name;
    END LOOP;
END
$body$
LANGUAGE plpgsql;

SELECT remove_triggers();

DROP FUNCTION remove_triggers;

DROP FUNCTION IF EXISTS process_audit;
