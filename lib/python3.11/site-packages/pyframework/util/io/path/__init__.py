# -*- coding: utf-8 -*-



import os


class PathHelper:
    @classmethod
    def join(self, path, *paths):
        return os.path.join(path, *paths)

    @classmethod
    def split(self, path):
        return os.path.split(path)

    @classmethod
    def mkdir(self, path, mode=None):
        if self.is_file(path):
            path = self.dirname(path)

        try:
            kwargs = {}

            if mode:
                kwargs['mode'] = mode

            if not self.is_dir(path):
                os.makedirs(path, **kwargs)

        except Exception as e:
            self.logging.exception(e)
            pass

        return self.is_dir(path)

    @classmethod
    def browse(self, path, fullpath=True, recursive=False, appendpath=None, conditions=None):
        output = [os.path.join(path, e) if fullpath else e for e in os.listdir(path)]

        output_recursive = []

        for e in output:
            if recursive and self.is_dir(e if fullpath else os.path.join(path, e)):
                appendpath_ = (self.join(appendpath, e) if appendpath else e) if not fullpath else None
                output_recursive += self.browse(
                    path=os.path.join(path, e),
                    fullpath=fullpath,
                    recursive=recursive,
                    appendpath=appendpath_,
                    conditions=conditions)
            else:
                if self._browse_filter(path, e, conditions):
                    output_recursive.append(self.join(appendpath, e) if appendpath else e)

        return output_recursive

    @classmethod
    def _browse_filter(self, path, name, conditions):
        if not conditions:
            return True

        if 'ext' in conditions:
            ext = self.ext(name, dot='').lower()

            if isinstance(conditions['ext'], (list, tuple)):
                if ext not in conditions['ext']:
                    return False
            elif ext != conditions['ext']:
                return False

        return True

    @classmethod
    def is_dir(self, path):
        return True if os.path.isdir(path) else False

    @classmethod
    def is_file(self, path):
        return True if os.path.isfile(path) else False

    @classmethod
    def dirname(self, path):
        return os.path.dirname(path)

    @classmethod
    def cwd(self):
        return os.getcwd()

    @classmethod
    def ext(self, path, dot='.'):
        ext = os.path.splitext(path)[-1]

        return '%s%s' % (dot or '', ext[1:]) if ext else ''
