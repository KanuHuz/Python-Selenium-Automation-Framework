# -*- coding: utf-8 -*-

import os
import sys
from pyframework.util.properties import Properties
from pyframework.util.logger import LoggerUtil
from pyframework.webframework.route import route
from pyframework.core.exception.core_exception import CoreException

# from pyframework.webframework.controller import *
from pyframework.util.io.path import PathHelper
import importlib
import platform

import multiprocessing
import time
import tornado.log

from pyframework.core.server.singleton_pyframework import SingletonPyframework
from pyframework.util.cache.cache_factory import CacheFactory
from pyframework.util.string import StringHelper

if hasattr(sys, '_getframe'):
    currentframe = lambda: sys._getframe(3)
else:  # pragma: no cover
    def currentframe():
        """Return the frame object for the caller's stack frame."""
        try:
            raise Exception
        except Exception:
            return sys.exc_info()[2].tb_frame.f_back

_srcfile = os.path.normcase(currentframe.__code__.co_filename)


def findCaller():
    f = currentframe()

    rv = "(unknown file)"
    while hasattr(f, "f_code"):
        co = f.f_code
        filename = os.path.normcase(co.co_filename)
        if filename == _srcfile:
            f = f.f_back
            continue

        rv = co.co_filename
        break
    return rv


class RestfulApplication(tornado.web.Application):
    def __init__(self, handlers, kwargs):
        self.startup_at = int(round(time.time() * 1000))

        super(RestfulApplication, self).__init__(handlers, **kwargs)


