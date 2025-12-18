"""
Swiss Spa Premium Theme - 真正的极简高端
设计理念: 温暖灰调 + 大量留白 + 精致细节
参考: Linear.app, Notion, Raycast
"""

# ============================================================
# COLOR PALETTE - Warm Neutral (不是冷冰冰的纯黑)
# ============================================================
APPLE_COLORS = {
    # 背景层级 - 温暖的深灰，不是纯黑
    "bg_base": "#1A1A1C",        # 最深，主编辑区
    "bg_surface": "#232326",     # 工具栏/状态栏
    "bg_elevated": "#2C2C2F",    # 悬浮/下拉
    "bg_hover": "#38383B",       # 悬停状态

    # 文字层级 - 柔和的白，不是刺眼纯白
    "text_primary": "#F5F5F7",   # 主文字
    "text_secondary": "#A1A1A6", # 次要文字
    "text_tertiary": "#6E6E73",  # 占位符/禁用
    "text_muted": "#48484A",     # 极淡文字

    # 唯一强调色 - 温暖的琥珀色 (不是冷蓝)
    "accent": "#F5A623",         # 主强调 - 温暖琥珀
    "accent_hover": "#FFBC42",   # 悬停
    "accent_subtle": "rgba(245, 166, 35, 0.12)",  # 背景

    # 边框 - 极其微妙
    "border": "rgba(255, 255, 255, 0.06)",
    "border_focus": "rgba(245, 166, 35, 0.5)",

    # 语义色 (仅必要时使用)
    "success": "#34C759",
    "warning": "#FF9500",
    "error": "#FF3B30",

    # 兼容旧 API
    "system_blue": "#F5A623",    # 统一用琥珀色
    "system_green": "#34C759",
    "system_red": "#FF3B30",
    "system_gray": "#8E8E93",
    "system_gray2": "#636366",
    "system_gray3": "#48484A",
    "system_gray4": "#3A3A3C",
    "system_gray5": "#2C2C2E",
    "system_gray6": "#1C1C1E",
    "label_primary": "#F5F5F7",
    "label_secondary": "#A1A1A6",
    "label_tertiary": "#6E6E73",
    "label_quaternary": "#48484A",
    "bg_primary": "#1A1A1C",
    "bg_secondary": "#232326",
    "bg_tertiary": "#2C2C2F",
    "separator": "rgba(255, 255, 255, 0.06)",
    "separator_opaque": "#2C2C2F",
}

# ============================================================
# TYPOGRAPHY - 精致排版
# ============================================================
APPLE_FONT_FAMILY = "'SF Pro Display', 'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif"
APPLE_MONO_FONT = "'SF Mono', 'JetBrains Mono', 'Fira Code', Menlo, monospace"

# ============================================================
# SPACING - 8px Grid (严格遵守)
# ============================================================
SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "2xl": "48px",
}

# ============================================================
# ICONS - 精简的 Unicode 符号
# ============================================================
ICONS = {
    "search": "⌕",
    "close": "×",
    "arrow_up": "↑",
    "arrow_down": "↓",
    "check": "✓",
    "chevron": "›",
    "file": "◇",
    "copy": "⧉",
    "delete": "−",
    "add": "+",
}


