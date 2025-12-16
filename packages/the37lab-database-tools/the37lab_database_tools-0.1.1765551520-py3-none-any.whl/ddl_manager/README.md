# DDL Manager

A Python library for managing PostgreSQL database schema changes (DDL) using APPLY/REVERT migration files.

## Overview

DDL Manager provides a simple, file-based approach to database migrations. It tracks applied migrations in a `db_change` table and supports both forward migrations (APPLY) and rollbacks (REVERT).

## What You Need to Do as a Developer

As a developer using this library, you only need to do two things:

1. **Create files called `APPLY-xxx.ddl`** - These files contain the SQL statements that make changes to your database (like creating tables, adding columns, etc.)

2. **Create files called `REVERT-xxx.ddl`** - These files contain the SQL statements that undo the changes made by the matching `APPLY-xxx.ddl` file (like dropping tables, removing columns, etc.)

That's it! The library handles everything else - tracking which migrations have been applied, running them in the right order, and supporting rollbacks.

**Important**: Every `APPLY-xxx.ddl` file must have a matching `REVERT-xxx.ddl` file with the same version number and description. For example:
- `APPLY-000001-create_users_table.ddl` needs `REVERT-000001-create_users_table.ddl`
- `APPLY-000002-add_email_column.ddl` needs `REVERT-000002-add_email_column.ddl`

## Features

- File-based migration system using `.ddl` files
- Automatic validation that every APPLY file has a matching REVERT file (and vice versa)
- Automatic tracking of applied migrations in `db_change` table
- Support for rollback operations
- CLI interface for common operations
- Programmatic API for integration
- JSON output support for scripting

## Installation

The library uses `psycopg2` for PostgreSQL connectivity. Ensure it's installed:

```bash
pip install psycopg2
```

## File Naming Convention

DDL files must follow a strict naming pattern:

- **APPLY files**: `APPLY-{dddddd}-{text}.ddl`
  - Example: `APPLY-000001-create_users_table.ddl`
  - Example: `APPLY-000002-add_email_column.ddl`

- **REVERT files**: `REVERT-{dddddd}-{text}.ddl`
  - Example: `REVERT-000001-create_users_table.ddl`
  - Example: `REVERT-000002-add_email_column.ddl`

The `{dddddd}` portion is a numeric identifier (at least 6 digits) used for ordering. Files are processed in lexicographical order. The `{text}` portion is descriptive and should match between APPLY and REVERT files for the same migration.

**Important**: Every APPLY file must have a corresponding REVERT file with the same version ID, and vice versa. The library will fail to initialize if there are any mismatches.

## Database Schema

The library automatically creates a `db_change` table if it doesn't exist:

```sql
CREATE TABLE db_change (
    id SERIAL PRIMARY KEY,
    time TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    update_id TEXT NOT NULL,
    sql TEXT NOT NULL,
    output TEXT,
    result TEXT NOT NULL CHECK (result IN ('SUCCESS', 'FAILED'))
);
```

## Usage

### Programmatic API

#### Initialization

```python
from ddl_manager import DDLManager

manager = DDLManager(
    dsn="postgresql://user:password@host:port/database",
    ddl_directory="path/to/ddl/files"
)
```

#### Check Status

```python
applied, unapplied = manager.status()

print("Applied migrations:", applied)
print("Unapplied migrations:", unapplied)
```

Returns a tuple of two sorted lists:
- First list: APPLY migrations that have been applied and not undone
- Second list: APPLY migrations that have not been applied or have been undone

#### Apply Migrations

```python
# Apply all unapplied migrations
manager.update()

# Apply up to a specific version (can omit APPLY- prefix)
manager.update(version="000002")

# Update with rollback support
manager.update(version="000005", rollback=True)

# Record a manually applied migration (without executing SQL)
manager.update(version="000002", manual=True)

# Record a manually undone migration (without executing SQL)
manager.update(version="000002", manual=False)
```

#### View Migration Log

```python
log_entries = manager.log()
for entry in log_entries:
    print(f"{entry['time']}: {entry['update_id']} - {entry['result']}")
```

### CLI Interface

The CLI can be used as a module:

```bash
python -m ddl_manager <command> [options]
```

Set environment variables:
- `POSTGRES_DSN`: PostgreSQL connection string
- `DDL_DIRECTORY`: Path to directory containing DDL files

#### Commands

**Status**

```bash
# Text output
python -m ddl_manager status

# JSON output
python -m ddl_manager status --json
```

**Log**

```bash
# Text output
python -m ddl_manager log

# JSON output
python -m ddl_manager log --json
```

