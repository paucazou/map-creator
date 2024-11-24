import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QPoint, QRectF

class DrawingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Store points and state
        self.points = []
        self.is_drawing = False
        self.current_point = None
        self.dragging_point_index = None
        self.hover_point_index = None
        self.hover_line = None
        
        # Point visualization parameters
        self.point_radius = 5
        self.highlight_radius = 8
        self.click_tolerance = 10
        self.line_click_tolerance = 5

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.GlobalColor.white)
        self.setPalette(palette)

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw lines between points
        if len(self.points) > 1:
            pen = QPen(Qt.GlobalColor.black, 2)
            painter.setPen(pen)
            for i in range(len(self.points) - 1):
                painter.drawLine(self.points[i], self.points[i + 1])
            
            # Draw line to current position if drawing
            if self.is_drawing and self.current_point is not None:
                painter.drawLine(self.points[-1], self.current_point)
                
            # Draw line to first point if figure is closed
            if not self.is_drawing and len(self.points) > 2:
                painter.drawLine(self.points[-1], self.points[0])
        
        # Draw points
        for i, point in enumerate(self.points):
            # Highlight first point when hover
            if (i == 0 and self.is_drawing and self.current_point is not None and 
                self.is_point_near(point, self.current_point)):
                painter.setPen(QPen(Qt.GlobalColor.green, 2))
                painter.drawEllipse(point, self.highlight_radius, self.highlight_radius)
            
            # Highlight point under mouse
            elif i == self.hover_point_index:
                painter.setPen(QPen(Qt.GlobalColor.blue, 2))
                painter.drawEllipse(point, self.highlight_radius, self.highlight_radius)
            
            # Normal point
            else:
                painter.setPen(QPen(Qt.GlobalColor.red, 2))
                painter.drawEllipse(point, self.point_radius, self.point_radius)
        
        # Highlight potential new point position on line
        if self.hover_line is not None and not self.is_drawing:
            painter.setPen(QPen(Qt.GlobalColor.blue, 2))
            painter.drawEllipse(self.hover_line, self.point_radius, self.point_radius)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            point = event.pos()
            
            # Start new figure
            if not self.points:
                self.points.append(point)
                self.is_drawing = True
            
            # Check if clicking near first point to close figure
            elif self.is_drawing and self.is_point_near(self.points[0], point):
                self.is_drawing = False
            
            # Check if clicking on existing point to drag
            elif not self.is_drawing:
                for i, existing_point in enumerate(self.points):
                    if self.is_point_near(existing_point, point):
                        self.dragging_point_index = i
                        break
                else:
                    # Check if clicking on line to add new point
                    new_point = self.get_point_on_line(point)
                    if new_point:
                        insert_index = self.get_line_segment_index(point) + 1
                        self.points.insert(insert_index, new_point)
                        self.dragging_point_index = insert_index
                        # Start dragging the newly created point immediately
                        self.points[self.dragging_point_index] = point
            
            # Add new point to figure
            elif self.is_drawing:
                self.points.append(point)
            
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging_point_index = None
            self.update()

    def mouseMoveEvent(self, event):
        point = event.pos()
        self.current_point = point
        
        # Handle dragging
        if self.dragging_point_index is not None:
            self.points[self.dragging_point_index] = point
        
        # Handle hovering
        elif not self.is_drawing:
            # Check for hover over points
            self.hover_point_index = None
            for i, existing_point in enumerate(self.points):
                if self.is_point_near(existing_point, point):
                    self.hover_point_index = i
                    self.hover_line = None
                    break
            else:
                # Check for hover over lines
                self.hover_line = self.get_point_on_line(point)
        
        self.update()

    def is_point_near(self, p1, p2):
        if p1 is None or p2 is None:
            return False
        return ((p1.x() - p2.x()) ** 2 + (p1.y() - p2.y()) ** 2) ** 0.5 < self.click_tolerance
        # This is probably better
        return (p1 - p2).manhattanLength() < self.click_tolerance

    def get_point_on_line(self, point):
        if len(self.points) < 2:
            return None
            
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            
            # Calculate distance from point to line segment
            line_length = ((p2.x() - p1.x()) ** 2 + (p2.y() - p1.y()) ** 2) ** 0.5
            if line_length == 0:
                continue
                
            t = max(0, min(1, ((point.x() - p1.x()) * (p2.x() - p1.x()) +
                              (point.y() - p1.y()) * (p2.y() - p1.y())) /
                              (line_length ** 2)))
            
            proj_x = p1.x() + t * (p2.x() - p1.x())
            proj_y = p1.y() + t * (p2.y() - p1.y())
            
            dist = ((point.x() - proj_x) ** 2 + (point.y() - proj_y) ** 2) ** 0.5
            
            if dist < self.line_click_tolerance:
                return QPoint(int(proj_x), int(proj_y))
        
        # Check last line segment if figure is closed
        if not self.is_drawing and len(self.points) > 2:
            p1 = self.points[-1]
            p2 = self.points[0]
            
            line_length = ((p2.x() - p1.x()) ** 2 + (p2.y() - p1.y()) ** 2) ** 0.5
            if line_length > 0:
                t = max(0, min(1, ((point.x() - p1.x()) * (p2.x() - p1.x()) +
                                  (point.y() - p1.y()) * (p2.y() - p1.y())) /
                                  (line_length ** 2)))
                
                proj_x = p1.x() + t * (p2.x() - p1.x())
                proj_y = p1.y() + t * (p2.y() - p1.y())
                
                dist = ((point.x() - proj_x) ** 2 + (point.y() - proj_y) ** 2) ** 0.5
                
                if dist < self.line_click_tolerance:
                    return QPoint(int(proj_x), int(proj_y))
        
        return None

    def get_line_segment_index(self, point):
        if len(self.points) < 2:
            return -1
            
        min_dist = float('inf')
        min_index = -1
        
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            
            line_length = ((p2.x() - p1.x()) ** 2 + (p2.y() - p1.y()) ** 2) ** 0.5
            if line_length == 0:
                continue
                
            t = max(0, min(1, ((point.x() - p1.x()) * (p2.x() - p1.x()) +
                              (point.y() - p1.y()) * (p2.y() - p1.y())) /
                              (line_length ** 2)))
            
            proj_x = p1.x() + t * (p2.x() - p1.x())
            proj_y = p1.y() + t * (p2.y() - p1.y())
            
            dist = ((point.x() - proj_x) ** 2 + (point.y() - proj_y) ** 2) ** 0.5
            
            if dist < min_dist:
                min_dist = dist
                min_index = i
        
        return min_index

class FigureDrawingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Figure Drawing App")
        self.setGeometry(100, 100, 800, 600)
        
        # Create and set the drawing widget as the central widget
        self.drawing_widget = DrawingWidget(self)
        self.setCentralWidget(self.drawing_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FigureDrawingApp()
    window.show()
    sys.exit(app.exec())
