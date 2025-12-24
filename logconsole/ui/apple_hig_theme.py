"""
Neo-Terminal Theme - Retro-Futuristic Command Center
Design Philosophy: Classic terminal aesthetics + modern refinement
Visual Identity: Phosphor green glow, CRT scanlines, monospace precision
"""

# ============================================================
# COLOR PALETTE - Phosphor Green Terminal
# ============================================================
TERMINAL_COLORS = {
    # Background hierarchy - Deep space black
    "bg_void": "#000000",           # Pure black for contrast
    "bg_base": "#0D1117",           # GitHub dark - main editor
    "bg_surface": "#161B22",        # Elevated surfaces
    "bg_elevated": "#1C2128",       # Dialogs, dropdowns
    "bg_hover": "#21262D",          # Hover states
    "bg_active": "#2D333B",         # Active/pressed states

    # Phosphor Green - Primary accent
    "phosphor": "#00FF41",          # Classic terminal green
    "phosphor_dim": "#00CC33",      # Dimmed green
    "phosphor_glow": "rgba(0, 255, 65, 0.15)",  # Subtle glow
    "phosphor_bright": "#39FF14",   # Neon bright for highlights

    # Amber - Secondary accent (like old monitors)
    "amber": "#FFB000",             # Classic amber
    "amber_dim": "#CC8800",         # Dimmed amber
    "amber_glow": "rgba(255, 176, 0, 0.12)",

    # Text hierarchy
    "text_primary": "#E6EDF3",      # Bright white (not pure)
    "text_secondary": "#8B949E",    # Muted gray
    "text_tertiary": "#484F58",     # Very muted
    "text_ghost": "#30363D",        # Almost invisible

    # Semantic colors
    "error": "#F85149",             # Red alert
    "warning": "#D29922",           # Warning amber
    "success": "#3FB950",           # Success green
    "info": "#58A6FF",              # Info blue

    # Borders - Very subtle
    "border": "rgba(48, 54, 61, 0.8)",
    "border_focus": "rgba(0, 255, 65, 0.5)",
    "border_glow": "rgba(0, 255, 65, 0.3)",

    # Log level colors (enhanced visibility)
    "log_error": "#FF6B6B",
    "log_warn": "#FFE66D",
    "log_info": "#4ECDC4",
    "log_debug": "#95A5A6",
    "log_trace": "#6C7A89",

    # Backward compatibility aliases (for existing code)
    "accent": "#00FF41",             # Maps to phosphor
    "accent_hover": "#39FF14",       # Maps to phosphor_bright
    "accent_subtle": "rgba(0, 255, 65, 0.15)",  # Maps to phosphor_glow
    "text_muted": "#30363D",         # Maps to text_ghost
    "label_primary": "#E6EDF3",      # Maps to text_primary
    "label_secondary": "#8B949E",    # Maps to text_secondary
    "label_tertiary": "#484F58",     # Maps to text_tertiary
    "label_quaternary": "#30363D",   # Maps to text_ghost
    "separator": "rgba(48, 54, 61, 0.8)",  # Maps to border
    "separator_opaque": "#21262D",   # Maps to bg_hover
    "bg_primary": "#0D1117",         # Maps to bg_base
    "bg_secondary": "#161B22",       # Maps to bg_surface
    "bg_tertiary": "#1C2128",        # Maps to bg_elevated
    "system_blue": "#00FF41",        # Maps to phosphor
    "system_green": "#3FB950",       # Maps to success
    "system_red": "#F85149",         # Maps to error
    "system_gray": "#8B949E",
    "system_gray2": "#6E7681",
    "system_gray3": "#484F58",
    "system_gray4": "#30363D",
    "system_gray5": "#21262D",
    "system_gray6": "#161B22",
}

# ============================================================
# TYPOGRAPHY - Monospace Excellence
# ============================================================
TERMINAL_FONT = "'JetBrains Mono', 'Fira Code', 'Source Code Pro', 'IBM Plex Mono', 'Cascadia Code', monospace"
TERMINAL_FONT_UI = "'JetBrains Mono', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif"

# ============================================================
# SPACING - 8px Grid
# ============================================================
SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
}

# ============================================================
# ICONS - Terminal-style Unicode
# ============================================================
ICONS = {
    "search": "⌕",
    "close": "×",
    "arrow_up": "▲",
    "arrow_down": "▼",
    "check": "✓",
    "chevron": "›",
    "file": "◈",
    "folder": "▤",
    "terminal": "▸",
    "copy": "⎘",
    "delete": "⌫",
    "add": "+",
    "filter": "⫧",
    "cursor": "█",
}

