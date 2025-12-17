import logging
import os
import re
from pathlib import Path
from typing import Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class DDLManager:
    def __init__(self, dsn: str, ddl_directory: str):
        self.dsn = dsn
        self.ddl_directory = Path(ddl_directory)
        if not self.ddl_directory.exists():
            raise ValueError(f"DDL directory does not exist: {ddl_directory}. Current working directory: {os.getcwd()}")
        if not self.ddl_directory.is_dir():
            raise ValueError(f"DDL directory is not a directory: {ddl_directory}. Current working directory: {os.getcwd()}")
        
        self._validate_ddl_files()
        self._init_db()
    
    def _get_connection(self):
        return psycopg2.connect(self.dsn)
    
    def _validate_ddl_files(self):
        apply_pattern = re.compile(r'^APPLY-(\d{6,}-.+?)\.ddl$')
        undo_pattern = re.compile(r'^REVERT-(\d{6,}-.+?)\.ddl$')
        
        apply_versions = set()
        undo_versions = set()
        
        for file_path in self.ddl_directory.glob('*.ddl'):
            filename = file_path.name
            apply_match = apply_pattern.match(filename)
            undo_match = undo_pattern.match(filename)
            
            if apply_match:
                version_id = apply_match.group(1)
                apply_versions.add(version_id)
            elif undo_match:
                version_id = undo_match.group(1)
                undo_versions.add(version_id)
        
        missing_undo = apply_versions - undo_versions
        missing_apply = undo_versions - apply_versions
        
        if missing_undo or missing_apply:
            errors = []
            if missing_undo:
                errors.append(f"APPLY files without matching REVERT: {sorted(missing_undo)}")
            if missing_apply:
                errors.append(f"REVERT files without matching APPLY: {sorted(missing_apply)}")
            raise ValueError(f"DDL file mismatch detected:\n" + "\n".join(errors))
    
    def _init_db(self):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS db_change (
                        id SERIAL PRIMARY KEY,
                        time TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
                        update_id TEXT NOT NULL,
                        sql TEXT NOT NULL,
                        output TEXT,
                        result TEXT NOT NULL CHECK (result IN ('SUCCESS', 'FAILED'))
                    )
                """)
                conn.commit()
                logger.info("db_change table initialized")
    
    def _scan_ddl_files(self) -> Tuple[list[str], dict[str, str], dict[str, str]]:
        apply_files = []
        apply_map = {}
        undo_map = {}
        
        apply_pattern = re.compile(r'^APPLY-(\d{6,}-.+?)\.ddl$')
        undo_pattern = re.compile(r'^REVERT-(\d{6,}-.+?)\.ddl$')
        
        for file_path in self.ddl_directory.glob('*.ddl'):
            filename = file_path.name
            apply_match = apply_pattern.match(filename)
            undo_match = undo_pattern.match(filename)
            
            if apply_match:
                version_id = apply_match.group(1)
                apply_files.append(version_id)
                apply_map[version_id] = str(file_path)
            elif undo_match:
                version_id = undo_match.group(1)
                undo_map[version_id] = str(file_path)
        
        apply_files.sort()
        return apply_files, apply_map, undo_map
    
    def _read_ddl_file(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _get_applied_versions(self) -> list[dict]:
        """
        Return all db_change rows relevant for status() in chronological order.

        We deliberately include both APPLY-* and REVERT-* so that status()
        can derive the effective set of applied versions.
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT update_id, result
                    FROM db_change
                    WHERE update_id LIKE 'APPLY-%' OR update_id LIKE 'REVERT-%'
                    ORDER BY id
                    """
                )
                return cur.fetchall()
    
    def status(self) -> Tuple[list[str], list[str]]:
        all_applies, apply_map, undo_map = self._scan_ddl_files()
        applied_records = self._get_applied_versions()
        
        applied_set = set()
        undone_set = set()
        
        for record in applied_records:
            update_id = record['update_id']
            if update_id.startswith('APPLY-'):
                version_id = update_id[6:]
                if record['result'] == 'SUCCESS':
                    applied_set.add(version_id)
                elif record['result'] == 'FAILED':
                    undone_set.add(version_id)
        
        for record in applied_records:
            update_id = record['update_id']
            if update_id.startswith('REVERT-'):
                version_id = update_id[7:]
                if record['result'] == 'SUCCESS':
                    if version_id in applied_set:
                        applied_set.remove(version_id)
                        undone_set.add(version_id)
        
        applied_and_not_undone = [v for v in all_applies if v in applied_set]
        not_applied_or_undone = [v for v in all_applies if v not in applied_set]
        
        return applied_and_not_undone, not_applied_or_undone
    
    def _normalize_version(self, version: str, all_applies: Optional[list[str]] = None) -> str:
        """
        Normalize a version string.

        - If it starts with 'APPLY-', strip that prefix.
        - If only the numeric part is provided (e.g. '000002') and all_applies is given,
          resolve it to the unique matching '{number}-text' entry in all_applies.
        """
        # Strip APPLY- prefix if present
        if version.startswith('APPLY-'):
            base = version[6:]
        else:
            base = version

        # If we don't have the list of known applies, just return the base
        if all_applies is None:
            return base

        # If it's just digits (no suffix), try to resolve to a unique full version id
        if re.fullmatch(r'\d{6,}', base):
            candidates = [v for v in all_applies if v.startswith(base + '-')]
            if len(candidates) == 1:
                return candidates[0]
            if len(candidates) == 0:
                raise ValueError(f"Version not found: {version}")
            raise ValueError(f"Version '{version}' is ambiguous, matches: {candidates}")

        # For non-numeric inputs, require exact match
        if base not in all_applies:
            raise ValueError(f"Version not found: {version}")
        
        return base
    
    def _execute_ddl(self, update_id: str, sql: str) -> Tuple[str, str]:
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    conn.commit()
                    output = f"Executed successfully"
                    result = 'SUCCESS'
                    logger.info(f"{update_id} executed successfully")
                    return output, result
        except Exception as e:
            error_msg = str(e)
            logger.error(f"{update_id} failed: {error_msg}")
            return error_msg, 'FAILED'
    
    def _log_change(self, update_id: str, sql: str, output: str, result: str):
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO db_change (update_id, sql, output, result)
                    VALUES (%s, %s, %s, %s)
                """, (update_id, sql, output, result))
                conn.commit()
    
    def _get_highest_in_db_change(self) -> Optional[str]:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT update_id 
                    FROM db_change 
                    WHERE update_id LIKE 'APPLY-%' AND result = 'SUCCESS'
                    ORDER BY id DESC
                    LIMIT 1
                """)
                row = cur.fetchone()
                if row:
                    update_id = row[0]
                    return update_id[6:]
                return None
    
    def update(self, version: Optional[str] = None, rollback: bool = False, manual: Optional[bool] = None):
        all_applies, apply_map, undo_map = self._scan_ddl_files()
        
        # Manual recording path: just log APPLY/REVERT without executing SQL.
        if manual is not None and version is not None:
            normalized_version = self._normalize_version(version, all_applies)
            # _normalize_version raises if version not found or ambiguous
            
            if manual:
                if normalized_version not in apply_map:
                    raise ValueError(f"APPLY file not found for version: {version}")
                file_path = apply_map[normalized_version]
                sql = self._read_ddl_file(file_path)
                update_id = f"APPLY-{normalized_version}"
                output = "Manually applied by user"
            else:
                if normalized_version not in undo_map:
                    raise ValueError(f"REVERT file not found for version: {version}")
                file_path = undo_map[normalized_version]
                sql = self._read_ddl_file(file_path)
                update_id = f"REVERT-{normalized_version}"
                output = "Manually reverted by user"
            
            self._log_change(update_id, sql, output, 'SUCCESS')
            logger.info(f"Recorded manual {update_id}")
            return

        applied, unapplied = self.status()

        # Determine target version (if any) and enforce rollback rules
        target: Optional[str] = None
        if version is not None:
            normalized_version = self._normalize_version(version, all_applies)
            # _normalize_version may raise if ambiguous / not found
            target = normalized_version

            if applied:
                current_highest = applied[-1]
                if normalized_version < current_highest and not rollback:
                    raise ValueError(
                        f"Target version {version} is lower than current applied {current_highest} "
                        f"and rollback=False"
                    )

        # a) If target specified, revert applied versions higher than target
        if target is not None:
            for v in reversed(applied):
                if v > target:
                    if v not in undo_map:
                        raise ValueError(f"REVERT file not found for version: {v}")
                    undo_file = undo_map[v]
                    sql = self._read_ddl_file(undo_file)
                    update_id = f"REVERT-{v}"

                    output, result = self._execute_ddl(update_id, sql)
                    self._log_change(update_id, sql, output, result)

                    if result == 'FAILED':
                        raise Exception(f"Failed to revert {update_id}: {output}")
                else:
                    break

            # Refresh state after reverts
            applied, unapplied = self.status()

        # b) Apply forward
        if target is None:
            forward_versions = unapplied
        else:
            forward_versions = [v for v in unapplied if v <= target]

        for v in forward_versions:
            if v not in apply_map:
                raise ValueError(f"APPLY file not found for version: {v}")
            apply_file = apply_map[v]
            sql = self._read_ddl_file(apply_file)
            update_id = f"APPLY-{v}"

            output, result = self._execute_ddl(update_id, sql)
            self._log_change(update_id, sql, output, result)

            if result == 'FAILED':
                raise Exception(f"Failed to apply {update_id}: {output}")
    
    def log(self) -> list[dict]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, time, update_id, sql, output, result
                    FROM db_change
                    ORDER BY id
                """)
                return [dict(row) for row in cur.fetchall()]