def get_main_window_style():
    """主窗口 - 温暖深色基底"""
    return f"""
        QMainWindow {{
            background-color: {APPLE_COLORS['bg_base']};
        }}

        /* 编辑器区域 - 大量呼吸空间 */
        QTextEdit, QPlainTextEdit {{
            background-color: {APPLE_COLORS['bg_base']};
            color: {APPLE_COLORS['text_primary']};
            border: none;
            padding: 24px 32px;
            font-family: {APPLE_MONO_FONT};
            font-size: 13px;
            line-height: 1.7;
            letter-spacing: 0.02em;
            selection-background-color: {APPLE_COLORS['accent_subtle']};
            selection-color: {APPLE_COLORS['text_primary']};
        }}

        /* 状态栏 - 极简 */
        QStatusBar {{
            background-color: {APPLE_COLORS['bg_surface']};
            color: {APPLE_COLORS['text_tertiary']};
            border: none;
            min-height: 28px;
            padding: 0 16px;
        }}
        QStatusBar QLabel {{
            color: {APPLE_COLORS['text_tertiary']};
            font-family: {APPLE_FONT_FAMILY};
            font-size: 11px;
            font-weight: 400;
            padding: 0 12px;
        }}

        /* 滚动条 - 几乎隐形 */
        QScrollBar:vertical {{
            background: transparent;
            width: 6px;
            margin: 4px 2px;
        }}
        QScrollBar::handle:vertical {{
            background: {APPLE_COLORS['text_muted']};
            border-radius: 3px;
            min-height: 32px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {APPLE_COLORS['text_tertiary']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            height: 0;
            background: transparent;
        }}

        QScrollBar:horizontal {{
            background: transparent;
            height: 6px;
            margin: 2px 4px;
        }}
        QScrollBar::handle:horizontal {{
            background: {APPLE_COLORS['text_muted']};
            border-radius: 3px;
            min-width: 32px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {APPLE_COLORS['text_tertiary']};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            width: 0;
            background: transparent;
        }}

        /* 分割器 - 几乎看不见 */
        QSplitter::handle {{
            background: {APPLE_COLORS['border']};
        }}
        QSplitter::handle:vertical {{ height: 1px; }}
        QSplitter::handle:horizontal {{ width: 1px; }}

        /* 对话框 */
        QMessageBox, QInputDialog, QFileDialog {{
            background-color: {APPLE_COLORS['bg_elevated']};
            color: {APPLE_COLORS['text_primary']};
        }}
        QMessageBox QLabel, QInputDialog QLabel {{
            color: {APPLE_COLORS['text_primary']};
            font-size: 13px;
        }}
        QMessageBox QPushButton, QInputDialog QPushButton {{
            background-color: {APPLE_COLORS['bg_hover']};
            color: {APPLE_COLORS['text_primary']};
            border: none;
            border-radius: 6px;
            padding: 8px 20px;
            font-size: 13px;
            font-weight: 500;
            min-width: 72px;
        }}
        QMessageBox QPushButton:hover, QInputDialog QPushButton:hover {{
            background-color: {APPLE_COLORS['text_muted']};
        }}
        QMessageBox QPushButton:default {{
            background-color: {APPLE_COLORS['accent']};
            color: #000000;
        }}
    """


def get_toolbar_style():
    """工具栏 - 极简图标式"""
    return f"""
        QToolBar {{
            background-color: {APPLE_COLORS['bg_surface']};
            border: none;
            padding: 8px 16px;
            spacing: 4px;
        }}
        QToolBar::separator {{
            width: 0;
            margin: 0 8px;
        }}

        /* 工具栏按钮 - 纯文字，无边框 */
        QToolBar QPushButton {{
            background: transparent;
            color: {APPLE_COLORS['text_secondary']};
            border: none;
            border-radius: 6px;
            padding: 8px 12px;
            font-family: {APPLE_FONT_FAMILY};
            font-size: 13px;
            font-weight: 500;
        }}
        QToolBar QPushButton:hover {{
            background-color: {APPLE_COLORS['bg_hover']};
            color: {APPLE_COLORS['text_primary']};
        }}
        QToolBar QPushButton:pressed {{
            background-color: {APPLE_COLORS['text_muted']};
        }}
        QToolBar QPushButton:checked {{
            color: {APPLE_COLORS['accent']};
        }}

        /* 标签文字 */
        QToolBar QLabel {{
            color: {APPLE_COLORS['text_tertiary']};
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.05em;
            padding: 0 8px;
        }}
    """


def get_tab_widget_style():
    """标签页 - 精致下划线"""
    return f"""
        QTabWidget::pane {{
            border: none;
            background: {APPLE_COLORS['bg_base']};
        }}

        QTabBar {{
            background: {APPLE_COLORS['bg_surface']};
        }}
        QTabBar::tab {{
            background: transparent;
            color: {APPLE_COLORS['text_tertiary']};
            padding: 10px 16px;
            margin: 0;
            border: none;
            border-bottom: 2px solid transparent;
            font-family: {APPLE_FONT_FAMILY};
            font-size: 12px;
            font-weight: 500;
        }}
        QTabBar::tab:selected {{
            color: {APPLE_COLORS['text_primary']};
            border-bottom: 2px solid {APPLE_COLORS['accent']};
        }}
        QTabBar::tab:hover:!selected {{
            color: {APPLE_COLORS['text_secondary']};
        }}

        /* 关闭按钮 */
        QTabBar::close-button {{
            image: none;
            subcontrol-position: right;
            padding: 4px;
        }}
        QTabBar::close-button:hover {{
            background: {APPLE_COLORS['error']};
            border-radius: 3px;
        }}
    """


def get_combobox_style():
    """下拉框 - 简洁"""
    return f"""
        QComboBox {{
            background: {APPLE_COLORS['bg_hover']};
            color: {APPLE_COLORS['text_primary']};
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
            padding-right: 28px;
            font-family: {APPLE_FONT_FAMILY};
            font-size: 12px;
            min-width: 100px;
        }}
        QComboBox:hover {{
            background: {APPLE_COLORS['text_muted']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid {APPLE_COLORS['text_secondary']};
            margin-right: 8px;
        }}
        QComboBox QAbstractItemView {{
            background: {APPLE_COLORS['bg_elevated']};
            color: {APPLE_COLORS['text_primary']};
            border: 1px solid {APPLE_COLORS['border']};
            border-radius: 8px;
            padding: 4px;
            selection-background-color: {APPLE_COLORS['accent_subtle']};
        }}
        QComboBox QAbstractItemView::item {{
            padding: 8px 12px;
            border-radius: 4px;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background: {APPLE_COLORS['bg_hover']};
        }}
    """


