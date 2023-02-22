# -*- coding: utf-8 -*-


from pyframework.util.type import TypeHelper


class ObjectCheckHelper:
    @staticmethod
    def numeric(val):
        return True if isinstance(val, TypeHelper.numeric()) else False

    @staticmethod
    def string(val):
        return True if isinstance(val, TypeHelper.string()) else False

    @staticmethod
    def array(val):
        return True if isinstance(val, TypeHelper.array()) else False

    @staticmethod
    def dict(val):
        return True if isinstance(val, TypeHelper.dict()) else False
