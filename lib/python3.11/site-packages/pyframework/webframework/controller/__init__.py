# coding:utf-8

import tornado.web
import json
from pyframework.core.server.startup import SingletonPyframework
from pyframework.webframework.exception.web_exception import WebException
from pyframework.webframework.data.response import Response
from pyframework.util.string.serialization import SerializationHelper
from pyframework.util.logger import LoggerUtil

from pyframework.util.type.check import ObjectCheckHelper
from pyframework.webframework.route import *
from pyframework.util.concurrent.atomic import *
import datetime


class InterruptException(Exception):
    def __init__(self, handler):
        self.handler = handler


class BaseController(tornado.web.RequestHandler):
    __atomicThreadCount = AtomicInteger();  # 不要直接操作这个变量，也尽量避免访问它

    @classmethod
    def get_thread_count(cls):
        return cls.__atomicThreadCount.value

    @classmethod
    def inc_thread_count(cls):
        return cls.__atomicThreadCount.inc()

    @classmethod
    def dec_thread_count(cls):
        return cls.__atomicThreadCount.dec()

    @property
    def executor(self):
        LoggerUtil.debug_by_logger("pyframework", "初始化了异步 excutor ")
        return self._executor("pyframe_async")

    def _executor(self, identifier=None):
        return SingletonPyframework().executor(identifier)

    def render(self, fn=None, kwargs={}):
        if not fn:
            fn = '%s.html' % self.__class__.__name__.lower()
        # if not fn:
        #     fn = ('/%s/%s.html' % (
        #         '/'.join(self.__module__.split('.')[1:-1]),
        #         self.__class__.__name__.lower()
        #     )).replace(r'//', r'/')

        kwargs.update({
            'req': self,
            # 'config': config,
            'static': self.static_url,
            'url_for': self.reverse_url,
            'xsrf_token': self.xsrf_form_html(),
            'csrf_token': self.xsrf_form_html(),
        })
        lookup = self.get_lookup_jinja2()
        if lookup:
            tmpl = lookup.get_template(fn)
            self.finish(tmpl.render(**kwargs))
        else:
            if fn.startswith('/'):
                fn = '.' + fn
            if 'page_title' not in kwargs:
                kwargs['page_title'] = None
            super(BaseController, self).render(fn, **kwargs)

    def initialize(self):
        self.session = SimpleSession(self)
        super(BaseController, self).initialize()

    def flush(self, include_footers=False, callback=None):
        self.session.flush()
        super(BaseController, self).flush(include_footers, callback)

    def data_received(self, chunk):
        """ just for pycharm warning fix """
        pass

    def output_json(self, json_data={"code": 9, "message": "null output json"}):
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        if not isinstance(json_data, (dict)):
            raise WebException(9, "json格式错误，需要为dict类型")
        chunk = SerializationHelper.serialize(json_data, method='json')
        self.finish(chunk)

    def output_data(self, data="no data", content_type=None):
        if not content_type:
            self.set_header('Content-Type', 'text/html; charset=UTF-8')
        self.finish(data)

    def head(self, path=None):
        self.routed = True
        self.__processor('head', path)

    def get(self, path=None):
        self.routed = True

        if (SingletonPyframework().properties.server.async == '1'):
            self.__processor(HttpMethod.get, path)
        else:
            self.do_process_wrapper(HttpMethod.get, path);

    def verify_http_method(self, method):
        http_method = route.method_dict.get(self.__class__.__module__ + "." + self.__class__.__name__)
        if isinstance(http_method, (tuple, list)) and method in http_method:
            pass  # 设置了httpmethod，并且匹配成功
        elif ObjectCheckHelper.numeric(http_method) and method == http_method:
            pass  # httpmethod = 当前method
        else:
            raise WebException("当前http method不允许访问，只能用 %s 访问" % str(http_method))

    def post(self, path=None):
        self.routed = True

        if (SingletonPyframework().properties.server.async == '1'):
            self.__processor(HttpMethod.post, path)
        else:
            self.do_process_wrapper(HttpMethod.post, path);

    def delete(self, path=None):
        self.routed = True
        self.__processor(HttpMethod.delete, path)

    def patch(self, path=None):
        self.routed = True
        self.__processor(HttpMethod.patch, path)

    def put(self, path=None):
        self.routed = True
        self.__processor(HttpMethod.put, path)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def __processor(self, method, path):
        # _singletonPyframework = SingletonPyframework()
        # if ConcurrentDecorator._concurrent_enabled_:
        #这个日志不好判断，初始化为0 ，用过一段时间后，两个线程占用为2，被抢占后逐渐变为0
        # LoggerUtil.debug_by_logger("pyframework", " excutor 当前执行队列为 " + str(len(self.executor._work_queue.not_empty._waiters)))
        try:
            current_thread_count = self.inc_thread_count();
            max_worker = int(SingletonPyframework().properties.server.max_worker);
            if(current_thread_count > max_worker):
                self.finish_with_error(503, 'exceed thread count limited')
                return

            x = yield self.do_request(method, path)
        finally:
            self.dec_thread_count()
        # try:
        #     x = tornado.gen.with_timeout(datetime.timedelta(seconds=20), [self.do_request(method, path)],
        #                  quiet_exceptions=tornado.gen.TimeoutError)
        # except tornado.gen.TimeoutError:
        #     self.write("Timeout")
        #     print("Timeout")
        # else:
        #     x = self.do_request(method, path)

        # try:
        # self.postprocess(x)

        # except Exception as e:
        # self.logger.exception(e)

        # raise e

    def do_process_wrapper(self, method, path):
        try:
            self.verify_http_method(method)
            self.do_process()
            return
        except tornado.web.HTTPError as e:
            raise e
        except WebException as e:
            self.set_status(e.http_status_code)
            response = Response(e.code, e.message)
            self.finish(response.response())
        except Exception as e:
            LoggerUtil.exception_by_logger("pyframework", '执行 do_process 出错了，错误 = %s' % str(e))
            self.finish_with_error(500)

            return False

        self.finish_with_error(404, 'Page Not Found')

    @staticmethod
    def finish_with_error(status_code, message='An error has occurred'):
        raise tornado.web.HTTPError(status_code, reason=message)

    def do_process(self):
        raise NotImplementedError

    @tornado.concurrent.run_on_executor
    def do_request(self, method, path, initialize=None):
        self.do_process_wrapper(method, path);

    # @property
    # def headers_written(self):
    #     return self._headers_written
    #
    # def postprocess(self, x):
    #     if self._headers_written:
    #         return
    #
    #     if not x:
    #         return
    #
    #     for k, v in x._headers:
    #         self.set_header(k, v)
    #
    #     if x._render:
    #         self.__render(x)
    #     elif x._finish:
    #         self.__finish(x)
    #     elif x._write:
    #         self.__write(x)
    #
    #     for handler in self.handlers:
    #         on_finish = getattr(handler, 'on_finish', None)
    #
    #         if on_finish:
    #             if on_finish(self.get_status()) is True:
    #                 break
    #
    # def __render(self, x):
    #     if not x._render:
    #         return
    #
    #     t = x._render['t']
    #     k = x._render['k']
    #
    #     self.finish(self.view.render_string(self, t, k, encode=False))
    #
    # def __write(self, x):
    #     if not x._write:
    #         return
    #
    #     for s in x._write:
    #         self.write(s)
    #
    # def __finish(self, x):
    #     if not x._finish:
    #         return
    #
    #     self.finish(x._finish)

    def get_lookup_jinja2(_globals={}, extensions=[]):
        from jinja2 import Environment, FileSystemLoader

        _lookup = Environment(
            loader=FileSystemLoader(['./static/templates'], encoding='utf-8'),
            extensions=extensions
        )
        # mako 没有全局变量特性，这里为了一致性 jinjia 向 mako 妥协
        # _lookup.globals['url_for'] = url_for
        # _lookup.globals['config'] = config
        _lookup.globals.update(_globals)
        return _lookup


# Session
class SimpleSession(object):
    def __init__(self, request):
        self._request = request
        self._data = self.load()

    def __delitem__(self, key):
        del self._data[key]

    def __getitem__(self, key):
        return self._data.get(key)

    def __setitem__(self, key, value):
        self._data[key] = value

    def load(self):
        _s = self._request.get_secure_cookie('session') or '{}'
        try:
            _s = _s.decode('utf-8')  # fix:py2
        except:
            pass
        return json.loads(_s)

    def flush(self):
        self._request.set_secure_cookie('session', json.dumps(self._data))