class PyframeworkServer(object):

    def __init__(self):
        # print('当前行', inspect.stack()[0][2])
        # print('调用该函数的行', inspect.stack()[1][2])
        # print('调用该函数的文件', inspect.stack()[1][1])
        # # 获取被调用函数名称
        # print(sys._getframe().f_code.co_name)
        #
        # # 获取被调用函数在被调用时所处代码行数
        # print(sys._getframe().f_back.f_lineno)

        # # 获取被调用函数所在模块文件名
        # print(sys._getframe().f_code.co_filename)

        SingletonPyframework._pyframeworkserver = self;
        singletonPyframework = SingletonPyframework();

        singletonPyframework.application_path = os.path.dirname(
            sys.executable)  # 这个地方是python的执行目录，比如 d://python/python.exe
        singletonPyframework.application_path = os.path.dirname(
            __file__)  # 依赖上这个是当前文件的地址，'D:\\develop\\Python36\\lib\\site-packages\\pyframework\\core\\server'

        # print("########         当前application_path = %s       #########" % singletonPyframework.application_path)

        singletonPyframework.application_path = os.path.dirname(sys._getframe().f_back.f_code.co_filename)

        if StringHelper.is_empty(singletonPyframework.application_path):
            print(
                "########     try   findCaller  当前application_path = %s       #########" % singletonPyframework.application_path)
            singletonPyframework.application_path = os.path.dirname(findCaller())
            print(
                "########     try   findCaller  当前application_path = %s       #########" % singletonPyframework.application_path)

        if StringHelper.is_empty(singletonPyframework.application_path):
            print(
                "########     try   inspect.stack  当前application_path = %s       #########" % singletonPyframework.application_path)
            import inspect
            caller_abs_path = os.path.abspath((inspect.stack()[1])[3])
            singletonPyframework.application_path = os.path.dirname(caller_abs_path)
            print(
                "########     try   inspect.stack  当前application_path = %s       #########" % singletonPyframework.application_path)

        print("########         当前application_path = %s       #########" % singletonPyframework.application_path)
        dir_pos = singletonPyframework.application_path.find("pyframework%score%sserver" % ('/', '/'))
        if dir_pos >= 0:
            singletonPyframework.application_path = singletonPyframework.application_path[:dir_pos - 1]
        # if not singletonPyframework.application_path.endswith('/'):
        #     singletonPyframework.application_path = singletonPyframework.application_path + '/'
        # self.application_path_example = singletonPyframework.application_path + "example"

        print("########         当前application_path = %s       #########" % singletonPyframework.application_path)

        singletonPyframework.args = self.parse_args()  # 初始化命令行参数
        # self.logger = Logger()

        conf_env = os.environ.get('conf.env')

        if not conf_env:
            conf_env = "local"
            print("########         conf.env没有配置使用默认值 = %s       #########" % conf_env)
        else:
            print("########         conf.env配置了，值 = %s       #########" % conf_env)

        properties_file = "config-" + conf_env + ".properties"
        properties_file_path = os.path.join(singletonPyframework.application_path, properties_file)
        singletonPyframework.properties = Properties(properties_file_path)

        num_processes = singletonPyframework.properties.server.get('num_processes', default=1)
        if not num_processes:
            singletonPyframework.properties.server.set('num_processes', 1)
            print("没有配置 num_processes ，默认设置num_processes =  %d " % num_processes)
        sysstr = platform.system()
        if (sysstr == "Windows"):
            singletonPyframework.properties.server.set('num_processes', 1)
            print("windows不能fork 子进程 ，默认设置num_processes =  %d " % 1)

        # 初始化日志系统
        LoggerUtil.init_logger(singletonPyframework.application_path, singletonPyframework.properties)

        settings = self.get_tornado_setting()
        num_processed = singletonPyframework.properties.server.num_processes if singletonPyframework.properties.server.num_processes \
            else multiprocessing.cpu_count()

        LoggerUtil.info_by_logger("pyframework", 'Server time : %s' % time.strftime('%Y.%m.%d %H:%M:%S'))
        # LoggerUtil.info_by_logger("pyframework", 'Server Port : %s' % singletonPyframework.properties.server.port)
        LoggerUtil.info_by_logger("pyframework", 'Processors  : %s' % num_processed)
        LoggerUtil.info_by_logger("pyframework", 'CPU Count   : %d' % multiprocessing.cpu_count())
        LoggerUtil.info_by_logger("pyframework", '---------------------------------')

        controller_base_package = singletonPyframework.properties.server.controller_base_package

        if controller_base_package is None:
            # 抛出错误
            raise CoreException("配置文件中没有在server section 下配置 controller_base_package")
        else:
            LoggerUtil.info_by_logger("pyframework", '通过配置文件加载到 controller 包路径为 : %s' % controller_base_package)

        controller_base_file_path = controller_base_package.replace('.', os.sep)

        controller_base_file_path = singletonPyframework.application_path + os.sep + controller_base_file_path

        if os.path.exists(controller_base_file_path):
            controller_file_paths = PathHelper.browse(controller_base_file_path, True, False, None,
                                                      {"ext": ["py", "so"]})

            for controller_file_path in controller_file_paths:

                if controller_file_path is not None:
                    s = str.split(controller_file_path, os.sep)
                    class_file_name = s.pop()
                    module_path = controller_base_package + "." + class_file_name.split(".")[0]
                    # module_path = '.'.join(s)

                    handler_module = importlib.import_module(module_path)
                    LoggerUtil.info_by_logger("pyframework", '扫描到 : %s  模块加载成功' % module_path)

        LoggerUtil.info_by_logger("pyframework", '准备初始化 WebApplication， setting = %s' % str(settings))
        self.application = RestfulApplication(route.urls, settings)
        self.service = tornado.httpserver.HTTPServer(
            self.application,
            xheaders=True,
            max_body_size=int(singletonPyframework.properties.server.max_body_size))

        cache_module = "kernel"
        singletonPyframework.cache = CacheFactory.get_cache_conn(cache_module)
        LoggerUtil.info_by_logger("pyframework", '加载缓存模块 %s 成功' % cache_module)

        try:
            address = singletonPyframework.properties.server.get('address', default="0.0.0.0")
            self.service.bind(singletonPyframework.properties.server.port, address=address)
            LoggerUtil.info_by_logger("pyframework", '服务器启动成功，绑定地址%s : 端口%d ' % (
                singletonPyframework.properties.server.address, int(singletonPyframework.properties.server.port)))
        except Exception as e:
            LoggerUtil.exception_by_logger("pyframework",
                                           'Failed to service binding. (port %s)' % singletonPyframework.properties.server.port)

            # return False

    def parse_args(self):
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('-p', '--port', type=int, help='Binding port', default=None)

        return parser.parse_args()

    def get_tornado_setting(self):

        LoggerUtil.info_by_logger("pyframework", '检查初始化properties')

        singletonPyframework = SingletonPyframework();
        combined_path = singletonPyframework.properties.static.get('path', default='combined')
        static_prefix = singletonPyframework.properties.static.get('prefix', default='/s/')
        static_minify = singletonPyframework.properties.static.get('minify', default=True)

        if combined_path.find('{server_name}') != -1:
            import socket
            combined_path = combined_path.replace('{server_name}', socket.gethostname())

        if static_prefix[-1] != '/':
            static_prefix = '%s/' % static_prefix

        if combined_path[0] == '/':
            combined_path = combined_path[1:]

        if combined_path[-1] == '/':
            combined_path = combined_path[:-1]

        combined_prefix = '%s%s/' % (static_prefix, combined_path)
        combined_url = combined_path
        combined_path = os.path.join(singletonPyframework.application_path, 'static', combined_path)

        singletonPyframework.properties.static.set('combined_prefix', combined_prefix)
        singletonPyframework.properties.static.set('combined_url', combined_url)
        singletonPyframework.properties.static.set('combined_path', combined_path)
        singletonPyframework.properties.static.set('path_sys',
                                                   os.path.join(singletonPyframework.application_path, 'static'))

        singletonPyframework.properties.server.set('application_path', singletonPyframework.application_path)
        singletonPyframework.properties.server.set('python', sys.executable)

        if singletonPyframework.args.port:
            singletonPyframework.properties.server.set('port', singletonPyframework.args.port)

        # Setup Options
        server_debug = singletonPyframework.properties.server.get('debug', default=0)
        max_worker = singletonPyframework.properties.server.get('max_worker', default=1)

        if not max_worker:
            singletonPyframework.properties.server.set('max_worker', 1)
            LoggerUtil.info_by_logger("pyframework", "没有配置 max_worker 最大线程数，默认设置为 %d " % max_worker)

        controller_base_package = singletonPyframework.properties.server.get('controller_base_package', default=None)
        if controller_base_package:
            LoggerUtil.info_by_logger("pyframework", "配置当前工程的controller路径为 %s " % controller_base_package)
        else:
            raise RuntimeError('没有配置controller的扫描路径，请配置properties里的 controller_base_package 参数')
        server_gzip = singletonPyframework.properties.server.get('gzip', default=True)
        # crypto_key = singletonPyframework.properties.crypto.get('key', default='CR$t0-$CR@T')

        # expire_in = singletonPyframework.properties.session.get('expire_in', default=7200)
        max_body_size = singletonPyframework.properties.server.get('max_body_size', default=1024 * 1024 * 10)
        if not max_body_size:
            singletonPyframework.properties.server.set('max_body_size', 10485760)
            LoggerUtil.info_by_logger("pyframework", "没有配置 max_body_size ，默认设置为 %s " % "10MB")
        else:
            LoggerUtil.info_by_logger("pyframework", " max_body_size 设置为 %s " % str(max_body_size))

        cookie_secret = singletonPyframework.properties.server.get('cookie_secret', default='default_cookie_secret')

        # # If enabled debugging mode, disable process forking.
        # if server_debug:
        #     singletonPyframework.properties.server.set('num_processes', 1)

        # m17n = singletonPyframework.properties.server.get('m17n', default='').strip()
        # m17n = m17n.split(',') if m17n else ['dummy']
        # m17n = [e.strip() for e in m17n]
        #
        # singletonPyframework.properties.server.set('m17n', m17n)

        # # exception_delegate = singletonPyframework.properties.logging.get('exception_delegate', default='') or None
        # access_logging = singletonPyframework.properties.logging.get('access', default=False)
        # sql_logging = singletonPyframework.properties.logging.get('sql', default=False)
        # http_logging = singletonPyframework.properties.logging.get('http', default=False)

        # if exception_delegate:
        #     try:
        #         exception_delegate = eval('engine.%s' % exception_delegate)
        #         self.logger.set_delegate_handler(exception_delegate)
        #     except AttributeError:
        #         logging.error('The specified exception delegate is invalid.')
        #         exception_delegate = None
        #
        # singletonPyframework.properties.logging.set('exception_delegate', exception_delegate)

        # # Access Logging
        # self.logger.set_level(tornado.log.access_log.name, logging.DEBUG if access_logging else logging.WARN)
        #
        # # SQLAlchemy logging level
        # if sql_logging:
        #     logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        #
        # # Requests logging level
        # if not http_logging:
        #     logging.getLogger('requests').setLevel(logging.WARNING)
        #

        return {
            'template_path': os.path.join(singletonPyframework.application_path, 'view'),
            'static_path': os.path.join(singletonPyframework.application_path, 'static'),
            # 'static_handler_class': StaticHandler,
            'static_url_prefix': static_prefix,
            'static_minify': int(static_minify),
            'static_combined_url': combined_url,
            'combined_static_path': combined_path,
            'combined_static_url_prefix': combined_prefix,
            'debug': int(server_debug),
            'gzip': int(server_gzip),
            'cookie_secret': cookie_secret
        }

    def start(self):
        singletonPyframework = SingletonPyframework();

        num_processes = int(singletonPyframework.properties.server.num_processes);
        debug = int(singletonPyframework.properties.server.debug);
        if (num_processes > 1 and debug != 0):
            LoggerUtil.error_by_logger("pyframework", "检测到准备启动多进程模式，server.debug必须为0")
            sys.exit(0);

        if num_processes > 1:
            LoggerUtil.debug_by_logger("pyframework", "！！！！！！！！！！！！！！！！！检测到准备启动多进程模式，这种编程模型不推荐，慎用！！！！！！！！！！！！！！！！！")

        max_worker = int(singletonPyframework.properties.server.max_worker);
        if max_worker > 1:
            LoggerUtil.debug_by_logger("pyframework", "启动多线程模式，线程数 max_worker = %d " % max_worker)

        if max_worker == 1 and num_processes == 1:
            LoggerUtil.debug_by_logger("pyframework", "启动单进程单线程模式");

        self.service.start(num_processes)
        import random
        self.application.identifier = random.randint(100000, 999999)

        try:
            instance = tornado.ioloop.IOLoop.instance()
            instance.__setattr__('startup_at', getattr(self.application, 'startup_at'))

            instance.start()

        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    server = PyframeworkServer();
    server.start()
