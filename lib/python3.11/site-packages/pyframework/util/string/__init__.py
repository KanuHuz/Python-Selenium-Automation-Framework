# -*- coding: utf-8 -*-


from __future__ import absolute_import

import string


class StringHelper:
    @staticmethod
    def ascii_uppercase(self):
        return string.ascii_uppercase

    @staticmethod
    def ascii_lowercase(self):
        return string.ascii_lowercase

    @staticmethod
    def ascii_letters(self):
        return string.ascii_letters

    @staticmethod
    def punctuation(self):
        return string.punctuation

    @staticmethod
    def digits(self):
        return string.digits

    @staticmethod
    def printable(self):
        return string.printable

    @staticmethod
    def whitespace(self):
        return string.whitespace

    @staticmethod
    def is_empty (mystring):
        if mystring and mystring.strip():
            #myString is not None AND myString is not empty or blank
            return False
        #myString is None OR myString is empty or blank
        return True

    @staticmethod
    def is_not_empty(mystring):
        if mystring and mystring.strip():
            # myString is not None AND myString is not empty or blank
            return True
        # myString is None OR myString is empty or blank
        return False