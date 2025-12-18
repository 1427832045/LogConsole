"""
Minimap Widget - VSCode-style code minimap for log viewer
High-performance implementation with viewport slider and scroll sync
"""
from PyQt5.QtWidgets import (
    QWidget, QPlainTextEdit, QVBoxLayout, QFrame,
    QGraphicsOpacityEffect, QApplication
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QPoint
)
from PyQt5.QtGui import (
    QFont, QPainter, QColor, QBrush, QPen, QTextDocument,
    QTextCursor, QTextCharFormat, QSyntaxHighlighter
)
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QTextEdit

# ============================================================
# MINIMAP CONSTANTS
# ============================================================
MINIMAP_WIDTH = 120
MINIMAP_FONT_SIZE = 1  # Very small font for overview
MINIMAP_BG_COLOR = "#141416"
MINIMAP_TEXT_COLOR = "#6E6E73"
SLIDER_COLOR = "rgba(245, 166, 35, 0.25)"
SLIDER_BORDER_COLOR = "rgba(245, 166, 35, 0.6)"
HOVER_OPACITY_MIN = 0.5
HOVER_OPACITY_MAX = 1.0
ANIMATION_DURATION = 200


class SliderOverlay(QWidget):
    """Viewport indicator overlay - shows visible area in minimap"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setCursor(Qt.OpenHandCursor)
        self._dragging = False
        self._drag_start_y = 0
        self._drag_start_value = 0

    def paintEvent(self, event):
        """Draw semi-transparent slider rectangle"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fill with accent color
        painter.fillRect(
            self.rect(),
            QBrush(QColor(245, 166, 35, 64))  # #F5A623 @ 25%
        )

        # Draw border
        pen = QPen(QColor(245, 166, 35, 153))  # #F5A623 @ 60%
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

    def mousePressEvent(self, event):
        """Start drag operation"""
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_start_y = event.globalY()
            minimap = self.parent()
            if hasattr(minimap, '_editor') and minimap._editor:
                self._drag_start_value = minimap._editor.verticalScrollBar().value()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        """Handle drag scrolling"""
        if self._dragging:
            delta_y = event.globalY() - self._drag_start_y
            minimap = self.parent()
            if hasattr(minimap, '_scroll_by_minimap_delta'):
                minimap._scroll_by_minimap_delta(delta_y, self._drag_start_value)

    def mouseReleaseEvent(self, event):
        """End drag operation"""
        if event.button() == Qt.LeftButton:
            self._dragging = False
            self.setCursor(Qt.OpenHandCursor)


class MinimapHighlighter(QSyntaxHighlighter):
    """Simplified highlighter for minimap - only color bands, no details"""

    def __init__(self, parent: QTextDocument):
        super().__init__(parent)
        self._rules = []

    def set_rules(self, rules: list):
        """Set highlight rules from template"""
        import re
        self._rules = []
        for rule in rules:
            try:
                pattern = re.compile(rule['pattern']) if rule.get('is_regex') else re.compile(re.escape(rule['pattern']))
                fmt = QTextCharFormat()
                if rule.get('foreground'):
                    fmt.setForeground(QColor(rule['foreground']))
                if rule.get('background'):
                    fmt.setBackground(QColor(rule['background']))
                self._rules.append((pattern, fmt))
            except:
                pass

    def highlightBlock(self, text: str):
        """Apply simplified highlighting"""
        for pattern, fmt in self._rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)


