import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsScene, QGraphicsView, 
                            QVBoxLayout, QWidget, QPushButton, QGraphicsLineItem, 
                            QHBoxLayout, QGraphicsPathItem)
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPen, QColor, QPainter, QPainterPath

class FigureGraphicsItem(QGraphicsPathItem):
    def __init__(self):
        super().__init__()
        self.points = []
        self.temp_point = None
        self.is_closed = False
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setAcceptHoverEvents(True)

    def add_point(self, point):
        self.points.append(point)
        self.update_path()

    def update_temp_point(self, point):
        self.temp_point = point
        self.update_path()

    def update_path(self):
        path = QPainterPath()
        if len(self.points) > 0:
            path.moveTo(self.points[0])
            for point in self.points[1:]:
                path.lineTo(point)
            
            if self.temp_point and not self.is_closed:
                path.lineTo(self.temp_point)

            if self.is_closed:
                path.lineTo(self.points[0])

        self.setPath(path)

    def try_close_figure(self, point, threshold=10.0):
        if len(self.points) > 2:
            start_point = self.points[0]
            distance = (point - start_point).manhattanLength()
            if distance < threshold:
                self.is_closed = True
                self.update_path()
                return True
        return False

class ZoomableView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.scale_factor = 1.15

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                scaling_factor = self.scale_factor
            else:
                scaling_factor = 1.0 / self.scale_factor
            self.scale(scaling_factor, scaling_factor)
        else:
            super().wheelEvent(event)

    def reset_zoom(self):
        self.resetTransform()
        self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

class DrawingScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.current_figure = None
        self.mode = "draw"  # Modes: "draw", "edit", "remove"
        self.selected_item = None

    def mousePressEvent(self, event):
        pos = event.scenePos()
        
        if self.mode == "draw":
            if not self.current_figure:
                # Start new figure
                self.current_figure = FigureGraphicsItem()
                self.addItem(self.current_figure)
                self.current_figure.add_point(pos)
            else:
                # Try to close the figure if near starting point
                if self.current_figure.try_close_figure(pos):
                    self.current_figure = None
                else:
                    # Add new point to current figure
                    self.current_figure.add_point(pos)
        
        elif self.mode == "remove":
            items = self.items(pos)
            for item in items:
                if isinstance(item, FigureGraphicsItem):
                    self.removeItem(item)
                    break

    def mouseMoveEvent(self, event):
        pos = event.scenePos()
        if self.mode == "draw" and self.current_figure:
            self.current_figure.update_temp_point(pos)

    def mouseReleaseEvent(self, event):
        pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Complex Figure Drawing App")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create scene and view
        self.scene = DrawingScene()
        self.view = ZoomableView(self.scene)
        layout.addWidget(self.view)

        # Create button layouts
        button_layout = QHBoxLayout()
        mode_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        layout.addLayout(mode_layout)

        # Create zoom buttons
        zoom_in_button = QPushButton("Zoom In")
        zoom_out_button = QPushButton("Zoom Out")
        reset_zoom_button = QPushButton("Reset Zoom")
        
        # Add zoom buttons to layout
        button_layout.addWidget(zoom_in_button)
        button_layout.addWidget(zoom_out_button)
        button_layout.addWidget(reset_zoom_button)

        # Create mode buttons
        draw_button = QPushButton("Draw Mode")
        remove_button = QPushButton("Remove Mode")

        # Add mode buttons to layout
        mode_layout.addWidget(draw_button)
        mode_layout.addWidget(remove_button)

        # Connect zoom buttons
        zoom_in_button.clicked.connect(self.zoom_in)
        zoom_out_button.clicked.connect(self.zoom_out)
        reset_zoom_button.clicked.connect(self.view.reset_zoom)

        # Connect mode buttons
        draw_button.clicked.connect(lambda: self.set_mode("draw"))
        remove_button.clicked.connect(lambda: self.set_mode("remove"))

        # Initialize scene
        self.scene.setSceneRect(0, 0, 780, 520)
        self.view.setScene(self.scene)

        # Status message
        self.status_label = QWidget()
        layout.addWidget(self.status_label)

    def zoom_in(self):
        self.view.scale(self.view.scale_factor, self.view.scale_factor)

    def zoom_out(self):
        self.view.scale(1.0 / self.view.scale_factor, 1.0 / self.view.scale_factor)

    def set_mode(self, mode):
        self.scene.mode = mode

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