# ============================================================
# CRT EFFECTS - Subtle scanlines and glow
# ============================================================
CRT_SCANLINE_OPACITY = 0.03  # Very subtle
CRT_GLOW_BLUR = "2px"
CRT_VIGNETTE = "radial-gradient(ellipse at center, transparent 60%, rgba(0,0,0,0.4) 100%)"


def get_main_window_style():
    """Main window - Deep space command center"""
    return f"""
        QMainWindow {{
            background-color: {TERMINAL_COLORS['bg_base']};
        }}

        /* Editor area - Terminal aesthetic */
        QTextEdit, QPlainTextEdit {{
            background-color: {TERMINAL_COLORS['bg_base']};
            color: {TERMINAL_COLORS['text_primary']};
            border: none;
            padding: 20px 24px;
            font-family: {TERMINAL_FONT};
            font-size: 13px;
            line-height: 1.6;
            letter-spacing: 0.01em;
            selection-background-color: {TERMINAL_COLORS['phosphor_glow']};
            selection-color: {TERMINAL_COLORS['phosphor']};
        }}

        /* Status bar - Minimal terminal prompt style */
        QStatusBar {{
            background-color: {TERMINAL_COLORS['bg_surface']};
            color: {TERMINAL_COLORS['text_tertiary']};
            border: none;
            border-top: 1px solid {TERMINAL_COLORS['border']};
            min-height: 28px;
            padding: 0 12px;
            font-family: {TERMINAL_FONT};
            font-size: 11px;
        }}
        QStatusBar QLabel {{
            color: {TERMINAL_COLORS['text_secondary']};
            font-family: {TERMINAL_FONT};
            font-size: 11px;
            padding: 0 8px;
        }}
        QStatusBar::item {{
            border: none;
        }}

        /* Scrollbar - Thin phosphor accent */
        QScrollBar:vertical {{
            background: transparent;
            width: 8px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {TERMINAL_COLORS['text_ghost']};
            border-radius: 4px;
            min-height: 40px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {TERMINAL_COLORS['phosphor_dim']};
        }}
        QScrollBar::handle:vertical:pressed {{
            background: {TERMINAL_COLORS['phosphor']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            height: 0;
            background: transparent;
        }}

        QScrollBar:horizontal {{
            background: transparent;
            height: 8px;
            margin: 0;
        }}
        QScrollBar::handle:horizontal {{
            background: {TERMINAL_COLORS['text_ghost']};
            border-radius: 4px;
            min-width: 40px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {TERMINAL_COLORS['phosphor_dim']};
        }}
        QScrollBar::handle:horizontal:pressed {{
            background: {TERMINAL_COLORS['phosphor']};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            width: 0;
            background: transparent;
        }}

        /* Splitter - Subtle divider */
        QSplitter::handle {{
            background: {TERMINAL_COLORS['border']};
        }}
        QSplitter::handle:vertical {{ height: 1px; }}
        QSplitter::handle:horizontal {{ width: 1px; }}
        QSplitter::handle:hover {{
            background: {TERMINAL_COLORS['phosphor_dim']};
        }}

        /* Dialogs */
        QMessageBox, QInputDialog, QFileDialog {{
            background-color: {TERMINAL_COLORS['bg_elevated']};
            color: {TERMINAL_COLORS['text_primary']};
        }}
        QMessageBox QLabel, QInputDialog QLabel {{
            color: {TERMINAL_COLORS['text_primary']};
            font-family: {TERMINAL_FONT_UI};
            font-size: 13px;
        }}
        QMessageBox QPushButton, QInputDialog QPushButton {{
            background-color: {TERMINAL_COLORS['bg_hover']};
            color: {TERMINAL_COLORS['text_primary']};
            border: 1px solid {TERMINAL_COLORS['border']};
            border-radius: 4px;
            padding: 8px 16px;
            font-family: {TERMINAL_FONT_UI};
            font-size: 12px;
            font-weight: 500;
            min-width: 72px;
        }}
        QMessageBox QPushButton:hover, QInputDialog QPushButton:hover {{
            background-color: {TERMINAL_COLORS['bg_active']};
            border-color: {TERMINAL_COLORS['phosphor_dim']};
        }}
        QMessageBox QPushButton:default {{
            background-color: {TERMINAL_COLORS['phosphor_dim']};
            color: {TERMINAL_COLORS['bg_base']};
            border-color: {TERMINAL_COLORS['phosphor']};
        }}
        QMessageBox QPushButton:default:hover {{
            background-color: {TERMINAL_COLORS['phosphor']};
        }}
    """


