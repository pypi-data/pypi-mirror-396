import argparse
import json
import logging
import os
import sys
from typing import List

from . import DDLManager

logger = logging.getLogger(__name__)


def cli(argv: List[str], dsn: str, ddl_directory: str):
    parser = argparse.ArgumentParser(description='DDL Management CLI')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    status_parser = subparsers.add_parser('status', help='Show migration status')
    status_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    log_parser = subparsers.add_parser('log', help='Show migration log')
    log_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    update_parser = subparsers.add_parser('update', help='Update database')
    update_parser.add_argument('--version', type=str, help='Target version (can omit APPLY- prefix)')
    update_parser.add_argument('--rollback', type=str, default='false', help='Allow rollback (true/false)')
    update_parser.add_argument('--manual', type=str, help='Record manual apply/undo (true/false). If set, only records the change without executing SQL.')
    
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = DDLManager(dsn, ddl_directory)
    
    if args.command == 'status':
        applied, unapplied = manager.status()
        
        if args.json:
            print(json.dumps({
                'applied': applied,
                'unapplied': unapplied
            }, indent=2))
        else:
            print("Applied (and not undone):")
            for version in applied:
                print(f"  {version}")
            print("\nNot applied (or undone):")
            for version in unapplied:
                print(f"  {version}")
    
    elif args.command == 'log':
        log_entries = manager.log()
        
        if args.json:
            for entry in log_entries:
                if entry['time']:
                    entry['time'] = entry['time'].isoformat()
            print(json.dumps(log_entries, indent=2))
        else:
            for entry in log_entries:
                print(f"ID: {entry['id']}")
                print(f"Time: {entry['time']}")
                print(f"Update ID: {entry['update_id']}")
                print(f"Result: {entry['result']}")
                if entry['output']:
                    print(f"Output: {entry['output']}")
                print(f"SQL: {entry['sql'][:100]}..." if len(entry['sql']) > 100 else f"SQL: {entry['sql']}")
                print("-" * 80)
    
    elif args.command == 'update':
        if args.manual is not None:
            if not args.version:
                print("Error: --version is required when using --manual", file=sys.stderr)
                sys.exit(1)
            manual_value = args.manual.lower() in ('true', '1', 'yes', 'on')
            try:
                manager.update(version=args.version, manual=manual_value)
                print(f"Recorded manual {'APPLY' if manual_value else 'REVERT'} for version {args.version}")
            except Exception as e:
                logger.error(f"Failed to record manual change: {e}")
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            rollback = args.rollback.lower() in ('true', '1', 'yes', 'on')
            try:
                manager.update(version=args.version, rollback=rollback)
                print("Update completed successfully")
            except Exception as e:
                logger.error(f"Update failed: {e}")
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)

    sys.exit(0)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    dsn = os.environ.get('POSTGRES_DSN')
    if not dsn:
        print("Error: POSTGRES_DSN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    ddl_directory = os.environ.get('DDL_DIRECTORY')
    if not ddl_directory:
        print("Error: DDL_DIRECTORY environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    cli(sys.argv[1:], dsn, ddl_directory)
