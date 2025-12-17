from datetime import datetime, timedelta, date
import functools
import json
from contextlib import contextmanager
import threading
import traceback

import logging
import psycopg2
from psycopg2 import pool, extras
from psycopg2.extras import Json

connection = None

psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)

_pool = None
_pool_dsn = None
_logging = False
_sql_log = logging.getLogger("psycopg2.sql")

def init_pool(dsn: str, minconn: int = 1, maxconn: int = 100, logging = False):
    """Initialize the connection pool with the provided DSN.
    
    Args:
        dsn: PostgreSQL connection string (DSN)
        minconn: Minimum number of connections in the pool
        maxconn: Maximum number of connections in the pool
    """
    global _pool, _pool_dsn, _logging
    _pool_dsn = dsn
    _logging = logging
    if not _logging:
        _pool = psycopg2.pool.ThreadedConnectionPool(minconn, maxconn, dsn)
    return _pool

def pool():
    """Get the connection pool. Raises RuntimeError if not initialized."""
    global _pool
    if _pool is None:
        raise RuntimeError("Connection pool not initialized. Call init_pool(dsn) first.")
    return _pool


def reconnect(dsn: str = None):
    """Create a direct connection. Uses pool DSN if dsn is not provided."""
    global connection, _pool_dsn
    if dsn is None:
        if _pool_dsn is None:
            raise RuntimeError("No DSN provided and pool not initialized. Call init_pool(dsn) first or provide dsn parameter.")
        dsn = _pool_dsn
    connection = psycopg2.connect(dsn)
    return connection


connfunc = None

__connections = {}
__connections_lock = threading.Lock()

@contextmanager
def get_cursor(connection=None):
    with get_connection() as conn:
        psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)
        if conn.autocommit:
            conn.autocommit = False
        cursor = conn.cursor()
        yield cursor
        cursor.execute('ROLLBACK')
        cursor.close()
            
_last_dump = datetime.now()            

@contextmanager
def get_connection():
    if _logging:
        conn = psycopg2.connect(
            _pool_dsn,
            connection_factory=extras.LoggingConnection,
        )
        conn.initialize(_sql_log)
        yield conn
        conn.close()
        return
        
    global _last_dump
    nconn = None
    stacktrace_list = traceback.format_stack()
    with __connections_lock:
        nconn = max(__connections.keys(), default=-1) + 1
        __connections[nconn] = (datetime.now(), stacktrace_list)
        
        if len(__connections) > 100 and datetime.now() - _last_dump > timedelta(seconds=300):
            print(f'DUMP OF CONNECTIONS: {len(__connections)}')

            for k, v in sorted(__connections.items(), key=lambda item: item[1][0]):
                connection_time, stacktrace = v
                print(f'Connection ID: {k}')
                print(f'Connection Time: {connection_time}')
                print('Stacktrace:')
                for line in stacktrace:
                    print('  ' + line)
                print('--------------------------------')
            _last_dump = datetime.now()
            print('=================================')
        
    conn = pool().getconn()
    
    yield conn
    pool().putconn(conn)
    with __connections_lock:
        __connections.pop(nconn)


def db_to(arg):
    return arg


def db_from(arg):
    return arg


def _j(c):
    if isinstance(c, tuple):
        return c[0]
    return c


def _d(c):
    if isinstance(c, tuple):
        return c[1]
    return c


def post_insert_hook(table_conv):
    """Decorator to register a function as a post-insert hook for a specific table.
    
    Usage:
        @post_insert_hook(stories_api.conv)
        def on_story_insert(cursor, inserted_data, original_data):
            # Your logic here
            pass
    """
    def decorator(func):
        table_conv.add_post_insert_hook(func)
        return func
    return decorator


