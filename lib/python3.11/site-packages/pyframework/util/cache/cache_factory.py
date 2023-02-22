# -*- coding: utf-8 -*-


from pyframework.util.cache.impl.redis_cache import RedisCacheDriver as redisCacheDriver
from pyframework.util.cache.impl.sqlite_cache import SqliteCacheDriver
from pyframework.core.server.singleton_pyframework import SingletonPyframework
import threading
from pyframework.core.exception.core_exception import CoreException


class CacheFactory():
    _instance_lock = threading.Lock()
    #
    # def __init__(self):
    #     pass
    #
    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(Cache, "_instance"):
    #         with Cache._instance_lock:
    #             if not hasattr(Cache, "_instance"):
    #                 Cache._instance = object.__new__(cls)
    #     return Cache._instance

    pools = {}

    @staticmethod
    def _getdriver(cache_key):
        if not hasattr(CacheFactory.pools, cache_key):
            with CacheFactory._instance_lock:
                if not hasattr(CacheFactory.pools, cache_key):
                    pyframework_props = SingletonPyframework().properties
                    cache_section = cache_key + "_cache"
                    host = pyframework_props._parser.get(cache_section, "cache_host", "127.0.0.1")
                    port = pyframework_props._parser.get(cache_section, "cache_port", 6379)

                    user = pyframework_props._parser.get(cache_section, "cache_user", "admin")
                    password = pyframework_props._parser.get(cache_section, "cache_passwd", "123")
                    maxconn = pyframework_props._parser.get(cache_section, "cache_maxconn", None)

                    cache_type = pyframework_props._parser.get(cache_section, "cache_type", "sqlite")

                    if cache_type == "redis":
                        database = pyframework_props._parser.get(cache_section, "cache_db", 0)
                        CacheFactory.pools[cache_key] = redisCacheDriver.getpool(
                            host,
                            port,
                            database,
                            user,
                            password,
                            maxconn)
                    elif cache_type == "sqlite":
                        database = pyframework_props._parser.get(cache_section, "cache_db", "sqlite")
                        CacheFactory.pools[cache_key] = SqliteCacheDriver.getpool(
                            host,
                            port,
                            database,
                            user,
                            password)
                    else:
                        raise CoreException("不支持的cache类型，只支持 redis/sqlite")
        return CacheFactory.pools[cache_key]

    @staticmethod
    def get_cache_conn(cache_key):
        driver = CacheFactory._getdriver(cache_key)

        if not driver:
            raise Exception('Cache pool initialized failed.')

        # return driver.getconn()
        return driver;
