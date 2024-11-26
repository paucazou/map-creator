import sys
import math
from dataclasses import dataclass, field
from typing import List, Tuple

from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView,
                           QGraphicsScene, QVBoxLayout, QWidget, QToolBar,
                           QColorDialog)
from PyQt6.QtGui import QPainter, QPen, QColor, QAction
from PyQt6.QtCore import Qt, QPointF, QRectF

@dataclass
class VectorLine:
    """Represents a line as a vector of two points"""
    start: QPointF
    end: QPointF
    color: QColor
    width: float = 2.0

class DrawingCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        
        # Create scene with a white background
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(Qt.GlobalColor.white)
        self.setScene(self.scene)
        
        # Enable antialiasing for smoother drawing
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set scene rect to a large virtual canvas
        #self.scene.setSceneRect(-10000, -10000, 20000, 20000) # PROBABLY USELESS
        
        # Setup viewport optimizations
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate)
        self.setOptimizationFlags(
            QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing |
            QGraphicsView.OptimizationFlag.DontSavePainterState
        )
        
        # Drawing state
        self.last_point = None
        self.drawing = False
        self.preview_line = None
        
        # Current drawing settings
        self.current_color = Qt.GlobalColor.black
        self.current_pen_width = 2
        
        # Vector storage
        self.vector_lines: List[VectorLine] = []
        
        # Set initial view to center
        self.centerOn(0, 0)

    def clear_preview(self):
        """Clear any existing preview line"""
        if self.preview_line:
            self.scene.removeItem(self.preview_line)
            self.preview_line = None

    def is_line_visible(self, line: VectorLine, viewport_rect: QRectF) -> bool:
        """
        Check if the line is within or intersects the visible viewport

        Uses a simple bounding box check with a small padding for line width
        """
        # Create a bounding rect for the line with padding
        padding = line.width  # Add some padding for line width
        line_rect = QRectF(
            min(line.start.x(), line.end.x()) - padding,
            min(line.start.y(), line.end.y()) - padding,
            abs(line.end.x() - line.start.x()) + 2 * padding,
            abs(line.end.y() - line.start.y()) + 2 * padding
        )

        # Check if line rect intersects with viewport
        return line_rect.intersects(viewport_rect)

    def render_lines(self):
        """Render only lines within the visible viewport"""
        # Clear the scene first
        self.scene.clear()

        # Get the current viewport rect in scene coordinates
        viewport_rect = self.mapToScene(self.viewport().rect()).boundingRect()

        # Re-add only visible vector lines
        for line in self.vector_lines:
            if self.is_line_visible(line, viewport_rect):
                pen = QPen(line.color, line.width, Qt.PenStyle.SolidLine)
                self.scene.addLine(
                    line.start.x(), line.start.y(),
                    line.end.x(), line.end.y(),
                    pen
                )

    def render_lines_deprecated(self):
        """Render all stored vector lines"""
        # Clear the scene first
        self.scene.clear()
        
        # Re-add all vector lines
        for line in self.vector_lines:
            pen = QPen(line.color, line.width, Qt.PenStyle.SolidLine)
            self.scene.addLine(
                line.start.x(), line.start.y(),
                line.end.x(), line.end.y(),
                pen
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = self.mapToScene(event.pos())
            self.clear_preview()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.last_point is not None:
            current_point = self.mapToScene(event.pos())
            
            # Create vector line and store it
            vector_line = VectorLine(
                start=self.last_point, 
                end=current_point, 
                color=QColor(self.current_color),
                width=self.current_pen_width
            )
            self.vector_lines.append(vector_line)
            
            # Clear preview and render all lines
            self.clear_preview()
            self.render_lines()
            
            self.drawing = False
            self.last_point = None

    def mouseMoveEvent(self, event):
        if self.drawing and self.last_point is not None:
            # Temporary line preview
            current_point = self.mapToScene(event.pos())
            
            # Clear previous preview
            self.clear_preview()
            
            # Draw preview line
            preview_pen = QPen(self.current_color, self.current_pen_width, Qt.PenStyle.SolidLine)
            self.preview_line = self.scene.addLine(
                self.last_point.x(),
                self.last_point.y(),
                current_point.x(),
                current_point.y(),
                preview_pen
            )

    def wheelEvent(self, event):
        """Handle zooming"""
        zoom_factor = 1.1
        
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1/zoom_factor, 1/zoom_factor)
        
        # Re-render lines after zooming
        self.render_lines()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.render_lines()

class DrawingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vector Drawing App")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create and add canvas
        self.canvas = DrawingCanvas()
        layout.addWidget(self.canvas)

        # Create toolbar
        self.init_toolbar()

    def init_toolbar(self):
        """Initialize toolbar with color and pen width controls"""
        toolbar = self.addToolBar("Tools")
        
        # Color selection action
        color_action = QAction("Color", self)
        color_action.triggered.connect(self.choose_color)
        toolbar.addAction(color_action)

    def choose_color(self):
        """Open color picker dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.current_color = color

def main():
    app = QApplication(sys.argv)
    window = DrawingWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
