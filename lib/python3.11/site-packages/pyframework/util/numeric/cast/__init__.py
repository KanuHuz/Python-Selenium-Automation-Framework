# -*- coding: utf-8 -*-

from pyframework.util.system import SystemHelper


class CastHelper:
    @staticmethod
    def int(a, raise_exception=False):
        try:
            if SystemHelper.py_version() <= 2:
                return int(a) if a else 0
            else:
                return int(a) if a else 0

        except ValueError as e:
            if raise_exception:
                raise e

            return False

    @staticmethod
    def long(a, raise_exception=False):
        try:
            if SystemHelper.py_version() <= 2:
                return long(a) if a else long(0)
            else:
                return int(a) if a else 0

        except ValueError as e:
            if raise_exception:
                raise e

            return False

    @staticmethod
    def float(a, raise_exception=False):
        try:
            return float(a) if a else 0

        except ValueError as e:
            if raise_exception:
                raise e

            return False
