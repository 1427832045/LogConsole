"""
关键词高亮管理面板
支持添加/删除/管理关键词高亮，保存/加载用户模板
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QLineEdit, QComboBox,
    QDialogButtonBox, QWidget, QGridLayout, QFrame, QMenu,
    QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

from ..core.keyword_highlight import (
    KeywordHighlightManager, KeywordHighlight, PRESET_COLORS
)
from .apple_hig_theme import (
    get_color_picker_dialog_style, get_highlight_panel_style, APPLE_COLORS
)


class ColorPickerDialog(QDialog):
    """颜色选择对话框 - 预制颜色网格"""

    def __init__(self, parent=None, current_color: dict = None):
        super().__init__(parent)
        self.selected_color = current_color or PRESET_COLORS[0]
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Select Color")
        self.setFixedSize(280, 200)
        self.setStyleSheet(get_color_picker_dialog_style())

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # 标题
        title = QLabel("Choose Highlight Color")
        title.setStyleSheet(f"font-weight: 600; font-size: 14px;")
        layout.addWidget(title)

        # 颜色网格
        grid = QGridLayout()
        grid.setSpacing(8)

        self.color_buttons = []
        for i, color in enumerate(PRESET_COLORS):
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color['fg']};
                    border: 2px solid transparent;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    border-color: {APPLE_COLORS['text_secondary']};
                }}
                QPushButton:checked {{
                    border-color: {APPLE_COLORS['accent']};
                    border-width: 3px;
                }}
            """)
            btn.setCheckable(True)
            btn.setToolTip(color['name'])
            btn.setProperty("color_data", color)
            btn.clicked.connect(lambda checked, b=btn: self._on_color_selected(b))

            # 默认选中第一个或当前颜色
            if color['fg'] == self.selected_color['fg']:
                btn.setChecked(True)

            row, col = divmod(i, 5)
            grid.addWidget(btn, row, col)
            self.color_buttons.append(btn)

        layout.addLayout(grid)

        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_color_selected(self, btn: QPushButton):
        # 取消其他按钮的选中状态
        for b in self.color_buttons:
            if b != btn:
                b.setChecked(False)
        btn.setChecked(True)
        self.selected_color = btn.property("color_data")

    def get_selected_color(self) -> dict:
        return self.selected_color


