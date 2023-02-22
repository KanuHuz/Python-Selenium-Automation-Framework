# -*- coding: utf-8 -*-

try:
    import cPickle as cPickle
except ImportError:
    import pickle as cPickle

try:
    unicode = unicode
except NameError:
    unicode = str

try:
    long = long
except NameError:
    long = int

from pyframework.util.cache.base_cache import CacheDriver
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from pyframework.core.server.singleton_pyframework import SingletonPyframework
from pyframework.util.datetime.timestamp import TimestampHelper
from pyframework.util.system import SystemHelper
from pyframework.util.string.cast import CastHelper
from pyframework.util.string.serialization import SerializationHelper
from pyframework.util.logger import LoggerUtil
import os


class _Empty(object):
    pass


class _Pickled(object):
    pass


pickled = _Pickled()
empty = _Empty()


class SqliteCacheDriver(CacheDriver):

    @staticmethod
    def getpool(host=None, port=None, database=None, user=None, password=None):

        pyframework_props = SingletonPyframework().properties
        convert_unicode = pyframework_props._parser.get("cache", "convert_unicode", None)
        echo = pyframework_props._parser.get("cache", "echo", None)
        echo_pool = pyframework_props._parser.get("cache", "echo_pool", None)
        pool_size = pyframework_props._parser.get("cache", "pool_size", None)
        pool_recycle = pyframework_props._parser.get("cache", "pool_recycle", None)
        max_overflow = pyframework_props._parser.get("cache", "max_overflow", None)
        pool_timeout = pyframework_props._parser.get("cache", "pool_timeout", None)
        isolation_level = pyframework_props._parser.get("cache", "isolation_level", None)

        app_path = pyframework_props.server.application_path

        db_dir_path = app_path + '/' + 'resource' + '/' + 'database' + '/' + 'sqlite'

        if os.path.exists(db_dir_path) and os.path.isdir(db_dir_path):
            pass
        else:
            os.makedirs(db_dir_path)

        path = '%s/%s.db' \
               % (db_dir_path, database)

        connection_args = {'check_same_thread': False}
        connection_url = 'sqlite:///%s' % path

        params = {
            'convert_unicode': convert_unicode if convert_unicode is not None else True,
            'echo': echo if echo is not None else False,
            'echo_pool': echo_pool if echo_pool is not None else False,
            'pool_size': pool_size if pool_size is not None else 16,
            'poolclass': QueuePool,
            'pool_recycle': pool_recycle if pool_recycle is not None else 3600,
            'max_overflow': max_overflow if max_overflow is not None else -1,
            'pool_timeout': pool_timeout if pool_timeout is not None else 30,
            'connect_args': connection_args
        }

        if isolation_level is not None:
            params['isolation_level'] = isolation_level

        engine = create_engine(connection_url, **params)

        driver = SqliteCacheDriver()
        driver._reference_count = 0
        driver._engine = engine

        return driver

    def begin(self):
        connection = self.getconn()
        transaction = connection.begin()

        return TransactionProxy(self, connection, transaction)

    def commit(self, proxy, return_connection=True):
        result = proxy.transaction.commit()

        if return_connection:
            proxy.connection.close()

        return result

    def rollback(self, proxy, return_connection=True):
        result = proxy.transaction.rollback()

        if return_connection:
            proxy.connection.close()

        return result

    def close(self, proxy):
        return proxy.connection.close()

    def _bind_helper(self, conn, sql, bind):
        """
          tuple style binding -> dict style binding

        if conn and \
                getattr(conn, 'engine', None) and \
                getattr(getattr(conn, 'engine'), 'url', None) and \
                getattr(getattr(conn, 'engine'), 'url').drivername == 'sqlite':
            if sql.find('%s') != -1 and isinstance(bind, (tuple, list)):
                param = tuple([':param_%s' % k for k in range(len(bind))])
                bind = dict([('param_%s' % k, bind[k]) for k in range(len(bind))])
                sql = sql % param
        """

        return sql, bind

    def execute(self, sql, bind=None, cache=False):

        conn = self.getconn()
        conn = conn.connection if isinstance(conn, TransactionProxy) else conn

        sql, bind = self._bind_helper(conn, sql, bind)

        if isinstance(bind, dict):
            result = conn.execute(sql, **bind)
        elif isinstance(bind, list):
            result = conn.execute(sql, *bind)
        elif bind is not None:
            result = conn.execute(sql, (bind,))
        else:
            result = conn.execute(sql)

        conn.close()

        return result

    def row(self, sql, bind=None, cache=False, *args, **kwargs):

        conn = self.getconn()
        result = self.execute(sql, bind, cache=cache)
        to_dict = True if 'to_dict' in kwargs else False

        row = None

        for r in result:
            row = r if not to_dict else dict(r.items())
            break

        conn.close()

        return row

    def rows(self, sql, bind=None, cache=False, *args, **kwargs):

        conn = self.getconn()
        result = self.execute(sql, bind, cache=cache)
        to_dict = True if 'to_dict' in kwargs else False

        rows = []

        for r in result:
            rows.append(r if not to_dict else dict(r.items()))

        conn.close()

        return rows

    def scalar(self, sql, bind=None, cache=False):

        conn = self.getconn()
        result = self.execute(sql, bind, cache=cache)
        value = result.scalar() if result else None

        conn.close()

        return value

    def _table_name(self):
        return ('table_sqlite_cache').replace('/', '_').replace('.', '_')

    def create_table(self, clear=False):
        table_name = self._table_name()

        proxy = self.begin( )
        proxy.execute("""
            CREATE TABLE IF NOT EXISTS %(table_name)s (
                key TEXT PRIMARY KEY ASC NOT NULL,
                val TEXT,
                type INT,
                expire_at integer DEFAULT NULL
            )
        """ % {'table_name': table_name})
        proxy.execute('CREATE INDEX IF NOT EXISTS %(table_name)s_key_idx ON %(table_name)s (expire_at);'
                      % {'table_name': table_name})

        if clear:
            proxy.execute('DELETE FROM %(table_name)s' % {'table_name': table_name})

        proxy.commit()

    @staticmethod
    def _types():
        return {
            1: str,
            2: unicode,
            3: int,
            4: long,
            5: float,
            6: list,
            7: tuple,
            8: dict,
            9: pickled
        }

    @staticmethod
    def _types_required_serialize():
        return {
            6: list,
            7: tuple,
            8: dict
        }

    @staticmethod
    def _type_to_key(t):
        for key, val in SqliteCacheDriver._types().items():
            if t == val:
                return key

        return None

    @staticmethod
    def _key_to_type(key):
        types = SqliteCacheDriver._types()

        return types[key] if key in types else None

    @staticmethod
    def _val_to_type(val):
        return SqliteCacheDriver._type_to_key(val.__class__)

    def getconn(self):
        return self._engine.connect()

    def flushall(self):
        for e in self.rows("""
                SELECT
                    `name`
                FROM
                    sqlite_master
                WHERE
                    `type` = 'table'""", None, cache=True):
            self.execute(
                'DROP TABLE IF EXISTS {table_name}'.replace('{table_name}', e['name']),
                None,

                cache=True)

    def flushdb(self):
        return self.execute(
            'DROP TABLE IF EXISTS {table_name}'.replace('{table_name}', self._table_name()),
            None,

            cache=True)

    def _referenced(self):
        self._reference_count += 1
        self._try_clear_expired()

    def _try_clear_expired(self):
        if self._reference_count > 100000:
            self._exec_clear_expired()

    def _exec_clear_expired(self):
        self._reference_count = 0

        return self.execute(
            'DELETE FROM {table_name} WHERE expire_at < ?'.replace('{table_name}', self._table_name()),
            TimestampHelper.now(), cache=True)

    def get(self, key, expire_in=None, retry_count=0, raise_error=False):
        self._referenced()

        try:
            result = self.row(
                """SELECT
                        *
                    FROM
                        {table_name}
                    WHERE
                        key = ?""".replace('{table_name}', self._table_name()),
                key, cache=True)

        except OperationalError as e:
            # Retry (hack for sqlite database locking)
            if retry_count:
                import time
                time.sleep(0.02)

                try:
                    self.create_table()
                except:
                    pass

                return self.get(key, retry_count - 1)

            else:
                if raise_error:
                    raise e

                else:
                    return None

        if result:
            if result['expire_at'] and result['expire_at'] < TimestampHelper.now():
                return None
            else:
                if expire_in:
                    self.expire(key, expire_in)

                type = self._key_to_type(result['type'])

                if result['type'] in self._types_required_serialize():
                    try:
                        ret = SerializationHelper.serialize(
                            result['val'], method='json', raise_exception=True)

                        if type is tuple:
                            return tuple(ret)

                        else:
                            return ret

                    except:  # Failed to json deserialization
                        LoggerUtil.exception_by_logger("pyframework", result)
                        return None

                elif type is pickled:
                    try:
                        if SystemHelper.py_version() <= 2:
                            return cPickle.loads(CastHelper.string(result['val']))
                        else:
                            return cPickle.loads(result['val'])

                    except:  # Failed to unpickling
                        LoggerUtil.exception_by_logger("pyframework", result)
                        return None

                elif type is str:
                    return CastHelper.string(result['val'])

                elif type is unicode:
                    return CastHelper.unicode(result['val'])

                elif type is int:
                    return int(result['val'])

                elif type is long:
                    return long(result['val'])

                elif type is float:
                    return float(result['val'])

                else:
                    return result['val']

        else:
            return None

    # def set(self, key, val, expire_in=1209600, retry_count=10, raise_error=False):
    def set(self, key, val, expire_in=None, retry_count=10, raise_error=False):
        if expire_in is not None:
            expire_in = TimestampHelper.now() + expire_in

        type = self._val_to_type(val)
        val_serialized = empty

        if not type or type in self._types_required_serialize():
            try:
                try:
                    if type:
                        val_serialized = SerializationHelper.serialize(
                            val, method='json', raise_exception=True)

                    else:
                        raise Exception()

                except:
                    val_serialized = cPickle.dumps(val)
                    type = self._type_to_key(pickled)

            except:
                pass

        else:
            val_serialized = str(val)

        if val_serialized == empty:
            return False

        try:
            if expire_in:
                ret = self.execute(
                    """INSERT OR REPLACE INTO {table_name} (key, val, type, expire_at)
                            VALUES (?, ?, ?, ?)""".replace('{table_name}', self._table_name()),
                    (key, val_serialized, type, expire_in), cache=True)

            else:
                ret = self.execute(
                    """INSERT OR REPLACE INTO {table_name} (key, val, type, expire_at)
                            VALUES (?, ?, ?, (SELECT expire_at FROM {table_name} WHERE key = ?))""".replace(
                        '{table_name}', self._table_name()),
                    (key, val_serialized, type, key), cache=True)

            return ret

        except OperationalError as e:
            # Retry (hack for sqlite database locking)
            if retry_count:
                import time
                time.sleep(0.02)

                try:
                    self.create_table()
                except:
                    pass

                return self.set(key, val, expire_in, retry_count - 1)

            else:
                if raise_error:
                    raise e

                else:
                    return False

    def delete(self, key):
        return self.execute("""
            DELETE FROM {table_name}
                WHERE
                    key = ?""".replace('{table_name}', self._table_name()),
                            key, cache=True)

    def increase(self, key, amount, expire_in=None):
        if expire_in is not None:
            expire_in = TimestampHelper.now() + expire_in

        if expire_in:
            return self.execute("""
                UPDATE {table_name}
                   SET
                       val = val + ?,
                       expire_at = ?
                   WHERE
                       key = ?""".replace('{table_name}', self._table_name()),
                                (amount, expire_in, key), cache=True)

        else:
            return self.execute("""
                UPDATE {table_name}
                   SET
                       val = val + ?
                   WHERE
                       key = ?""".replace('{table_name}', self._table_name()),
                                (amount, key), cache=True)

    def expire(self, key, expire_in=None):
        expire_in = TimestampHelper.now() + (expire_in or 0)

        return self.execute("""
            UPDATE {table_name}
               SET
                   expire_at = ?
               WHERE
                   key = ?""".replace('{table_name}', self._table_name()),
                            (expire_in, key), cache=True)

    def ttl(self, key):
        record = self.row("""
                SELECT
                    *
                FROM
                    {table_name}
                WHERE
                    key = ?""".replace('{table_name}',
                                       self._table_name()), key, cache=True)

        if not record:
            return -2
        elif not record['expire_at']:
            return -1
        else:
            return record['expire_at'] - TimestampHelper.now()


class TransactionProxy(object):
    def __init__(self, sqliteCacheDriver, connection, transaction):
        self._sqliteCacheDriver = sqliteCacheDriver
        self._connection = connection
        self._transaction = transaction

    @property
    def connection(self):
        return self._connection

    @property
    def transaction(self):
        return self._transaction

    def commit(self, return_connection=True):
        return self._sqliteCacheDriver.commit(self, return_connection)

    def rollback(self, return_connection=True):
        return self._sqliteCacheDriver.rollback(self, return_connection)

    def close(self):
        return self._sqliteCacheDriver.close(self)

    def execute(self, sql, bind=None):
        return self._sqliteCacheDriver.execute(sql, bind)

    def row(self, sql, bind=None):
        return self._sqliteCacheDriver.row(sql, bind)

    def rows(self, sql, bind=None):
        return self._sqliteCacheDriver.rows(sql, bind)

    def scalar(self, sql, bind=None):
        return self._sqliteCacheDriver.scalar(sql, bind)
