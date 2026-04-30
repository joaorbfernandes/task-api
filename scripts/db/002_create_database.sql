SELECT format(
    'CREATE DATABASE %I OWNER %I ENCODING ''UTF8'' TEMPLATE template0',
    :'DB_NAME',
    :'DB_MIGRATION_USER'
)
WHERE NOT EXISTS (
    SELECT 1
    FROM pg_database
    WHERE datname = :'DB_NAME'
)\gexec