def get_toolbar_style():
    """Toolbar - Minimal terminal command bar"""
    return f"""
        QToolBar {{
            background-color: {TERMINAL_COLORS['bg_surface']};
            border: none;
            border-bottom: 1px solid {TERMINAL_COLORS['border']};
            padding: 6px 12px;
            spacing: 4px;
        }}
        QToolBar::separator {{
            width: 1px;
            background: {TERMINAL_COLORS['border']};
            margin: 4px 8px;
        }}

        /* Toolbar buttons - Terminal command style */
        QToolBar QPushButton {{
            background: transparent;
            color: {TERMINAL_COLORS['text_secondary']};
            border: 1px solid transparent;
            border-radius: 4px;
            padding: 6px 12px;
            font-family: {TERMINAL_FONT_UI};
            font-size: 12px;
            font-weight: 500;
        }}
        QToolBar QPushButton:hover {{
            background-color: {TERMINAL_COLORS['bg_hover']};
            color: {TERMINAL_COLORS['phosphor']};
            border-color: {TERMINAL_COLORS['border']};
        }}
        QToolBar QPushButton:pressed {{
            background-color: {TERMINAL_COLORS['bg_active']};
            color: {TERMINAL_COLORS['phosphor_bright']};
        }}
        QToolBar QPushButton:checked {{
            color: {TERMINAL_COLORS['phosphor']};
            border-color: {TERMINAL_COLORS['phosphor_dim']};
            background-color: {TERMINAL_COLORS['phosphor_glow']};
        }}

        /* Labels in toolbar */
        QToolBar QLabel {{
            color: {TERMINAL_COLORS['text_tertiary']};
            font-family: {TERMINAL_FONT};
            font-size: 11px;
            letter-spacing: 0.05em;
            padding: 0 8px;
        }}
    """


def get_tab_widget_style():
    """Tab bar - Terminal session tabs"""
    return f"""
        QTabWidget::pane {{
            border: none;
            background: {TERMINAL_COLORS['bg_base']};
        }}

        QTabBar {{
            background: {TERMINAL_COLORS['bg_surface']};
            border-bottom: 1px solid {TERMINAL_COLORS['border']};
        }}
        QTabBar::tab {{
            background: transparent;
            color: {TERMINAL_COLORS['text_tertiary']};
            padding: 10px 16px;
            margin: 0;
            border: none;
            border-bottom: 2px solid transparent;
            font-family: {TERMINAL_FONT_UI};
            font-size: 12px;
            font-weight: 500;
        }}
        QTabBar::tab:selected {{
            color: {TERMINAL_COLORS['phosphor']};
            border-bottom: 2px solid {TERMINAL_COLORS['phosphor']};
            background: {TERMINAL_COLORS['phosphor_glow']};
        }}
        QTabBar::tab:hover:!selected {{
            color: {TERMINAL_COLORS['text_primary']};
            background: {TERMINAL_COLORS['bg_hover']};
        }}

        /* Close button on tabs */
        QTabBar::close-button {{
            image: none;
            subcontrol-position: right;
            padding: 4px;
            margin-left: 4px;
        }}
        QTabBar::close-button:hover {{
            background: {TERMINAL_COLORS['error']};
            border-radius: 2px;
        }}
    """


