# The37Lab Database Tools

A collection of PostgreSQL database utilities for Python, including DDL migration management and connection pooling.

## Packages

This package contains two main modules:

### `ddl_manager`

A PostgreSQL DDL migration management tool that tracks schema changes using APPLY/REVERT migration files. Provides both a CLI interface and programmatic API.

**Features:**
- File-based migration system using `.ddl` files
- Automatic validation of APPLY/REVERT file pairs
- Migration tracking in database
- Rollback support
- CLI and programmatic interfaces

See [ddl_manager documentation](src/ddl_manager/README.md) for detailed usage.

### `postgres_pool`

PostgreSQL connection pooling and database utilities with convenient abstractions for common database operations.

**Features:**
- Thread-safe connection pooling
- Database conversion utilities (`DBConversion` class)
- JSON column support
- Tag management helpers
- Post-insert hooks

## Installation

### From Source (Development)

```bash
pip install -e .
```

### Regular Install

```bash
pip install .
```

### Dependencies

- Python 3.7+
- `psycopg2-binary>=2.9.0`

## Quick Start

### DDL Manager

```python
from ddl_manager import DDLManager

manager = DDLManager(
    dsn="postgresql://user:password@host:port/database",
    ddl_directory="path/to/ddl/files"
)

# Check status
applied, unapplied = manager.status()

# Apply migrations
manager.update()
```

**CLI Usage:**

Set environment variables:
```bash
export POSTGRES_DSN="postgresql://user:password@host:port/database"
export DDL_DIRECTORY="path/to/ddl/files"
```

Then run:
```bash
ddl_manager status
ddl_manager update
ddl_manager log --json
```

Or use as a module:
```bash
python -m ddl_manager status
```

### Postgres Pool

```python
from postgres_pool import init_pool, get_connection, get_cursor, DBConversion

# Initialize the connection pool with DSN
init_pool("postgresql://user:password@host:port/database")

# Use connection pool
with get_connection() as conn:
    with get_cursor(conn) as cur:
        cur.execute("SELECT * FROM users")
        results = cur.fetchall()

# Use DBConversion for table operations
conv = DBConversion(
    table="users",
    cols=["id", "name", "email"],
    convs={},
    bools=[],
    autos=["id"]
)

with get_cursor() as cur:
    user = conv.select_id(cur, 1)
    new_user = conv.insert(cur, {"name": "John", "email": "john@example.com"})
```

## Environment Variables

### DDL Manager

- `POSTGRES_DSN`: PostgreSQL connection string
- `DDL_DIRECTORY`: Path to directory containing DDL migration files

### Postgres Pool

The connection pool must be initialized explicitly by calling `init_pool(dsn)` before use. No environment variables are required.

## License

MIT

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

