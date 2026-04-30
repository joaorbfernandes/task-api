# Database Bootstrap (Development)

These scripts are responsible for **environment bootstrap**, not for schema migrations.

## Responsibilities

Bootstrap handles:

- creating PostgreSQL roles/users
- creating the target database
- configuring schema ownership and grants
- configuring default privileges for future tables and sequences

Alembic handles:

- creating tables
- evolving schema objects over time
- versioning schema changes

## Roles

The project uses two PostgreSQL users per environment.

### `task_api_migrator_dev`

Used for:

- Alembic migrations
- schema creation
- schema evolution

This role owns the target database schema objects managed by migrations.

### `task_api_app_dev`

Used for:

- application runtime
- reading and writing application data

This role can use the `public` schema, but cannot create objects in it.

## Files

### `001_create_roles.sql`

Creates the PostgreSQL roles if they do not already exist:

- `task_api_migrator_dev`
- `task_api_app_dev`

### `002_create_database.sql`

Creates the target database if it does not already exist:

- `task_api_dev`

The database owner is:

- `task_api_migrator_dev`

### `003_grants.sql`

Configures:

- `public` schema ownership
- runtime CRUD privileges for `task_api_app_dev`
- default privileges for future tables and sequences created by `task_api_migrator_dev`

### `bootstrap_dev.sh`

Loads values from `.env` and executes the bootstrap SQL scripts in the correct order.

It expects the PostgreSQL admin user to be provided at execution time.

## Environment Variables

The bootstrap script reads `.env`

The PostgreSQL admin user is not stored in `.env`

It must be provided when the script is executed, for example:

```bash
DB_BOOTSTRAP_ADMIN_USER=postgres ./scripts/db/bootstrap_dev.sh
```

## Before Running Bootstrap

Make sure PostgreSQL is already running locally and reachable at the configured DB_HOST and DB_PORT.

The bootstrap script does not start PostgreSQL for you. It assumes the database server is already available.

## Execution Order

The bootstrap process must run in this order:

1. 001_create_roles.sql
2. 002_create_database.sql
3. 003_grants.sql

The bootstrap_dev.sh script already executes them in this order.

## How to Run
Make sure the script is executable:
```bash
chmod +x scripts/db/bootstrap_dev.sh
```

Then run:
```bash
DB_BOOTSTRAP_ADMIN_USER=postgres ./scripts/db/bootstrap_dev.sh
```

You can also use another PostgreSQL admin user, for example:

```bash
DB_BOOTSTRAP_ADMIN_USER=username ./scripts/db/bootstrap_dev.sh
```

## Next Step After Bootstrap

Bootstrap does not create the application tables.

After bootstrap completes successfully, apply the Alembic migrations:

```bash
alembic upgrade head
```