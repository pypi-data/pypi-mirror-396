# Copyright (c) ZhangYundi.
# Licensed under the MIT License. 
# Created on 2025/7/18 20:28
# Description:

import sys
from pathlib import Path
from typing import Optional

from loguru import logger


def patch_name(record):
    record["extra"].setdefault("name", "?")


logger = logger.patch(patch_name)


class Logger:

    def __init__(self, name: str, debug_mode: bool = False, fname: str = None):

        _prod_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<lvl>{level:<8}</lvl> | - "
            "<green>[{extra[name]}:{line}]</green> <lvl>{message}</lvl>"
        )

        _debug_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<lvl>{level:<8}</lvl> | "
            "<cyan>{process}:{thread.name}</cyan> | "
            "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | - "
            "<green>[{extra[name]}]</green> {message}"
        )

        self._fname = fname
        self._format = _debug_format if debug_mode else _prod_format

        logger.remove()
        self._logger = logger.bind(name=name)

        self._setup_console_logging()
        self._setup_file_logging()
        self._setup_global_exception_handling()

    def _setup_console_logging(self):

        logger.add(
            sys.stderr,
            format=self._format,
            level="TRACE",
            colorize=True,
        )

    def _setup_file_logging(self):
        log_dir = "logs" if not self._fname else self._fname
        logs_dir = Path(log_dir)
        logs_dir.mkdir(exist_ok=True)

        self._logger.add(
            logs_dir / "{time:YYYYMMDD}.log",
            retention="10 days",
            format=self._format,
            level="TRACE"
        )

    def _setup_global_exception_handling(self):
        # 设置全局异常捕获
        def handle_exception(exc_type, exc_value, exc_traceback):
            """全局异常处理函数"""
            self._logger.opt(exception=(exc_type, exc_value, exc_traceback)).critical(
                "Unhandled exception occurred"
            )

        sys.excepthook = handle_exception

    def _msgs_to_str(self, *msg: str) -> str:
        return " ".join([str(m) for m in msg])

    def trace(self, *msg: str, **kwargs) -> None:
        """TRACE级别日志"""
        self._logger.opt(depth=1).trace(self._msgs_to_str(*msg), **kwargs)

    def debug(self, *msg: str, **kwargs) -> None:
        """DEBUG级别日志"""
        self._logger.opt(depth=1).debug(self._msgs_to_str(*msg), **kwargs)

    def info(self, *msg: str, **kwargs) -> None:
        """INFO级别日志"""
        self._logger.opt(depth=1, ).info(self._msgs_to_str(*msg), **kwargs)

    def warning(self, *msg: str, **kwargs) -> None:
        """WARNING级别日志"""
        self._logger.opt(depth=1).warning(self._msgs_to_str(*msg), **kwargs)

    def error(self, *msg: str, exc_info: Optional[BaseException] = None, **kwargs) -> None:
        """ERROR级别日志"""
        if exc_info:
            self._logger.opt(depth=1, exception=exc_info).error(self._msgs_to_str(*msg), **kwargs)
        else:
            self._logger.opt(depth=1).error(self._msgs_to_str(*msg), **kwargs)

    def critical(self, *msg: str, exc_info: Optional[BaseException] = None, **kwargs) -> None:
        """CRITICAL级别日志"""
        if exc_info:
            self._logger.opt(depth=1, exception=exc_info).critical(self._msgs_to_str(*msg), **kwargs)
        else:
            self._logger.opt(depth=1).critical(self._msgs_to_str(*msg), **kwargs)


def get_logger(name, debug_mode: bool = False, fname: str = None):
    return Logger(name=name, debug_mode=debug_mode, fname=fname)
