"""
高级搜索弹窗 - 极简重设计
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QCheckBox, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal

from .apple_hig_theme import APPLE_COLORS, APPLE_FONT_FAMILY


class SearchDialog(QDialog):
    """高级搜索弹窗 - 极简风格"""

    find_next = pyqtSignal(str, bool, bool)
    find_prev = pyqtSignal(str, bool, bool)
    find_count = pyqtSignal(str, bool, bool)
    find_in_current = pyqtSignal(str, bool, bool)
    find_in_all = pyqtSignal(str, bool, bool)
    clear_results = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("查找")
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setModal(False)
        self.setFixedWidth(420)
        self.setup_ui()
        self.apply_style()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # 搜索输入
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索...")
        self.search_input.returnPressed.connect(self._on_find_next)
        layout.addWidget(self.search_input)

        # 选项行 - 只保留常用的
        options_layout = QHBoxLayout()
        options_layout.setSpacing(16)

        self.case_check = QCheckBox("区分大小写")
        self.mode_regex = QCheckBox("正则")
        self.whole_word_check = QCheckBox("全词")

        options_layout.addWidget(self.case_check)
        options_layout.addWidget(self.mode_regex)
        options_layout.addWidget(self.whole_word_check)
        options_layout.addStretch()
        layout.addLayout(options_layout)

        # 分隔
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background: {APPLE_COLORS['border']}; border: none; max-height: 1px;")
        layout.addWidget(line)

        # 按钮区 - 简化为两行
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        self.find_prev_btn = QPushButton("↑")
        self.find_prev_btn.setToolTip("上一个 (Shift+F3)")
        self.find_prev_btn.setFixedWidth(44)
        self.find_prev_btn.clicked.connect(self._on_find_prev)

        self.find_next_btn = QPushButton("↓")
        self.find_next_btn.setToolTip("下一个 (F3)")
        self.find_next_btn.setFixedWidth(44)
        self.find_next_btn.clicked.connect(self._on_find_next)

        self.find_in_current_btn = QPushButton("查找全部")
        self.find_in_current_btn.setObjectName("primaryBtn")
        self.find_in_current_btn.clicked.connect(self._on_find_in_current)

        row1.addWidget(self.find_prev_btn)
        row1.addWidget(self.find_next_btn)
        row1.addStretch()
        row1.addWidget(self.find_in_current_btn)
        layout.addLayout(row1)

        # 第二行 - 次要操作
        row2 = QHBoxLayout()
        row2.setSpacing(8)

        self.find_in_all_btn = QPushButton("所有文件")
        self.find_in_all_btn.setObjectName("secondaryBtn")
        self.find_in_all_btn.clicked.connect(self._on_find_in_all)

        self.clear_btn = QPushButton("清空")
        self.clear_btn.setObjectName("secondaryBtn")
        self.clear_btn.clicked.connect(self.clear_results.emit)

        self.count_btn = QPushButton("计数")
        self.count_btn.setObjectName("secondaryBtn")
        self.count_btn.clicked.connect(self._on_count)

        row2.addWidget(self.find_in_all_btn)
        row2.addWidget(self.clear_btn)
        row2.addStretch()
        row2.addWidget(self.count_btn)
        layout.addLayout(row2)

        # 状态
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)

        # 保持兼容 - 隐藏的选项
        self.reverse_check = QCheckBox()
        self.reverse_check.hide()
        self.wrap_check = QCheckBox()
        self.wrap_check.setChecked(True)
        self.wrap_check.hide()
        self.mode_normal = type('FakeRadio', (), {'isChecked': lambda: not self.mode_regex.isChecked()})()
        self.mode_extended = type('FakeRadio', (), {'isChecked': lambda: False})()

    def apply_style(self):
        self.setStyleSheet(f"""
            QDialog {{
                background: {APPLE_COLORS['bg_elevated']};
                color: {APPLE_COLORS['text_primary']};
                font-family: {APPLE_FONT_FAMILY};
            }}

            QLineEdit {{
                background: {APPLE_COLORS['bg_base']};
                color: {APPLE_COLORS['text_primary']};
                border: 1px solid {APPLE_COLORS['border']};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                selection-background-color: {APPLE_COLORS['accent_subtle']};
            }}
            QLineEdit:focus {{
                border-color: {APPLE_COLORS['accent']};
            }}
            QLineEdit::placeholder {{
                color: {APPLE_COLORS['text_tertiary']};
            }}

            QCheckBox {{
                color: {APPLE_COLORS['text_secondary']};
                font-size: 12px;
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border-radius: 3px;
                border: 1px solid {APPLE_COLORS['text_muted']};
                background: transparent;
            }}
            QCheckBox::indicator:checked {{
                background: {APPLE_COLORS['accent']};
                border-color: {APPLE_COLORS['accent']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {APPLE_COLORS['text_tertiary']};
            }}

            QPushButton {{
                background: {APPLE_COLORS['bg_hover']};
                color: {APPLE_COLORS['text_primary']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {APPLE_COLORS['text_muted']};
            }}
            QPushButton:pressed {{
                background: {APPLE_COLORS['bg_surface']};
            }}

            QPushButton#primaryBtn {{
                background: {APPLE_COLORS['accent']};
                color: {APPLE_COLORS['bg_base']};
                font-weight: 600;
                padding: 8px 20px;
            }}
            QPushButton#primaryBtn:hover {{
                background: {APPLE_COLORS['accent_hover']};
            }}

            QPushButton#secondaryBtn {{
                background: transparent;
                color: {APPLE_COLORS['text_secondary']};
                font-weight: 400;
            }}
            QPushButton#secondaryBtn:hover {{
                background: {APPLE_COLORS['bg_hover']};
                color: {APPLE_COLORS['text_primary']};
            }}

            QLabel#statusLabel {{
                color: {APPLE_COLORS['text_tertiary']};
                font-size: 11px;
                padding-top: 4px;
            }}

            QFrame {{
                background: transparent;
            }}
        """)

    def _get_search_params(self):
        pattern = self.search_input.text()
        is_regex = self.mode_regex.isChecked()
        case_sensitive = self.case_check.isChecked()
        return pattern, is_regex, case_sensitive

    def _on_find_next(self):
        pattern, is_regex, case_sensitive = self._get_search_params()
        if pattern:
            self.find_next.emit(pattern, is_regex, case_sensitive)

    def _on_find_prev(self):
        pattern, is_regex, case_sensitive = self._get_search_params()
        if pattern:
            self.find_prev.emit(pattern, is_regex, case_sensitive)

    def _on_count(self):
        pattern, is_regex, case_sensitive = self._get_search_params()
        if pattern:
            self.find_count.emit(pattern, is_regex, case_sensitive)

    def _on_find_in_current(self):
        pattern, is_regex, case_sensitive = self._get_search_params()
        if pattern:
            self.find_in_current.emit(pattern, is_regex, case_sensitive)

    def _on_find_in_all(self):
        pattern, is_regex, case_sensitive = self._get_search_params()
        if pattern:
            self.find_in_all.emit(pattern, is_regex, case_sensitive)

    def set_search_text(self, text: str):
        self.search_input.setText(text)
        self.search_input.selectAll()

    def update_status(self, message: str):
        self.status_label.setText(message)

    def show_dialog(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self.search_input.setFocus()
        self.search_input.selectAll()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
        elif event.key() == Qt.Key_F3:
            if event.modifiers() & Qt.ShiftModifier:
                self._on_find_prev()
            else:
                self._on_find_next()
        else:
            super().keyPressEvent(event)
