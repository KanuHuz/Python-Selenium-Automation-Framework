# -*- coding: utf-8 -*-

import sys


class SystemHelper:
    @staticmethod
    def py_version():
        return sys.version_info[0]


if __name__ == "__main__":
    print ("version = " + str(SystemHelper.py_version()))