#!/usr/bin/env bash
set -euo pipefail

if [ ! -f ".env" ]; then
  echo "Error: .env file not found in project root."
  exit 1
fi

set -a
source .env
set +a

required_vars=(
  DB_HOST
  DB_PORT
  DB_NAME
  DB_APP_USER
  DB_APP_PASSWORD
  DB_MIGRATION_USER
  DB_MIGRATION_PASSWORD
)

for var_name in "${required_vars[@]}"; do
  if [ -z "${!var_name:-}" ]; then
    echo "Error: Required environment variable '$var_name' is not set."
    exit 1
  fi
done

if [ -z "${DB_BOOTSTRAP_ADMIN_USER:-}" ]; then
  echo "Error: DB_BOOTSTRAP_ADMIN_USER is not set."
  echo "Run like:"
  echo "DB_BOOTSTRAP_ADMIN_USER=postgres ./scripts/db/bootstrap_dev.sh"
  exit 1
fi

read -s -p "PostgreSQL admin password: " DB_BOOTSTRAP_ADMIN_PASSWORD
echo

export PGPASSWORD="$DB_BOOTSTRAP_ADMIN_PASSWORD"

echo "==> Checking PostgreSQL admin connection..."

if ! psql \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_BOOTSTRAP_ADMIN_USER" \
  -d postgres \
  -c "SELECT 1;" >/dev/null 2>&1; then
  echo "Error: Could not connect to PostgreSQL at ${DB_HOST}:${DB_PORT} as admin user '${DB_BOOTSTRAP_ADMIN_USER}'."
  echo "Make sure the PostgreSQL server is already running and accepting connections."
  echo "If PostgreSQL is stopped, start it first and run the bootstrap again."
  exit 1
fi

echo "==> Creating roles if needed..."
psql -v ON_ERROR_STOP=1 \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_BOOTSTRAP_ADMIN_USER" \
  -d postgres \
  -v DB_MIGRATION_USER="$DB_MIGRATION_USER" \
  -v DB_MIGRATION_PASSWORD="$DB_MIGRATION_PASSWORD" \
  -v DB_APP_USER="$DB_APP_USER" \
  -v DB_APP_PASSWORD="$DB_APP_PASSWORD" \
  -f scripts/db/001_create_roles.sql

echo "==> Creating database if needed..."
psql -v ON_ERROR_STOP=1 \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_BOOTSTRAP_ADMIN_USER" \
  -d postgres \
  -v DB_NAME="$DB_NAME" \
  -v DB_MIGRATION_USER="$DB_MIGRATION_USER" \
  -f scripts/db/002_create_database.sql

echo "==> Applying grants and default privileges..."
psql -v ON_ERROR_STOP=1 \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_BOOTSTRAP_ADMIN_USER" \
  -d "$DB_NAME" \
  -v DB_NAME="$DB_NAME" \
  -v DB_MIGRATION_USER="$DB_MIGRATION_USER" \
  -v DB_APP_USER="$DB_APP_USER" \
  -f scripts/db/003_grants.sql

echo "==> Bootstrap completed successfully."
echo "==> Next step: apply all pending migrations with: alembic upgrade head"