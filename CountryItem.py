from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtGui import QColor, QPen

class CountryItem(QGraphicsPathItem):
    def __init__(self, country_data, path):
        super().__init__(path)
        self.country_data = country_data #from country object
        self.setToolTip(self.country_data.name)
        
        # Style the country shape
        self.setPen(QPen(QColor("white"), 0.5))
        self.setBrush(QColor("lightgray"))
        
        # Allow interaction
        self.setAcceptHoverEvents(True)

    def mousePressEvent(self, event):
        #logic for when a user clicks the country.
        print(f"Clicked on: {self.country_data.get_info()}")
        super().mousePressEvent(event)