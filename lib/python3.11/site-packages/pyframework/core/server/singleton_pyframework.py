# -*- coding: utf-8 -*-

import inspect
import threading
import tornado.concurrent
from pyframework.util.logger import LoggerUtil


class SingletonPyframework(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(SingletonPyframework, "_instance"):
            with SingletonPyframework._instance_lock:
                if not hasattr(SingletonPyframework, "_instance"):
                    SingletonPyframework._instance = object.__new__(cls)
        return SingletonPyframework._instance

    def executor(self, identifier=None):
        if not hasattr(self, '_executor_%s' % identifier):

            LoggerUtil.debug_by_logger("pyframework", '没有 _executor 属性，准备设置')
            if self.properties.server.max_worker is None:
                return None

            if self.properties.server.max_worker:
                LoggerUtil.debug_by_logger("pyframework", '设置了 max_worker == %s ，准备初始化executor' % (
                    str(self.properties.server.max_worker)))
                setattr(self,
                        '_executor_%s' % identifier,
                        tornado.concurrent.futures.ThreadPoolExecutor(
                            int(self.properties.server.get('max_worker', 1))))
            else:
                LoggerUtil.debug_by_logger("pyframework", '没有设置 max_worker 属性，excutor设为None')
                setattr(self, '_executor_%s' % identifier, None)

        return getattr(self, '_executor_%s' % identifier)
