import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QGraphicsView, QGraphicsScene)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen

class ScaleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        
        # Create scale bar and label
        self.scale_bar = QWidget()
        self.scale_bar.setFixedHeight(20)
        self.scale_bar.setFixedWidth(100)
        self.scale_label = QLabel()
        
        self.layout.addWidget(self.scale_bar)
        self.layout.addWidget(self.scale_label)
        self.layout.addStretch()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw scale bar
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Draw horizontal line
        painter.drawLine(10, 15, 110, 15)
        # Draw vertical ends
        painter.drawLine(10, 10, 10, 20)
        painter.drawLine(110, 10, 110, 20)

class MapView(QGraphicsView):
    def __init__(self, scale_widget):
        super().__init__()
        self.scale_widget = scale_widget
        self.setScene(QGraphicsScene())
        
        # Load and set initial map
        self.map_pixmap = QPixmap("map.png")  # User needs to provide their map image
        self.scene().addPixmap(self.map_pixmap)
        
        # Set view properties
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        # Initialize scale factors
        self.base_scale = 1.0
        self.current_scale = 1.0
        self.updateScale()

    def wheelEvent(self, event):
        # Handle zoom with mouse wheel
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        
        # Save the scene pos
        old_pos = self.mapToScene(event.position().toPoint())
        
        # Zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
            
        self.scale(zoom_factor, zoom_factor)
        self.current_scale *= zoom_factor
        
        # Get the new position
        new_pos = self.mapToScene(event.position().toPoint())
        
        # Move scene to old position
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
        
        # Update scale indicator
        self.updateScale()
        
    def updateScale(self):
        # Calculate real-world distance based on current zoom level
        # This is a simplified example - you'd need to adjust based on your map's actual scale
        base_distance = 1  # 1 km at base scale
        current_distance = base_distance / self.current_scale
        
        # Choose appropriate unit based on distance
        if current_distance >= 1:
            unit = "km"
            value = current_distance
        else:
            unit = "m"
            value = current_distance * 1000
            
        # Update scale label
        self.scale_widget.scale_label.setText(f"1 cm = {value:.1f} {unit}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map Viewer with Scale")
        self.setGeometry(100, 100, 800, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create scale widget
        scale_widget = ScaleWidget()
        
        # Create map view
        map_view = MapView(scale_widget)
        
        # Add widgets to layout
        layout.addWidget(map_view)
        layout.addWidget(scale_widget)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
