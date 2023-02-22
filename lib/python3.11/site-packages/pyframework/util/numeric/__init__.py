# -*- coding: utf-8 -*-


from __future__ import absolute_import

import re
from pyframework.util.type.check import ObjectCheckHelper
from pyframework.util.numeric.cast import CastHelper
from pyframework.util.system import SystemHelper


class NumericHelper:
    @staticmethod
    def extract_numbers(string):
        if SystemHelper.py_version() <= 2:
            types = basestring,
            types_num = (int, long)
        else:
            types = str,
            types_num = (int,)

        if isinstance(string, types_num):
            return str(string)

        if not isinstance(string, types):
            return None

        return re.sub(r'\D+', '', string)

    @staticmethod
    def number_format(value, tsep=',', dsep='.'):
        if ObjectCheckHelper.string(value):
            value = value.replace(',', '')

            if '.' in value:
                value_cast = CastHelper.float(value)
            else:
                value_cast = CastHelper.long(value)

            if value_cast is not False:
                value = value_cast
            else:
                value = NumericHelper.extract_numbers(value)
        elif ObjectCheckHelper.numeric(value):
            value = value
        else:
            raise Exception('Invalid value.')

        if not value:
            return '0'

        s = str(value)
        cnt = 0
        numchars = dsep + '0123456789'
        ls = len(s)
        while cnt < ls and s[cnt] not in numchars:
            cnt += 1

        lhs = s[:cnt]
        s = s[cnt:]
        if not dsep:
            cnt = -1
        else:
            cnt = s.rfind(dsep)
        if cnt > 0:
            rhs = dsep + s[cnt + 1:]
            s = s[:cnt]
        else:
            rhs = ''

        splt = ''
        while s != '':
            splt = s[-3:] + tsep + splt
            s = s[:-3]

        return lhs + splt[:-1] + rhs
