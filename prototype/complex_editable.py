import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsScene, QGraphicsView, 
                            QVBoxLayout, QWidget, QPushButton, QGraphicsLineItem, 
                            QHBoxLayout, QGraphicsPathItem, QGraphicsEllipseItem)
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPen, QColor, QPainter, QPainterPath

class ControlPoint(QGraphicsEllipseItem):
    def __init__(self, pos, parent=None):
        super().__init__(-4, -4, 8, 8, parent)
        self.setPos(pos)
        self.setBrush(Qt.GlobalColor.blue)
        self.setPen(QPen(Qt.GlobalColor.black, 1))
        self.setFlags(self.GraphicsItemFlag.ItemIsMovable | 
                     self.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
    def mouseMoveEvent(self, event):
        print("ok")
        super().mouseMoveEvent(event)
        # Update the parent figure when control point is moved
        if isinstance(self.parentItem(), FigureGraphicsItem):
            self.parentItem().update_path()

class FigureGraphicsItem(QGraphicsPathItem):
    def __init__(self):
        super().__init__()
        self.points = []
        self.control_points = []
        self.temp_point = None
        self.is_closed = False
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setAcceptHoverEvents(True)
        self.setFlags(self.GraphicsItemFlag.ItemIsSelectable)

    def add_point(self, point):
        self.points.append(point)
        control_point = ControlPoint(point, self)
        self.control_points.append(control_point)
        self.update_path()

    def insert_point(self, index, point):
        self.points.insert(index, point)
        control_point = ControlPoint(point, self)
        self.control_points.insert(index, control_point)
        self.update_path()
        return control_point

    def update_temp_point(self, point):
        self.temp_point = point
        self.update_path()

    def update_path(self):
        # Update points based on control points positions
        for i, cp in enumerate(self.control_points):
            self.points[i] = cp.pos()

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

    def find_closest_segment(self, point):
        min_distance = float('inf')
        insert_index = -1
        
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            
            # Calculate distance from point to line segment
            line_vector = p2 - p1
            point_vector = point - p1
            
            # Calculate projection
            line_length = line_vector.x() * line_vector.x() + line_vector.y() * line_vector.y()
            if line_length == 0:
                continue
                
            t = max(0, min(1, (point_vector.x() * line_vector.x() + 
                             point_vector.y() * line_vector.y()) / line_length))
            
            projection = p1 + t * line_vector
            distance = (point - projection).manhattanLength()
            
            if distance < min_distance:
                min_distance = distance
                insert_index = i + 1
                self.projection_point = projection
        
        return insert_index if min_distance < 10 else -1

class DrawingScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.current_figure = None
        self.mode = "draw"  # Modes: "draw", "edit", "remove"
        self.selected_item = None
        self.dragging_point = None

    def mousePressEvent(self, event):
        pos = event.scenePos()
        
        if self.mode == "draw":
            if not self.current_figure:
                self.current_figure = FigureGraphicsItem()
                self.addItem(self.current_figure)
                self.current_figure.add_point(pos)
            else:
                if self.current_figure.try_close_figure(pos):
                    self.current_figure = None
                else:
                    self.current_figure.add_point(pos)
        
        elif self.mode == "edit":
            items = self.items(pos)
            for item in items:
                if isinstance(item, FigureGraphicsItem):
                    # Find the closest line segment and insert a new point
                    insert_index = item.find_closest_segment(pos)
                    if insert_index != -1:
                        new_point = item.projection_point
                        control_point = item.insert_point(insert_index, new_point)
                        # Start dragging the new point
                        control_point.setSelected(True)
                        break
        
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
        super().mouseReleaseEvent(event)

# [Previous MainWindow class and ZoomableView class remain the same]
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

class _DrawingScene(QGraphicsScene):
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
        edit_button = QPushButton("Edit mode")

        # Add mode buttons to layout
        mode_layout.addWidget(draw_button)
        mode_layout.addWidget(remove_button)
        mode_layout.addWidget(edit_button)

        # Connect zoom buttons
        zoom_in_button.clicked.connect(self.zoom_in)
        zoom_out_button.clicked.connect(self.zoom_out)
        reset_zoom_button.clicked.connect(self.view.reset_zoom)

        # Connect mode buttons
        draw_button.clicked.connect(lambda: self.set_mode("draw"))
        remove_button.clicked.connect(lambda: self.set_mode("remove"))
        edit_button.clicked.connect(lambda: self.set_mode("edit"))

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

