# -*- coding: utf-8 -*-


class WebException(Exception):
    def __init__(self, code=0, message='An WebException has occurred', http_status_code=200, *args, **kwargs):
        super().__init__()
        self._code = code
        self._http_status_code = http_status_code
        self._message = message

    @property
    def http_status_code(self):
        return self._http_status_code

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message

    def __str__(self):
        return 'http_code:%s,code:%s,message:%s' % (self.http_status_code, self.code, self.message)

    def response(self):
        return str(self)


if __name__ == "__main__":
    import logging

    try:
        raise WebException()
    except WebException as e:
        logging.exception(e)
