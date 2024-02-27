from datetime import datetime
import logging
from colorama import Fore, Back, Style
import sys
from info import PROJECT_LOG
import inspect
import os

# 创建日志记录器对象
logger = logging.getLogger('cgrepbot')
logger.setLevel(logging.INFO)

# 创建终端处理器，并设置日志级别
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建文件处理器，并设置日志级别和输出文件名
file_handler = logging.FileHandler(PROJECT_LOG)
file_handler.setLevel(logging.INFO)

# 创建格式化器，并将其应用于处理器
formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 将处理器添加到日志记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def get_call_format():
    frame = inspect.currentframe().f_back.f_back.f_back
    caller_filename = frame.f_code.co_filename
    filename_with_extension = os.path.basename(caller_filename)
    filename = os.path.splitext(filename_with_extension)[0]
    caller_lineno = frame.f_lineno
    function_name = frame.f_code.co_name
    if function_name == "<module>":
        function_name = inspect.getmodule(frame).__name__
    return filename, caller_lineno,function_name

def build_message(m_type, msg):
    filename, lineno,function_name = get_call_format()
    cur_tiem = datetime.now().strftime("%S.%f")
    return f"{cur_tiem} {filename}:{lineno:<3} [{function_name}] -> [{m_type}]: {str(msg)}"

class LOG:


    @staticmethod
    def debug(msg):
        logger.debug(f"{Fore.WHITE} {build_message('DEBUG',msg)} {Style.RESET_ALL}")

    @staticmethod
    def info(msg):
        logger.info(f"{Fore.GREEN} {build_message('INFO',msg)} {Style.RESET_ALL}")

    @staticmethod
    def warning(msg):
        logger.warning(f"\033[38;5;214m {build_message('WRANING',msg)} \033[m")

    @staticmethod
    def error(msg):
        logger.error(f"{Fore.RED} {build_message('ERROR',msg)} {Style.RESET_ALL}")

    @staticmethod
    def critical(msg):
        logger.critical(f"{Fore.RED} {build_message('CRITICAL',msg)} {Style.RESET_ALL}")
