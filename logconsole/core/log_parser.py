"""
日志解析器 - 支持大文件分块读取和编码检测
"""
import os
from typing import List, Optional, Callable, Dict
import chardet


class LogParser:
    """日志文件解析器，支持 GB 级文件"""

    def __init__(self, chunk_size: int = 8 * 1024 * 1024):
        """
        初始化日志解析器

        Args:
            chunk_size: 块大小（默认 8MB）
        """
        self.chunk_size = chunk_size
        self.lines: List[str] = []
        self.encoding: str = "utf-8"
        self.file_path: Optional[str] = None

    def detect_encoding(self, file_path: str) -> str:
        """
        检测文件编码 - 优先尝试常见编码，chardet 作为后备

        Args:
            file_path: 文件路径

        Returns:
            编码名称（utf-8, gbk 等）
        """
        with open(file_path, "rb") as f:
            raw_data = f.read(32768)  # 读取 32KB 用于检测

        # 1. 检查 BOM
        if raw_data.startswith(b'\xef\xbb\xbf'):
            return "utf-8-sig"
        elif raw_data.startswith(b'\xff\xfe'):
            return "utf-16-le"
        elif raw_data.startswith(b'\xfe\xff'):
            return "utf-16-be"

        # 2. 优先尝试 UTF-8（最常见）
        try:
            raw_data.decode("utf-8")
            return "utf-8"
        except UnicodeDecodeError:
            pass

        # 3. 尝试 GBK（中文环境常见）
        try:
            raw_data.decode("gbk")
            return "gbk"
        except UnicodeDecodeError:
            pass

        # 4. chardet 作为后备
        result = chardet.detect(raw_data)
        encoding = result.get("encoding", "utf-8")

        # 统一处理常见编码
        if encoding and encoding.lower() in ["gb2312", "gb18030"]:
            return "gbk"

        return encoding or "utf-8"

    def load(
        self,
        file_path: str,
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, any]:
        """
        加载日志文件

        Args:
            file_path: 文件路径
            on_progress: 进度回调函数 (bytes_read, total_bytes)

        Returns:
            包含 lines, encoding, line_count 的字典
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        self.file_path = file_path
        self.encoding = self.detect_encoding(file_path)
        self.lines = []

        file_size = os.path.getsize(file_path)
        bytes_read = 0

        with open(file_path, "r", encoding=self.encoding, errors="replace") as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break

                # 按行分割
                chunk_lines = chunk.splitlines()
                self.lines.extend(chunk_lines)

                # 更新进度
                bytes_read = f.tell()
                if on_progress:
                    on_progress(bytes_read, file_size)

        return {
            "lines": self.lines,
            "encoding": self.encoding,
            "line_count": len(self.lines),
            "file_size": file_size
        }

    def get_line_count(self) -> int:
        """获取总行数"""
        return len(self.lines)

    def get_lines(self, start: int, end: int) -> List[str]:
        """
        获取指定范围的行

        Args:
            start: 起始行号（从 0 开始）
            end: 结束行号（不包含）

        Returns:
            行内容列表
        """
        start = max(0, start)
        end = min(len(self.lines), end)
        return self.lines[start:end]

    def get_line(self, line_number: int) -> Optional[str]:
        """
        获取单行内容

        Args:
            line_number: 行号（从 0 开始）

        Returns:
            行内容，如果超出范围返回 None
        """
        if 0 <= line_number < len(self.lines):
            return self.lines[line_number]
        return None
