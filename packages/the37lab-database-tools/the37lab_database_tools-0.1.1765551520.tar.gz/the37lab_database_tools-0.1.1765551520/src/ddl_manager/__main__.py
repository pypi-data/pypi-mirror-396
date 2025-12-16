import logging
import os
import sys

from .cli import cli

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    dsn = os.environ.get('POSTGRES_DSN')
    if not dsn:
        print("Error: POSTGRES_DSN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    ddl_directory = os.environ.get('DDL_DIRECTORY')
    if not ddl_directory:
        print("Error: DDL_DIRECTORY environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    cli(sys.argv[1:], dsn, ddl_directory)

