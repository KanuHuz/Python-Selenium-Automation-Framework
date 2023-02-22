# coding:utf-8

from pyframework.webframework.route import route
from pyframework.webframework.controller import BaseController
import time
import threading
from pyframework.webframework.exception.web_exception import WebException
from pyframework.util.logger import LoggerUtil
from pyframework.webframework.route import HttpMethod


@route('/in', name='index', method=[HttpMethod.post,HttpMethod.get])
class IndexController(BaseController):
    def do_process(self):
        LoggerUtil.debug("index  准备休息15秒， thread id  = " + str(threading.current_thread()))
        time.sleep(15)
        LoggerUtil.debug("index  请求完成， thread id  = " + str(threading.current_thread()))
        # raise WebException(1111,"出错了")
        data = {}
        data["xxxxx"] = "fffff hello 哈哈 !!!!"
        self.output_json(data)
        # self.render("index.html", data)

@route('/in2', name='index2', method=[HttpMethod.post,HttpMethod.get])
class IndexController(BaseController):
    def do_process(self):
        LoggerUtil.debug("index2  准备休息15秒， thread id  = " + str(threading.current_thread()))
        time.sleep(60)
        LoggerUtil.debug("index2  请求完成， thread id  = " + str(threading.current_thread()))
        # raise WebException(1111,"出错了")
        data = {}
        data["xxxxx"] = "ffff2f222 hello 哈哈 !!!!"
        self.output_json(data)
