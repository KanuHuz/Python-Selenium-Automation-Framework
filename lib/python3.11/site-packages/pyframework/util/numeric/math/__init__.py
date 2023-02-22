# -*- coding: utf-8 -*-


from __future__ import absolute_import
from dp_tornado.engine.helper import Helper as dpHelper

import math


class MathHelper(dpHelper):
    @staticmethod
    def floor(  x):
        return math.floor(x)

    @staticmethod
    def ceil(  x):
        return math.ceil(x)

    @staticmethod
    def round( number, ndigits=None):
        return round(number, ndigits)
