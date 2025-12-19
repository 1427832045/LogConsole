"""
虚拟滚动日志查看器 - 支持 GB 级文件秒开
只渲染可见区域的行，内存占用极低
"""
import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollBar, QPlainTextEdit,
    QHBoxLayout, QFrame, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor, QColor, QPalette, QTextCharFormat


class VirtualLogViewer(QWidget):
    """虚拟滚动日志查看器 - 只渲染可见行"""

    # 信号
    selection_changed = pyqtSignal(str)  # 选中文本变化
    context_menu_requested = pyqtSignal(object)  # 右键菜单请求
    scroll_changed = pyqtSignal()  # 滚动变化信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lines = []  # 原始行数据
        self.visible_lines = 50  # 可见行数
        self.line_height = 18  # 行高（像素）
        self.current_top_line = 0  # 当前顶部行号
        self.show_line_numbers = True

        # 高亮状态
        self._search_pattern = None  # 搜索模式
        self._selection_word = None  # 选中词高亮
        self._pending_highlight = False  # 是否有待处理的高亮

        self.init_ui()

    def init_ui(self):
        """初始化 UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 文本显示区域（使用 QPlainTextEdit 作为显示器）
        self.text_view = QPlainTextEdit()
        self.text_view.setReadOnly(True)
        self.text_view.setFont(QFont("Menlo", 11))
        self.text_view.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.text_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_view.customContextMenuRequested.connect(
            lambda pos: self.context_menu_requested.emit(pos)
        )

        # 应用样式
        self.text_view.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0D1117;
                color: #C9D1D9;
                border: none;
                selection-background-color: #1F6FEB;
                selection-color: #FFFFFF;
                padding: 4px;
            }
        """)

        layout.addWidget(self.text_view)

        # 自定义滚动条
        self.scrollbar = QScrollBar(Qt.Vertical)
        self.scrollbar.setStyleSheet("""
            QScrollBar:vertical {
                background-color: #161B22;
                width: 12px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #30363D;
                min-height: 30px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #484F58;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        self.scrollbar.valueChanged.connect(self.on_scroll)
        layout.addWidget(self.scrollbar)

        # 监听文本区域的滚轮事件
        self.text_view.wheelEvent = self.handle_wheel_event

    def handle_wheel_event(self, event):
        """处理滚轮事件"""
        delta = event.angleDelta().y()
        lines_to_scroll = -delta // 40  # 每次滚动 3 行左右
        new_value = self.scrollbar.value() + lines_to_scroll
        self.scrollbar.setValue(max(0, min(new_value, self.scrollbar.maximum())))

    def set_lines(self, lines: list):
        """设置日志行数据"""
        self.lines = lines
        self.current_top_line = 0

        # 更新滚动条范围
        max_scroll = max(0, len(lines) - self.visible_lines)
        self.scrollbar.setRange(0, max_scroll)
        self.scrollbar.setValue(0)

        # 渲染可见区域
        self.render_visible_lines()

    def render_visible_lines(self):
        """渲染可见区域的行"""
        if not self.lines:
            self.text_view.setPlainText("")
            return

        start = self.current_top_line
        end = min(start + self.visible_lines + 10, len(self.lines))  # 多渲染几行做缓冲

        # 构建可见文本
        if self.show_line_numbers:
            visible_text = "\n".join(
                f"{i+1:6d} │ {self.lines[i]}"
                for i in range(start, end)
            )
        else:
            visible_text = "\n".join(self.lines[start:end])

        # 更新显示（保持水平滚动位置）
        h_scroll = self.text_view.horizontalScrollBar().value()
        self.text_view.setPlainText(visible_text)
        self.text_view.horizontalScrollBar().setValue(h_scroll)

    def on_scroll(self, value):
        """滚动事件处理"""
        self.current_top_line = value
        self.render_visible_lines()
        self._apply_highlights()
        self.scroll_changed.emit()

    def scroll_to_line(self, line_num: int, highlight: bool = True):
        """滚动到指定行"""
        if not self.lines or line_num < 0 or line_num >= len(self.lines):
            return

        # 计算目标滚动位置（居中显示）
        target = max(0, line_num - self.visible_lines // 2)
        self.scrollbar.setValue(target)

        if highlight:
            # 高亮目标行
            QTimer.singleShot(50, lambda: self.highlight_line(line_num))

    def highlight_line(self, line_num: int):
        """高亮指定行"""
        # 计算相对于当前视口的行号
        relative_line = line_num - self.current_top_line
        if relative_line < 0 or relative_line >= self.visible_lines + 10:
            return

        cursor = self.text_view.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, relative_line)
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        self.text_view.setTextCursor(cursor)

    def get_selected_text(self) -> str:
        """获取选中的文本"""
        return self.text_view.textCursor().selectedText()

    def get_word_at_position(self, pos) -> str:
        """获取指定位置的单词"""
        cursor = self.text_view.cursorForPosition(pos)
        cursor.select(QTextCursor.WordUnderCursor)
        return cursor.selectedText()

    def get_actual_line_number(self, relative_line: int) -> int:
        """获取实际行号（从相对行号）"""
        return self.current_top_line + relative_line

    def set_line_wrap(self, enabled: bool):
        """设置自动换行"""
        mode = QPlainTextEdit.WidgetWidth if enabled else QPlainTextEdit.NoWrap
        self.text_view.setLineWrapMode(mode)

    def resizeEvent(self, event):
        """窗口大小变化时重新计算可见行数"""
        super().resizeEvent(event)
        # 根据窗口高度计算可见行数
        self.visible_lines = max(10, self.height() // self.line_height)
        self.render_visible_lines()

    def toPlainText(self) -> str:
        """兼容 QTextEdit 接口 - 返回所有行"""
        if self.show_line_numbers:
            return "\n".join(
                f"{i+1:6d} │ {line}"
                for i, line in enumerate(self.lines)
            )
        return "\n".join(self.lines)

    def textCursor(self):
        """兼容 QTextEdit 接口"""
        return self.text_view.textCursor()

    def setTextCursor(self, cursor):
        """兼容 QTextEdit 接口"""
        self.text_view.setTextCursor(cursor)

    def ensureCursorVisible(self):
        """兼容 QTextEdit 接口"""
        self.text_view.ensureCursorVisible()

    def cursorForPosition(self, pos):
        """兼容 QTextEdit 接口"""
        return self.text_view.cursorForPosition(pos)

    def mapToGlobal(self, pos):
        """兼容 QTextEdit 接口"""
        return self.text_view.mapToGlobal(pos)

    # ========== 高亮功能 ==========

    def set_search_pattern(self, pattern: str, is_regex: bool = False, case_sensitive: bool = False):
        """设置搜索高亮模式"""
        if pattern:
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                if is_regex:
                    self._search_pattern = re.compile(pattern, flags)
                else:
                    self._search_pattern = re.compile(re.escape(pattern), flags)
            except re.error:
                self._search_pattern = None
        else:
            self._search_pattern = None
        self._apply_highlights()

    def set_selection_highlight(self, word: str):
        """设置选中词高亮"""
        if word and len(word) >= 2:
            try:
                self._selection_word = re.compile(re.escape(word), re.IGNORECASE)
            except re.error:
                self._selection_word = None
        else:
            self._selection_word = None
        self._apply_highlights()

    def clear_selection_highlight(self):
        """清除选中词高亮"""
        self._selection_word = None
        self._apply_highlights()

    def _apply_highlights(self):
        """应用高亮到当前可见区域（使用 ExtraSelections）"""
        selections = []
        doc = self.text_view.document()

        # 搜索高亮（黄色背景）
        if self._search_pattern:
            search_fmt = QTextCharFormat()
            search_fmt.setBackground(QColor("#FFE66D"))
            search_fmt.setForeground(QColor("#000000"))
            search_fmt.setFontWeight(QFont.Bold)

            block = doc.begin()
            while block.isValid():
                text = block.text()
                block_pos = block.position()
                for match in self._search_pattern.finditer(text):
                    sel = QTextEdit.ExtraSelection()
                    cursor = QTextCursor(doc)
                    cursor.setPosition(block_pos + match.start())
                    cursor.setPosition(block_pos + match.end(), QTextCursor.KeepAnchor)
                    sel.cursor = cursor
                    sel.format = search_fmt
                    selections.append(sel)
                block = block.next()

        # 选中词高亮（橙色背景）
        if self._selection_word:
            sel_fmt = QTextCharFormat()
            sel_fmt.setBackground(QColor("#FF9500"))
            sel_fmt.setForeground(QColor("#FFFFFF"))
            sel_fmt.setFontWeight(QFont.Bold)

            block = doc.begin()
            while block.isValid():
                text = block.text()
                block_pos = block.position()
                for match in self._selection_word.finditer(text):
                    sel = QTextEdit.ExtraSelection()
                    cursor = QTextCursor(doc)
                    cursor.setPosition(block_pos + match.start())
                    cursor.setPosition(block_pos + match.end(), QTextCursor.KeepAnchor)
                    sel.cursor = cursor
                    sel.format = sel_fmt
                    selections.append(sel)
                block = block.next()

        self.text_view.setExtraSelections(selections)
