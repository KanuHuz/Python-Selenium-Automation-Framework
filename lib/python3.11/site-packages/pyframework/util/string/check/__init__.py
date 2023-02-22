# -*- coding: utf-8 -*-

from pyframework.util.type.check import ObjectCheckHelper
from pyframework.util.string import StringHelper


class StringCheckHelper:
    @staticmethod
    def exist_repeated_text(s, criteria=3):
        if not ObjectCheckHelper.string(s):
            return False

        k = s[0]
        n = 0

        for c in s:
            if c == k:
                n += 1

                if n >= criteria:
                    return True

            else:
                k = c
                n = 1

        return False

    @staticmethod
    def alphanumericpunc(s, add=None):
        return StringCheckHelper._check(
            s, StringHelper.digits + StringHelper.ascii_letters + StringHelper.punctuation, add)

    @staticmethod
    def alphanumeric(self, s, add=None):
        return StringCheckHelper._check(s, StringHelper.digits + StringHelper.ascii_letters, add)

    @staticmethod
    def alphabet(self, s, add=None):
        return StringCheckHelper._check(s, StringHelper.ascii_letters, add)

    @staticmethod
    def numeric(self, s, add=None):
        return StringCheckHelper._check(s, StringHelper.digits, add)

    @staticmethod
    def _check(s, criteria, add):
        if not ObjectCheckHelper.string(s):
            return False

        add = add if add else ''
        v = any(char not in set(c for c in criteria + add) for char in s)
        return True if not v else False