def get_tree_widget_style():
    """树形控件 - 搜索结果 (极简风格，原生折叠箭头)"""
    return f"""
        QTreeWidget {{
            background: {APPLE_COLORS['bg_surface']};
            color: {APPLE_COLORS['text_primary']};
            border: none;
            font-family: {APPLE_FONT_FAMILY};
            font-size: 12px;
            padding: 8px;
            outline: none;
        }}
        QTreeWidget::item {{
            padding: 5px 8px;
            border-radius: 4px;
            margin: 1px 0;
        }}
        QTreeWidget::item:hover {{
            background: {APPLE_COLORS['bg_hover']};
        }}
        QTreeWidget::item:selected {{
            background: {APPLE_COLORS['accent_subtle']};
            color: {APPLE_COLORS['text_primary']};
        }}
        QTreeWidget::branch {{
            background: transparent;
        }}
        QTreeWidget::branch:has-siblings:!adjoins-item {{
            border-image: none;
        }}
        QTreeWidget::branch:has-siblings:adjoins-item {{
            border-image: none;
        }}
        QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {{
            border-image: none;
        }}
        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:closed:has-children:has-siblings {{
            border-image: none;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNNCAxTDkgNkw0IDExIiBzdHJva2U9IiNGNUE2MjMiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PC9zdmc+);
        }}
        QTreeWidget::branch:open:has-children:!has-siblings,
        QTreeWidget::branch:open:has-children:has-siblings {{
            border-image: none;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMSA0TDYgOUwxMSA0IiBzdHJva2U9IiNGNUE2MjMiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PC9zdmc+);
        }}
        QHeaderView::section {{
            background: {APPLE_COLORS['bg_surface']};
            color: {APPLE_COLORS['text_secondary']};
            border: none;
            padding: 8px;
            font-size: 11px;
            font-weight: 500;
        }}
    """


def get_search_panel_style():
    """搜索面板 - 浮动感"""
    return f"""
        ModernSearchPanel {{
            background: {APPLE_COLORS['bg_surface']};
            border: none;
        }}

        QLineEdit {{
            background: {APPLE_COLORS['bg_hover']};
            color: {APPLE_COLORS['text_primary']};
            border: 1px solid transparent;
            border-radius: 8px;
            padding: 10px 14px;
            font-family: {APPLE_FONT_FAMILY};
            font-size: 14px;
            selection-background-color: {APPLE_COLORS['accent_subtle']};
        }}
        QLineEdit:focus {{
            border: 1px solid {APPLE_COLORS['accent']};
            background: {APPLE_COLORS['bg_elevated']};
        }}
        QLineEdit::placeholder {{
            color: {APPLE_COLORS['text_tertiary']};
        }}

        QPushButton {{
            background: {APPLE_COLORS['bg_hover']};
            color: {APPLE_COLORS['text_primary']};
            border: none;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background: {APPLE_COLORS['text_muted']};
        }}

        QPushButton#closeBtn {{
            background: transparent;
            color: {APPLE_COLORS['text_tertiary']};
            padding: 4px;
            font-size: 16px;
        }}
        QPushButton#closeBtn:hover {{
            color: {APPLE_COLORS['error']};
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

        QLabel {{
            color: {APPLE_COLORS['text_secondary']};
            font-size: 12px;
        }}
        QLabel#matchCount {{
            color: {APPLE_COLORS['accent']};
            font-weight: 600;
            padding: 4px 8px;
            background: {APPLE_COLORS['accent_subtle']};
            border-radius: 4px;
        }}
    """


def get_context_menu_style():
    """右键菜单 - 毛玻璃感"""
    return f"""
        QMenu {{
            background: {APPLE_COLORS['bg_elevated']};
            color: {APPLE_COLORS['text_primary']};
            border: 1px solid {APPLE_COLORS['border']};
            border-radius: 10px;
            padding: 6px;
            font-family: {APPLE_FONT_FAMILY};
            font-size: 13px;
        }}
        QMenu::item {{
            padding: 8px 16px;
            border-radius: 6px;
            margin: 2px;
        }}
        QMenu::item:selected {{
            background: {APPLE_COLORS['accent_subtle']};
            color: {APPLE_COLORS['accent']};
        }}
        QMenu::separator {{
            height: 1px;
            background: {APPLE_COLORS['border']};
            margin: 6px 8px;
        }}
    """


