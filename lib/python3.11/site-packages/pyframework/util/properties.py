# -*- coding: utf-8 -*-

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import os


class PropertiesSection(object):
    def __init__(self, parser, section):
        self.__dict__['_parser'] = parser
        self.__dict__['_section'] = section
        self.__dict__['_options'] = {}

    def __getattr__(self, name):
        try:
            return self.__getattribute__(name)
        except AttributeError:
            pass

        return self.__dict__['_options'][name] if name in self._options else None

    def __setattr__(self, key, value):
        self.__dict__['_options'][key] = value

    def get(self, key, default=None):
        if key in self.__dict__['_options']:
            return self.__dict__['_options'][key]

        got = self.__dict__['_parser'].get(section=self._section, key=key, default=default)
        self.__setattr__(key, got)

        return got

    def set(self, key, val):
        self.__setattr__(key, val)


class PropertiesParser(object):
    def __init__(self, parser):
        self._parser = parser

    def get(self, section, key, default=None):
        try:
            if not self._parser:
                got = False
            else:
                got = self._parser.get(section, key)

            if default is True or default is False:
                return True if got == '1' else False

            elif isinstance(default, str):
                return str(got)

            elif isinstance(default, int):
                return int(got)

            else:
                return got

        except (configparser.NoSectionError, configparser.NoOptionError):
            return default


class Properties():
    def __init__(self, properties_file=None):
        self.__dict__['_sections'] = {}
        self.__dict__['_parser'] = None
        self.properties_file = properties_file
        if self.__dict__['_parser']:
            return self.__dict__['_parser']
        else:
            if not self.properties_file:
                parser = None

            else:
                parser = configparser.RawConfigParser()
                parser.read(self.properties_file)
            properties_parser = PropertiesParser(parser)
            self.__dict__['_parser'] = properties_parser

            # 根据section把key、value写入字典
            for section in parser.sections():
                propertiesSection = self.__getattr__(section)
                for keyname, value in parser.items(section):
                    propertiesSection.set(keyname, value)


    def __getattr__(self, name):
        try:
            return self.__getattribute__(name)
        except AttributeError:
            pass

        section = self.__dict__['_sections'][name] if name in self.__dict__['_sections'] else None

        if not section:
            section = PropertiesSection(self._parser, name)
            self.__dict__['_sections'][name] = section

        return section


# -*- coding: utf-8 -*-
'''
File Name: handle_config.py
Author: WillDX
mail: xiang.dai@shuyun.com
Created Time: 2015年09月12日 星期六 22时04分20秒
'''

class HandleConfig():
    def __init__(self, file):
        self.cp = configparser()
        self.cp.read(file)
        self.file = file
        # print "self.file:",file

    def get_all_sections(self):
        '''返回所有配置文件中所有sections组成的列表'''
        result = self.cp.sections()
        return result

    def get_section_option(self, sec):
        '''返回一个section的所有options组成的列表'''
        result = self.cp.options(sec)
        return result

    def get_section_items(self, sec):
        '''获取指定section的配置信息,返回列表格式为[{option_name:option_value},]'''
        result = self.cp.items(sec)
        return result

    def get_section_option_value(self, sec, opt):
        '''读取指定的section内的option的值'''
        result = self.cp.get(sec, opt)
        return result

    def write_section_option(self, sec, opt, value):
        """写入指定的section内的option的值,原有的值被替换"""
        self.cp.set(sec, opt, value)
        self.cp.write(open(self.file, "w"))
        return None

    def add_section(self, sec):
        '''添加一个section'''
        self.cp.add_section(sec)
        self.cp.write(open(self.file, "w"))
        return None

    def remove_section(self, sec):
        '''移除section'''
        self.cp.remove_section(sec)
        self.cp.write(open(self.file, "w"))
        return None

    def remove_section_option(self, sec, opt):
        '''移除一个section的option'''
        self.cp.remove_option(sec, opt)
        self.cp.write(open(self.file, "w"))
        return None
#
# if __name__ == "__main__":

# print info0000000000000000000000000000000000
