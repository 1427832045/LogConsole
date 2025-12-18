"""
搜索引擎 - 支持正则表达式、忽略大小写、全文搜索
"""
import re
from typing import List, Tuple, Optional
from enum import Enum


class SearchMode(Enum):
    """搜索模式"""
    PLAIN = "plain"          # 普通文本
    REGEX = "regex"          # 正则表达式
    CASE_INSENSITIVE = "case_insensitive"  # 忽略大小写


class SearchEngine:
    """日志搜索引擎"""

    def __init__(self):
        self.matches: List[Tuple[int, int, int]] = []  # (line_number, start_pos, end_pos)
        self.current_match_index: int = -1

    def search(
        self,
        lines: List[str],
        pattern: str,
        mode: SearchMode = SearchMode.PLAIN,
        case_sensitive: bool = True
    ) -> List[Tuple[int, int, int]]:
        """
        搜索日志内容

        Args:
            lines: 日志行列表
            pattern: 搜索模式
            mode: 搜索模式（普通/正则/忽略大小写）
            case_sensitive: 是否区分大小写

        Returns:
            匹配结果列表 [(行号, 起始位置, 结束位置)]
        """
        if not pattern:
            self.matches = []
            return self.matches

        self.matches = []

        try:
            # 构建正则表达式
            if mode == SearchMode.REGEX:
                flags = 0 if case_sensitive else re.IGNORECASE
                regex = re.compile(pattern, flags)
            else:
                # 普通文本，转义特殊字符
                escaped = re.escape(pattern)
                flags = 0 if case_sensitive else re.IGNORECASE
                regex = re.compile(escaped, flags)

            # 搜索所有行
            for line_num, line in enumerate(lines):
                for match in regex.finditer(line):
                    self.matches.append((line_num, match.start(), match.end()))

        except re.error:
            # 正则表达式错误，返回空结果
            self.matches = []

        self.current_match_index = 0 if self.matches else -1
        return self.matches

    def get_match_count(self) -> int:
        """获取匹配数量"""
        return len(self.matches)

    def get_current_match(self) -> Optional[Tuple[int, int, int]]:
        """获取当前匹配"""
        if 0 <= self.current_match_index < len(self.matches):
            return self.matches[self.current_match_index]
        return None

    def next_match(self) -> Optional[Tuple[int, int, int]]:
        """跳转到下一个匹配"""
        if not self.matches:
            return None

        self.current_match_index = (self.current_match_index + 1) % len(self.matches)
        return self.get_current_match()

    def prev_match(self) -> Optional[Tuple[int, int, int]]:
        """跳转到上一个匹配"""
        if not self.matches:
            return None

        self.current_match_index = (self.current_match_index - 1 + len(self.matches)) % len(self.matches)
        return self.get_current_match()

    def clear(self):
        """清除搜索结果"""
        self.matches = []
        self.current_match_index = -1