class DBConversion:
    def __init__(self, table, cols, convs, bools, autos, jsons=None, primary_key=None):
        self.table = '"' + table + '"'
        self.cols = cols
        self.convs = convs
        self.bools = bools
        self.autos = autos
        self.jsons = jsons or []
        if primary_key is None:
            primary_key = ['id']
        if isinstance(primary_key, str):
            primary_key = [primary_key]
        self.primary_key = primary_key
        self._post_insert_hooks = []

    def _pk_where_clause(self, alias=None):
        if alias is None:
            alias = self.table
        return ' AND '.join([f'{alias}."{pk}"=%s' for pk in self.primary_key])

    def _normalize_pk(self, pk):
        if isinstance(pk, dict):
            return tuple(pk[col] for col in self.primary_key)
        if len(self.primary_key) == 1:
            if isinstance(pk, (list, tuple)):
                if len(pk) != 1:
                    raise ValueError('Primary key length mismatch')
                return tuple(pk)
            return (pk,)
        if not isinstance(pk, (list, tuple)) or len(pk) != len(self.primary_key):
            raise ValueError('Primary key length mismatch')
        return tuple(pk)

    def _jsoncols(self):
        return [_j(c) for c in self.cols]

    def _dbcols(self):
        return [_j(c) for c in self.cols]

    def from_db(self, res, start_index=0):
        ret = {}
        index = start_index
        for col in self.cols:
            v = res[index]
            if v:
                if _j(col) in self.bools:
                    v = not not v
                if _j(col) in self.convs:
                    v = db_from(v)
                if _j(col) in self.jsons:
                    if isinstance(v, memoryview):
                        v = bytes(v)
                    if isinstance(v, (bytes, bytearray)):
                        v = v.decode('utf-8', errors='ignore')
                    if isinstance(v, str):
                        trimmed = v.strip()
                        if trimmed:
                            try:
                                v = json.loads(trimmed)
                            except json.JSONDecodeError:
                                v = trimmed
                        else:
                            v = None
            ret[_j(col)] = v
            index += 1
        return ret

    def to_db(self, res):
        ret = []
        index = 0
        for col in self.cols:
            if _d(col) in self.primary_key:
                continue
            v = res.get(_j(col))
            if _j(col) in self.convs and v is not None:
                v = db_to(v)
            if _j(col) in self.jsons:
                v = json.dumps(v) if v is not None else None
            ret += [v]
            index += 1
        extra_keys = [key for key in res if key not in [_j(col) for col in self.cols]]
        if extra_keys:
            print(f'UNKNOWN COLUMNS for {self.table}: ', extra_keys)
        return tuple(ret)

    def _to_db_all(self, res):
        """Convert all columns (including primary key) for insert/upsert."""
        ret = []
        for col in self.cols:
            v = res.get(_j(col))
            if _j(col) in self.convs and v is not None:
                v = db_to(v)
            if _j(col) in self.jsons:
                v = json.dumps(v) if v is not None else None
            ret.append(v)
        return tuple(ret)

    def insert_cols(self):
        return ','.join([_d(c) for c in self.cols if _d(c) not in self.primary_key])

    def insert_placeholders(self):
        return ','.join(['%s' for c in self.cols if _d(c) not in self.primary_key])

    def ret_cols(self, alias=None):
        if alias is None:
            alias = self.table
        return ','.join([f'{alias}."{_d(c)}"' for c in self.cols])

    def update_set(self, data):
        names = []
        l = [c for c in self.cols if _d(c) not in self.primary_key and not _j(c) in self.autos]
        for param in l:
            if _j(param) in data:
                names += [_d(param)]
        return ','.join([f'"{n}"=%s' for n in names])

    def update_data(self, id, data):
        params = []
        l = [_j(c) for c in self.cols if _d(c) not in self.primary_key and not _j(c) in self.autos]
        for param in l:
            if param in data:
                value = data[param]
                if param in self.convs and value is not None:
                    value = db_to(value)
                if param in self.jsons:
                    value = json.dumps(value) if value is not None else None
                params += [value]
        params += list(self._normalize_pk(id))
        return tuple(params)

    def add_post_insert_hook(self, func):
        """Register a function to be called after insert operations.
        
        Args:
            func: Function that takes (cursor, inserted_data, original_data) as arguments
        """
        self._post_insert_hooks.append(func)
    
    def insert(self, cur, data):
        print('INSERT INTO ' + self.table + ' '
                                            '(' + self.insert_cols() + ') '
                                                                       'VALUES (' + self.insert_placeholders() + ') '
                                                                                                                 'RETURNING ' + self.ret_cols() + ';')
        cur.execute(
            'INSERT INTO ' + self.table + ' '
                                          '(' + self.insert_cols() + ') '
                                                                     'VALUES (' + self.insert_placeholders() + ') '
                                                                                                               'RETURNING ' + self.ret_cols() + ';',
            self.to_db(data)
        )
        np = cur.fetchone()
        result = self.from_db(np)
        
        # Call post-insert hooks
        for hook in self._post_insert_hooks:
            try:
                hook(cur, result, data)
            except Exception as e:
                print(f"Post-insert hook error for {self.table}: {e}")
        
        return result

    def select_all(self, cur):
        cur.execute('SELECT ' + self.ret_cols() + ' FROM ' + self.table + ';')
        nps = cur.fetchall()
        return [self.from_db(np) for np in nps]

    def select_all_where(self, cur, where, data):
        cur.execute('SELECT ' + self.ret_cols() + ' FROM ' + self.table + ' WHERE ' + where, data)
        nps = cur.fetchall()
        return [self.from_db(np) for np in nps]

    def select_one_where(self, cur, where, data):
        cur.execute('SELECT ' + self.ret_cols() + ' FROM ' + self.table + ' WHERE ' + where + ' LIMIT 1', data)
        np = cur.fetchone()
        return self.from_db(np) if np else None

    def select_id(self, cur, id):
        cur.execute('SELECT ' + self.ret_cols() + ' FROM ' + self.table + ' WHERE ' + self._pk_where_clause(self.table),
                    self._normalize_pk(id))
        np = cur.fetchone()
        if not np:
            return None
        return self.from_db(np)

    def update(self, cur, id, data):
        update_string = self.update_set(data)
        if update_string:
            cur.execute(f'UPDATE {self.table} SET {update_string} WHERE {self._pk_where_clause(self.table)} RETURNING {self.ret_cols()}',
                self.update_data(id, data))
        else:
            cur.execute(f'SELECT {self.ret_cols()} FROM {self.table} WHERE {self._pk_where_clause(self.table)}',
                        self._normalize_pk(id))
        np = cur.fetchone()
        if not np:
            return None
        return self.from_db(np)

    def delete(self, cur, id):
        cur.execute('DELETE FROM ' + self.table + ' WHERE ' + self._pk_where_clause(self.table) + ' RETURNING 1;',
                    self._normalize_pk(id))
        deleted = cur.fetchone()
        return not not deleted

    def upsert(self, cur, data):
        """Insert or update a row based on the primary key.

        Expects `data` to contain all primary key fields using the JSON names.
        """
        all_db_cols = [_d(c) for c in self.cols]
        pk_cols = list(self.primary_key)
        non_pk_db_cols = [c for c in all_db_cols if c not in pk_cols]

        insert_cols = ','.join(all_db_cols)
        placeholders = ','.join(['%s' for _ in all_db_cols])
        update_set = ','.join([f'"{c}"=EXCLUDED."{c}"' for c in non_pk_db_cols])
        conflict_cols = ','.join([f'"{c}"' for c in pk_cols])

        sql = (
            f'INSERT INTO {self.table} ({insert_cols}) '
            f'VALUES ({placeholders}) '
            f'ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_set} '
            f'RETURNING {self.ret_cols()};'
        )
        cur.execute(sql, self._to_db_all(data))
        np = cur.fetchone()
        return self.from_db(np) if np else None


