# -*- coding: utf-8 -*-


from pyframework.util.string.serialization.json import JsonHelper


class SerializationHelper:
    @staticmethod
    def serialize(obj, method='json', beautify=False, raise_exception=False):
        if method == 'json':
            return JsonHelper.stringify(
                obj=obj, beautify=beautify, raise_exception=raise_exception)
        else:
            raise Exception('The specified method is not supported.')

    @staticmethod
    def deserialize(text, method='json', encoding='utf8', raise_exception=False):
        if method == 'json':
            return JsonHelper.parse(
                text=text, encoding=encoding, raise_exception=raise_exception)
        else:
            raise Exception('The specified method is not supported.')