def get_combobox_style():
    """Combobox - Terminal dropdown selector"""
    return f"""
        QComboBox {{
            background: {TERMINAL_COLORS['bg_hover']};
            color: {TERMINAL_COLORS['text_primary']};
            border: 1px solid {TERMINAL_COLORS['border']};
            border-radius: 4px;
            padding: 6px 12px;
            padding-right: 28px;
            font-family: {TERMINAL_FONT_UI};
            font-size: 12px;
            min-width: 100px;
        }}
        QComboBox:hover {{
            border-color: {TERMINAL_COLORS['phosphor_dim']};
        }}
        QComboBox:focus {{
            border-color: {TERMINAL_COLORS['phosphor']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid {TERMINAL_COLORS['text_secondary']};
            margin-right: 8px;
        }}
        QComboBox QAbstractItemView {{
            background: {TERMINAL_COLORS['bg_elevated']};
            color: {TERMINAL_COLORS['text_primary']};
            border: 1px solid {TERMINAL_COLORS['border']};
            border-radius: 4px;
            padding: 4px;
            selection-background-color: {TERMINAL_COLORS['phosphor_glow']};
            selection-color: {TERMINAL_COLORS['phosphor']};
            outline: none;
        }}
        QComboBox QAbstractItemView::item {{
            padding: 8px 12px;
            border-radius: 2px;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background: {TERMINAL_COLORS['bg_hover']};
        }}
        QComboBox QAbstractItemView::item:selected {{
            background: {TERMINAL_COLORS['phosphor_glow']};
            color: {TERMINAL_COLORS['phosphor']};
        }}
    """


def get_tree_widget_style():
    """Tree widget - Terminal file browser style"""
    return f"""
        QTreeWidget {{
            background: {TERMINAL_COLORS['bg_surface']};
            color: {TERMINAL_COLORS['text_primary']};
            border: none;
            font-family: {TERMINAL_FONT};
            font-size: 12px;
            padding: 8px;
            outline: none;
            alternate-background-color: {TERMINAL_COLORS['bg_base']};
        }}
        QTreeWidget::item {{
            padding: 6px 8px;
            border-radius: 2px;
            margin: 1px 0;
        }}
        QTreeWidget::item:hover {{
            background: {TERMINAL_COLORS['bg_hover']};
        }}
        QTreeWidget::item:selected {{
            background: {TERMINAL_COLORS['phosphor_glow']};
            color: {TERMINAL_COLORS['phosphor']};
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
        QHeaderView::section {{
            background: {TERMINAL_COLORS['bg_surface']};
            color: {TERMINAL_COLORS['text_secondary']};
            border: none;
            border-bottom: 1px solid {TERMINAL_COLORS['border']};
            padding: 8px;
            font-family: {TERMINAL_FONT_UI};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
    """


def get_search_panel_style():
    """Search panel - Command input style"""
    return f"""
        ModernSearchPanel {{
            background: {TERMINAL_COLORS['bg_surface']};
            border: none;
            border-bottom: 1px solid {TERMINAL_COLORS['border']};
        }}

        QLineEdit {{
            background: {TERMINAL_COLORS['bg_base']};
            color: {TERMINAL_COLORS['phosphor']};
            border: 1px solid {TERMINAL_COLORS['border']};
            border-radius: 4px;
            padding: 10px 14px;
            font-family: {TERMINAL_FONT};
            font-size: 14px;
            selection-background-color: {TERMINAL_COLORS['phosphor_glow']};
            selection-color: {TERMINAL_COLORS['phosphor_bright']};
        }}
        QLineEdit:focus {{
            border-color: {TERMINAL_COLORS['phosphor']};
            background: {TERMINAL_COLORS['bg_void']};
        }}
        QLineEdit::placeholder {{
            color: {TERMINAL_COLORS['text_tertiary']};
        }}

        QPushButton {{
            background: {TERMINAL_COLORS['bg_hover']};
            color: {TERMINAL_COLORS['text_primary']};
            border: 1px solid {TERMINAL_COLORS['border']};
            border-radius: 4px;
            padding: 8px 12px;
            font-family: {TERMINAL_FONT_UI};
            font-size: 12px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background: {TERMINAL_COLORS['bg_active']};
            border-color: {TERMINAL_COLORS['phosphor_dim']};
            color: {TERMINAL_COLORS['phosphor']};
        }}
        QPushButton:pressed {{
            background: {TERMINAL_COLORS['phosphor_glow']};
        }}

        QPushButton#closeBtn {{
            background: transparent;
            color: {TERMINAL_COLORS['text_tertiary']};
            border: none;
            padding: 4px;
            font-size: 16px;
        }}
        QPushButton#closeBtn:hover {{
            color: {TERMINAL_COLORS['error']};
        }}

        QCheckBox {{
            color: {TERMINAL_COLORS['text_secondary']};
            font-family: {TERMINAL_FONT_UI};
            font-size: 12px;
            spacing: 6px;
        }}
        QCheckBox::indicator {{
            width: 14px;
            height: 14px;
            border-radius: 3px;
            border: 1px solid {TERMINAL_COLORS['text_tertiary']};
            background: transparent;
        }}
        QCheckBox::indicator:hover {{
            border-color: {TERMINAL_COLORS['phosphor_dim']};
        }}
        QCheckBox::indicator:checked {{
            background: {TERMINAL_COLORS['phosphor']};
            border-color: {TERMINAL_COLORS['phosphor']};
        }}

        QLabel {{
            color: {TERMINAL_COLORS['text_secondary']};
            font-family: {TERMINAL_FONT_UI};
            font-size: 12px;
        }}
        QLabel#matchCount {{
            color: {TERMINAL_COLORS['phosphor']};
            font-family: {TERMINAL_FONT};
            font-weight: 600;
            padding: 4px 10px;
            background: {TERMINAL_COLORS['phosphor_glow']};
            border: 1px solid {TERMINAL_COLORS['phosphor_dim']};
            border-radius: 4px;
        }}
    """


