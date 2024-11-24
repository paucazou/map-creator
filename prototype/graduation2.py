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
        self.scale_bar.setFixedHeight(30)  # Increased height for better visibility
        self.scale_bar.setFixedWidth(500)  # Increased width to accommodate 5cm
        self.scale_label = QLabel()
        
        self.layout.addWidget(self.scale_bar)
        self.layout.addWidget(self.scale_label)
        self.layout.addStretch()
        
        # Set minimum size for the widget
        self.setMinimumWidth(600)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw scale bar
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Calculate dimensions (1cm = 100 pixels on screen)
        cm_pixel = 100  # 1cm = 100 pixels
        total_width = 5 * cm_pixel  # 5cm
        
        # Draw main horizontal line
        painter.drawLine(10, 15, 10 + total_width, 15)
        
        # Draw vertical ends and intermediate marks
        for i in range(6):  # 0 to 5 marks
            x = 10 + (i * cm_pixel)
            # Main vertical marks
            painter.drawLine(x, 10, x, 20)
            

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
        self.initial_km_per_cm = 100  # Starting with 1cm = 100km
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
        current_km_per_cm = self.initial_km_per_cm / self.current_scale
        
        # Choose appropriate unit based on distance
        if current_km_per_cm >= 1:
            unit = "km"
            value = current_km_per_cm
        else:
            unit = "m"
            value = current_km_per_cm * 1000
            
        # Update scale label - show total distance for 5cm
        self.scale_widget.scale_label.setText(f"1 cm = {value:.1f} {unit}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map Viewer with Scale")
        self.setGeometry(100, 100, 1000, 800)  # Increased window size
        
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
