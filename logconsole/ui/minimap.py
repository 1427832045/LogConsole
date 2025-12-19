"""
Minimap Widget - VSCode-style code minimap for log viewer
Uses custom QPainter rendering with colored rectangles for each character
"""
from PyQt5.QtWidgets import QWidget, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QPainter, QColor, QImage, QFont
from typing import Optional, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QTextEdit

# ============================================================
# MINIMAP CONSTANTS
# ============================================================
MINIMAP_WIDTH = 100
CHAR_WIDTH = 2       # Each character = 2px wide
CHAR_HEIGHT = 3      # Each line = 3px tall
LINE_SPACING = 1     # Gap between lines
MAX_CHARS_PER_LINE = 40  # Max characters to render per line
SLIDER_COLOR = QColor(245, 166, 35, 50)
SLIDER_BORDER = QColor(245, 166, 35, 120)
BG_COLOR = QColor(20, 20, 22)
DEFAULT_TEXT_COLOR = QColor(110, 110, 115)


class MiniMap(QWidget):
    """
    VSCode-style minimap using custom painting.
    Each character is rendered as a small colored rectangle.
    """
    scroll_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._editor: Optional['QTextEdit'] = None
        self._lines: List[str] = []
        self._line_colors: List[List[Tuple[int, int, QColor]]] = []  # [(start, end, color), ...]
        self._cache_image: Optional[QImage] = None
        self._cache_valid = False
        self._slider_top = 0
        self._slider_height = 50
        self._dragging = False
        self._drag_start_y = 0
        self._drag_start_scroll = 0
        self._sync_in_progress = False

        self._init_ui()
        self._setup_animation()

    def _init_ui(self):
        self.setFixedWidth(MINIMAP_WIDTH)
        self.setMinimumHeight(100)
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)

    def _setup_animation(self):
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(0.6)
        self._animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

    def attach_editor(self, editor: 'QTextEdit'):
        if self._editor:
            self._detach_editor()
        self._editor = editor
        scrollbar = editor.verticalScrollBar()
        scrollbar.valueChanged.connect(self._on_editor_scroll)
        editor.document().contentsChanged.connect(self._on_document_changed)
        self._sync_content()
        self._update_slider()

    def _detach_editor(self):
        if self._editor:
            try:
                self._editor.verticalScrollBar().valueChanged.disconnect(self._on_editor_scroll)
                self._editor.document().contentsChanged.disconnect(self._on_document_changed)
            except:
                pass
        self._editor = None

    def _sync_content(self):
        if not self._editor:
            return
        text = self._editor.document().toPlainText()
        raw_lines = text.split('\n')

        # Strip line numbers if present
        self._lines = []
        for line in raw_lines:
            if ' │ ' in line:
                self._lines.append(line.split(' │ ', 1)[1])
            else:
                self._lines.append(line)

        self._extract_colors()
        self._cache_valid = False
        self.update()

    def _extract_colors(self):
        """Extract syntax highlighting colors from editor document"""
        self._line_colors = []
        if not self._editor:
            return

        doc = self._editor.document()
        block = doc.begin()

        while block.isValid():
            line_formats = []
            it = block.begin()

            while not it.atEnd():
                fragment = it.fragment()
                if fragment.isValid():
                    fmt = fragment.charFormat()
                    fg = fmt.foreground().color()
                    if fg.isValid() and fg.alpha() > 0:
                        start = fragment.position() - block.position()
                        length = fragment.length()
                        line_formats.append((start, start + length, fg))
                it += 1

            self._line_colors.append(line_formats)
            block = block.next()

    def _on_document_changed(self):
        QTimer.singleShot(100, self._sync_content)
        QTimer.singleShot(150, self._update_slider)

    def _on_editor_scroll(self, value):
        if self._sync_in_progress:
            return
        self._update_slider()

    def _update_slider(self):
        if not self._editor or not self._lines:
            return

        scrollbar = self._editor.verticalScrollBar()
        max_scroll = scrollbar.maximum()

        if max_scroll == 0:
            self._slider_top = 0
            self._slider_height = self.height()
        else:
            viewport_h = self._editor.viewport().height()
            line_height = max(1, self._editor.fontMetrics().lineSpacing())
            visible_lines = viewport_h // line_height
            total_lines = len(self._lines)

            minimap_content_height = total_lines * (CHAR_HEIGHT + LINE_SPACING)
            scale = min(1.0, self.height() / max(1, minimap_content_height))

            ratio = scrollbar.value() / max(1, max_scroll)
            visible_ratio = visible_lines / max(1, total_lines)

            self._slider_height = max(20, int(self.height() * visible_ratio))
            max_slider_top = self.height() - self._slider_height
            self._slider_top = int(ratio * max_slider_top)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # Background
        painter.fillRect(self.rect(), BG_COLOR)

        # Left border
        painter.setPen(QColor(255, 255, 255, 15))
        painter.drawLine(0, 0, 0, self.height())

        if not self._lines:
            return

        # Calculate scale to fit content
        total_lines = len(self._lines)
        line_unit = CHAR_HEIGHT + LINE_SPACING
        content_height = total_lines * line_unit

        if content_height > self.height():
            scale = self.height() / content_height
        else:
            scale = 1.0

        scaled_line_height = max(1, int(line_unit * scale))
        scaled_char_height = max(1, int(CHAR_HEIGHT * scale))

        # Draw lines as colored blocks
        y = 0
        for i, line in enumerate(self._lines):
            if y > self.height():
                break

            x = 4  # Left padding
            line_colors = self._line_colors[i] if i < len(self._line_colors) else []

            # Render each character as a small rectangle
            for j, char in enumerate(line[:MAX_CHARS_PER_LINE]):
                if char.isspace():
                    x += CHAR_WIDTH
                    continue

                # Find color for this position
                color = DEFAULT_TEXT_COLOR
                for start, end, fmt_color in line_colors:
                    if start <= j < end:
                        color = fmt_color
                        break

                painter.fillRect(x, y, CHAR_WIDTH, scaled_char_height, color)
                x += CHAR_WIDTH

            y += scaled_line_height

        # Draw viewport slider
        slider_rect = QRect(0, self._slider_top, self.width(), self._slider_height)
        painter.fillRect(slider_rect, SLIDER_COLOR)
        painter.setPen(SLIDER_BORDER)
        painter.drawRect(slider_rect.adjusted(0, 0, -1, -1))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._slider_top <= event.y() <= self._slider_top + self._slider_height:
                self._dragging = True
                self._drag_start_y = event.y()
                self._drag_start_scroll = self._editor.verticalScrollBar().value() if self._editor else 0
                self.setCursor(Qt.ClosedHandCursor)
            else:
                self._scroll_to_y(event.y())

    def mouseMoveEvent(self, event):
        if self._dragging and self._editor:
            delta = event.y() - self._drag_start_y
            max_slider_top = self.height() - self._slider_height
            if max_slider_top > 0:
                scroll_ratio = delta / max_slider_top
                max_scroll = self._editor.verticalScrollBar().maximum()
                new_scroll = int(self._drag_start_scroll + scroll_ratio * max_scroll)
                self._sync_in_progress = True
                self._editor.verticalScrollBar().setValue(max(0, min(new_scroll, max_scroll)))
                self._sync_in_progress = False
                self._update_slider()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = False
            self.setCursor(Qt.PointingHandCursor)

    def _scroll_to_y(self, y: int):
        if not self._editor:
            return
        self._sync_in_progress = True
        max_scroll = self._editor.verticalScrollBar().maximum()
        ratio = y / max(1, self.height())
        self._editor.verticalScrollBar().setValue(int(ratio * max_scroll))
        self._sync_in_progress = False
        self._update_slider()

    def enterEvent(self, event):
        self._animation.stop()
        self._animation.setStartValue(self._opacity_effect.opacity())
        self._animation.setEndValue(1.0)
        self._animation.start()

    def leaveEvent(self, event):
        self._animation.stop()
        self._animation.setStartValue(self._opacity_effect.opacity())
        self._animation.setEndValue(0.6)
        self._animation.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._cache_valid = False
        self._update_slider()

    def set_highlight_rules(self, rules: list):
        """Compatibility - colors are extracted from editor document"""
        pass

    def refresh(self):
        self._sync_content()
        self._update_slider()


class MinimapContainer(QWidget):
    """Container for editor + minimap side by side"""

    def __init__(self, editor: 'QTextEdit', parent=None):
        super().__init__(parent)
        from PyQt5.QtWidgets import QHBoxLayout

        self._editor = editor
        self._minimap = MiniMap()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if editor.parent():
            editor.setParent(self)

        layout.addWidget(editor, 1)
        layout.addWidget(self._minimap)
        self._minimap.attach_editor(editor)

    @property
    def editor(self):
        return self._editor

    @property
    def minimap(self):
        return self._minimap