def get_context_menu_style():
    """Context menu - Terminal command palette"""
    return f"""
        QMenu {{
            background: {TERMINAL_COLORS['bg_elevated']};
            color: {TERMINAL_COLORS['text_primary']};
            border: 1px solid {TERMINAL_COLORS['border']};
            border-radius: 6px;
            padding: 6px;
            font-family: {TERMINAL_FONT_UI};
            font-size: 13px;
        }}
        QMenu::item {{
            padding: 8px 16px 8px 12px;
            border-radius: 4px;
            margin: 2px;
        }}
        QMenu::item:selected {{
            background: {TERMINAL_COLORS['phosphor_glow']};
            color: {TERMINAL_COLORS['phosphor']};
        }}
        QMenu::item:disabled {{
            color: {TERMINAL_COLORS['text_tertiary']};
        }}
        QMenu::separator {{
            height: 1px;
            background: {TERMINAL_COLORS['border']};
            margin: 6px 8px;
        }}
        QMenu::icon {{
            margin-left: 8px;
        }}
    """


def get_search_dialog_style():
    """Advanced search dialog"""
    return f"""
        QDialog {{
            background: {TERMINAL_COLORS['bg_elevated']};
            color: {TERMINAL_COLORS['text_primary']};
            font-family: {TERMINAL_FONT_UI};
        }}

        QLabel {{
            color: {TERMINAL_COLORS['text_primary']};
            font-size: 13px;
        }}

        QLineEdit {{
            background: {TERMINAL_COLORS['bg_base']};
            color: {TERMINAL_COLORS['phosphor']};
            border: 1px solid {TERMINAL_COLORS['border']};
            border-radius: 4px;
            padding: 10px 14px;
            font-family: {TERMINAL_FONT};
            font-size: 14px;
        }}
        QLineEdit:focus {{
            border-color: {TERMINAL_COLORS['phosphor']};
        }}

        QCheckBox, QRadioButton {{
            color: {TERMINAL_COLORS['text_primary']};
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
            border: 1px solid {TERMINAL_COLORS['text_tertiary']};
            background: transparent;
        }}
        QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
            background: {TERMINAL_COLORS['phosphor']};
            border-color: {TERMINAL_COLORS['phosphor']};
        }}

        QGroupBox {{
            color: {TERMINAL_COLORS['text_secondary']};
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            border: 1px solid {TERMINAL_COLORS['border']};
            border-radius: 6px;
            margin-top: 16px;
            padding: 16px 12px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
        }}

        QPushButton {{
            background: {TERMINAL_COLORS['bg_hover']};
            color: {TERMINAL_COLORS['text_primary']};
            border: 1px solid {TERMINAL_COLORS['border']};
            border-radius: 4px;
            padding: 10px 16px;
            font-size: 13px;
            font-weight: 500;
            min-width: 100px;
        }}
        QPushButton:hover {{
            background: {TERMINAL_COLORS['bg_active']};
            border-color: {TERMINAL_COLORS['phosphor_dim']};
        }}
        QPushButton#primaryBtn {{
            background: {TERMINAL_COLORS['phosphor_dim']};
            color: {TERMINAL_COLORS['bg_base']};
            border-color: {TERMINAL_COLORS['phosphor']};
        }}
        QPushButton#primaryBtn:hover {{
            background: {TERMINAL_COLORS['phosphor']};
        }}

        QFrame[frameShape="4"] {{
            background: {TERMINAL_COLORS['border']};
            max-height: 1px;
        }}
    """


