from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtGui import QColor, QPen
from PyQt6.QtCore import Qt

class CountryItem(QGraphicsPathItem):
    def __init__(self, country_data, path):
        super().__init__(path)
        self.country_data = country_data #from country object
        self.setToolTip(self.country_data.name)
        
        # Style the country shape
        self.setPen(QPen(QColor("white"), 0.5))
        self.setBrush(QColor("lightgray"))
        
        # Define color palette
        self.default_color = QColor("lightgray")
        self.hover_color = QColor("lightblue")

        # Allow interaction
        self.setAcceptHoverEvents(True)

    def mousePressEvent(self, event):
        #logic for when a user clicks the country.
        print(f"Clicked on: {self.country_data.get_info()}")
        super().mousePressEvent(event)

    def hoverEnterEvent(self, event):
        # trigger when mouse enter the country
        self.setBrush(self.hover_color)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        # trigger when mouse leave the country
        self.setBrush(self.default_color)
        super().hoverLeaveEvent(event)

    def change_color(self, color_name):
        # Permanently change country color (for quiz mode)
        self.default_color = QColor(color_name)
        self.setBrush(self.default_color)