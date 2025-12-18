"""
LogConsole - 专业日志查看工具
Material Design 3 Dark Theme
"""

__version__ = "0.1.0"
__author__ = "LogConsole Team"

from .core.log_parser import LogParser
from .core.search_engine import SearchEngine
from .ui.main_window import MainWindow

__all__ = ["LogParser", "SearchEngine", "MainWindow"]
