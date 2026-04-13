from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import Qt

class MapView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Make the map look smooth and allow dragging
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        # Background color (like the ocean)
        self.setBackgroundBrush(Qt.GlobalColor.blue)

    def render_map(self, countries):
        """Placeholder for SVG file"""
        pass