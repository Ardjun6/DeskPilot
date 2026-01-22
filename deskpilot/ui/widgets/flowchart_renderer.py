from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFontMetrics, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from ..theme_manager import Theme, ThemeManager


class FlowchartWidget(QWidget):
    def __init__(self, theme_manager: ThemeManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.theme_manager = theme_manager
        self._steps: List[str] = []
        self._theme = theme_manager.current
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        self.setMinimumHeight(220)

    def set_steps(self, steps: List[str]) -> None:
        self._steps = steps
        self.update()

    def _on_theme_changed(self, theme: Theme) -> None:
        self._theme = theme
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        theme = self._theme
        colors = theme.colors
        nodes = ["Start"] + self._steps + ["End"]
        if not nodes:
            return

        margin = 16
        width = self.width() - margin * 2
        height = self.height() - margin * 2
        width = max(width, 80)
        height = max(height, 80)

        count = len(nodes)
        gap = 18
        node_height = max(30, min(48, int((height - gap * max(count - 1, 0)) / count)))
        if node_height * count + gap * max(count - 1, 0) > height:
            gap = max(12, int((height - node_height * count) / max(count - 1, 1)))
        total = node_height * count + gap * max(count - 1, 0)
        start_y = margin + max(0, (height - total) // 2)
        node_width = min(width, 320)
        start_x = margin + (width - node_width) / 2

        pen = QPen()
        pen.setWidthF(1.4)
        pen.setColor(QColor(colors["flow_border"]))
        painter.setPen(pen)

        for idx, label in enumerate(nodes):
            y = start_y + idx * (node_height + gap)
            rect = QRectF(start_x, y, node_width, node_height)
            if idx == 0:
                painter.setBrush(QColor(colors["flow_start"]))
                painter.drawEllipse(rect)
            elif idx == count - 1:
                painter.setBrush(QColor(colors["flow_end"]))
                painter.drawEllipse(rect)
            else:
                painter.setBrush(QColor(colors["flow_step"]))
                painter.drawRoundedRect(rect, 12, 12)

            text = self._elide_text(label, rect.width() - 20)
            painter.setPen(QColor(colors["flow_text"]))
            painter.drawText(rect, Qt.AlignCenter, text)
            painter.setPen(pen)

            if idx < count - 1:
                start = QPointF(rect.center().x(), rect.bottom())
                end = QPointF(rect.center().x(), rect.bottom() + gap)
                self._draw_arrow(painter, start, end, colors["flow_arrow"])

    def _draw_arrow(self, painter: QPainter, start: QPointF, end: QPointF, color: str) -> None:
        arrow_pen = QPen(QColor(color))
        arrow_pen.setWidthF(1.4)
        painter.setPen(arrow_pen)
        path = QPainterPath(start)
        path.lineTo(end)
        painter.drawPath(path)

        arrow_size = 6
        angle = -90
        painter.save()
        painter.translate(end)
        painter.rotate(angle)
        painter.drawLine(0, 0, -arrow_size, -arrow_size)
        painter.drawLine(0, 0, arrow_size, -arrow_size)
        painter.restore()

    def _elide_text(self, text: str, width: float) -> str:
        metrics = QFontMetrics(self.font())
        return metrics.elidedText(text, Qt.ElideRight, int(width))