class HighlightManagePanel(QDialog):
    """高亮管理面板 - 管理关键词高亮和模板"""

    highlight_changed = pyqtSignal()

    def __init__(self, parent=None, manager: KeywordHighlightManager = None):
        super().__init__(parent)
        self.manager = manager or KeywordHighlightManager()
        self.setup_ui()
        self.refresh_list()
        self.refresh_templates()

    def setup_ui(self):
        self.setWindowTitle("Keyword Highlights")
        self.setMinimumSize(450, 400)
        self.setStyleSheet(get_highlight_panel_style())

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # 顶部：模板选择
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("Template:"))

        self.template_combo = QComboBox()
        self.template_combo.setMinimumWidth(150)
        self.template_combo.currentTextChanged.connect(self._on_template_selected)
        template_layout.addWidget(self.template_combo)

        save_tpl_btn = QPushButton("Save")
        save_tpl_btn.setFixedWidth(60)
        save_tpl_btn.clicked.connect(self._save_template)
        template_layout.addWidget(save_tpl_btn)

        del_tpl_btn = QPushButton("Delete")
        del_tpl_btn.setFixedWidth(60)
        del_tpl_btn.clicked.connect(self._delete_template)
        template_layout.addWidget(del_tpl_btn)

        template_layout.addStretch()
        layout.addLayout(template_layout)

        # 分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background: {APPLE_COLORS['border']}; max-height: 1px;")
        layout.addWidget(sep)

        # 关键词列表
        list_label = QLabel("Current Highlights:")
        list_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(list_label)

        self.keyword_list = QListWidget()
        self.keyword_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.keyword_list.customContextMenuRequested.connect(self._show_list_menu)
        self.keyword_list.itemDoubleClicked.connect(self._edit_keyword)
        layout.addWidget(self.keyword_list)

        # 添加新关键词
        add_layout = QHBoxLayout()

        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Enter keyword...")
        self.keyword_input.returnPressed.connect(self._add_keyword)
        add_layout.addWidget(self.keyword_input)

        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(36, 36)
        self._current_color = PRESET_COLORS[0]
        self._update_color_button()
        self.color_btn.clicked.connect(self._pick_color)
        add_layout.addWidget(self.color_btn)

        add_btn = QPushButton("Add")
        add_btn.setObjectName("primaryBtn")
        add_btn.clicked.connect(self._add_keyword)
        add_layout.addWidget(add_btn)

        layout.addLayout(add_layout)

        # 底部按钮
        bottom_layout = QHBoxLayout()

        clear_btn = QPushButton("Clear All")
        clear_btn.setObjectName("dangerBtn")
        clear_btn.clicked.connect(self._clear_all)
        bottom_layout.addWidget(clear_btn)

        bottom_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        bottom_layout.addWidget(close_btn)

        layout.addLayout(bottom_layout)

    def _update_color_button(self):
        """更新颜色按钮外观"""
        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self._current_color['fg']};
                border: 2px solid {APPLE_COLORS['border']};
                border-radius: 6px;
            }}
            QPushButton:hover {{
                border-color: {APPLE_COLORS['text_secondary']};
            }}
        """)
        self.color_btn.setToolTip(self._current_color['name'])

    def _pick_color(self):
        """弹出颜色选择器"""
        dialog = ColorPickerDialog(self, self._current_color)
        if dialog.exec_() == QDialog.Accepted:
            self._current_color = dialog.get_selected_color()
            self._update_color_button()

    def _add_keyword(self):
        """添加关键词"""
        keyword = self.keyword_input.text().strip()
        if not keyword:
            return

        self.manager.add_keyword(
            keyword,
            fg_color=self._current_color['fg'],
            bg_color=self._current_color['bg']
        )
        self.keyword_input.clear()
        self.refresh_list()
        self.highlight_changed.emit()

    def _edit_keyword(self, item: QListWidgetItem):
        """编辑关键词颜色"""
        keyword = item.data(Qt.UserRole)
        kw_obj = self.manager.find_keyword(keyword)
        if not kw_obj:
            return

        # 找到当前颜色
        current = {"fg": kw_obj.fg_color, "bg": kw_obj.bg_color, "name": "Current"}
        for c in PRESET_COLORS:
            if c['fg'] == kw_obj.fg_color:
                current = c
                break

        dialog = ColorPickerDialog(self, current)
        if dialog.exec_() == QDialog.Accepted:
            new_color = dialog.get_selected_color()
            kw_obj.fg_color = new_color['fg']
            kw_obj.bg_color = new_color['bg']
            self.refresh_list()
            self.highlight_changed.emit()

    def _show_list_menu(self, pos):
        """显示右键菜单"""
        item = self.keyword_list.itemAt(pos)
        if not item:
            return

        keyword = item.data(Qt.UserRole)
        menu = QMenu(self)

        toggle_action = menu.addAction("Toggle Enable")
        toggle_action.triggered.connect(lambda: self._toggle_keyword(keyword))

        edit_action = menu.addAction("Change Color")
        edit_action.triggered.connect(lambda: self._edit_keyword(item))

        menu.addSeparator()

        remove_action = menu.addAction("Remove")
        remove_action.triggered.connect(lambda: self._remove_keyword(keyword))

        menu.exec_(self.keyword_list.mapToGlobal(pos))

    def _toggle_keyword(self, keyword: str):
        """切换启用状态"""
        self.manager.toggle_keyword(keyword)
        self.refresh_list()
        self.highlight_changed.emit()

    def _remove_keyword(self, keyword: str):
        """移除关键词"""
        self.manager.remove_keyword(keyword)
        self.refresh_list()
        self.highlight_changed.emit()

    def _clear_all(self):
        """清除所有"""
        if self.manager.keywords:
            reply = QMessageBox.question(
                self, "Confirm",
                "Clear all keyword highlights?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.manager.clear_all()
                self.refresh_list()
                self.highlight_changed.emit()

    def refresh_list(self):
        """刷新列表"""
        self.keyword_list.clear()
        for kw in self.manager.keywords:
            item = QListWidgetItem()
            # 显示文字：关键词 + 颜色标记
            status = "" if kw.enabled else " (disabled)"
            item.setText(f"● {kw.keyword}{status}")
            item.setForeground(QColor(kw.fg_color))
            item.setData(Qt.UserRole, kw.keyword)
            self.keyword_list.addItem(item)

    def refresh_templates(self):
        """刷新模板列表"""
        self.template_combo.blockSignals(True)
        self.template_combo.clear()
        self.template_combo.addItem("-- Select Template --")
        for name in self.manager.get_template_names():
            self.template_combo.addItem(name)
        self.template_combo.blockSignals(False)

    def _on_template_selected(self, name: str):
        """选择模板"""
        if name == "-- Select Template --":
            return
        if self.manager.load_template(name):
            self.refresh_list()
            self.highlight_changed.emit()

    def _save_template(self):
        """保存为模板"""
        if not self.manager.keywords:
            QMessageBox.warning(self, "Warning", "No keywords to save.")
            return

        name, ok = QInputDialog.getText(
            self, "Save Template",
            "Template name:",
            text=""
        )
        if ok and name.strip():
            self.manager.save_as_template(name.strip())
            self.refresh_templates()
            # 选中新保存的模板
            idx = self.template_combo.findText(name.strip())
            if idx >= 0:
                self.template_combo.setCurrentIndex(idx)

    def _delete_template(self):
        """删除当前选中的模板"""
        name = self.template_combo.currentText()
        if name == "-- Select Template --":
            return

        reply = QMessageBox.question(
            self, "Confirm",
            f"Delete template '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.manager.delete_template(name)
            self.refresh_templates()
