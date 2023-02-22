# -*- coding: utf-8 -*-

from pyframework.util.type.check import ObjectCheckHelper
from pyframework.util.system import SystemHelper

unicode_type = type(u'')


class CastHelper:
    @staticmethod
    def string(s, preserve_none=True):
        if s is None:
            return s if preserve_none else ''

        if not ObjectCheckHelper.string(s):
            s = str(s)

        if type(s) == unicode_type:
            if SystemHelper.py_version() <= 2:
                return s.encode('UTF-8')
            else:
                return s
        else:
            return s

    @staticmethod
    def unicode(s, preserve_none=True):
        if s is None:
            return s if preserve_none else u''

        if not ObjectCheckHelper.string(s):
            s = str(s)

        if type(s) != unicode_type:
            return s.decode('UTF-8')
        else:
            return s
