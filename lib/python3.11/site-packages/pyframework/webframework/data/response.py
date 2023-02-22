# -*- coding: utf-8 -*-


class Response():
    def __init__(self, code=0, message='An error has occurred', *args, **kwargs):
        super().__init__()
        self._code = code
        self._message = message

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message

    def __str__(self):
        return 'code:%s,message: %s' % (self.code, self.message)

    def response(self):
        return {"code": self.code, "message": str(self.message)}
