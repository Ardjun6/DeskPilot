from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFontMetrics, QPainter, QPainterPath, QPen, QBrush, QLinearGradient
from PySide6.QtWidgets import QWidget

from ..theme_manager import Theme, ThemeManager


class FlowchartWidget(QWidget):
    """Visual flowchart renderer for action/macro steps."""

    def __init__(self, theme_manager: ThemeManager, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.theme_manager = theme_manager
        self._steps: List[str] = []
        self._theme = theme_manager.current
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        # Will be adjusted based on content
        self.setMinimumWidth(200)
        self._node_height = 44
        self._gap = 24
        self._margin = 20

    def set_steps(self, steps: List[str]) -> None:
        self._steps = steps
        self._update_size()
        self.update()

    def _update_size(self) -> None:
        """Calculate required height based on number of steps."""
        count = len(self._steps) + 2  # +2 for Start and End
        total_height = (
            self._margin * 2 +
            count * self._node_height +
            (count - 1) * self._gap
        )
        self.setMinimumHeight(max(200, total_height))
        self.setFixedHeight(max(200, total_height))

    def _on_theme_changed(self, theme: Theme) -> None:
        self._theme = theme
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        theme = self._theme
        colors = theme.colors
        nodes = ["▶ Start"] + self._steps + ["⬛ End"]
        if not nodes:
            return

        margin = self._margin
        node_height = self._node_height
        gap = self._gap
        
        width = self.width() - margin * 2
        width = max(width, 100)

        count = len(nodes)
        start_y = margin
        node_width = min(width, 280)
        start_x = margin + (width - node_width) / 2

        # Draw connecting lines first (behind nodes)
        for idx in range(count - 1):
            y = start_y + idx * (node_height + gap)
            rect = QRectF(start_x, y, node_width, node_height)
            start = QPointF(rect.center().x(), rect.bottom())
            end = QPointF(rect.center().x(), rect.bottom() + gap)
            self._draw_arrow(painter, start, end, colors["flow_arrow"])

        # Draw nodes
        for idx, label in enumerate(nodes):
            y = start_y + idx * (node_height + gap)
            rect = QRectF(start_x, y, node_width, node_height)
            
            # Node shadow
            shadow_rect = rect.adjusted(2, 2, 2, 2)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 0, 0, 20))
            if idx == 0 or idx == count - 1:
                painter.drawEllipse(shadow_rect)
            else:
                painter.drawRoundedRect(shadow_rect, 14, 14)

            # Node border
            pen = QPen(QColor(colors["flow_border"]))
            pen.setWidthF(1.5)
            painter.setPen(pen)

            # Node fill with gradient
            if idx == 0:
                gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
                gradient.setColorAt(0, QColor(colors["flow_start"]))
                gradient.setColorAt(1, self._darken(colors["flow_start"], 10))
                painter.setBrush(QBrush(gradient))
                painter.drawEllipse(rect)
            elif idx == count - 1:
                gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
                gradient.setColorAt(0, QColor(colors["flow_end"]))
                gradient.setColorAt(1, self._darken(colors["flow_end"], 10))
                painter.setBrush(QBrush(gradient))
                painter.drawEllipse(rect)
            else:
                gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
                gradient.setColorAt(0, QColor(colors["flow_step"]))
                gradient.setColorAt(1, self._darken(colors["flow_step"], 8))
                painter.setBrush(QBrush(gradient))
                painter.drawRoundedRect(rect, 14, 14)

            # Node text
            text = self._elide_text(label, rect.width() - 24)
            painter.setPen(QColor(colors["flow_text"]))
            font = painter.font()
            font.setPointSize(10)
            if idx == 0 or idx == count - 1:
                font.setBold(True)
            else:
                font.setBold(False)
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignCenter, text)

    def _draw_arrow(self, painter: QPainter, start: QPointF, end: QPointF, color: str) -> None:
        arrow_pen = QPen(QColor(color))
        arrow_pen.setWidthF(2)
        painter.setPen(arrow_pen)
        
        # Draw line
        path = QPainterPath(start)
        path.lineTo(end)
        painter.drawPath(path)

        # Draw arrowhead
        arrow_size = 7
        painter.save()
        painter.translate(end)
        painter.rotate(-90)
        
        arrow_path = QPainterPath()
        arrow_path.moveTo(0, 0)
        arrow_path.lineTo(-arrow_size, -arrow_size)
        arrow_path.moveTo(0, 0)
        arrow_path.lineTo(arrow_size, -arrow_size)
        painter.drawPath(arrow_path)
        
        painter.restore()

    def _elide_text(self, text: str, width: float) -> str:
        metrics = QFontMetrics(self.font())
        return metrics.elidedText(text, Qt.ElideRight, int(width))

    def _darken(self, hex_color: str, amount: int) -> QColor:
        color = QColor(hex_color)
        return color.darker(100 + amount)
