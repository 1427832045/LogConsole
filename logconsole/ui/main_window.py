"""
LogConsole 主窗口 - 专业美化版
参考 VSCode/IntelliJ IDEA 设计
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPlainTextEdit, QPushButton, QLineEdit, QLabel,
    QFileDialog, QStatusBar, QCheckBox, QAction,
    QToolBar, QMessageBox, QFrame, QShortcut, QSplitter,
    QListWidget, QListWidgetItem, QComboBox, QTabWidget, QMenu,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QStyledItemDelegate,
    QStyle, QStyleOptionViewItem, QApplication
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import (
    QFont, QColor, QPalette, QTextCharFormat,
    QTextCursor, QSyntaxHighlighter, QKeySequence,
    QTextDocument, QIcon
)
from typing import Optional

from ..core.log_parser import LogParser
from ..core.search_engine import SearchEngine, SearchMode
from ..core.template_manager import TemplateManager
from ..core.highlight_template import HighlightTemplate, HighlightRule
from .virtual_log_viewer import VirtualLogViewer
from .search_dialog import SearchDialog
from .apple_hig_theme import (
    APPLE_COLORS, APPLE_FONT_FAMILY, APPLE_MONO_FONT, ICONS,
    get_main_window_style, get_toolbar_style, get_tab_widget_style,
    get_combobox_style, get_tree_widget_style, get_search_panel_style,
    get_context_menu_style, get_grep_filter_bar_style, get_grep_tag_style,
    get_count_label_style, get_add_grep_dialog_style
)
from ..core.keyword_highlight import KeywordHighlightManager, PRESET_COLORS
from .highlight_panel import HighlightManagePanel, ColorPickerDialog

# 大文件阈值（字节），超过此大小使用虚拟滚动
LARGE_FILE_THRESHOLD = 10 * 1024 * 1024  # 10MB


# ========== 搜索结果富文本代理 ==========
class HighlightDelegate(QStyledItemDelegate):
    """支持 HTML 富文本渲染的 QTreeWidget 代理，用于部分高亮匹配词"""

    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget else QApplication.style()

        # 使用 QTextDocument 渲染 HTML
        doc = QTextDocument()
        doc.setDefaultFont(option.font)
        # 设置默认文字颜色（浅灰色，适配深色背景）
        doc.setDefaultStyleSheet(f"body {{ color: {APPLE_COLORS['text_primary']}; }}")
        doc.setHtml(f"<body>{option.text}</body>")

        # 绘制背景（选中/悬停状态）
        option.text = ""
        style.drawControl(QStyle.CE_ItemViewItem, option, painter, option.widget)

        # 绘制文本 - 垂直居中
        painter.save()
        text_rect = style.subElementRect(QStyle.SE_ItemViewItemText, option, option.widget)
        # 计算垂直居中偏移
        doc_height = doc.size().height()
        y_offset = max(0, (text_rect.height() - doc_height) / 2)
        painter.translate(text_rect.left(), text_rect.top() + y_offset)
        painter.setClipRect(text_rect.translated(-text_rect.left(), -text_rect.top() - y_offset))
        doc.drawContents(painter)
        painter.restore()

    def sizeHint(self, option, index):
        # 使用默认 sizeHint，保持行高一致
        size = super().sizeHint(option, index)
        # 确保最小行高为 24px
        size.setHeight(max(size.height(), 24))
        return size


# ========== 现代化日志语法高亮器 ==========
class ModernLogHighlighter(QSyntaxHighlighter):
    """现代化日志语法高亮器 - 支持模板系统 + 用户关键词高亮"""

    def __init__(self, parent: QTextDocument, template: Optional[HighlightTemplate] = None):
        super().__init__(parent)
        self.template = template
        self.search_pattern = None
        self.compiled_rules = []
        self.user_keyword_rules = []  # 用户关键词高亮规则
        self._dirty_blocks = set()  # 需要重新高亮的 block
        self.apply_template(template)

    def apply_template(self, template: Optional[HighlightTemplate]):
        """应用模板"""
        self.template = template
        self.compiled_rules = []

        if not template:
            return

        # 按优先级排序规则
        sorted_rules = sorted(template.rules, key=lambda r: r.priority, reverse=True)

        # 预编译正则表达式
        import re
        for rule in sorted_rules:
            if not rule.enabled:
                continue

            try:
                if rule.is_regex:
                    pattern = re.compile(rule.pattern)
                else:
                    pattern = re.compile(re.escape(rule.pattern))

                # 创建格式
                fmt = QTextCharFormat()
                if rule.foreground:
                    fmt.setForeground(QColor(rule.foreground))
                if rule.background:
                    fmt.setBackground(QColor(rule.background))
                if rule.bold:
                    fmt.setFontWeight(QFont.Bold)
                if rule.italic:
                    fmt.setFontItalic(True)
                if rule.underline:
                    fmt.setFontUnderline(True)

                self.compiled_rules.append((rule.name, pattern, fmt, rule.priority))
            except re.error:
                # 忽略无效正则
                pass

        # 搜索高亮格式（最高优先级）
        self.search_highlight_fmt = QTextCharFormat()
        self.search_highlight_fmt.setBackground(QColor("#FFE66D"))
        self.search_highlight_fmt.setForeground(QColor("#000000"))
        self.search_highlight_fmt.setFontWeight(QFont.Bold)

    def set_search_pattern(self, pattern: str, is_regex: bool = False, case_sensitive: bool = False):
        """设置搜索模式"""
        import re
        if pattern:
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                if is_regex:
                    self.search_pattern = re.compile(pattern, flags)
                else:
                    self.search_pattern = re.compile(re.escape(pattern), flags)
            except:
                self.search_pattern = None
        else:
            self.search_pattern = None

    def set_user_keywords(self, keywords: list, mark_dirty: bool = True):
        """设置用户关键词高亮规则"""
        import re
        self.user_keyword_rules = []
        for kw in keywords:
            if not kw.enabled:
                continue
            try:
                pattern = re.compile(re.escape(kw.keyword), re.IGNORECASE)
                fmt = QTextCharFormat()
                fmt.setForeground(QColor(kw.fg_color))
                if kw.bg_color:
                    fmt.setBackground(QColor(kw.bg_color))
                if kw.bold:
                    fmt.setFontWeight(QFont.Bold)
                self.user_keyword_rules.append((kw.keyword, pattern, fmt))
            except re.error:
                pass

        # 标记所有 block 为脏（需要重新高亮）
        if mark_dirty:
            self._needs_full_rehighlight = True

    def highlightBlock(self, text: str):
        """高亮单行文本"""
        # 1. 应用模板规则（按优先级）
        for rule_name, pattern, fmt, priority in self.compiled_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)

        # 2. 应用用户关键词高亮（优先级高于模板）
        for keyword, pattern, fmt in self.user_keyword_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)

        # 3. 搜索匹配高亮（最高优先级，覆盖所有其他格式）
        if self.search_pattern:
            for match in self.search_pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), self.search_highlight_fmt)


# ========== 文件加载线程 ==========
class LoadFileThread(QThread):
    """文件加载线程"""
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.parser = LogParser()

    def run(self):
        try:
            result = self.parser.load(
                self.file_path,
                on_progress=lambda br, tb: self.progress.emit(br, tb)
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# ========== 专业搜索面板 ==========
class ModernSearchPanel(QFrame):
    """现代化搜索面板 - 参考 IntelliJ IDEA"""

    search_requested = pyqtSignal(str, bool, bool)
    next_match = pyqtSignal()
    prev_match = pyqtSignal()
    closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """设置 UI"""
        self.setFrameShape(QFrame.StyledPanel)
        self.setAutoFillBackground(True)

        # Apple HIG 风格样式
        self.setStyleSheet(get_search_panel_style())

        # 主布局 - 8px Grid
        layout = QHBoxLayout()
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(16)

        # 搜索输入区
        search_container = QHBoxLayout()
        search_container.setSpacing(12)

        # 搜索图标
        search_icon = QLabel("⌕")
        search_icon.setStyleSheet(f"font-size: 14px; color: {APPLE_COLORS['label_tertiary']};")
        search_container.addWidget(search_icon)

        # 搜索输入框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.setMinimumWidth(320)
        self.search_input.returnPressed.connect(self._emit_search)
        self.search_input.textChanged.connect(self._emit_search)
        search_container.addWidget(self.search_input)

        layout.addLayout(search_container)

        # 匹配计数 - Pill 样式
        self.match_label = QLabel("0 / 0")
        self.match_label.setObjectName("matchCount")
        self.match_label.setMinimumWidth(72)
        self.match_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.match_label)

        # 导航按钮组
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(4)

        prev_btn = QPushButton("↑")
        prev_btn.setFixedSize(32, 32)
        prev_btn.setToolTip("Previous (Shift+F3)")
        prev_btn.clicked.connect(self.prev_match.emit)
        nav_layout.addWidget(prev_btn)

        next_btn = QPushButton("↓")
        next_btn.setFixedSize(32, 32)
        next_btn.setToolTip("Next (F3)")
        next_btn.clicked.connect(self.next_match.emit)
        nav_layout.addWidget(next_btn)

        layout.addLayout(nav_layout)

        # 分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"background-color: {APPLE_COLORS['separator']}; max-width: 1px;")
        layout.addWidget(sep)

        # 搜索选项
        options_layout = QHBoxLayout()
        options_layout.setSpacing(16)

        self.regex_check = QCheckBox("Regex")
        self.regex_check.setToolTip("Use regular expression")
        self.regex_check.stateChanged.connect(self._emit_search)
        options_layout.addWidget(self.regex_check)

        self.case_check = QCheckBox("Case")
        self.case_check.setToolTip("Match case")
        self.case_check.setChecked(False)
        self.case_check.stateChanged.connect(self._emit_search)
        options_layout.addWidget(self.case_check)

        self.whole_word_check = QCheckBox("Word")
        self.whole_word_check.setToolTip("Whole word")
        options_layout.addWidget(self.whole_word_check)

        layout.addLayout(options_layout)
        layout.addStretch()

        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(28, 28)
        close_btn.setToolTip("Close (Esc)")
        close_btn.clicked.connect(self.close_panel)
        layout.addWidget(close_btn)

        self.setLayout(layout)
        self.setFixedHeight(56)
        self.hide()

        # 匹配结果列表（可选显示）
        self.results_list = None

    def _emit_search(self):
        """触发搜索信号"""
        self.search_requested.emit(
            self.search_input.text(),
            self.regex_check.isChecked(),
            self.case_check.isChecked()
        )

    def show_panel(self):
        """显示面板并聚焦"""
        self.show()
        self.search_input.setFocus()
        self.search_input.selectAll()

    def close_panel(self):
        """关闭面板"""
        self.hide()
        self.closed.emit()

    def update_match_count(self, current: int, total: int):
        """更新匹配计数"""
        if total > 0:
            self.match_label.setText(f"{current} / {total}")
        else:
            self.match_label.setText("无匹配")


# ========== 专业主窗口 ==========
class MainWindow(QMainWindow):
    """LogConsole 主窗口 - 专业美化版"""

    def __init__(self):
        super().__init__()
        self.parser = LogParser()
        self.search_engine = SearchEngine()
        self.template_manager = TemplateManager()
        self.keyword_highlight_manager = KeywordHighlightManager()
        self.lines = []
        self.grep_tabs = {}  # 存储 Grep 标签页 {tab_index: filters}
        self.active_search_context = None  # 当前搜索上下文
        self.is_large_file = False  # 是否为大文件模式
        self.virtual_viewer = None  # 虚拟滚动查看器（大文件用）
        self.search_dialog = None  # 高级搜索弹窗
        self.search_results = []  # 多次搜索历史 [{search_id, query, ...}]
        self.highlight_panel = None  # 高亮管理面板

        # 监听关键词变化
        self.keyword_highlight_manager.on_change(self._on_keyword_highlight_changed)

        self.init_ui()
        self.apply_professional_theme()
        self.setup_shortcuts()

    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("LogConsole - 专业日志分析工具")
        self.setGeometry(100, 100, 1600, 1000)
        self.setMinimumSize(1000, 600)

        # 中心 widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        # 工具栏
        toolbar = self.create_modern_toolbar()
        main_layout.addWidget(toolbar)

        # 浮动搜索面板
        self.search_panel = ModernSearchPanel()
        self.search_panel.search_requested.connect(self.perform_search)
        self.search_panel.next_match.connect(self.next_match)
        self.search_panel.prev_match.connect(self.prev_match)
        self.search_panel.closed.connect(self.clear_search)
        main_layout.addWidget(self.search_panel)

        # 垂直分割器：日志查看器 + 匹配结果列表（下侧）
        self.main_splitter = QSplitter(Qt.Vertical)
        splitter = self.main_splitter

        # ========== 标签页系统 ==========
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setElideMode(Qt.ElideRight)
        self.tab_widget.tabCloseRequested.connect(self.close_grep_tab)
        self.tab_widget.setStyleSheet(get_tab_widget_style())

        # 设置标签页不扩展，靠左对齐
        tab_bar = self.tab_widget.tabBar()
        tab_bar.setExpanding(False)
        tab_bar.setDrawBase(False)

        # 主日志查看器
        self.main_log_viewer = QTextEdit()
        self.main_log_viewer.setReadOnly(True)
        self.main_log_viewer.setFont(QFont("Menlo", 11))
        self.main_log_viewer.setLineWrapMode(QTextEdit.NoWrap)
        self.main_log_viewer.setTabStopDistance(40)
        self.main_log_viewer.setContextMenuPolicy(Qt.CustomContextMenu)
        self.main_log_viewer.customContextMenuRequested.connect(self.show_context_menu)
        self.main_log_viewer.viewport().installEventFilter(self)  # 监听鼠标释放
        self._selection_highlight_word = None  # 当前选中高亮的词
        self._is_selecting = False  # 是否正在拖动选择

        # 监听滚动事件，更新关键词高亮
        self.main_log_viewer.verticalScrollBar().valueChanged.connect(self._on_scroll_update_highlights)

        # 设置语法高亮（使用当前模板）
        current_template = self.template_manager.get_current_template()
        self.main_highlighter = ModernLogHighlighter(self.main_log_viewer.document(), current_template)

        # 添加主标签页（标题初始为"Untitled"）
        self.main_tab_index = self.tab_widget.addTab(self.main_log_viewer, "Untitled")

        # 保持向后兼容
        self.log_viewer = self.main_log_viewer
        self.highlighter = self.main_highlighter

        splitter.addWidget(self.tab_widget)

        # 匹配结果树（初始隐藏）- 支持按行分组
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["搜索结果"])
        self.results_tree.setHeaderHidden(True)
        self.results_tree.setStyleSheet(get_tree_widget_style())
        self.results_tree.itemDoubleClicked.connect(self.on_result_double_clicked)
        self.results_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_tree.customContextMenuRequested.connect(self.show_results_context_menu)
        self.results_tree.setItemDelegate(HighlightDelegate(self.results_tree))
        self.results_tree.hide()
        splitter.addWidget(self.results_tree)

        # 设置树控件信号
        self._setup_tree_signals()

        # 兼容性别名
        self.results_list = self.results_tree

        splitter.setStretchFactor(0, 3)  # 日志区占 75%（上方）
        splitter.setStretchFactor(1, 1)  # 结果列表占 25%（下方）

        main_layout.addWidget(splitter)

        # 状态栏
        self.create_status_bar()

    def create_modern_toolbar(self) -> QToolBar:
        """创建现代化工具栏 - 极简高端风格"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet(get_toolbar_style())

        # 打开文件按钮 - 纯文字
        open_btn = QPushButton("Open")
        open_btn.setToolTip("打开文件 (Ctrl+O)")
        open_btn.clicked.connect(self.open_file)
        toolbar.addWidget(open_btn)

        toolbar.addSeparator()

        # 导出按钮 - 纯文字
        export_btn = QPushButton("Export")
        export_btn.setToolTip("导出日志 (Ctrl+E)")
        export_btn.clicked.connect(self.export_log)
        toolbar.addWidget(export_btn)

        # 模板选择器 - 无标签，直接下拉
        self.template_selector = QComboBox()
        self.template_selector.setMinimumWidth(120)
        self.template_selector.setStyleSheet(get_combobox_style())
        self.populate_template_selector()
        self.template_selector.currentTextChanged.connect(self.on_template_changed)
        toolbar.addWidget(self.template_selector)

        # 查找按钮
        find_btn = QPushButton("⌕")
        find_btn.setToolTip("Find (⌘F)")
        find_btn.clicked.connect(self.show_search_panel)
        toolbar.addWidget(find_btn)

        # 跳转按钮
        jump_btn = QPushButton("⌗")
        jump_btn.setToolTip("Go to Line (⌘G)")
        jump_btn.clicked.connect(self.jump_to_line)
        toolbar.addWidget(jump_btn)

        # 自动换行切换
        self.wrap_btn = QPushButton("⏎")
        self.wrap_btn.setToolTip("Wrap Lines")
        self.wrap_btn.setCheckable(True)
        self.wrap_btn.setChecked(False)
        self.wrap_btn.clicked.connect(self.toggle_word_wrap)
        toolbar.addWidget(self.wrap_btn)

        # 高亮管理按钮
        highlight_btn = QPushButton("◆")
        highlight_btn.setToolTip("Keyword Highlights (Ctrl+H)")
        highlight_btn.clicked.connect(self.show_highlight_panel)
        toolbar.addWidget(highlight_btn)

        # 添加弹性空间
        spacer = QWidget()
        spacer.setSizePolicy(QWidget().sizePolicy().Expanding, QWidget().sizePolicy().Preferred)
        toolbar.addWidget(spacer)

        return toolbar

    def create_status_bar(self):
        """创建专业状态栏 - 极简设计"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.file_label = QLabel("No file")
        self.size_label = QLabel("")
        self.line_label = QLabel("")
        self.encoding_label = QLabel("")
        self.cursor_label = QLabel("Ln 1, Col 1")

        # 添加状态栏组件 - 无分隔符，靠内边距区分
        self.status_bar.addWidget(self.file_label)
        self.status_bar.addWidget(self.size_label)
        self.status_bar.addWidget(self.line_label)
        self.status_bar.addWidget(self.encoding_label)
        self.status_bar.addPermanentWidget(self.cursor_label)

    def setup_shortcuts(self):
        """设置快捷键"""
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.show_search_panel)
        QShortcut(QKeySequence("Esc"), self).activated.connect(self.hide_search_panel)
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.open_file)
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self.export_log)
        QShortcut(QKeySequence("Ctrl+G"), self).activated.connect(self.jump_to_line)
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(self.show_highlight_panel)

    def apply_professional_theme(self):
        """应用专业主题 - Apple HIG 风格"""
        self.setStyleSheet(get_main_window_style())

    def show_search_panel(self):
        """显示搜索面板 - 改用独立弹窗"""
        self._ensure_search_dialog()
        # 如果有选中文本，自动填充到搜索框
        ctx = self.get_active_viewer_context()
        if ctx:
            cursor = ctx["viewer"].textCursor()
            selected_text = cursor.selectedText().strip()
            if selected_text:
                self.search_dialog.set_search_text(selected_text)
        self.search_dialog.show_dialog()

    def _ensure_search_dialog(self):
        """确保搜索弹窗已创建"""
        if self.search_dialog is None:
            self.search_dialog = SearchDialog(self)
            # 连接信号
            self.search_dialog.find_next.connect(self._on_dialog_find_next)
            self.search_dialog.find_prev.connect(self._on_dialog_find_prev)
            self.search_dialog.find_count.connect(self._on_dialog_count)
            self.search_dialog.find_in_current.connect(self._on_dialog_find_in_current)
            self.search_dialog.find_in_all.connect(self._on_dialog_find_in_all)
            self.search_dialog.clear_results.connect(self._on_dialog_clear_results)

    def _on_dialog_find_next(self, pattern: str, is_regex: bool, case_sensitive: bool):
        """弹窗：查找下一个（仅跳转，不保存结果）"""
        print(f"[find_next] ENTER: pattern='{pattern}', regex={is_regex}, case={case_sensitive}")
        ctx = self.get_active_viewer_context()
        if not ctx or not pattern:
            print(f"[find_next] EXIT: ctx={ctx is not None}, pattern='{pattern}'")
            return

        # 检查是否需要重新搜索（pattern 或搜索参数变化）
        need_search = (
            not self.search_engine.matches or
            getattr(self, '_last_search_pattern', None) != pattern or
            getattr(self, '_last_search_ctx_id', None) != id(ctx["lines"])
        )
        print(f"[find_next] need_search={need_search}, matches={len(self.search_engine.matches)}, last_pattern={getattr(self, '_last_search_pattern', None)}")

        if need_search:
            mode = SearchMode.REGEX if is_regex else SearchMode.PLAIN
            self.search_engine.search(ctx["lines"], pattern, mode, case_sensitive)
            self._last_search_pattern = pattern
            self._last_search_ctx_id = id(ctx["lines"])
            self.active_search_context = ctx
            print(f"[find_next] search done: {len(self.search_engine.matches)} matches")
            # 仅设置高亮 pattern，不执行 rehighlight（避免 UI 卡死）
            if ctx["highlighter"]:
                ctx["highlighter"].set_search_pattern(pattern, is_regex, case_sensitive)

        matches = self.search_engine.matches
        if matches:
            prev_idx = self.search_engine.current_match_index
            match = self.search_engine.next_match()
            print(f"[find_next] next_match: prev_idx={prev_idx}, new_idx={self.search_engine.current_match_index}, match={match}")
            if match:
                self.scroll_to_match(match[0], match[1], match[2], select=True)
                idx = self.search_engine.current_match_index + 1
                self.search_dialog.update_status(f"第 {idx}/{len(matches)} 个匹配")
        else:
            print(f"[find_next] no matches found")
            self.search_dialog.update_status("未找到匹配项")

    def _on_dialog_find_prev(self, pattern: str, is_regex: bool, case_sensitive: bool):
        """弹窗：查找上一个（仅跳转，不保存结果）"""
        print(f"[find_prev] ENTER: pattern='{pattern}', regex={is_regex}, case={case_sensitive}")
        ctx = self.get_active_viewer_context()
        if not ctx or not pattern:
            print(f"[find_prev] EXIT: ctx={ctx is not None}, pattern='{pattern}'")
            return

        # 检查是否需要重新搜索（pattern 或搜索参数变化）
        need_search = (
            not self.search_engine.matches or
            getattr(self, '_last_search_pattern', None) != pattern or
            getattr(self, '_last_search_ctx_id', None) != id(ctx["lines"])
        )
        print(f"[find_prev] need_search={need_search}, matches={len(self.search_engine.matches)}, last_pattern={getattr(self, '_last_search_pattern', None)}")

        if need_search:
            mode = SearchMode.REGEX if is_regex else SearchMode.PLAIN
            self.search_engine.search(ctx["lines"], pattern, mode, case_sensitive)
            self._last_search_pattern = pattern
            self._last_search_ctx_id = id(ctx["lines"])
            self.active_search_context = ctx
            print(f"[find_prev] search done: {len(self.search_engine.matches)} matches")
            # 仅设置高亮 pattern，不执行 rehighlight（避免 UI 卡死）
            if ctx["highlighter"]:
                ctx["highlighter"].set_search_pattern(pattern, is_regex, case_sensitive)

        matches = self.search_engine.matches
        if matches:
            prev_idx = self.search_engine.current_match_index
            match = self.search_engine.prev_match()
            print(f"[find_prev] prev_match: prev_idx={prev_idx}, new_idx={self.search_engine.current_match_index}, match={match}")
            if match:
                self.scroll_to_match(match[0], match[1], match[2], select=True)
                idx = self.search_engine.current_match_index + 1
                self.search_dialog.update_status(f"第 {idx}/{len(matches)} 个匹配")
        else:
            print(f"[find_prev] no matches found")
            self.search_dialog.update_status("未找到匹配项")

    def _on_dialog_count(self, pattern: str, is_regex: bool, case_sensitive: bool):
        """弹窗：计数（仅统计，不保存结果）"""
        ctx = self.get_active_viewer_context()
        if not ctx or not pattern:
            return

        mode = SearchMode.REGEX if is_regex else SearchMode.PLAIN
        matches = self.search_engine.search(ctx["lines"], pattern, mode, case_sensitive)
        self.search_dialog.update_status(f"共 {len(matches)} 个匹配")

    def _on_dialog_find_in_current(self, pattern: str, is_regex: bool, case_sensitive: bool):
        """弹窗：在当前文件中查找（保存结果到面板）"""
        self._do_find_and_save(pattern, is_regex, case_sensitive, all_files=False)

    def _on_dialog_find_in_all(self, pattern: str, is_regex: bool, case_sensitive: bool):
        """弹窗：在所有打开文件中查找（保存结果到面板）"""
        self._do_find_and_save(pattern, is_regex, case_sensitive, all_files=True)

    def _do_find_and_save(self, pattern: str, is_regex: bool, case_sensitive: bool, all_files: bool):
        """执行搜索并保存结果到三级树形结构"""
        import uuid
        import os
        from datetime import datetime

        if not pattern:
            return

        # 收集要搜索的文件
        files_to_search = []

        if all_files:
            # 主文件
            if self.lines:
                filename = os.path.basename(self.parser.file_path) if self.parser.file_path else "主文件"
                files_to_search.append({
                    "tab_index": self.main_tab_index,
                    "filename": filename,
                    "lines": self.lines,
                    "highlighter": self.highlighter
                })
            # Grep 标签页
            for tab_idx, tab_info in self.grep_tabs.items():
                tab_name = self.tab_widget.tabText(tab_idx)
                grep_text = tab_info["viewer"].toPlainText()
                grep_lines = []
                for line in grep_text.split("\n"):
                    if " │ " in line:
                        grep_lines.append(line.split(" │ ", 1)[1])
                    else:
                        grep_lines.append(line)
                files_to_search.append({
                    "tab_index": tab_idx,
                    "filename": tab_name,
                    "lines": grep_lines,
                    "highlighter": tab_info.get("highlighter")
                })
        else:
            # 仅当前文件
            ctx = self.get_active_viewer_context()
            if not ctx:
                return
            current_tab = self.tab_widget.currentIndex()
            filename = self.tab_widget.tabText(current_tab)
            files_to_search.append({
                "tab_index": current_tab,
                "filename": filename,
                "lines": ctx["lines"],
                "highlighter": ctx["highlighter"]
            })

        # 执行搜索
        mode = SearchMode.REGEX if is_regex else SearchMode.PLAIN
        total_matches = 0
        file_results = []

        for file_info in files_to_search:
            matches = self.search_engine.search(file_info["lines"], pattern, mode, case_sensitive)
            if matches:
                total_matches += len(matches)
                file_results.append({
                    "tab_index": file_info["tab_index"],
                    "filename": file_info["filename"],
                    "lines": file_info["lines"],
                    "matches": matches,
                    "highlighter": file_info["highlighter"]
                })
                # 仅设置高亮 pattern，不调用 rehighlight（避免 UI 卡死）
                if file_info["highlighter"]:
                    file_info["highlighter"].set_search_pattern(pattern, is_regex, case_sensitive)

        if total_matches == 0:
            self.search_dialog.update_status("未找到匹配项")
            return

        # 创建搜索结果记录
        search_id = str(uuid.uuid4())[:8]
        search_result = {
            "search_id": search_id,
            "query": pattern,
            "is_regex": is_regex,
            "case_sensitive": case_sensitive,
            "timestamp": datetime.now(),
            "file_results": file_results,
            "total_matches": total_matches
        }

        # 检查是否已有相同搜索词，有则更新
        existing_idx = next((i for i, r in enumerate(self.search_results) if r["query"] == pattern), None)
        if existing_idx is not None:
            self.search_results[existing_idx] = search_result
        else:
            # 限制历史数量（10条）
            if len(self.search_results) >= 10:
                self.search_results.pop(0)
            self.search_results.append(search_result)

        # 更新结果树
        self._rebuild_results_tree()

        # 更新状态
        self.search_dialog.update_status(f"共 {total_matches} 个匹配，{len(file_results)} 个文件")

        # 跳转到第一个匹配
        if file_results and file_results[0]["matches"]:
            first_match = file_results[0]["matches"][0]
            self.scroll_to_match(first_match[0], first_match[1], first_match[2])

    def _rebuild_results_tree(self):
        """重建结果树 - 极简风格，支持折叠"""
        self.results_tree.clear()

        if not self.search_results:
            self.results_tree.hide()
            return

        self.results_tree.show()

        for search_result in self.search_results:
            query = search_result["query"]
            file_results = search_result["file_results"]
            total_matches = search_result["total_matches"]
            search_id = search_result["search_id"]

            # L1: 搜索词节点 - 带折叠箭头
            l1_text = f"▼ \"{query}\" · {total_matches}"
            l1_item = QTreeWidgetItem([l1_text])
            l1_item.setData(0, Qt.UserRole, {"type": "search", "search_id": search_id})
            l1_item.setForeground(0, QColor(APPLE_COLORS['text_primary']))
            self.results_tree.addTopLevelItem(l1_item)

            for file_result in file_results:
                filename = file_result["filename"]
                matches = file_result["matches"]
                tab_index = file_result["tab_index"]
                lines = file_result["lines"]

                # L2: 文件节点
                l2_text = f"▼ {filename} · {len(matches)}"
                l2_item = QTreeWidgetItem([l2_text])
                l2_item.setData(0, Qt.UserRole, {
                    "type": "file",
                    "search_id": search_id,
                    "tab_index": tab_index
                })
                l2_item.setForeground(0, QColor(APPLE_COLORS['text_primary']))
                l1_item.addChild(l2_item)

                # L3: 平铺显示所有匹配（不分组）
                for match_idx, (line_num, start_pos, end_pos) in enumerate(matches[:500]):
                    line_text = lines[line_num] if line_num < len(lines) else ""
                    context = self._get_match_context(line_text, start_pos, end_pos)
                    l3_text = f"{line_num + 1}: {context}"
                    l3_item = QTreeWidgetItem([l3_text])
                    l3_item.setData(0, Qt.UserRole, {
                        "type": "match",
                        "search_id": search_id,
                        "tab_index": tab_index,
                        "line_num": line_num,
                        "start_pos": start_pos,
                        "end_pos": end_pos
                    })
                    # 高亮匹配词
                    self._highlight_match_in_item(l3_item, query)
                    l2_item.addChild(l3_item)

                l2_item.setExpanded(True)

            l1_item.setExpanded(True)

        # 动态调整 splitter 大小 - 根据内容自适应
        self._adjust_results_tree_height()

    def _setup_tree_signals(self):
        """设置树控件信号（仅连接一次）"""
        if not hasattr(self, '_tree_signals_connected'):
            self.results_tree.itemExpanded.connect(self._on_tree_item_expanded)
            self.results_tree.itemCollapsed.connect(self._on_tree_item_collapsed)
            self._tree_signals_connected = True

    def _on_tree_item_expanded(self, item: QTreeWidgetItem):
        """树节点展开时更新箭头"""
        text = item.text(0)
        if text.startswith("▶"):
            item.setText(0, "▼" + text[1:])

    def _on_tree_item_collapsed(self, item: QTreeWidgetItem):
        """树节点折叠时更新箭头"""
        text = item.text(0)
        if text.startswith("▼"):
            item.setText(0, "▶" + text[1:])

    def _highlight_match_in_item(self, item: QTreeWidgetItem, query: str):
        """在树节点中高亮匹配词（使用 HTML 富文本，仅高亮匹配部分）"""
        import re
        import html

        text = item.text(0)
        if not query or not text:
            return

        # 转义 HTML 特殊字符，但保留原始文本用于搜索
        # 先找到匹配位置，再构建 HTML
        try:
            pattern = re.compile(re.escape(query), re.IGNORECASE)
            match = pattern.search(text)
            if match:
                start, end = match.start(), match.end()
                # 分割文本：前缀 + 匹配词 + 后缀
                prefix = html.escape(text[:start])
                matched = html.escape(text[start:end])
                suffix = html.escape(text[end:])
                # 构建 HTML，设置整体文字颜色，高亮匹配部分
                text_color = APPLE_COLORS['text_primary']  # 浅色文字
                highlight_color = APPLE_COLORS['accent']    # 橙色高亮
                html_text = f'<span style="color:{text_color};">{prefix}<span style="color:{highlight_color};font-weight:bold;">{matched}</span>{suffix}</span>'
                item.setText(0, html_text)
        except re.error:
            pass

    def _adjust_results_tree_height(self):
        """根据内容自动调整结果树高度"""
        if not self.results_tree.isVisible():
            return

        # 计算内容所需高度
        item_height = 26  # 每项高度
        total_items = 0

        for i in range(self.results_tree.topLevelItemCount()):
            item = self.results_tree.topLevelItem(i)
            total_items += 1
            if item.isExpanded():
                total_items += item.childCount()
                # 递归计算展开的子项
                for j in range(item.childCount()):
                    child = item.child(j)
                    if child.isExpanded():
                        total_items += child.childCount()

        # 计算理想高度（加上 padding）
        content_height = total_items * item_height + 24
        min_height = 80
        max_height = 300

        ideal_height = max(min_height, min(content_height, max_height))

        # 获取窗口总高度
        total_height = self.main_splitter.height()

        # 设置 splitter 大小
        self.main_splitter.setSizes([total_height - ideal_height, ideal_height])

    def _on_dialog_clear_results(self):
        """弹窗：清空所有搜索结果"""
        self.search_results.clear()
        self.results_tree.clear()
        self.results_tree.hide()
        self.clear_search()

    def hide_search_panel(self):
        """隐藏搜索面板"""
        self.search_panel.close_panel()

    def populate_template_selector(self):
        """填充模板选择器 - 极简风格"""
        self.template_selector.clear()

        # 内置模板（无标题分隔）
        for template in self.template_manager.get_builtin_templates():
            self.template_selector.addItem(template.name, template.id)

        # 用户模板
        user_templates = self.template_manager.get_user_templates()
        if user_templates:
            # 仅用细线分隔，不用丑陋的 ═══
            self.template_selector.insertSeparator(self.template_selector.count())
            for template in user_templates:
                self.template_selector.addItem(template.name, template.id)

        # 选中当前模板
        current_id = self.template_manager.current_template_id
        for i in range(self.template_selector.count()):
            if self.template_selector.itemData(i) == current_id:
                self.template_selector.setCurrentIndex(i)
                break

    def on_template_changed(self, template_name: str):
        """模板切换事件"""
        # 获取选中的模板 ID
        template_id = self.template_selector.currentData()
        if not template_id:
            return

        # 切换模板
        if self.template_manager.switch_template(template_id):
            # 更新高亮器（大文件模式无高亮器）
            if self.highlighter:
                new_template = self.template_manager.get_current_template()
                self.highlighter.apply_template(new_template)
                self.highlighter.rehighlight()

            # 显示提示
            self.file_label.setText(f"Theme: {template_name}")
            QTimer.singleShot(2000, lambda: self.restore_file_label())

    def restore_file_label(self):
        """恢复文件标签"""
        if self.lines:
            import os
            filename = os.path.basename(self.parser.file_path) if self.parser.file_path else "Unknown"
            self.file_label.setText(filename)
        else:
            self.file_label.setText("No file")

    def get_active_viewer_context(self):
        """获取当前活动标签页的视图上下文"""
        current_index = self.tab_widget.currentIndex()

        # 如果是主标签页 (index 0)
        if current_index == 0:
            # 根据文件大小选择正确的 viewer
            if self.is_large_file and self.virtual_viewer:
                viewer = self.virtual_viewer
            else:
                viewer = self.main_log_viewer
            return {
                "viewer": viewer,
                "highlighter": self.highlighter,
                "lines": self.lines,
                "is_grep": False,
                "is_virtual": self.is_large_file
            }

        # 如果是 Grep 标签页
        if current_index in self.grep_tabs:
            tab_info = self.grep_tabs[current_index]
            # 从 grep viewer 中提取行（去掉行号前缀）
            grep_text = tab_info["viewer"].toPlainText()
            grep_lines = []
            for line in grep_text.split("\n"):
                # 格式: "   123 │ 实际内容"
                if " │ " in line:
                    grep_lines.append(line.split(" │ ", 1)[1])
                else:
                    grep_lines.append(line)
            return {
                "viewer": tab_info["viewer"],
                "highlighter": tab_info["highlighter"],
                "lines": grep_lines,
                "is_grep": True,
                "is_virtual": False
            }

        return None

    def show_context_menu(self, pos):
        """显示右键菜单"""
        # 获取当前活动的 viewer
        ctx = self.get_active_viewer_context()
        if not ctx:
            return
        viewer = ctx["viewer"]

        # 优先使用用户实际选中的文本
        cursor = viewer.textCursor()
        selected_text = cursor.selectedText().strip()

        # 如果没有选中文本，才使用光标下的单词
        if not selected_text:
            cursor = viewer.cursorForPosition(pos)
            cursor.select(QTextCursor.WordUnderCursor)
            selected_text = cursor.selectedText().strip()

        if not selected_text:
            return

        # 创建菜单 - Apple HIG 风格
        menu = QMenu(self)
        menu.setStyleSheet(get_context_menu_style())

        # ========== 高亮相关 ==========
        # 检查是否已高亮
        existing_kw = self.keyword_highlight_manager.find_keyword(selected_text)

        if existing_kw:
            # 已高亮：显示移除选项
            remove_hl_action = QAction(f"Remove Highlight: \"{selected_text}\"", self)
            remove_hl_action.triggered.connect(
                lambda checked, k=selected_text: self._remove_keyword_highlight(k)
            )
            menu.addAction(remove_hl_action)
        else:
            # 未高亮：显示高亮子菜单（带颜色选择）
            highlight_menu = QMenu(f"Highlight: \"{selected_text}\"", self)
            highlight_menu.setStyleSheet(get_context_menu_style())

            for color in PRESET_COLORS:
                color_action = QAction(f"● {color['name']}", self)
                color_action.setIcon(self._create_color_icon(color['fg']))
                color_action.triggered.connect(
                    lambda checked, k=selected_text, c=color: self._add_keyword_highlight(k, c)
                )
                highlight_menu.addAction(color_action)

            menu.addMenu(highlight_menu)

        menu.addSeparator()

        # ========== Grep 相关 ==========
        grep_action = QAction(f"Grep: \"{selected_text}\"", self)
        grep_action.triggered.connect(lambda checked, k=selected_text: self.grep_to_new_tab(k))
        menu.addAction(grep_action)

        # Add Grep 动作（只有当存在 Grep 标签页时才显示）
        if len(self.grep_tabs) > 0:
            add_grep_action = QAction(f"Add Grep: \"{selected_text}\"", self)
            add_grep_action.triggered.connect(lambda checked, k=selected_text: self.show_add_grep_dialog(k))
            menu.addAction(add_grep_action)

        menu.exec_(self.main_log_viewer.mapToGlobal(pos))

    def _create_color_icon(self, color: str):
        """创建颜色图标"""
        from PyQt5.QtGui import QPixmap, QPainter
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(color))
        return QIcon(pixmap)

    def _add_keyword_highlight(self, keyword: str, color: dict):
        """添加关键词高亮"""
        self.keyword_highlight_manager.add_keyword(
            keyword,
            fg_color=color['fg'],
            bg_color=color['bg']
        )

    def _remove_keyword_highlight(self, keyword: str):
        """移除关键词高亮"""
        self.keyword_highlight_manager.remove_keyword(keyword)

    def _on_keyword_highlight_changed(self):
        """关键词高亮变化回调 - 使用 ExtraSelections 实现，不调用 rehighlight"""
        keywords = self.keyword_highlight_manager.get_enabled_keywords()

        # 更新高亮器规则（用于新加载的文件）
        if self.highlighter:
            self.highlighter.set_user_keywords(keywords, mark_dirty=False)

        # 使用 ExtraSelections 实现高亮（不卡顿）
        self._apply_keyword_extra_selections(self.main_log_viewer, keywords)

        # 更新所有 Grep 标签页
        for tab_info in self.grep_tabs.values():
            hl = tab_info.get("highlighter")
            viewer = tab_info.get("viewer")
            if hl:
                hl.set_user_keywords(keywords, mark_dirty=False)
            if viewer:
                self._apply_keyword_extra_selections(viewer, keywords)

    def _apply_keyword_extra_selections(self, viewer, keywords):
        """使用 ExtraSelections 应用关键词高亮 - 仅可见区域"""
        if not viewer or not keywords:
            viewer.setExtraSelections([]) if viewer else None
            return

        import re
        selections = []
        doc = viewer.document()

        # 只处理可见区域的文本块
        cursor_top = viewer.cursorForPosition(viewer.viewport().rect().topLeft())
        cursor_bottom = viewer.cursorForPosition(viewer.viewport().rect().bottomRight())
        start_block = cursor_top.block()
        end_block = cursor_bottom.block()

        # 预编译所有关键词模式
        kw_patterns = []
        for kw in keywords:
            if not kw.enabled:
                continue
            try:
                pattern = re.compile(re.escape(kw.keyword), re.IGNORECASE)
                kw_patterns.append((pattern, kw.fg_color, kw.bg_color, kw.bold))
            except re.error:
                pass

        if not kw_patterns:
            viewer.setExtraSelections([])
            return

        # 遍历可见的 block
        block = start_block
        while block.isValid():
            text = block.text()
            block_pos = block.position()

            for pattern, fg, bg, bold in kw_patterns:
                for match in pattern.finditer(text):
                    selection = QTextEdit.ExtraSelection()
                    cursor = QTextCursor(doc)
                    cursor.setPosition(block_pos + match.start())
                    cursor.setPosition(block_pos + match.end(), QTextCursor.KeepAnchor)

                    fmt = QTextCharFormat()
                    fmt.setForeground(QColor(fg))
                    if bg:
                        fmt.setBackground(QColor(bg))
                    if bold:
                        fmt.setFontWeight(QFont.Bold)

                    selection.cursor = cursor
                    selection.format = fmt
                    selections.append(selection)

            if block == end_block:
                break
            block = block.next()

        viewer.setExtraSelections(selections)

    def _on_scroll_update_highlights(self):
        """滚动时更新可见区域的高亮"""
        keywords = self.keyword_highlight_manager.get_enabled_keywords()
        if keywords:
            self._apply_keyword_extra_selections(self.main_log_viewer, keywords)

    def show_highlight_panel(self):
        """显示高亮管理面板"""
        if self.highlight_panel is None:
            self.highlight_panel = HighlightManagePanel(self, self.keyword_highlight_manager)
            self.highlight_panel.highlight_changed.connect(self._on_keyword_highlight_changed)
        self.highlight_panel.refresh_list()
        self.highlight_panel.show()
        self.highlight_panel.raise_()

    def grep_to_new_tab(self, keyword: str):
        """Grep 到新标签页"""
        if not self.lines or not keyword:
            return

        # 过滤日志行
        filtered_lines = [
            f"{i+1:6d} │ {line}"
            for i, line in enumerate(self.lines)
            if keyword in line
        ]

        if not filtered_lines:
            QMessageBox.information(self, "Grep 结果", f"未找到包含 '{keyword}' 的日志")
            return

        # 创建容器 widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 创建条件栏 - Apple HIG 风格
        filter_bar = QFrame()
        filter_bar.setStyleSheet(get_grep_filter_bar_style())
        filter_layout = QHBoxLayout(filter_bar)
        filter_layout.setContentsMargins(8, 4, 8, 4)
        filter_layout.setSpacing(8)

        # 匹配数量标签 - Apple HIG 风格
        count_label = QLabel(f"{len(filtered_lines)}/{len(self.lines)}")
        count_label.setStyleSheet(get_count_label_style())
        filter_layout.addWidget(count_label)

        # 过滤条件标签 - Apple HIG 风格
        filter_tag = QLabel(keyword)
        filter_tag.setStyleSheet(get_grep_tag_style(is_primary=True))
        filter_layout.addWidget(filter_tag)

        filter_layout.addStretch()
        container_layout.addWidget(filter_bar)

        # 创建 QPlainTextEdit - Apple HIG 风格
        grep_viewer = QPlainTextEdit()
        grep_viewer.setReadOnly(True)
        grep_viewer.setFont(QFont(APPLE_MONO_FONT.split(',')[0].strip("'"), 12))
        grep_viewer.setLineWrapMode(QPlainTextEdit.NoWrap)
        grep_viewer.setTabStopDistance(40)
        # 主样式已在 get_main_window_style() 中定义

        # 大量结果时禁用高亮（>5000行）
        grep_highlighter = None
        if len(filtered_lines) <= 5000:
            current_template = self.template_manager.get_current_template()
            grep_highlighter = ModernLogHighlighter(grep_viewer.document(), current_template)

        # 显示过滤后的内容
        grep_viewer.setPlainText("\n".join(filtered_lines))

        container_layout.addWidget(grep_viewer)

        # 添加标签页
        tab_index = self.tab_widget.addTab(container, keyword)
        self.tab_widget.setCurrentIndex(tab_index)

        # 记录过滤关键词
        self.grep_tabs[tab_index] = {
            "filters": [keyword],
            "viewer": grep_viewer,
            "highlighter": grep_highlighter,
            "container": container,
            "filter_bar": filter_bar,
            "count_label": count_label
        }

        # 显示提示
        self.file_label.setText(f"Grep: {len(filtered_lines)} matches")
        QTimer.singleShot(2000, self.restore_file_label)

    def show_add_grep_dialog(self, keyword: str):
        """显示 Add Grep 选择对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle("选择目标 Console")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet(get_add_grep_dialog_style())

        layout = QVBoxLayout()

        # 添加选项
        radio_buttons = []

        # 当前标签页选项（只在 Grep 标签页时显示）
        current_index = self.tab_widget.currentIndex()
        if current_index != self.main_tab_index and current_index in self.grep_tabs:
            current_tab_name = self.tab_widget.tabText(current_index)
            rb = QRadioButton(f"1 [This Console] {current_tab_name}")
            rb.setChecked(True)
            rb.setProperty("tab_index", current_index)
            rb.setProperty("is_new", False)
            radio_buttons.append(rb)
            layout.addWidget(rb)
            index_offset = 2
        else:
            index_offset = 1

        # 所有已有的 Grep 标签页
        for tab_idx, tab_info in self.grep_tabs.items():
            if tab_idx != current_index:
                tab_name = self.tab_widget.tabText(tab_idx)
                rb = QRadioButton(f"{index_offset} {tab_name}")
                rb.setProperty("tab_index", tab_idx)
                rb.setProperty("is_new", False)
                if not radio_buttons:  # 如果还没有选中的，选中第一个
                    rb.setChecked(True)
                radio_buttons.append(rb)
                layout.addWidget(rb)
                index_offset += 1

        # 新建标签页选项
        new_rb = QRadioButton(f"{index_offset} [New]")
        new_rb.setProperty("is_new", True)
        radio_buttons.append(new_rb)
        layout.addWidget(new_rb)

        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            # 找到选中的选项
            selected_rb = next((rb for rb in radio_buttons if rb.isChecked()), None)
            if selected_rb:
                is_new = selected_rb.property("is_new")
                if is_new:
                    # 创建新标签页
                    self.grep_to_new_tab(keyword)
                else:
                    # 添加到选中的标签页
                    tab_idx = selected_rb.property("tab_index")
                    self.add_grep_to_tab(keyword, tab_idx)

    def add_grep_to_tab(self, keyword: str, tab_index: int):
        """Add Grep 到指定标签页"""
        if tab_index not in self.grep_tabs:
            return

        # 获取标签页信息
        tab_info = self.grep_tabs[tab_index]
        existing_filters = tab_info["filters"]
        grep_viewer = tab_info["viewer"]

        # 添加新关键词
        existing_filters.append(keyword)

        # 重新过滤日志（OR 逻辑）
        filtered_lines = []
        for i, line in enumerate(self.lines):
            if any(f in line for f in existing_filters):
                filtered_lines.append(f"{i+1:6d} │ {line}")

        # 更新标签页内容
        grep_viewer.setPlainText("\n".join(filtered_lines))

        # 更新条件栏 - 添加新标签
        if "filter_bar" in tab_info:
            filter_layout = tab_info["filter_bar"].layout()
            # 在 stretch 之前插入新标签
            new_tag = QLabel(f"+ {keyword}")
            new_tag.setStyleSheet(get_grep_tag_style(is_primary=False))
            # 插入到 count_label 后面，stretch 前面
            filter_layout.insertWidget(filter_layout.count() - 1, new_tag)

            # 更新计数
            if "count_label" in tab_info:
                tab_info["count_label"].setText(f"{len(filtered_lines)}/{len(self.lines)}")

        # 更新标签页标题
        title = ' + '.join(existing_filters)
        if len(title) > 40:
            title = f"{len(existing_filters)} filters"
        self.tab_widget.setTabText(tab_index, title)

        # 切换到该标签页
        self.tab_widget.setCurrentIndex(tab_index)

        # 显示提示
        self.file_label.setText(f"Added: {len(filtered_lines)} matches")
        QTimer.singleShot(2000, self.restore_file_label)

    def add_grep_to_current_tab(self, keyword: str):
        """Add Grep 到当前标签页（已废弃，保留兼容性）"""
        self.show_add_grep_dialog(keyword)

    def close_grep_tab(self, index: int):
        """关闭 Grep 标签页"""
        # 不允许关闭主文件标签页（索引 0）
        if index == self.main_tab_index:
            return

        # 移除标签页
        self.tab_widget.removeTab(index)

        # 移除记录
        if index in self.grep_tabs:
            del self.grep_tabs[index]

        # 重新索引
        new_grep_tabs = {}
        for i in range(self.tab_widget.count()):
            # 跳过主标签页
            if i == self.main_tab_index:
                continue
            # 找到对应的 tab_info
            for old_idx, tab_info in self.grep_tabs.items():
                if self.tab_widget.widget(i) == tab_info["viewer"]:
                    new_grep_tabs[i] = tab_info
                    break
        self.grep_tabs = new_grep_tabs

    def open_file(self):
        """打开文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "打开日志文件",
            "",
            "日志文件 (*.log *.txt);;所有文件 (*.*)"
        )
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path: str):
        """加载文件"""
        self.file_label.setText("Loading...")
        self.log_viewer.clear()

        self.load_thread = LoadFileThread(file_path)
        self.load_thread.progress.connect(self.on_load_progress)
        self.load_thread.finished.connect(self.on_load_finished)
        self.load_thread.error.connect(self.on_load_error)
        self.load_thread.start()

    def on_load_progress(self, bytes_read: int, total_bytes: int):
        """加载进度"""
        progress = int((bytes_read / total_bytes) * 100)
        self.file_label.setText(f"Loading {progress}%")

    def on_load_finished(self, result: dict):
        """加载完成"""
        import os
        self.lines = result["lines"]
        self.parser = self.load_thread.parser
        file_size = result["file_size"]
        self.is_large_file = file_size > LARGE_FILE_THRESHOLD

        if self.is_large_file:
            # 大文件模式：使用虚拟滚动查看器
            self.switch_to_virtual_viewer()
            self.virtual_viewer.set_lines(self.lines)
        else:
            # 小文件模式：使用 QTextEdit + 语法高亮
            self.switch_to_normal_viewer()
            formatted_lines = [f"{i:6d} │ {line}" for i, line in enumerate(self.lines, 1)]
            self.main_log_viewer.setPlainText("\n".join(formatted_lines))

        # 更新主标签页标题为文件名
        filename = os.path.basename(self.parser.file_path) if self.parser.file_path else "Unknown"
        self.tab_widget.setTabText(self.main_tab_index, filename)

        # 更新状态栏
        file_size_mb = file_size / (1024 * 1024)
        self.file_label.setText(filename)
        self.size_label.setText(f" {file_size_mb:.2f} MB ")
        self.line_label.setText(f" {result['line_count']:,} 行 ")
        self.encoding_label.setText(f" {result['encoding'].upper()} ")

    def switch_to_virtual_viewer(self):
        """切换到虚拟滚动查看器（大文件模式）"""
        if self.virtual_viewer is None:
            self.virtual_viewer = VirtualLogViewer()
            self.virtual_viewer.context_menu_requested.connect(self.show_context_menu)

        # 替换主标签页内容
        current_widget = self.tab_widget.widget(self.main_tab_index)
        if current_widget != self.virtual_viewer:
            self.tab_widget.removeTab(self.main_tab_index)
            self.main_tab_index = self.tab_widget.insertTab(0, self.virtual_viewer, "Untitled")
            self.log_viewer = self.virtual_viewer
            self.highlighter = None  # 大文件模式无语法高亮

    def switch_to_normal_viewer(self):
        """切换到普通查看器（小文件模式）"""
        current_widget = self.tab_widget.widget(self.main_tab_index)
        if current_widget != self.main_log_viewer:
            self.tab_widget.removeTab(self.main_tab_index)
            self.main_tab_index = self.tab_widget.insertTab(0, self.main_log_viewer, "Untitled")
            self.log_viewer = self.main_log_viewer
            self.highlighter = self.main_highlighter

    def on_load_error(self, error: str):
        """加载错误"""
        QMessageBox.critical(self, "Error", f"Failed to load file:\n{error}")
        self.file_label.setText("Load failed")

    def perform_search(self, pattern: str, is_regex: bool, case_sensitive: bool):
        """执行搜索"""
        # 获取当前活动视图上下文
        ctx = self.get_active_viewer_context()
        if not ctx:
            return

        viewer = ctx["viewer"]
        highlighter = ctx["highlighter"]  # 大文件模式下为 None
        lines = ctx["lines"]

        if not pattern or not lines:
            if highlighter:
                highlighter.set_search_pattern(None)
                highlighter.rehighlight()
            self.search_panel.update_match_count(0, 0)
            self.results_tree.clear()
            self.results_tree.hide()
            return

        # 保存当前上下文以供后续导航使用
        self.active_search_context = ctx

        # 执行搜索（先搜索，后高亮，避免卡顿）
        mode = SearchMode.REGEX if is_regex else SearchMode.PLAIN
        matches = self.search_engine.search(lines, pattern, mode, case_sensitive)

        # 更新结果树
        self.results_tree.clear()
        current_tab_index = self.tab_widget.currentIndex()

        if matches:
            self.results_tree.show()

            # 平铺显示所有匹配（不分组）
            for match_idx, (line_num, start_pos, end_pos) in enumerate(matches[:500]):
                line_text = lines[line_num]
                context = self._get_match_context(line_text, start_pos, end_pos)
                item = QTreeWidgetItem([f"{line_num + 1}: {context}"])
                item.setData(0, Qt.UserRole, match_idx)
                item.setData(0, Qt.UserRole + 1, current_tab_index)
                item.setData(0, Qt.UserRole + 2, line_num)
                self.results_tree.addTopLevelItem(item)

            # 跳转到第一个匹配
            self.scroll_to_match(matches[0][0], matches[0][1], matches[0][2])
            self.search_panel.update_match_count(1, len(matches))

            # 选中第一项
            first_item = self.results_tree.topLevelItem(0)
            if first_item:
                self.results_tree.setCurrentItem(first_item)

            # 延迟高亮（搜索完成后再刷新，提升响应速度）
            if highlighter:
                highlighter.set_search_pattern(pattern, is_regex, case_sensitive)
                QTimer.singleShot(50, highlighter.rehighlight)
        else:
            self.results_tree.hide()
            self.search_panel.update_match_count(0, 0)

    def _get_match_context(self, line_text: str, start_pos: int, end_pos: int, context_chars: int = 30) -> str:
        """获取匹配位置的上下文片段"""
        context_start = max(0, start_pos - context_chars)
        context_end = min(len(line_text), end_pos + context_chars)
        context = line_text[context_start:context_end]
        if context_start > 0:
            context = "..." + context
        if context_end < len(line_text):
            context = context + "..."
        return context

    def clear_search(self):
        """清除搜索"""
        # 清除所有视图的搜索高亮（大文件模式无高亮器）
        if self.highlighter:
            self.highlighter.set_search_pattern(None)
            self.highlighter.rehighlight()

        # 也清除 Grep 标签页的高亮
        for tab_info in self.grep_tabs.values():
            if "highlighter" in tab_info and tab_info["highlighter"]:
                tab_info["highlighter"].set_search_pattern(None)
                tab_info["highlighter"].rehighlight()

        self.search_engine.clear()
        self.results_tree.clear()
        self.results_tree.hide()
        self.active_search_context = None

    def scroll_to_match(self, line_num: int, start_col: int = -1, end_col: int = -1, select: bool = False):
        """滚动到匹配位置 - 使用 ExtraSelections 高亮（高性能，不阻塞 UI）

        Args:
            line_num: 行号（0-based）
            start_col: 起始列（原始行中的位置）
            end_col: 结束列（原始行中的位置）
            select: 是否选中匹配文本（用于高亮当前匹配）
        """
        ctx = getattr(self, 'active_search_context', None) or self.get_active_viewer_context()
        if not ctx:
            return

        viewer = ctx["viewer"]

        if ctx.get("is_virtual") and hasattr(viewer, 'scroll_to_line'):
            viewer.scroll_to_line(line_num, highlight=True)
        else:
            doc = viewer.document()
            block = doc.findBlockByLineNumber(line_num)
            if not block.isValid():
                return

            # 行号前缀长度: "{i:6d} │ " = 9 字符
            LINE_PREFIX_LEN = 9
            actual_start = 0
            actual_end = 0

            if start_col >= 0:
                actual_start = LINE_PREFIX_LEN + start_col
                actual_end = LINE_PREFIX_LEN + end_col if end_col >= 0 else actual_start
                line_length = block.length() - 1
                actual_start = min(actual_start, line_length)
                actual_end = min(actual_end, line_length)

                target_pos = block.position() + actual_start
                cursor = QTextCursor(doc)
                cursor.setPosition(target_pos)

                if select and end_col > start_col:
                    end_pos = block.position() + actual_end
                    cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
            else:
                cursor = QTextCursor(block)

            viewer.setTextCursor(cursor)
            viewer.ensureCursorVisible()

            # 水平滚动
            cursor_rect = viewer.cursorRect(cursor)
            h_scroll = viewer.horizontalScrollBar()
            viewport_width = viewer.viewport().width()
            target_scroll = max(0, cursor_rect.x() - viewport_width // 4)
            h_scroll.setValue(target_scroll)

            # 使用 ExtraSelections 高亮当前匹配（高性能）
            self._apply_search_highlight(viewer, block, actual_start, actual_end)

        # 更新状态栏
        col_display = start_col + 1 if start_col >= 0 else 1
        self.cursor_label.setText(f" Ln {line_num + 1}, Col {col_display} ")

    def next_match(self):
        """下一个匹配"""
        print(f"[next_match] called, matches={len(self.search_engine.matches)}")
        match = self.search_engine.next_match()
        print(f"[next_match] result={match}")
        if match:
            self.scroll_to_match(match[0], match[1], match[2])
            idx = self.search_engine.current_match_index + 1
            self.search_panel.update_match_count(idx, len(self.search_engine.matches))

    def prev_match(self):
        """上一个匹配"""
        print(f"[prev_match] called, matches={len(self.search_engine.matches)}")
        match = self.search_engine.prev_match()
        print(f"[prev_match] result={match}")
        if match:
            self.scroll_to_match(match[0], match[1], match[2])
            idx = self.search_engine.current_match_index + 1
            self.search_panel.update_match_count(idx, len(self.search_engine.matches))

    def _sync_tree_selection(self, match_idx: int):
        """同步树形控件选中状态"""
        # 遍历所有项找到对应 match_idx 的项
        def find_item(parent_item=None):
            if parent_item is None:
                count = self.results_tree.topLevelItemCount()
                for i in range(count):
                    item = self.results_tree.topLevelItem(i)
                    if item.data(0, Qt.UserRole) == match_idx:
                        return item
                    # 检查子项
                    for j in range(item.childCount()):
                        child = item.child(j)
                        if child.data(0, Qt.UserRole) == match_idx:
                            return child
            return None

        target_item = find_item()
        if target_item:
            self.results_tree.setCurrentItem(target_item)
            self.results_tree.scrollToItem(target_item)

    def on_result_double_clicked(self, item: QTreeWidgetItem, column: int = 0):
        """双击结果树项跳转到对应标签页和匹配位置"""
        data = item.data(0, Qt.UserRole)

        # 新的数据格式（字典）
        if isinstance(data, dict):
            item_type = data.get("type")

            # L1 搜索词节点：不处理
            if item_type == "search":
                return

            # L2 文件节点：切换到对应标签页
            if item_type == "file":
                tab_index = data.get("tab_index")
                if tab_index is not None:
                    self.tab_widget.setCurrentIndex(tab_index)
                return

            # L3 行组节点：跳转到该行第一个匹配
            if item_type == "line_group":
                tab_index = data.get("tab_index")
                line_num = data.get("line_num")
                if tab_index is not None:
                    self.tab_widget.setCurrentIndex(tab_index)
                if line_num is not None:
                    # 延迟执行以确保标签页切换完成后再滚动居中
                    ln = line_num  # 捕获变量
                    QTimer.singleShot(0, lambda ln=ln: self.scroll_to_match(ln, -1, -1))
                return

            # L3/L4 匹配节点：精确跳转
            if item_type == "match":
                tab_index = data.get("tab_index")
                line_num = data.get("line_num")
                start_pos = data.get("start_pos", -1)
                end_pos = data.get("end_pos", -1)
                if tab_index is not None:
                    self.tab_widget.setCurrentIndex(tab_index)
                if line_num is not None:
                    # 延迟执行以确保标签页切换完成后再滚动居中
                    ln, sp, ep = line_num, start_pos, end_pos  # 捕获变量
                    QTimer.singleShot(0, lambda ln=ln, sp=sp, ep=ep: self.scroll_to_match(ln, sp, ep, select=True))
                return

        # 旧数据格式兼容（整数 match_idx）
        match_idx = data
        tab_index = item.data(0, Qt.UserRole + 1)

        # 如果是父节点（match_idx == -1），不处理（或跳到第一个子项）
        if match_idx == -1:
            if item.childCount() > 0:
                # 跳转到第一个子项的匹配位置
                first_child = item.child(0)
                match_idx = first_child.data(0, Qt.UserRole)
            else:
                return

        if match_idx is None or match_idx >= len(self.search_engine.matches):
            return

        # 切换到对应的标签页
        if tab_index is not None and tab_index != self.tab_widget.currentIndex():
            self.tab_widget.setCurrentIndex(tab_index)
            self.active_search_context = self.get_active_viewer_context()

        # 直接使用匹配索引定位
        self.search_engine.current_match_index = match_idx
        match = self.search_engine.matches[match_idx]
        self.scroll_to_match(match[0], match[1], match[2])
        self.search_panel.update_match_count(match_idx + 1, len(self.search_engine.matches))

    def on_result_clicked(self, item: QListWidgetItem):
        """单击结果列表项（保持选中，不跳转）"""
        pass  # 单击不做处理，双击才跳转

    def show_results_context_menu(self, pos):
        """显示搜索结果右键菜单"""
        item = self.results_tree.itemAt(pos)
        if not item:
            return

        data = item.data(0, Qt.UserRole)
        menu = QMenu(self)
        menu.setStyleSheet(get_context_menu_style())

        # 新的数据格式（字典）
        if isinstance(data, dict):
            item_type = data.get("type")
            search_id = data.get("search_id")

            if item_type == "search":
                # L1 搜索词节点：删除此搜索 / 复制搜索词
                delete_search_action = QAction(f"{ICONS['delete']} Delete Search", self)
                delete_search_action.triggered.connect(lambda: self._delete_search(search_id))
                menu.addAction(delete_search_action)

                copy_query_action = QAction(f"{ICONS['copy']} Copy Query", self)
                copy_query_action.triggered.connect(lambda: self._copy_query(search_id))
                menu.addAction(copy_query_action)

            elif item_type == "file":
                # L2 文件节点：从结果中移除此文件
                remove_file_action = QAction(f"{ICONS['delete']} Remove File", self)
                remove_file_action.triggered.connect(lambda: self._remove_file_from_results(item, search_id))
                menu.addAction(remove_file_action)

            elif item_type in ("match", "line_group"):
                # L3/L4 匹配节点：删除行 / 删除节 / 复制行内容
                delete_row_action = QAction(f"{ICONS['delete']} Delete Row", self)
                delete_row_action.triggered.connect(lambda: self._delete_result_item(item))
                menu.addAction(delete_row_action)

                delete_section_action = QAction(f"{ICONS['file']} Delete Section", self)
                delete_section_action.triggered.connect(lambda: self._delete_result_section(item))
                menu.addAction(delete_section_action)

                copy_line_action = QAction(f"{ICONS['copy']} Copy Line", self)
                copy_line_action.triggered.connect(lambda: self._copy_line_content(data))
                menu.addAction(copy_line_action)
        else:
            # 旧格式兼容
            delete_row_action = QAction(f"{ICONS['delete']} Delete Row", self)
            delete_row_action.triggered.connect(lambda: self.delete_result_row(item))
            menu.addAction(delete_row_action)

            delete_section_action = QAction(f"{ICONS['file']} Delete Section", self)
            delete_section_action.triggered.connect(lambda: self.delete_result_section(item))
            menu.addAction(delete_section_action)

        menu.exec_(self.results_tree.mapToGlobal(pos))

    def _delete_search(self, search_id: str):
        """删除整个搜索结果"""
        self.search_results = [r for r in self.search_results if r["search_id"] != search_id]
        self._rebuild_results_tree()

    def _copy_query(self, search_id: str):
        """复制搜索词到剪贴板"""
        from PyQt5.QtWidgets import QApplication
        for r in self.search_results:
            if r["search_id"] == search_id:
                QApplication.clipboard().setText(r["query"])
                break

    def _remove_file_from_results(self, item: QTreeWidgetItem, search_id: str):
        """从搜索结果中移除某个文件"""
        for r in self.search_results:
            if r["search_id"] == search_id:
                # 获取文件的 tab_index
                file_data = item.data(0, Qt.UserRole)
                tab_index = file_data.get("tab_index")
                r["file_results"] = [f for f in r["file_results"] if f["tab_index"] != tab_index]
                # 更新总匹配数
                r["total_matches"] = sum(len(f["matches"]) for f in r["file_results"])
                # 如果文件全删光了，删除整个搜索
                if not r["file_results"]:
                    self.search_results = [sr for sr in self.search_results if sr["search_id"] != search_id]
                break
        self._rebuild_results_tree()

    def _delete_result_item(self, item: QTreeWidgetItem):
        """删除单个结果项"""
        parent = item.parent()
        if parent:
            parent.removeChild(item)
            # 如果父项没有子项了，也删除父项
            if parent.childCount() == 0:
                grandparent = parent.parent()
                if grandparent:
                    grandparent.removeChild(parent)

    def _delete_result_section(self, item: QTreeWidgetItem):
        """删除整节（包括所有子项）"""
        parent = item.parent()
        if parent:
            parent.removeChild(item)
        else:
            # 是顶级项
            index = self.results_tree.indexOfTopLevelItem(item)
            if index >= 0:
                self.results_tree.takeTopLevelItem(index)

    def _copy_line_content(self, data: dict):
        """复制行内容到剪贴板"""
        from PyQt5.QtWidgets import QApplication
        search_id = data.get("search_id")
        tab_index = data.get("tab_index")
        line_num = data.get("line_num")

        for r in self.search_results:
            if r["search_id"] == search_id:
                for f in r["file_results"]:
                    if f["tab_index"] == tab_index:
                        lines = f.get("lines", [])
                        if line_num is not None and line_num < len(lines):
                            QApplication.clipboard().setText(lines[line_num])
                        break
                break

    def delete_result_row(self, item: QTreeWidgetItem):
        """删除搜索结果中的单行"""
        match_idx = item.data(0, Qt.UserRole)

        # 父节点不能直接删除行，只能删除节
        if match_idx == -1:
            return

        # 获取父项
        parent = item.parent()
        if parent:
            # 是子项，从父项中移除
            parent.removeChild(item)
            # 如果父项只剩一个子项，将其提升为顶级项
            if parent.childCount() == 1:
                remaining_child = parent.takeChild(0)
                # 更新显示文本（移除 [1] 前缀）
                line_num = remaining_child.data(0, Qt.UserRole + 2)
                match_idx_remain = remaining_child.data(0, Qt.UserRole)
                if match_idx_remain is not None and match_idx_remain < len(self.search_engine.matches):
                    match = self.search_engine.matches[match_idx_remain]
                    lines = self.active_search_context["lines"] if self.active_search_context else self.lines
                    if line_num < len(lines):
                        context = self._get_match_context(lines[line_num], match[1], match[2])
                        remaining_child.setText(0, f"行 {line_num + 1}: {context}")
                # 替换父项
                index = self.results_tree.indexOfTopLevelItem(parent)
                self.results_tree.takeTopLevelItem(index)
                self.results_tree.insertTopLevelItem(index, remaining_child)
            elif parent.childCount() == 0:
                # 没有子项了，删除父项
                index = self.results_tree.indexOfTopLevelItem(parent)
                self.results_tree.takeTopLevelItem(index)
            else:
                # 更新父项的计数
                line_num = parent.data(0, Qt.UserRole + 2)
                lines = self.active_search_context["lines"] if self.active_search_context else self.lines
                if line_num < len(lines):
                    line_preview = lines[line_num][:60] + "..." if len(lines[line_num]) > 60 else lines[line_num]
                    parent.setText(0, f"行 {line_num + 1}: {line_preview} ({parent.childCount()} 个匹配)")
        else:
            # 是顶级项，直接删除
            index = self.results_tree.indexOfTopLevelItem(item)
            self.results_tree.takeTopLevelItem(index)

        # 更新总数显示
        self._update_match_count_display()

    def delete_result_section(self, item: QTreeWidgetItem):
        """删除搜索结果中的整节（同一行的所有匹配）"""
        parent = item.parent()

        if parent:
            # 是子项，删除整个父节点
            index = self.results_tree.indexOfTopLevelItem(parent)
            self.results_tree.takeTopLevelItem(index)
        else:
            # 是顶级项（包括父节点和单独项），删除自己
            index = self.results_tree.indexOfTopLevelItem(item)
            self.results_tree.takeTopLevelItem(index)

        # 更新总数显示
        self._update_match_count_display()

    def _update_match_count_display(self):
        """更新搜索面板的匹配计数"""
        # 统计树中剩余的匹配数
        total_matches = 0
        for i in range(self.results_tree.topLevelItemCount()):
            item = self.results_tree.topLevelItem(i)
            if item.data(0, Qt.UserRole) == -1:
                # 父节点，计算子项数
                total_matches += item.childCount()
            else:
                # 单独项
                total_matches += 1

        if total_matches > 0:
            self.search_panel.update_match_count(1, total_matches)
        else:
            self.search_panel.update_match_count(0, 0)
            self.results_tree.hide()

    def jump_to_line(self):
        """跳转到行"""
        if not self.lines:
            return

        from PyQt5.QtWidgets import QInputDialog
        line_num, ok = QInputDialog.getInt(self, "跳转到行", "行号:", 1, 1, len(self.lines))

        if ok:
            cursor = self.log_viewer.textCursor()
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_num - 1)
            self.log_viewer.setTextCursor(cursor)
            self.log_viewer.ensureCursorVisible()

    def toggle_word_wrap(self):
        """切换自动换行"""
        wrap_enabled = self.wrap_btn.isChecked()
        wrap_mode = QTextEdit.WidgetWidth if wrap_enabled else QTextEdit.NoWrap

        # 应用到主日志查看器
        self.main_log_viewer.setLineWrapMode(wrap_mode)

        # 应用到虚拟查看器（如果存在）
        if self.virtual_viewer:
            self.virtual_viewer.set_line_wrap(wrap_enabled)

        # 应用到所有 Grep 标签页
        for tab_info in self.grep_tabs.values():
            if "viewer" in tab_info:
                tab_info["viewer"].setLineWrapMode(wrap_mode)

    def export_log(self):
        """导出日志"""
        if not self.lines:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出日志", "logconsole-export.txt", "文本文件 (*.txt)"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(self.lines))
                QMessageBox.information(self, "Export Success", f"Exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def _apply_search_highlight(self, viewer, block, match_start: int, match_end: int):
        """使用 ExtraSelections 高亮当前匹配行和搜索词（高性能，不阻塞 UI）"""
        selections = []

        # 1. 当前行背景高亮（深色半透明，更明显）
        line_selection = QTextEdit.ExtraSelection()
        line_fmt = QTextCharFormat()
        line_fmt.setBackground(QColor(255, 200, 50, 40))  # 暖黄色半透明
        line_fmt.setProperty(QTextCharFormat.FullWidthSelection, True)
        line_selection.format = line_fmt
        line_cursor = QTextCursor(block)
        line_cursor.clearSelection()
        line_selection.cursor = line_cursor
        selections.append(line_selection)

        # 2. 当前匹配词高亮（亮橙色背景 + 黑色加粗 + 边框）
        if match_end > match_start:
            word_selection = QTextEdit.ExtraSelection()
            word_fmt = QTextCharFormat()
            word_fmt.setBackground(QColor("#FF9500"))  # 亮橙色
            word_fmt.setForeground(QColor("#000000"))  # 黑色文字
            word_fmt.setFontWeight(QFont.Bold)
            # 添加下划线使匹配更醒目
            word_fmt.setUnderlineStyle(QTextCharFormat.SingleUnderline)
            word_fmt.setUnderlineColor(QColor("#FF5500"))
            word_selection.format = word_fmt

            word_cursor = QTextCursor(block)
            word_cursor.setPosition(block.position() + match_start)
            word_cursor.setPosition(block.position() + match_end, QTextCursor.KeepAnchor)
            word_selection.cursor = word_cursor
            selections.append(word_selection)

        viewer.setExtraSelections(selections)

    def _on_selection_changed(self):
        """选中文本变化时，高亮所有相同词语"""
        viewer = self.main_log_viewer
        cursor = viewer.textCursor()
        selected_text = cursor.selectedText().strip()

        # 如果选中的词和上次相同，不重复处理
        if selected_text == self._selection_highlight_word:
            return

        self._selection_highlight_word = selected_text

        # 如果没有选中文本或选中太短/太长，清除高亮
        if not selected_text or len(selected_text) < 2 or len(selected_text) > 100:
            viewer.setExtraSelections([])
            return

        # 如果选中包含换行，不处理
        if '\u2029' in selected_text:  # Qt 用 \u2029 表示换行
            viewer.setExtraSelections([])
            return

        # 使用 ExtraSelections 高亮所有相同词
        self._highlight_all_occurrences(viewer, selected_text)

    def _highlight_all_occurrences(self, viewer: QTextEdit, word: str):
        """高亮所有相同词语出现的位置（当前选中用橙色，其他用黄色）"""
        import re

        doc = viewer.document()
        text = doc.toPlainText()

        # 获取当前选中的位置范围
        current_cursor = viewer.textCursor()
        sel_start = current_cursor.selectionStart()
        sel_end = current_cursor.selectionEnd()

        # 搜索所有匹配位置（大小写不敏感）
        selections = []
        try:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            for match in pattern.finditer(text):
                selection = QTextEdit.ExtraSelection()
                fmt = QTextCharFormat()

                # 当前选中的词：橙色背景 + 白色文字 + 下划线（更醒目）
                if match.start() == sel_start and match.end() == sel_end:
                    fmt.setBackground(QColor("#FF9500"))  # 橙色背景
                    fmt.setForeground(QColor("#FFFFFF"))  # 白色文字
                    fmt.setFontWeight(QFont.Bold)
                    fmt.setUnderlineStyle(QTextCharFormat.SingleUnderline)
                    fmt.setUnderlineColor(QColor("#FF5500"))
                else:
                    # 其他相同词语：亮黄色背景 + 深灰色文字
                    fmt.setBackground(QColor("#FFEB3B"))
                    fmt.setForeground(QColor("#1A1A1A"))

                selection.format = fmt

                cursor = QTextCursor(doc)
                cursor.setPosition(match.start())
                cursor.setPosition(match.end(), QTextCursor.KeepAnchor)
                selection.cursor = cursor
                selections.append(selection)

                # 限制高亮数量，避免性能问题
                if len(selections) >= 500:
                    break
        except re.error:
            pass

        viewer.setExtraSelections(selections)

    def eventFilter(self, obj, event):
        """事件过滤器：监听鼠标事件处理选中高亮"""
        from PyQt5.QtCore import QEvent

        # 只处理主日志查看器的 viewport
        if obj == self.main_log_viewer.viewport():
            if event.type() == QEvent.MouseButtonPress:
                # 鼠标按下，标记正在选择
                self._is_selecting = True
                # 清除旧的高亮
                self.main_log_viewer.setExtraSelections([])
                self._selection_highlight_word = None
            elif event.type() == QEvent.MouseMove and self._is_selecting:
                # 拖拽过程中，实时显示当前选中文本的橙色高亮
                self._highlight_current_selection_only()
            elif event.type() == QEvent.MouseButtonRelease:
                # 鼠标释放，处理完整高亮（当前选中 + 其他匹配项）
                if self._is_selecting:
                    self._is_selecting = False
                    self._on_selection_changed()

        return super().eventFilter(obj, event)

    def _highlight_current_selection_only(self):
        """仅高亮当前选中的文本（拖拽过程中使用）"""
        cursor = self.main_log_viewer.textCursor()
        selected_text = cursor.selectedText().strip()

        if not selected_text or len(selected_text) < 2:
            self.main_log_viewer.setExtraSelections([])
            return

        # 创建当前选中的高亮样式（橙色背景 + 白色加粗下划线）
        from PyQt5.QtWidgets import QTextEdit
        from PyQt5.QtGui import QTextCharFormat, QColor, QFont

        selection = QTextEdit.ExtraSelection()
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#FF9500"))  # 橙色背景
        fmt.setForeground(QColor("#FFFFFF"))  # 白色文字
        fmt.setFontWeight(QFont.Bold)
        fmt.setFontUnderline(True)
        selection.format = fmt
        selection.cursor = cursor

        self.main_log_viewer.setExtraSelections([selection])
