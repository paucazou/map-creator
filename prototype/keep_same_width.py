import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QGraphicsScene, 
                             QVBoxLayout, QWidget, QGraphicsPathItem)
from PyQt6.QtGui import QPen, QColor, QPainterPath, QPainter
from PyQt6.QtCore import Qt, QPointF

class VectorLine:
    def __init__(self, points, width=20, color=Qt.GlobalColor.black):
        """
        Create a vector line with consistent properties
        
        :param points: List of QPointF points defining the line
        :param width: Line width in pixels
        :param color: Line color
        """
        self.points = points
        self.width = width
        self.color = color
    
    def to_path(self, scale=1.0):
        """
        Convert line points to a QPainterPath
        
        :param scale: Current zoom scale to maintain consistent line width
        :return: QPainterPath representing the line
        """
        path = QPainterPath()
        if not self.points:
            return path
        
        # Adjust line width based on scale
        adjusted_width = self.width / scale
        
        # Start the path
        path.moveTo(self.points[0])
        
        # Add lines to subsequent points
        for point in self.points[1:]:
            path.lineTo(point)
        
        return path

class DrawingView(QGraphicsView):
    def __init__(self):
        super().__init__()
        
        # Scene setup
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Drawing properties
        self.drawing = False
        self.current_line_points = []
        self.vector_lines = []
        self.line_width = 20  # Fixed line width in pixels
        
        # View settings
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        # Enable zooming
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            # Map screen coordinates to scene coordinates
            scene_pos = self.mapToScene(event.pos())
            self.current_line_points = [scene_pos]

    def mouseMoveEvent(self, event):
        if self.drawing:
            # Map screen coordinates to scene coordinates
            scene_pos = self.mapToScene(event.pos())
            
            # Add point to current line
            self.current_line_points.append(scene_pos)
            
            # Clear previous preview
            self.scene.clear()
            
            # Redraw all existing vector lines
            current_zoom = self.transform().m11()
            for vector_line in self.vector_lines:
                path_item = QGraphicsPathItem(vector_line.to_path(current_zoom))
                pen = QPen(vector_line.color, vector_line.width / current_zoom)
                path_item.setPen(pen)
                self.scene.addItem(path_item)
            
            # Draw current line in progress
            if len(self.current_line_points) > 1:
                current_line = VectorLine(self.current_line_points)
                path_item = QGraphicsPathItem(current_line.to_path(current_zoom))
                pen = QPen(Qt.GlobalColor.black, self.line_width / current_zoom)
                path_item.setPen(pen)
                self.scene.addItem(path_item)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.drawing = False
            
            # Only add line if it has more than one point
            if len(self.current_line_points) > 1:
                vector_line = VectorLine(self.current_line_points)
                self.vector_lines.append(vector_line)
            
            self.current_line_points = []

    def wheelEvent(self, event):
        # Zooming
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        
        if event.angleDelta().y() > 0:
            # Zoom in
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            # Zoom out
            self.scale(zoom_out_factor, zoom_out_factor)
        
        # Redraw lines to maintain consistent width
        self.redraw_lines()

    def redraw_lines(self):
        # Clear the scene
        self.scene.clear()
        
        # Get current zoom level
        current_zoom = self.transform().m11()
        
        # Redraw all vector lines
        for vector_line in self.vector_lines:
            path_item = QGraphicsPathItem(vector_line.to_path(current_zoom))
            pen = QPen(vector_line.color, vector_line.width / current_zoom)
            path_item.setPen(pen)
            self.scene.addItem(path_item)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vector Drawing App")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Drawing view
        self.drawing_view = DrawingView()
        layout.addWidget(self.drawing_view)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