def adapt_date_iso(val):
    """Adapt date to ISO 8601 date."""
    return val.isoformat()


def adapt_datetime_iso(val):
    """Adapt datetime to timezone-naive ISO 8601 date."""
    return val.isoformat()


def adapt_datetime_epoch(val):
    """Adapt datetime to Unix timestamp."""
    return int(val.timestamp())


def convert_date(val):
    """Convert ISO 8601 date to date object."""
    return date.fromisoformat(val.decode())


def convert_datetime(val):
    """Convert ISO 8601 datetime to datetime object."""
    return datetime.fromisoformat(val.decode())


def convert_timestamp(val):
    """Convert Unix epoch timestamp to datetime object."""
    return datetime.fromtimestamp(int(val))


def dt(t):
    return tuple(t if t else [-100000000000000])


def get_tags(cur, tags, create=False):
    tags = [ t for t in tags if not isinstance(t, int) ]
    if not tags:
        return {}
    cur.execute(f'SELECT id, name FROM tag WHERE name IN %s', (dt(tags),))
    d = { name: id for (id, name) in cur.fetchall() }
    defined = set(tags)
    defined.difference_update(set(d.keys()))
    if create and defined:
        cur.execute(f'INSERT INTO tag (name) VALUES {",".join(["(%s)" for _ in defined])} RETURNING name, id', tuple(defined))
        d |= { name: id for (name,id) in cur.fetchall() }
    return d