def get_grep_filter_bar_style():
    """Grep filter bar"""
    return f"""
        QFrame {{
            background: {TERMINAL_COLORS['bg_surface']};
            border: none;
            border-bottom: 1px solid {TERMINAL_COLORS['border']};
            padding: 6px 12px;
        }}
    """


def get_grep_tag_style(is_primary=True):
    """Grep tags"""
    color = TERMINAL_COLORS['phosphor'] if is_primary else TERMINAL_COLORS['amber']
    bg = TERMINAL_COLORS['phosphor_glow'] if is_primary else TERMINAL_COLORS['amber_glow']
    return f"""
        QLabel {{
            color: {color};
            font-family: {TERMINAL_FONT};
            font-size: 11px;
            font-weight: 500;
            padding: 3px 8px;
            background: {bg};
            border: 1px solid {color};
            border-radius: 3px;
        }}
    """


def get_count_label_style():
    """Count labels"""
    return f"""
        QLabel {{
            color: {TERMINAL_COLORS['text_secondary']};
            font-family: {TERMINAL_FONT};
            font-size: 11px;
            padding: 2px 6px;
            background: {TERMINAL_COLORS['bg_hover']};
            border-radius: 3px;
        }}
    """


def get_add_grep_dialog_style():
    """Add grep dialog"""
    return f"""
        QDialog {{
            background: {TERMINAL_COLORS['bg_elevated']};
            color: {TERMINAL_COLORS['text_primary']};
        }}
        QRadioButton {{
            color: {TERMINAL_COLORS['text_primary']};
            font-family: {TERMINAL_FONT_UI};
            font-size: 13px;
            padding: 8px;
        }}
        QRadioButton::indicator {{
            width: 14px;
            height: 14px;
            border-radius: 7px;
            border: 1px solid {TERMINAL_COLORS['text_tertiary']};
        }}
        QRadioButton::indicator:checked {{
            background: {TERMINAL_COLORS['phosphor']};
            border-color: {TERMINAL_COLORS['phosphor']};
        }}
        QDialogButtonBox QPushButton {{
            background: {TERMINAL_COLORS['bg_hover']};
            color: {TERMINAL_COLORS['text_primary']};
            border: 1px solid {TERMINAL_COLORS['border']};
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 13px;
            min-width: 72px;
        }}
        QDialogButtonBox QPushButton:hover {{
            background: {TERMINAL_COLORS['bg_active']};
            border-color: {TERMINAL_COLORS['phosphor_dim']};
        }}
        QDialogButtonBox QPushButton:default {{
            background: {TERMINAL_COLORS['phosphor_dim']};
            color: {TERMINAL_COLORS['bg_base']};
            border-color: {TERMINAL_COLORS['phosphor']};
        }}
    """


def get_minimap_style():
    """Minimap - Code overview"""
    return f"""
        MiniMap {{
            background: {TERMINAL_COLORS['bg_void']};
            border: none;
            border-left: 1px solid {TERMINAL_COLORS['border']};
        }}
        MiniMap QPlainTextEdit {{
            background: {TERMINAL_COLORS['bg_void']};
            color: {TERMINAL_COLORS['text_tertiary']};
            border: none;
            padding: 0;
            margin: 0;
        }}
    """


def get_color_picker_dialog_style():
    """Color picker dialog"""
    return f"""
        QDialog {{
            background: {TERMINAL_COLORS['bg_elevated']};
            color: {TERMINAL_COLORS['text_primary']};
        }}
        QLabel {{
            color: {TERMINAL_COLORS['text_primary']};
            font-size: 13px;
        }}
        QPushButton.colorBtn {{
            border: 2px solid transparent;
            border-radius: 4px;
            min-width: 36px;
            min-height: 36px;
        }}
        QPushButton.colorBtn:hover {{
            border-color: {TERMINAL_COLORS['text_secondary']};
        }}
        QPushButton.colorBtn:checked {{
            border-color: {TERMINAL_COLORS['phosphor']};
            border-width: 3px;
        }}
        QDialogButtonBox QPushButton {{
            background: {TERMINAL_COLORS['bg_hover']};
            color: {TERMINAL_COLORS['text_primary']};
            border: 1px solid {TERMINAL_COLORS['border']};
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 13px;
            min-width: 72px;
        }}
        QDialogButtonBox QPushButton:hover {{
            border-color: {TERMINAL_COLORS['phosphor_dim']};
        }}
        QDialogButtonBox QPushButton:default {{
            background: {TERMINAL_COLORS['phosphor_dim']};
            color: {TERMINAL_COLORS['bg_base']};
        }}
    """


