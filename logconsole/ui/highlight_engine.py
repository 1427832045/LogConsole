"""
高性能关键词高亮引擎
参考 VS Code / Sublime Text 的分层渲染架构

核心设计:
1. 分层管理 - 关键词/选中/搜索各层独立，合并时按优先级叠加
2. 懒加载 - 仅渲染可见区域 + 缓冲区
3. 防抖动 - 避免频繁触发重绘
4. 增量更新 - 滚动时仅更新新进入可见区的内容
"""
import re
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from PyQt5.QtWidgets import QTextEdit, QPlainTextEdit
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import QTimer, QObject, pyqtSignal


@dataclass
class HighlightRule:
    """高亮规则"""
    pattern: re.Pattern
    fg_color: str
    bg_color: str = ""
    bold: bool = False
    priority: int = 0  # 数值越高优先级越高


@dataclass
class HighlightLayer:
    """高亮层 - 存储一类高亮的所有 selections"""
    name: str
    priority: int  # 层优先级，数值越高越靠前渲染（会覆盖低优先级）
    selections: List[QTextEdit.ExtraSelection] = field(default_factory=list)
    enabled: bool = True


class HighlightEngine(QObject):
    """
    高性能高亮引擎

    特性:
    - 分层管理：keyword / selection / search / current_line 各层独立
    - 懒加载：仅处理可见区域 + 上下缓冲区
    - 防抖：合并短时间内的多次更新请求
    - 增量：滚动时仅处理新进入可见区的块
    """

    highlight_updated = pyqtSignal()

    # 层优先级常量（数值越高越靠后渲染，会覆盖前面的）
    LAYER_KEYWORD = 10
    LAYER_SELECTION = 20
    LAYER_SEARCH = 30
    LAYER_CURRENT_LINE = 5

    def __init__(self, viewer: QTextEdit, buffer_lines: int = 50):
        super().__init__()
        self.viewer = viewer
        self.buffer_lines = buffer_lines

        # 高亮层
        self._layers: Dict[str, HighlightLayer] = {
            "current_line": HighlightLayer("current_line", self.LAYER_CURRENT_LINE),
            "keyword": HighlightLayer("keyword", self.LAYER_KEYWORD),
            "selection": HighlightLayer("selection", self.LAYER_SELECTION),
            "search": HighlightLayer("search", self.LAYER_SEARCH),
        }

        # 关键词规则缓存
        self._keyword_rules: List[HighlightRule] = []

        # 防抖定时器
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._do_apply)
        self._debounce_ms = 16  # ~60fps

        # 上次可见区域（用于增量更新）
        self._last_visible_range = (0, 0)

        # 是否需要全量刷新
        self._needs_full_refresh = True

    def set_keyword_rules(self, rules: List[HighlightRule]):
        """设置关键词高亮规则"""
        self._keyword_rules = rules
        self._needs_full_refresh = True
        self._schedule_apply()

    def clear_keyword_rules(self):
        """清除关键词规则"""
        self._keyword_rules = []
        self._layers["keyword"].selections = []
        self._needs_full_refresh = True
        self._schedule_apply()

    def set_selection_highlight(self, word: str, current_pos: tuple = None):
        """设置选中词高亮（高亮所有相同词）"""
        if not word or len(word) < 2:
            self._layers["selection"].selections = []
            self._schedule_apply()
            return

        selections = []
        doc = self.viewer.document()

        try:
            pattern = re.compile(re.escape(word), re.IGNORECASE)

            # 仅在可见区域搜索（性能优化）
            start_block, end_block = self._get_visible_range()
            block = doc.findBlockByNumber(start_block)

            for _ in range(end_block - start_block + 1):
                if not block.isValid():
                    break

                text = block.text()
                block_pos = block.position()

                for match in pattern.finditer(text):
                    sel = QTextEdit.ExtraSelection()
                    cursor = QTextCursor(doc)
                    cursor.setPosition(block_pos + match.start())
                    cursor.setPosition(block_pos + match.end(), QTextCursor.KeepAnchor)

                    fmt = QTextCharFormat()
                    # 当前选中位置用不同颜色
                    if current_pos and match.start() + block_pos == current_pos[0]:
                        fmt.setBackground(QColor("#FF9500"))
                        fmt.setForeground(QColor("#FFFFFF"))
                        fmt.setFontWeight(QFont.Bold)
                    else:
                        fmt.setBackground(QColor("#FFEB3B"))
                        fmt.setForeground(QColor("#1A1A1A"))

                    sel.cursor = cursor
                    sel.format = fmt
                    selections.append(sel)

                block = block.next()

        except re.error:
            pass

        self._layers["selection"].selections = selections
        self._schedule_apply()

    def clear_selection_highlight(self):
        """清除选中高亮"""
        self._layers["selection"].selections = []
        self._schedule_apply()

    def set_search_highlight(self, block, match_start: int, match_end: int):
        """设置搜索结果高亮（当前匹配行 + 匹配词）"""
        selections = []

        # 当前行背景
        line_sel = QTextEdit.ExtraSelection()
        line_fmt = QTextCharFormat()
        line_fmt.setBackground(QColor(255, 200, 50, 40))
        line_fmt.setProperty(QTextCharFormat.FullWidthSelection, True)
        line_cursor = QTextCursor(block)
        line_cursor.clearSelection()
        line_sel.cursor = line_cursor
        line_sel.format = line_fmt
        selections.append(line_sel)

        # 匹配词高亮
        if match_end > match_start:
            word_sel = QTextEdit.ExtraSelection()
            word_fmt = QTextCharFormat()
            word_fmt.setBackground(QColor("#FF9500"))
            word_fmt.setForeground(QColor("#000000"))
            word_fmt.setFontWeight(QFont.Bold)
            word_fmt.setUnderlineStyle(QTextCharFormat.SingleUnderline)
            word_fmt.setUnderlineColor(QColor("#FF5500"))

            word_cursor = QTextCursor(block)
            word_cursor.setPosition(block.position() + match_start)
            word_cursor.setPosition(block.position() + match_end, QTextCursor.KeepAnchor)
            word_sel.cursor = word_cursor
            word_sel.format = word_fmt
            selections.append(word_sel)

        self._layers["search"].selections = selections
        self._schedule_apply()

    def clear_search_highlight(self):
        """清除搜索高亮"""
        self._layers["search"].selections = []
        self._schedule_apply()

    def refresh_keywords(self):
        """刷新关键词高亮（滚动时调用）"""
        if not self._keyword_rules:
            return
        self._build_keyword_selections()
        self._schedule_apply()

    def force_refresh(self):
        """强制全量刷新"""
        self._needs_full_refresh = True
        self._build_keyword_selections()
        self._do_apply()

    def _get_visible_range(self) -> tuple:
        """获取可见行范围（含缓冲区）"""
        doc = self.viewer.document()
        total_blocks = doc.blockCount()

        if total_blocks == 0:
            return (0, 0)

        # 获取可见区域
        viewport = self.viewer.viewport()
        top_cursor = self.viewer.cursorForPosition(viewport.rect().topLeft())
        bottom_cursor = self.viewer.cursorForPosition(viewport.rect().bottomRight())

        start = max(0, top_cursor.block().blockNumber() - self.buffer_lines)
        end = min(total_blocks - 1, bottom_cursor.block().blockNumber() + self.buffer_lines)

        return (start, end)

    def _build_keyword_selections(self):
        """构建关键词高亮 selections"""
        if not self._keyword_rules:
            self._layers["keyword"].selections = []
            return

        selections = []
        doc = self.viewer.document()
        total_blocks = doc.blockCount()

        # 小文件全量，大文件仅可见区域
        if total_blocks < 3000:
            start_num, end_num = 0, total_blocks - 1
        else:
            start_num, end_num = self._get_visible_range()

        block = doc.findBlockByNumber(start_num)

        for _ in range(end_num - start_num + 1):
            if not block.isValid():
                break

            text = block.text()
            block_pos = block.position()

            for rule in self._keyword_rules:
                for match in rule.pattern.finditer(text):
                    sel = QTextEdit.ExtraSelection()
                    cursor = QTextCursor(doc)
                    cursor.setPosition(block_pos + match.start())
                    cursor.setPosition(block_pos + match.end(), QTextCursor.KeepAnchor)

                    fmt = QTextCharFormat()
                    fmt.setForeground(QColor(rule.fg_color))
                    if rule.bg_color:
                        fmt.setBackground(QColor(rule.bg_color))
                    if rule.bold:
                        fmt.setFontWeight(QFont.Bold)

                    sel.cursor = cursor
                    sel.format = fmt
                    selections.append(sel)

            block = block.next()

        self._layers["keyword"].selections = selections

    def _schedule_apply(self):
        """调度应用（防抖）"""
        if not self._debounce_timer.isActive():
            self._debounce_timer.start(self._debounce_ms)

    def _do_apply(self):
        """执行应用 - 合并所有层并设置到 viewer"""
        # 按优先级排序层
        sorted_layers = sorted(
            self._layers.values(),
            key=lambda l: l.priority
        )

        # 合并所有启用的层
        merged = []
        for layer in sorted_layers:
            if layer.enabled:
                merged.extend(layer.selections)

        # 应用到 viewer
        self.viewer.setExtraSelections(merged)
        self.highlight_updated.emit()

    def on_scroll(self):
        """滚动事件处理 - 仅大文件需要"""
        doc = self.viewer.document()
        if doc.blockCount() >= 3000 and self._keyword_rules:
            self._build_keyword_selections()
            self._schedule_apply()


def create_highlight_engine(viewer: QTextEdit) -> HighlightEngine:
    """工厂函数 - 创建高亮引擎"""
    return HighlightEngine(viewer)
