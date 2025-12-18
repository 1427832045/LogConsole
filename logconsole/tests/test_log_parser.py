"""
LogParser 单元测试
"""
import pytest
import os
import tempfile
from logconsole.core.log_parser import LogParser


class TestLogParser:
    """LogParser 测试类"""

    @pytest.fixture
    def parser(self):
        """创建 LogParser 实例"""
        return LogParser()

    @pytest.fixture
    def sample_log_file(self):
        """创建示例日志文件"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.log') as f:
            f.write("2024-12-16 10:00:00 INFO Application started\n")
            f.write("2024-12-16 10:00:01 ERROR Connection refused\n")
            f.write("2024-12-16 10:00:02 WARN High memory usage\n")
            f.write("2024-12-16 10:00:03 DEBUG Query executed\n")
            f.write("2024-12-16 10:00:04 INFO User logged in\n")
            file_path = f.name

        yield file_path

        # 清理临时文件
        os.unlink(file_path)

    def test_load_file(self, parser, sample_log_file):
        """测试加载文件"""
        result = parser.load(sample_log_file)

        assert result["line_count"] == 5
        assert result["encoding"] in ["utf-8", "utf-8-sig", "ascii"]
        assert len(result["lines"]) == 5
        assert "ERROR Connection refused" in result["lines"][1]

    def test_detect_encoding_utf8(self, parser, sample_log_file):
        """测试 UTF-8 编码检测"""
        encoding = parser.detect_encoding(sample_log_file)
        assert encoding in ["utf-8", "utf-8-sig", "ascii"]

    def test_detect_encoding_utf8_bom(self, parser):
        """测试 UTF-8 BOM 检测"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.log') as f:
            f.write(b'\xef\xbb\xbf')  # UTF-8 BOM
            f.write("test content".encode('utf-8'))
            file_path = f.name

        try:
            encoding = parser.detect_encoding(file_path)
            assert encoding == "utf-8-sig"
        finally:
            os.unlink(file_path)

    def test_get_lines(self, parser, sample_log_file):
        """测试获取指定行"""
        parser.load(sample_log_file)

        lines = parser.get_lines(1, 3)
        assert len(lines) == 2
        assert "ERROR" in lines[0]
        assert "WARN" in lines[1]

    def test_get_line(self, parser, sample_log_file):
        """测试获取单行"""
        parser.load(sample_log_file)

        line = parser.get_line(1)
        assert "ERROR Connection refused" in line

        # 超出范围
        line = parser.get_line(999)
        assert line is None

    def test_get_line_count(self, parser, sample_log_file):
        """测试获取总行数"""
        parser.load(sample_log_file)
        assert parser.get_line_count() == 5

    def test_load_non_existent_file(self, parser):
        """测试加载不存在的文件"""
        with pytest.raises(FileNotFoundError):
            parser.load("/non/existent/file.log")

    def test_load_with_progress(self, parser, sample_log_file):
        """测试带进度回调的加载"""
        progress_calls = []

        def on_progress(bytes_read, total):
            progress_calls.append((bytes_read, total))

        result = parser.load(sample_log_file, on_progress=on_progress)

        assert result["line_count"] == 5
        assert len(progress_calls) > 0

    def test_large_file_chunking(self, parser):
        """测试大文件分块读取"""
        # 创建一个较大的文件（超过默认 chunk size）
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.log') as f:
            for i in range(10000):
                f.write(f"Line {i}: " + "A" * 100 + "\n")
            file_path = f.name

        try:
            result = parser.load(file_path)
            assert result["line_count"] == 10000
        finally:
            os.unlink(file_path)

    def test_empty_file(self, parser):
        """测试空文件"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.log') as f:
            file_path = f.name

        try:
            result = parser.load(file_path)
            assert result["line_count"] == 0
            assert len(result["lines"]) == 0
        finally:
            os.unlink(file_path)
