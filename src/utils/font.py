# Font rendering helpers
# Renders glyphs to transparent images so that font based text can be stored
# in the same image based formats that the compiler and exporters understand.

import hashlib
import re

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QImage, QPainter, QPixmap

DEFAULT_GLYPHS = "0123456789"
DEFAULT_FONT_SIZE = 32
DEFAULT_FONT_COLOR = "#FFFFFF"


def sanitize_filename(name: str) -> str:
    """Return a filesystem safe version of a widget name."""
    name = str(name or "text")
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name)
    name = name.strip("._")
    return name[:80] or "text"


def resource_stem(name: str) -> str:
    """Stable, collision resistant filename stem for generated resources."""
    safe = sanitize_filename(name)
    digest = hashlib.md5(str(name or "text").encode("utf8")).hexdigest()[:8]
    return f"{safe}_{digest}"


def parse_color(value) -> QColor:
    color = QColor(str(value) if value else DEFAULT_FONT_COLOR)
    if not color.isValid():
        color = QColor(DEFAULT_FONT_COLOR)
    return color


def render_glyphs(family: str, pixel_size, color, glyphs: str = DEFAULT_GLYPHS) -> list[QPixmap]:
    """
    Render every glyph in ``glyphs`` into its own pixmap.

    All returned pixmaps have exactly the same dimensions. The compiler requires
    every image in a number bitmap list to have the same width and height.
    """
    try:
        size = int(pixel_size)
    except (TypeError, ValueError):
        size = DEFAULT_FONT_SIZE
    size = max(1, min(size, 2048))

    font = QFont(str(family)) if family else QFont()
    font.setPixelSize(size)

    metrics = QFontMetrics(font)
    advance_widths = [max(1, metrics.horizontalAdvance(glyph)) for glyph in glyphs]
    padding = 2
    cell_width = max(advance_widths) + padding
    cell_height = max(1, metrics.height()) + padding
    ascent = metrics.ascent()

    pen = parse_color(color)
    pixmaps = []

    for glyph, advance in zip(glyphs, advance_widths):
        image = QImage(cell_width, cell_height, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        painter.setFont(font)
        painter.setPen(pen)

        # Center each glyph inside the common cell so spacing stays uniform.
        x = (cell_width - advance) / 2
        y = (padding / 2) + ascent
        painter.drawText(QPointF(x, y), glyph)
        painter.end()

        pixmaps.append(QPixmap.fromImage(image))

    return pixmaps
