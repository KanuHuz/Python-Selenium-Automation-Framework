# -*- coding: utf-8 -*-




class CacheDriver(object):
    def __init__(self, pool=None, conn=None):
        self._pool = pool
        self._conn = conn
        self._pipeline = None
        self._reference_count = 0

    @property
    def pool(self):
        return self._pool

    @property
    def conn(self):
        return self._conn

    @staticmethod
    def getpool(host=None, port=None, database=None, user=None, password=None):
        pass

    def getconn(self):
        pass

