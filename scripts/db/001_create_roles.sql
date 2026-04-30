SELECT format(
    'CREATE ROLE %I LOGIN PASSWORD %L',
    :'DB_MIGRATION_USER',
    :'DB_MIGRATION_PASSWORD'
)
WHERE NOT EXISTS (
    SELECT 1
    FROM pg_roles
    WHERE rolname = :'DB_MIGRATION_USER'
)\gexec

SELECT format(
    'CREATE ROLE %I LOGIN PASSWORD %L',
    :'DB_APP_USER',
    :'DB_APP_PASSWORD'
)
WHERE NOT EXISTS (
    SELECT 1
    FROM pg_roles
    WHERE rolname = :'DB_APP_USER'
)\gexec