def get_search_dialog_style():
    """搜索弹窗"""
    return f"""
        QDialog {{
            background: {APPLE_COLORS['bg_elevated']};
            color: {APPLE_COLORS['text_primary']};
            font-family: {APPLE_FONT_FAMILY};
        }}

        QLabel {{
            color: {APPLE_COLORS['text_primary']};
            font-size: 13px;
        }}

        QLineEdit {{
            background: {APPLE_COLORS['bg_hover']};
            color: {APPLE_COLORS['text_primary']};
            border: 1px solid transparent;
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 14px;
        }}
        QLineEdit:focus {{
            border-color: {APPLE_COLORS['accent']};
        }}

        QCheckBox, QRadioButton {{
            color: {APPLE_COLORS['text_primary']};
            font-size: 13px;
            spacing: 8px;
        }}
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 16px;
            height: 16px;
        }}
        QCheckBox::indicator {{
            border-radius: 4px;
        }}
        QRadioButton::indicator {{
            border-radius: 8px;
        }}
        QCheckBox::indicator, QRadioButton::indicator {{
            border: 1px solid {APPLE_COLORS['text_muted']};
            background: transparent;
        }}
        QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
            background: {APPLE_COLORS['accent']};
            border-color: {APPLE_COLORS['accent']};
        }}

        QGroupBox {{
            color: {APPLE_COLORS['text_secondary']};
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.05em;
            border: 1px solid {APPLE_COLORS['border']};
            border-radius: 8px;
            margin-top: 16px;
            padding: 16px 12px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
        }}

        QPushButton {{
            background: {APPLE_COLORS['bg_hover']};
            color: {APPLE_COLORS['text_primary']};
            border: none;
            border-radius: 6px;
            padding: 10px 16px;
            font-size: 13px;
            font-weight: 500;
            min-width: 100px;
        }}
        QPushButton:hover {{
            background: {APPLE_COLORS['text_muted']};
        }}
        QPushButton#primaryBtn {{
            background: {APPLE_COLORS['accent']};
            color: #000000;
        }}
        QPushButton#primaryBtn:hover {{
            background: {APPLE_COLORS['accent_hover']};
        }}

        QFrame[frameShape="4"] {{
            background: {APPLE_COLORS['border']};
            max-height: 1px;
        }}
    """


def get_grep_filter_bar_style():
    """Grep 过滤栏"""
    return f"""
        QFrame {{
            background: {APPLE_COLORS['bg_surface']};
            border: none;
            padding: 6px 12px;
        }}
    """


def get_grep_tag_style(is_primary=True):
    """Grep 标签"""
    color = APPLE_COLORS['success'] if is_primary else APPLE_COLORS['accent']
    return f"""
        QLabel {{
            color: {color};
            font-size: 11px;
            font-weight: 500;
            padding: 3px 8px;
            background: rgba(52, 199, 89, 0.12) if {is_primary} else {APPLE_COLORS['accent_subtle']};
            border-radius: 4px;
        }}
    """


def get_count_label_style():
    """计数标签"""
    return f"""
        QLabel {{
            color: {APPLE_COLORS['text_secondary']};
            font-size: 11px;
            padding: 2px 6px;
            background: {APPLE_COLORS['bg_hover']};
            border-radius: 3px;
        }}
    """


def get_add_grep_dialog_style():
    """Add Grep 对话框"""
    return f"""
        QDialog {{
            background: {APPLE_COLORS['bg_elevated']};
            color: {APPLE_COLORS['text_primary']};
        }}
        QRadioButton {{
            color: {APPLE_COLORS['text_primary']};
            font-size: 13px;
            padding: 8px;
        }}
        QRadioButton::indicator {{
            width: 14px;
            height: 14px;
            border-radius: 7px;
            border: 1px solid {APPLE_COLORS['text_muted']};
        }}
        QRadioButton::indicator:checked {{
            background: {APPLE_COLORS['accent']};
            border-color: {APPLE_COLORS['accent']};
        }}
        QDialogButtonBox QPushButton {{
            background: {APPLE_COLORS['bg_hover']};
            color: {APPLE_COLORS['text_primary']};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 13px;
            min-width: 72px;
        }}
        QDialogButtonBox QPushButton:hover {{
            background: {APPLE_COLORS['text_muted']};
        }}
        QDialogButtonBox QPushButton:default {{
            background: {APPLE_COLORS['accent']};
            color: #000000;
        }}
    """


# 导出兼容
SYSTEM_BLUE = APPLE_COLORS["accent"]
SYSTEM_GREEN = APPLE_COLORS["success"]
SYSTEM_RED = APPLE_COLORS["error"]
BG_PRIMARY = APPLE_COLORS["bg_base"]
BG_SECONDARY = APPLE_COLORS["bg_surface"]
BG_TERTIARY = APPLE_COLORS["bg_elevated"]
LABEL_PRIMARY = APPLE_COLORS["text_primary"]
LABEL_SECONDARY = APPLE_COLORS["text_secondary"]