def _get_param(data, key):
    if isinstance(data.get(key), str):
        return [data.get(key)]
    return data.get(key, [])

def set_tags(cur, table, id, data, tagmap=None, remove=True):
    _tags = _get_param(data, 'tags')
    _tags_add = _get_param(data, 'tags_add')
    _tags_remove = _get_param(data, 'tags_remove')
    if not tagmap:
        tagmap = get_tags(cur, _tags + _tags_add + _tags_remove, create=True)

    tags = [t if type(t) == int else tagmap[t] for t in _tags]
    tags_add = [t if type(t) == int else tagmap[t] for t in _tags_add]
    tags_remove = [t if type(t) == int else tagmap[t] for t in _tags_remove]

    tags_add = tags+tags_add
    if tags or tags_add:
        cur.execute(f'INSERT INTO {table}_tag ({table}_id, tag_id) VALUES {",".join(["(%s,%s)" for _ in tags_add])} ON CONFLICT DO NOTHING',
                    tuple(x for xs in [[id, tag] for tag in tags_add] for x in xs))
    if remove and 'tags' in data:
        cur.execute(f'DELETE FROM {table}_tag WHERE {table}_id=%s and tag_id NOT IN %s',
                    (id, dt(tags_add)))
    if tags_remove:
        cur.execute(
            f'DELETE FROM {table}_tag WHERE {table}_id=%s and tag_id IN %s', (id,dt(tags_remove)))
    cur.execute(f'SELECT tag.id, tag.name FROM tag JOIN {table}_tag ON {table}_tag.tag_id=tag.id WHERE {table}_id=%s', (id,))
    return { name:id for (id,name) in cur.fetchall() }


def set_data_tags(cur, table, np, data, tagmap=None):
    v = set_tags(cur, table, np['id'], data, tagmap)
    np['tags'] = list(v.keys())
    np['tag_ids'] = list(v.values())

def tag_fill(cur, l, table):
    d = {e['id']: e for e in l if isinstance(e['id'], int)}
    for e in d.values():
        e['tags'] = []
        e['tag_ids'] = []
    if not d:
        return
    cur.execute(f'SELECT {table}_id, tag.id, tag.name FROM {table}_tag JOIN tag on tag.id = {table}_tag.tag_id WHERE {table}_id IN %s', (dt(d.keys()),))
    for (id, tag_id, name) in cur.fetchall():
        d[id]['tags'] += [ name ]
        d[id]['tag_ids'] += [ tag_id ]

def tag_clean_dict(d):
    return {k: v for k, v in d.items() if k not in ('tags', 'tags_add', 'tags_remove')}