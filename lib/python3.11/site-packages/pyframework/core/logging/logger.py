# -*- coding: utf-8 -*-


import logging
import traceback
import threading
import os
import sys
import io
import cloghandler
from pyframework.util.string import *
from pyframework.core.server.singleton_pyframework import SingletonPyframework
from pyframework.core.exception.core_exception import *
from collections import namedtuple

try:
    import Queue as queue
except ImportError:
    import queue

from logging.handlers import RotatingFileHandler
import threading
import configparser


#
# class LogSignleton(object):
# 
#     def __new__(cls, log_config):
#         mutex = threading.Lock()
#         mutex.acquire()  # 上锁，防止多线程下出问题
# 
#         if not hasattr(cls, 'instance'):
#             cls.instance = super(LogSignleton, cls).__new__(cls)
# 
#             config = configparser.ConfigParser()
# 
#             config.read(log_config)
# 
#             cls.instance.log_filename = config.get('LOGGING', 'log_file')
# 
#             cls.instance.max_bytes_each = int(config.get('LOGGING', 'max_bytes_each'))
# 
#             cls.instance.backup_count = int(config.get('LOGGING', 'backup_count'))
# 
#             cls.instance.fmt = config.get('LOGGING', 'fmt')
# 
#             cls.instance.log_level_in_console = int(config.get('LOGGING', 'log_level_in_console'))
# 
#             cls.instance.log_level_in_logfile = int(config.get('LOGGING', 'log_level_in_logfile'))
# 
#             cls.instance.logger_name = config.get('LOGGING', 'logger_name')
# 
#             cls.instance.console_log_on = int(config.get('LOGGING', 'console_log_on'))
# 
#             cls.instance.logfile_log_on = int(config.get('LOGGING', 'logfile_log_on'))
# 
#             cls.instance.logger = logging.getLogger(cls.instance.logger_name)
# 
#             cls.instance.__config_logger()
# 
#         mutex.release()
# 
#         return cls.instance
# 
#     def get_logger(self):
# 
#         return self.logger
# 
#     def __config_logger(self):
# 
#         # 设置日志格式
# 
#         fmt = self.fmt.replace('|', '%')
# 
#         formatter = logging.Formatter(fmt)
# 
#         if self.console_log_on == 1:  # 如果开启控制台日志
# 
#             console = logging.StreamHandler()
# 
#             # console.setLevel(self.log_level_in_console)
# 
#             console.setFormatter(formatter)
# 
#             self.logger.addHandler(console)
# 
#             self.logger.setLevel(self.log_level_in_console)
# 
#         if self.logfile_log_on == 1:  # 如果开启文件日志
# 
#             rt_file_handler = RotatingFileHandler(self.log_filename, maxBytes=self.max_bytes_each,
#                                                   backupCount=self.backup_count)
# 
#             rt_file_handler.setFormatter(formatter)
# 
#             self.logger.addHandler(rt_file_handler)
# 
#             self.logger.setLevel(self.log_level_in_logfile)


class Logger():
    def __init__(self):
        self.loggers = {}

        # self.set_logger(self.default_logger, logging.DEBUG, None, True)
        # self.set_logger(self.sys_logger, logging.DEBUG)

        # self.delegate_queue = None
        # self.delegate_handler = None

    @property
    def default_logger_name(self):
        return 'pyframework_logger'

    @property
    def default_logger(self):
        return self.get_logger(self.default_logger_name)

    # @property
    # def sys_logger_name(self):
    #     return 'pyframework_logger_sys'
    #
    # @property
    # def sys_logger(self):
    #     return self.get_logger(self.sys_logger_name)

    def get_logger(self, name):
        if name in self.loggers:
            return self.loggers[name]

        logger = logging.getLogger(name)
        self.loggers[name] = logger

        return logger

    #
    # def set_logger(self, logger, level, format_string=None, add_handler=False):
    #     if format_string is None:
    #         format_string = '[%(asctime)s][%(levelname)s] %(message)s'
    #
    #     logger.setLevel(level)
    #     import sys
    #     handler = logging.StreamHandler(stream=sys.stdout)
    #     handler.setLevel(level)
    #
    #     if add_handler:
    #         formatter = logging.Formatter(format_string)
    #         handler.setFormatter(formatter)
    #         logger.addHandler(handler)

    # def set_delegate_handler(self, handler=None):
    #     self.delegate_handler = handler or self.engine.ini.logging.exception_delegate

    # def start_handler(self):
    #     if self.delegate_handler and not getattr(self, 'delegate', None):
    #         self.delegate_queue = queue.Queue()
    #         self.delegate = LoggerDelegate(self)
    #         self.delegate.start()

    # def interrupt(self):
    #     delegate = getattr(self, 'delegate', None)
    #
    #     if not delegate:
    #         return
    #
    #     self.delegate_interrupt()

    def strip(self, msg, strip=False):
        return msg.strip() if strip else msg

    def exception(self, exception, *args, **kwargs):
        msg = self.strip(str(exception), True)
        tb = traceback.format_exc()

        # if self.delegate_handler and self.delegate_queue:
        #     self.delegate_queue.put((logging.ERROR, msg, tb))

        self.default_logger.exception(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.default_logger.error(self.strip(str(msg), True), *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.default_logger.info(self.strip(msg), *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.default_logger.warning(self.strip(msg), *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.default_logger.debug(self.strip(msg), *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        self.default_logger.log(level, self.strip(msg), *args, **kwargs)

    # def sys_log(self, msg, *args, **kwargs):
    #     self.sys_logger.info(self.strip(msg), *args, **kwargs)

    # def delegate_interrupt(self):
    #     if self.delegate_handler:
    #         self.delegate.interrupted = True
    #         self.delegate_queue.put(False)

    def set_level(self, name, level):
        self.get_logger(name).setLevel(level)


# class LoggerDelegate(threading.Thread):
#     def __init__(self, logger):
#         self.interrupted = False
#         self.logger = logger
#
#         threading.Thread.__init__(self)
#
#     def run(self):
#         while not self.interrupted:
#             payload = self.logger.delegate_queue.get()
#
#             if not payload:
#                 break
#
#             self.logger.delegate_handler(*payload)


