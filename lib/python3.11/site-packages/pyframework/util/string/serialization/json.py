# -*- coding: utf-8 -*-

import json

class JsonHelper:
    @staticmethod
    def stringify(obj, beautify=False, raise_exception=False):
        try:
            if beautify:
                return json.dumps(obj, indent=4, sort_keys=True)
            else:
                return json.dumps(obj, separators=(',', ':'), indent=None, sort_keys=True)

        except Exception as e:
            if raise_exception:
                raise e

            return False

    @staticmethod
    def parse(text, encoding='utf8', raise_exception=False):
        try:
            return json.loads(text, encoding=encoding)

        except Exception as e:
            if raise_exception:
                raise e

            return False
