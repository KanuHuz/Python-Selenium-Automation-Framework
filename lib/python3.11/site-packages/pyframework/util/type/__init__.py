# -*- coding: utf-8 -*-

from pyframework.util.system import SystemHelper


class TypeHelper:
    @staticmethod
    def int():
        return int

    @staticmethod
    def long():
        if SystemHelper.py_version() <= 2:
            return long
        else:
            return int

    @staticmethod
    def float():
        return float

    @staticmethod
    def bool():
        return bool

    @staticmethod
    def numeric():
        if SystemHelper.py_version() <= 2:
            return int, long, float
        else:
            return int, float

    @staticmethod
    def string():
        if SystemHelper.py_version() <= 2:
            return basestring,
        else:
            return str,

    @staticmethod
    def array():
        return list, tuple

    @staticmethod
    def dict():
        return dict,