**Update**

```bash
# Update to latest
python -m ddl_manager update

# Update to specific version
python -m ddl_manager update --version=000002

# Update with rollback support
python -m ddl_manager update --version=000005 --rollback=true

# Record a manually applied migration (without executing SQL)
python -m ddl_manager update --version=000002 --manual=true

# Record a manually undone migration (without executing SQL)
python -m ddl_manager update --version=000002 --manual=false
```

#### CLI from Python Code

```python
from ddl_manager.cli import cli
import sys

cli(
    argv=sys.argv[1:],
    dsn="postgresql://user:pass@host/db",
    ddl_directory="restapi/ddl"
)
```

## Update Logic

The `update()` method handles version targeting:

1. **Manual recording (`manual` parameter)**:
   - `update(version="000002", manual=True)`: Records that the APPLY migration was done manually (reads SQL from file and logs as SUCCESS without executing)
   - `update(version="000002", manual=False)`: Records that the REVERT migration was done manually (reads SQL from file and logs as SUCCESS without executing)
   - Useful when migrations are applied outside of the DDL manager

2. **No version specified (`version=None`)**: Applies all unapplied migrations in order (equivalent to updating to the highest available version)

3. **Version specified**:
   - If target version is **lower** than current highest applied and `rollback=False`: Raises exception (prevents accidental rollback)
   - If target version is **lower** than current highest applied and `rollback=True`: 
     - First reverts all applied versions that are higher than target (in reverse order)
     - Then applies any unapplied versions up to and including target
   - If target version is **higher** than current: Applies all unapplied versions up to and including target
   - If target version equals current: No changes needed

The algorithm works by:
- Iterating over the `applied` list (from `status()`) in reverse to revert versions higher than target
- Iterating over the `unapplied` list (from `status()`) to apply versions up to target

## Version Format

When specifying versions:
- You can use the full format: `APPLY-000001-create_table`
- Or omit the `APPLY-` prefix: `000001-create_table`
- Status output always omits the `APPLY-` prefix

## Error Handling

All methods raise exceptions on failure:
- `ValueError`: Invalid version, missing files, etc.
- `Exception`: SQL execution failures, connection errors, etc.

The library uses Python's `logging` module for informational messages and errors.

## Example DDL Files

**APPLY-000001-create_example_table.ddl**
```sql
CREATE TABLE IF NOT EXISTS example_table (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);
```

**REVERT-000001-create_example_table.ddl**
```sql
DROP TABLE IF EXISTS example_table;
```

**APPLY-000002-add_example_column.ddl**
```sql
ALTER TABLE example_table ADD COLUMN IF NOT EXISTS description TEXT;
```

**REVERT-000002-add_example_column.ddl**
```sql
ALTER TABLE example_table DROP COLUMN IF EXISTS description;
```

## Best Practices

1. **Always create matching REVERT files** for each APPLY file
2. **Use descriptive text** in filenames to identify the migration purpose
3. **Test migrations** in a development environment before applying to production
4. **Use transactions** in your DDL files if your PostgreSQL version supports it
5. **Keep DDL files in version control** alongside your application code
6. **Review the log** after applying migrations to ensure success

## Integration Example

```python
from ddl_manager import DDLManager
import os

# Initialize with environment variables
manager = DDLManager(
    dsn=os.environ.get('POSTGRES_DSN'),
    ddl_directory=os.path.join(os.path.dirname(__file__), 'ddl')
)

# Check status before deployment
applied, unapplied = manager.status()
if unapplied:
    print(f"Applying {len(unapplied)} migrations...")
    manager.update()
    print("Migrations applied successfully")
else:
    print("Database is up to date")
```

## Troubleshooting

**Issue**: "DDL file mismatch detected"
- Every APPLY file must have a matching REVERT file with the same version ID
- Every REVERT file must have a matching APPLY file with the same version ID
- Check the error message for specific missing files
- Ensure the version ID (numeric part and text) matches exactly between APPLY and REVERT files

**Issue**: "Version not found"
- Ensure the DDL file exists in the specified directory
- Check that the filename matches the expected pattern

**Issue**: "REVERT file not found" (during update)
- This should not occur if initialization succeeded
- If it does, the DDL directory may have been modified after initialization

**Issue**: "Failed to apply/undo"
- Check the `db_change` table's `output` column for error details
- Verify SQL syntax is correct
- Ensure database user has necessary permissions

**Issue**: Connection errors
- Verify the DSN string is correct
- Check network connectivity to the database
- Ensure PostgreSQL is running and accessible

