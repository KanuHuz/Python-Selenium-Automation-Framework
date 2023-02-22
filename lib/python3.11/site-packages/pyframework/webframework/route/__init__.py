# coding:utf-8
import tornado.web

from enum import IntEnum


class HttpMethod(IntEnum):
    get = 1,
    post = 2,
    head = 3,
    delete = 4,
    put = 5,
    patch = 6


# route
class Route(object):
    urls = []
    method_dict = {}

    def __call__(self, url, name=None, method=HttpMethod.get):  # 默认只支持get模式
        def _(cls):
            module_name = cls.__module__;
            class_name = cls.__name__;
            qualname = module_name + "." + class_name;  # 因为__qualname__取不出来全路径采用保守拼接方式
            self.urls.append(tornado.web.URLSpec(url, cls, name=name))
            if method:
                self.method_dict[qualname] = method;
            return cls

        return _


route = Route()