class MiniMap(QWidget):
    """
    VSCode-style minimap widget for log viewer.

    Features:
    - Scaled-down view of entire document
    - Viewport slider showing visible area
    - Click/drag to navigate
    - Smooth hover animation
    - Scroll synchronization
    """

    # Signals
    scroll_requested = pyqtSignal(int)  # Request scroll to line

    def __init__(self, parent=None):
        super().__init__(parent)
        self._editor: Optional['QTextEdit'] = None
        self._document_lines = []
        self._lines_count = 0
        self._visible_start = 0
        self._visible_end = 0
        self._sync_in_progress = False
        self._highlighter = None

        self._init_ui()
        self._setup_animation()

    def _init_ui(self):
        """Initialize minimap UI"""
        self.setFixedWidth(MINIMAP_WIDTH)
        self.setMinimumHeight(100)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Minimap text view - read-only, tiny font
        self._text_view = QPlainTextEdit()
        self._text_view.setReadOnly(True)
        self._text_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._text_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._text_view.setLineWrapMode(QPlainTextEdit.NoWrap)
        self._text_view.setTextInteractionFlags(Qt.NoTextInteraction)
        self._text_view.viewport().setCursor(Qt.PointingHandCursor)

        # Tiny font for overview effect
        font = QFont("Menlo", MINIMAP_FONT_SIZE)
        font.setStyleHint(QFont.Monospace)
        self._text_view.setFont(font)

        # Apply dark style
        self._text_view.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {MINIMAP_BG_COLOR};
                color: {MINIMAP_TEXT_COLOR};
                border: none;
                border-left: 1px solid rgba(255, 255, 255, 0.06);
                padding: 0;
                margin: 0;
            }}
        """)

        layout.addWidget(self._text_view)

        # Viewport slider overlay
        self._slider = SliderOverlay(self)
        self._slider.setGeometry(0, 0, MINIMAP_WIDTH, 50)
        self._slider.raise_()

        # Setup highlighter
        self._highlighter = MinimapHighlighter(self._text_view.document())

        # Mouse events for click-to-scroll
        self._text_view.viewport().installEventFilter(self)

    def _setup_animation(self):
        """Setup hover opacity animation"""
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(HOVER_OPACITY_MIN)

        self._animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._animation.setDuration(ANIMATION_DURATION)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

    def attach_editor(self, editor: 'QTextEdit'):
        """Attach minimap to an editor widget"""
        if self._editor:
            self._detach_editor()

        self._editor = editor

        # Connect scroll signals
        scrollbar = editor.verticalScrollBar()
        scrollbar.valueChanged.connect(self._on_editor_scroll)

        # Connect document changes
        doc = editor.document()
        doc.contentsChanged.connect(self._on_document_changed)

        # Initial sync
        self._sync_content()
        self._update_slider()

    def _detach_editor(self):
        """Detach from current editor"""
        if self._editor:
            try:
                self._editor.verticalScrollBar().valueChanged.disconnect(self._on_editor_scroll)
                self._editor.document().contentsChanged.disconnect(self._on_document_changed)
            except:
                pass
        self._editor = None

    def _sync_content(self):
        """Sync minimap content with editor"""
        if not self._editor:
            return

        # Get document text
        doc = self._editor.document()
        text = doc.toPlainText()

        # Strip line number prefix for cleaner minimap
        lines = []
        for line in text.split('\n'):
            if ' │ ' in line:
                lines.append(line.split(' │ ', 1)[1] if ' │ ' in line else line)
            else:
                lines.append(line)

        self._document_lines = lines
        self._lines_count = len(lines)

        # Update minimap text (limit for performance)
        max_lines = 10000  # Limit for very large files
        display_lines = lines[:max_lines]
        self._text_view.setPlainText('\n'.join(display_lines))

    def _on_document_changed(self):
        """Handle document content changes"""
        QTimer.singleShot(100, self._sync_content)
        QTimer.singleShot(150, self._update_slider)

    def _on_editor_scroll(self, value):
        """Handle editor scroll - update slider position"""
        if self._sync_in_progress:
            return
        self._update_slider()

    def _update_slider(self):
        """Update slider position and size based on editor viewport"""
        if not self._editor or self._lines_count == 0:
            return

        scrollbar = self._editor.verticalScrollBar()
        max_scroll = scrollbar.maximum()

        # Calculate visible range
        if max_scroll == 0:
            # All content visible
            self._slider.setGeometry(0, 0, MINIMAP_WIDTH, self.height())
            return

        current_value = scrollbar.value()
        viewport_height = self._editor.viewport().height()

        # Estimate visible lines
        doc = self._editor.document()
        block_count = doc.blockCount()
        if block_count == 0:
            return

        # Calculate line height
        first_block = doc.firstBlock()
        line_height = self._editor.fontMetrics().lineSpacing()
        if line_height <= 0:
            line_height = 18

        visible_lines = viewport_height // line_height
        first_visible_line = int((current_value / max(1, max_scroll)) * max(1, block_count - visible_lines))

        # Map to minimap coordinates
        minimap_height = self.height()
        minimap_line_height = minimap_height / max(1, self._lines_count)

        slider_top = int(first_visible_line * minimap_line_height)
        slider_height = max(20, int(visible_lines * minimap_line_height))

        # Clamp values
        slider_top = max(0, min(slider_top, minimap_height - slider_height))

        self._slider.setGeometry(0, slider_top, MINIMAP_WIDTH, slider_height)

    def _scroll_by_minimap_delta(self, delta_y: int, start_value: int):
        """Scroll editor based on minimap drag delta"""
        if not self._editor or self._lines_count == 0:
            return

        self._sync_in_progress = True

        scrollbar = self._editor.verticalScrollBar()
        max_scroll = scrollbar.maximum()

        # Convert minimap delta to scroll delta
        minimap_height = self.height()
        scroll_ratio = max_scroll / max(1, minimap_height)
        new_value = int(start_value + delta_y * scroll_ratio)

        scrollbar.setValue(max(0, min(new_value, max_scroll)))

        self._sync_in_progress = False

    def _scroll_to_minimap_position(self, y: int):
        """Scroll editor to position corresponding to minimap y coordinate"""
        if not self._editor or self._lines_count == 0:
            return

        self._sync_in_progress = True

        minimap_height = self.height()
        scrollbar = self._editor.verticalScrollBar()
        max_scroll = scrollbar.maximum()

        # Calculate target scroll value
        ratio = y / max(1, minimap_height)
        target_value = int(ratio * max_scroll)

        scrollbar.setValue(max(0, min(target_value, max_scroll)))

        self._sync_in_progress = False
        self._update_slider()

    def eventFilter(self, obj, event):
        """Handle click events on minimap"""
        from PyQt5.QtCore import QEvent

        if obj == self._text_view.viewport():
            if event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self._scroll_to_minimap_position(event.y())
                    return True
            elif event.type() == QEvent.MouseButtonDblClick:
                # Double-click: scroll to exact line
                self._scroll_to_minimap_position(event.y())
                return True

        return super().eventFilter(obj, event)

    def enterEvent(self, event):
        """Mouse enter - fade in"""
        self._animation.stop()
        self._animation.setStartValue(self._opacity_effect.opacity())
        self._animation.setEndValue(HOVER_OPACITY_MAX)
        self._animation.start()

    def leaveEvent(self, event):
        """Mouse leave - fade out"""
        self._animation.stop()
        self._animation.setStartValue(self._opacity_effect.opacity())
        self._animation.setEndValue(HOVER_OPACITY_MIN)
        self._animation.start()

    def resizeEvent(self, event):
        """Handle resize - update slider"""
        super().resizeEvent(event)
        self._update_slider()

    def set_highlight_rules(self, rules: list):
        """Set syntax highlight rules"""
        if self._highlighter:
            self._highlighter.set_rules(rules)
            self._highlighter.rehighlight()

    def refresh(self):
        """Force refresh minimap content and slider"""
        self._sync_content()
        self._update_slider()


class MinimapContainer(QWidget):
    """
    Container widget that combines editor + minimap side by side.
    Use this to easily add minimap to any QTextEdit.
    """

    def __init__(self, editor: 'QTextEdit', parent=None):
        super().__init__(parent)
        self._editor = editor
        self._minimap = MiniMap()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create horizontal container
        from PyQt5.QtWidgets import QHBoxLayout, QWidget
        h_container = QWidget()
        h_layout = QHBoxLayout(h_container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)

        # Reparent editor if needed
        if editor.parent():
            editor.setParent(h_container)

        h_layout.addWidget(editor)
        h_layout.addWidget(self._minimap)

        layout.addWidget(h_container)

        # Attach minimap to editor
        self._minimap.attach_editor(editor)

    @property
    def editor(self):
        return self._editor

    @property
    def minimap(self):
        return self._minimap
