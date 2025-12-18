"""
SearchEngine 单元测试
"""
import pytest
from logconsole.core.search_engine import SearchEngine, SearchMode


class TestSearchEngine:
    """SearchEngine 测试类"""

    @pytest.fixture
    def engine(self):
        """创建 SearchEngine 实例"""
        return SearchEngine()

    @pytest.fixture
    def sample_lines(self):
        """示例日志行"""
        return [
            "2024-12-16 10:00:00 INFO Application started",
            "2024-12-16 10:00:01 ERROR Connection refused",
            "2024-12-16 10:00:02 WARN High memory usage",
            "2024-12-16 10:00:03 DEBUG Query executed",
            "2024-12-16 10:00:04 INFO User logged in",
            "2024-12-16 10:00:05 ERROR Database connection failed",
        ]

    def test_plain_search(self, engine, sample_lines):
        """测试普通文本搜索"""
        matches = engine.search(sample_lines, "ERROR", SearchMode.PLAIN)

        assert len(matches) == 2
        assert matches[0][0] == 1  # 第二行
        assert matches[1][0] == 5  # 第六行

    def test_case_insensitive_search(self, engine, sample_lines):
        """测试忽略大小写搜索"""
        matches = engine.search(sample_lines, "error", SearchMode.PLAIN, case_sensitive=False)

        assert len(matches) == 2

    def test_case_sensitive_search(self, engine, sample_lines):
        """测试区分大小写搜索"""
        matches = engine.search(sample_lines, "error", SearchMode.PLAIN, case_sensitive=True)

        assert len(matches) == 0  # 全是大写 ERROR

        matches = engine.search(sample_lines, "ERROR", SearchMode.PLAIN, case_sensitive=True)
        assert len(matches) == 2

    def test_regex_search(self, engine, sample_lines):
        """测试正则表达式搜索"""
        matches = engine.search(sample_lines, r"\d{4}-\d{2}-\d{2}", SearchMode.REGEX)

        assert len(matches) == 6  # 所有行都有日期

    def test_regex_error_handling(self, engine, sample_lines):
        """测试正则表达式错误处理"""
        # 无效的正则表达式
        matches = engine.search(sample_lines, r"[invalid(", SearchMode.REGEX)

        assert len(matches) == 0  # 应该返回空结果而不是崩溃

    def test_empty_pattern(self, engine, sample_lines):
        """测试空模式"""
        matches = engine.search(sample_lines, "", SearchMode.PLAIN)

        assert len(matches) == 0

    def test_no_matches(self, engine, sample_lines):
        """测试无匹配结果"""
        matches = engine.search(sample_lines, "NOTFOUND", SearchMode.PLAIN)

        assert len(matches) == 0
        assert engine.get_match_count() == 0

    def test_get_current_match(self, engine, sample_lines):
        """测试获取当前匹配"""
        engine.search(sample_lines, "ERROR", SearchMode.PLAIN)

        current = engine.get_current_match()
        assert current is not None
        assert current[0] == 1  # 第二行

    def test_next_match(self, engine, sample_lines):
        """测试跳转到下一个匹配"""
        engine.search(sample_lines, "ERROR", SearchMode.PLAIN)

        # 第一个匹配
        match1 = engine.get_current_match()
        assert match1[0] == 1

        # 下一个匹配
        match2 = engine.next_match()
        assert match2[0] == 5

        # 循环回第一个
        match3 = engine.next_match()
        assert match3[0] == 1

    def test_prev_match(self, engine, sample_lines):
        """测试跳转到上一个匹配"""
        engine.search(sample_lines, "ERROR", SearchMode.PLAIN)

        # 当前是第一个，上一个应该是最后一个
        match1 = engine.prev_match()
        assert match1[0] == 5

        # 再上一个
        match2 = engine.prev_match()
        assert match2[0] == 1

    def test_clear(self, engine, sample_lines):
        """测试清除搜索结果"""
        engine.search(sample_lines, "ERROR", SearchMode.PLAIN)
        assert engine.get_match_count() == 2

        engine.clear()
        assert engine.get_match_count() == 0
        assert engine.get_current_match() is None

    def test_match_positions(self, engine):
        """测试匹配位置"""
        lines = ["Error at start", "Middle Error here", "End of line Error"]
        matches = engine.search(lines, "Error", SearchMode.PLAIN)

        assert len(matches) == 3
        assert matches[0] == (0, 0, 5)     # 起始位置
        assert matches[1] == (1, 7, 12)    # 中间位置
        assert matches[2] == (2, 12, 17)   # 结尾位置（修正：实际位置是12-17）

    def test_multiple_matches_per_line(self, engine):
        """测试单行多个匹配"""
        lines = ["Error: Connection Error occurred"]
        matches = engine.search(lines, "Error", SearchMode.PLAIN)

        assert len(matches) == 2
        assert matches[0][1] == 0
        assert matches[1][1] == 18  # 修正：实际位置是18（"Connection Error"中的E）

    def test_special_regex_characters(self, engine):
        """测试特殊正则字符转义"""
        lines = ["Price: $100.00", "Score: 85%"]
        matches = engine.search(lines, "$100", SearchMode.PLAIN)

        assert len(matches) == 1  # 应该被正确转义