def get_highlight_panel_style():
    """Highlight management panel"""
    return f"""
        QDialog {{
            background: {TERMINAL_COLORS['bg_elevated']};
            color: {TERMINAL_COLORS['text_primary']};
        }}
        QLabel {{
            color: {TERMINAL_COLORS['text_primary']};
            font-size: 13px;
        }}
        QListWidget {{
            background: {TERMINAL_COLORS['bg_surface']};
            color: {TERMINAL_COLORS['text_primary']};
            border: 1px solid {TERMINAL_COLORS['border']};
            border-radius: 6px;
            padding: 4px;
            font-family: {TERMINAL_FONT};
            font-size: 13px;
            outline: none;
        }}
        QListWidget::item {{
            padding: 8px 12px;
            border-radius: 4px;
            margin: 2px;
        }}
        QListWidget::item:hover {{
            background: {TERMINAL_COLORS['bg_hover']};
        }}
        QListWidget::item:selected {{
            background: {TERMINAL_COLORS['phosphor_glow']};
            color: {TERMINAL_COLORS['phosphor']};
        }}
        QPushButton {{
            background: {TERMINAL_COLORS['bg_hover']};
            color: {TERMINAL_COLORS['text_primary']};
            border: 1px solid {TERMINAL_COLORS['border']};
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 13px;
            min-width: 80px;
        }}
        QPushButton:hover {{
            border-color: {TERMINAL_COLORS['phosphor_dim']};
            background: {TERMINAL_COLORS['bg_active']};
        }}
        QPushButton#primaryBtn {{
            background: {TERMINAL_COLORS['phosphor_dim']};
            color: {TERMINAL_COLORS['bg_base']};
            border-color: {TERMINAL_COLORS['phosphor']};
        }}
        QPushButton#primaryBtn:hover {{
            background: {TERMINAL_COLORS['phosphor']};
        }}
        QPushButton#dangerBtn {{
            background: {TERMINAL_COLORS['error']};
            color: #FFFFFF;
            border-color: {TERMINAL_COLORS['error']};
        }}
        QLineEdit {{
            background: {TERMINAL_COLORS['bg_base']};
            color: {TERMINAL_COLORS['phosphor']};
            border: 1px solid {TERMINAL_COLORS['border']};
            border-radius: 4px;
            padding: 8px 12px;
            font-family: {TERMINAL_FONT};
            font-size: 13px;
        }}
        QLineEdit:focus {{
            border-color: {TERMINAL_COLORS['phosphor']};
        }}
        QComboBox {{
            background: {TERMINAL_COLORS['bg_hover']};
            color: {TERMINAL_COLORS['text_primary']};
            border: 1px solid {TERMINAL_COLORS['border']};
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 13px;
            min-width: 120px;
        }}
        QComboBox:hover {{
            border-color: {TERMINAL_COLORS['phosphor_dim']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid {TERMINAL_COLORS['text_secondary']};
        }}
        QComboBox QAbstractItemView {{
            background: {TERMINAL_COLORS['bg_elevated']};
            color: {TERMINAL_COLORS['text_primary']};
            border: 1px solid {TERMINAL_COLORS['border']};
            border-radius: 4px;
            selection-background-color: {TERMINAL_COLORS['phosphor_glow']};
        }}
    """


# ============================================================
# COMPATIBILITY EXPORTS - For backward compatibility
# ============================================================
APPLE_COLORS = TERMINAL_COLORS  # Alias for old imports
APPLE_FONT_FAMILY = TERMINAL_FONT_UI
APPLE_MONO_FONT = TERMINAL_FONT

# Color exports
SYSTEM_BLUE = TERMINAL_COLORS["phosphor"]
SYSTEM_GREEN = TERMINAL_COLORS["success"]
SYSTEM_RED = TERMINAL_COLORS["error"]
BG_PRIMARY = TERMINAL_COLORS["bg_base"]
BG_SECONDARY = TERMINAL_COLORS["bg_surface"]
BG_TERTIARY = TERMINAL_COLORS["bg_elevated"]
LABEL_PRIMARY = TERMINAL_COLORS["text_primary"]
LABEL_SECONDARY = TERMINAL_COLORS["text_secondary"]