import logging
import traceback
import threading
import os
import sys
import io
import cloghandler
from pyframework.util.string import *
from pyframework.util.properties import Properties
from pyframework.core.exception.core_exception import *
from logging.handlers import RotatingFileHandler
import threading

if hasattr(sys, '_getframe'):
    currentframe = lambda: sys._getframe(3)
else:  # pragma: no cover
    def currentframe():
        """Return the frame object for the caller's stack frame."""
        try:
            raise Exception
        except Exception:
            return sys.exc_info()[2].tb_frame.f_back

_srcfile = os.path.normcase(currentframe.__code__.co_filename)


class LoggerUtil:
    # logger = Logger()
    log_dir = None;
    file_handler_level = None
    console_handler_level = None
    loggers = {}
    _lock = threading.Lock()
    max_bytes = None;
    backup_count = None;
    num_processes = None;
    root_logger_name = "";
    console_format = None;
    file_format = None;
    application_path = None;

    @staticmethod
    def get_logger(name, logger_dir, logger_name):
        if name in LoggerUtil.loggers:
            return LoggerUtil.loggers[name]
        else:
            with LoggerUtil._lock:
                if name not in LoggerUtil.loggers:
                    logger = logging.getLogger(name)
                    if not os.path.exists(logger_dir):
                        os.mkdir(logger_dir)

                    logger_path = logger_dir + "/" + logger_name

                    LoggerUtil.init_file_console_handler(logger, logger_path)
                    LoggerUtil.loggers[name] = logger
                else:
                    return LoggerUtil.loggers[name]
        return logger

    @staticmethod
    def get_logging_level(level_string):
        if level_string:
            logging_level = getattr(logging, level_string.upper(), logging.DEBUG)
            return logging_level
        return logging.DEBUG

    @staticmethod
    def init_logger_byfile(application_path=None, properties_file_path=None):
        if not application_path:
            raise CoreException("必须传入 application_path 参数")

        LoggerUtil.application_path = application_path;

        if not properties_file_path:
            raise CoreException("必须传入 properties_file_path 参数")

        if not os.path.exists(application_path):
            raise CoreException("application_path = %s 不存在" % application_path)

        if not os.path.exists(properties_file_path):
            raise CoreException("properties_file_path = %s 不存在" % properties_file_path)

        properties = Properties(properties_file_path)
        LoggerUtil.init_logger(application_path, properties)

    @staticmethod
    def init_logger(application_path=None, properties=None):
        if not application_path:
            raise CoreException("必须传入 application_path 参数")

        path_sep_pos = application_path.find('\\')
        if path_sep_pos >= 0:
            application_path = application_path.replace('\\', '/')

        if not application_path.endswith('/'):
            application_path = application_path + "/";
        LoggerUtil.application_path = application_path;

        logger_name = properties.logging.get('root_logger_name', default="root.log")
        LoggerUtil.max_bytes = int(properties.logging.get('max_bytes', default=1024 * 1024 * 10))
        LoggerUtil.backup_count = int(properties.logging.get('backup_count', default=5))
        LoggerUtil.num_processes = int(properties.server.num_processes)

        LoggerUtil.console_format = properties.logging.get('console_format',
                                                           default="%(asctime)s %(name)-8s %(levelname)-8s %(message)s")
        LoggerUtil.file_format = properties.logging.get('file_format',
                                                        default="%(asctime)s %(name)-8s %(levelname)-8s %(message)s")

        LoggerUtil.file_handler_level = properties.logging.file_handler_level
        LoggerUtil.console_handler_level = properties.logging.console_handler_level

        LoggerUtil.log_dir = properties.logging.log_dir;

        if StringHelper.is_empty(LoggerUtil.log_dir):
            raise CoreException("没有配置logging.log_dir，请配置！！")

        if not LoggerUtil.log_dir.endswith('/'):
            LoggerUtil.log_dir = LoggerUtil.log_dir + '/'
        # create logs file folder
        if os.path.exists(LoggerUtil.log_dir) and os.path.isdir(LoggerUtil.log_dir):
            pass
        else:
            os.makedirs(LoggerUtil.log_dir)
        logger_path = LoggerUtil.log_dir + logger_name

        root_logger = logging.getLogger(LoggerUtil.root_logger_name)
        LoggerUtil.init_file_console_handler(root_logger, logger_path)

    @staticmethod
    def init_file_console_handler(logger, logger_path):
        logging_file_handler_level = LoggerUtil.get_logging_level(LoggerUtil.file_handler_level)
        logging_console_handler_level = LoggerUtil.get_logging_level(LoggerUtil.console_handler_level)
        # define a rotating file handler
        if LoggerUtil.num_processes <= 1:  # 如果是单进程使用 RotatingFileHandler
            rotatingFileHandler = logging.handlers.RotatingFileHandler(filename=logger_path,
                                                                       maxBytes=LoggerUtil.max_bytes,
                                                                       backupCount=LoggerUtil.backup_count)
        else:
            rotatingFileHandler = cloghandler.ConcurrentRotatingFileHandler(filename=logger_path,
                                                                            maxBytes=LoggerUtil.max_bytes,
                                                                            backupCount=LoggerUtil.backup_count)
        formatter = logging.Formatter(LoggerUtil.file_format)
        rotatingFileHandler.setFormatter(formatter)
        rotatingFileHandler.setLevel(logging_file_handler_level)
        logger.addHandler(rotatingFileHandler)

        if logger.name and logger.name == "root":
            # define a handler whitch writes messages to sys
            console = logging.StreamHandler()
            console.setLevel(logging_console_handler_level)
            # set a format which is simple for console use
            formatter = logging.Formatter(LoggerUtil.console_format)
            # tell the handler to use this format
            console.setFormatter(formatter)
            # add the handler to the root logger
            logger.addHandler(console)

        # set initial log level
        logging_file_handler_level = LoggerUtil.get_logging_level(LoggerUtil.file_handler_level)
        logging_console_handler_level = LoggerUtil.get_logging_level(LoggerUtil.console_handler_level)
        logging_root_level = (
            logging_console_handler_level if logging_file_handler_level > logging_console_handler_level else logging_file_handler_level)
        logger.setLevel(logging_root_level)

    @staticmethod
    def findCaller(stack_info=False):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = currentframe()
        # On some versions of IronPython, currentframe() returns None if
        # IronPython isn't run with -X:Frames.
        # if f is not None:
        #     f = f.f_back

        rv = "(unknown file)", 0, "(unknown function)", None
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back
                continue
            sinfo = None
            if stack_info:
                sio = io.StringIO()
                sio.write('Stack (most recent call last):\n')
                traceback.print_stack(f, file=sio)
                sinfo = sio.getvalue()
                if sinfo[-1] == '\n':
                    sinfo = sinfo[:-1]
                sio.close()
            rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
            break
        return rv

    @staticmethod
    def debug(msg: str, *args, **kwargs):
        LoggerUtil.debug_by_logger("", msg)

    @staticmethod
    def info(msg: str, *args, **kwargs):
        LoggerUtil.info_by_logger("", msg)

    @staticmethod
    def warning(msg: str, *args, **kwargs):
        LoggerUtil.warning_by_logger("", msg)

    @staticmethod
    def error(msg: str, *args, **kwargs):
        LoggerUtil.error_by_logger("", msg)

    @staticmethod
    def exception(msg: str, *args, **kwargs):
        LoggerUtil.exception_by_logger("", msg)

    @staticmethod
    def debug_by_logger(logger_name: str, msg: str, *args, **kwargs):

        fn, lno, func, sinfo = LoggerUtil.find_caller()

        package_path = LoggerUtil.gen_package_path(fn)
        module_file_path = LoggerUtil.gen_module_file_path(package_path)
        logger = LoggerUtil.get_logger_bymodule(logger_name, package_path, 'debug.log')

        msg = "%s  %s  %s  %s" % (module_file_path, func, lno, msg)
        logger.debug(msg)

    @staticmethod
    def info_by_logger(logger_name: str, msg: str, *args, **kwargs):
        fn, lno, func, sinfo = LoggerUtil.find_caller()
        package_path = LoggerUtil.gen_package_path(fn)
        module_file_path = LoggerUtil.gen_module_file_path(package_path)
        logger = LoggerUtil.get_logger_bymodule(logger_name, package_path, 'info.log')

        msg = "%s  %s  %s  %s" % (module_file_path, func, lno, msg)
        logger.info(msg)

    @staticmethod
    def warning_by_logger(logger_name, msg, *args, **kwargs):
        fn, lno, func, sinfo = LoggerUtil.find_caller()
        package_path = LoggerUtil.gen_package_path(fn)
        module_file_path = LoggerUtil.gen_module_file_path(package_path)
        logger = LoggerUtil.get_logger_bymodule(logger_name, package_path, 'warning.log')

        msg = "%s  %s  %s  %s" % (module_file_path, func, lno, msg)
        logger.warning(msg)

    @staticmethod
    def error_by_logger(logger_name, msg, *args, **kwargs):
        fn, lno, func, sinfo = LoggerUtil.find_caller()
        package_path = LoggerUtil.gen_package_path(fn)
        module_file_path = LoggerUtil.gen_module_file_path(package_path)
        logger = LoggerUtil.get_logger_bymodule(logger_name, package_path, 'error.log')

        msg = "%s  %s  %s  %s" % (module_file_path, func, lno, msg)
        logger.error(msg)

    @staticmethod
    def exception_by_logger(logger_name, msg, *args, **kwargs):
        fn, lno, func, sinfo = LoggerUtil.find_caller(True)
        package_path = LoggerUtil.gen_package_path(fn)
        module_file_path = LoggerUtil.gen_module_file_path(package_path)
        logger = LoggerUtil.get_logger_bymodule(logger_name, package_path, 'exception.log')

        msg = "%s  %s  %s  %s  %s" % (module_file_path, func, lno, msg, sinfo)
        logger.exception(msg)

    @staticmethod
    def find_caller(stack_info=False):
        try:
            fn, lno, func, sinfo = LoggerUtil.findCaller(stack_info)
        except ValueError:  # pragma: no cover
            fn, lno, func, sinfo = "(unknown file)", 0, "(unknown function)", None

        return (fn, lno, func, sinfo)

    @staticmethod
    def gen_package_path(fn):
        application_path = LoggerUtil.application_path;
        dir_pos = fn.find(application_path)
        if dir_pos >= 0:
            package_path = fn[len(application_path):]
            return package_path.replace('\\', '/')
        else:
            pyframe_dir_pos = fn.find("pyframework")
            if pyframe_dir_pos >= 0:
                package_path = fn[pyframe_dir_pos:]
                return package_path.replace('\\', '/')

        return application_path

    @staticmethod
    def get_logger_bymodule(logger_name, package_path, file_name):
        package_path = package_path[:package_path.rfind('/')]
        module_path = package_path.replace('/', '.')
        if StringHelper.is_not_empty(logger_name):
            cur_dir = LoggerUtil.log_dir + logger_name
            # module_name = module_path + '.' + logger_name
            logger = LoggerUtil.get_logger(logger_name, cur_dir, file_name)
        else:
            logger = logging.getLogger(LoggerUtil.root_logger_name)
        return logger

    @staticmethod
    def gen_module_file_path(package_path):
        module_file_path = package_path[:package_path.rfind('.')]
        module_file_path = module_file_path.replace('/', '.')
        return module_file_path


if __name__ == "__main__":
    # import sys
    # logger = logging.getLogger('')
    # format = logging.Formatter("%(asctime)s - %(message)s")  # output format
    # sh = logging.StreamHandler(stream=sys.stdout)  # output to standard output
    # sh.setFormatter(format)
    # logger.addHandler(sh)
    #
    # logger.setLevel(logging.NOTSET)
    # logger.info("this is info")
    # logger.debug("this is debug")
    # logger.warning("this is warning")
    # logging.error("this is error")
    # logger.critical("this is critical")

    LoggerUtil.debugTrace("debug 测试日志组件")  # 通用rootlogger

    LoggerUtil.debug("debug", "debug 测试日志组件")
    LoggerUtil.info("info", "info 测试日志组件")
    LoggerUtil.warning("warning", "warning 测试日志组件")
    LoggerUtil.error("error", "error 测试日志组件")

    LoggerUtil.exception("exception", "exception 测试日志组件")

    # logsignleton = LogSignleton('./config/logconfig.conf')
    # logger = logsignleton.get_logger()
