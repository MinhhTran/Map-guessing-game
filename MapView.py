import xml.etree.ElementTree as ET
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPainterPath
from CountryItem import CountryItem
from svg.path import parse_path, Move, Line, CubicBezier, QuadraticBezier, Arc, Close

class MapView(QGraphicsView):
    # a signal that emit the country code string
    country_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setBackgroundBrush(Qt.GlobalColor.blue)
        self.country_items = {}

    def svg_to_qpath(self, path_string, existing_qpath=None):
        #Converts an SVG path string and appends it to a QPainterPath.
        q_path = existing_qpath if existing_qpath is not None else QPainterPath()
        
        try:
            parsed_path = parse_path(path_string)
            for segment in parsed_path:
                # Handle the Close segment
                if isinstance(segment, Close) or type(segment).__name__ == 'Close':
                    q_path.closeSubpath()
                    continue

                # Draw the segment based on its mathematical type
                if isinstance(segment, Move):
                    q_path.moveTo(segment.end.real, segment.end.imag)
                elif isinstance(segment, Line):
                    q_path.lineTo(segment.end.real, segment.end.imag)
                elif isinstance(segment, CubicBezier):
                    q_path.cubicTo(
                        segment.control1.real, segment.control1.imag,
                        segment.control2.real, segment.control2.imag,
                        segment.end.real, segment.end.imag
                    )
                elif isinstance(segment, QuadraticBezier):
                    q_path.quadTo(
                        segment.control.real, segment.control.imag,
                        segment.end.real, segment.end.imag
                    )
                elif isinstance(segment, Arc):
                    # Approximate the arc by sampling points
                    # increase range -> higher detail
                    for i in range(1, 11):
                        t = i / 10.0
                        point = segment.point(t)
                        q_path.lineTo(point.real, point.imag)
        except Exception as e:
            print(f"Path parsing error: {e}")
            
        return q_path

    def render_map(self, countries_dict):
        tree = ET.parse('BlankMap-World.svg')
        root = tree.getroot()
        
        # 1. Create a map of every ID in the SVG
        svg_id_map = {}
        for elem in root.iter():
            elem_id = elem.get('id')
            if elem_id:
                # lowercase key to match JSON data
                svg_id_map[elem_id.lower()] = elem

        # Loop through the countries
        for country_code, country_obj in countries_dict.items():
            if country_code in svg_id_map:
                element = svg_id_map[country_code]
                master_qpath = QPainterPath()
                
                # collect the 'd' string (if element itself is a path)
                paths_to_draw = []
                if element.tag.endswith('path') and element.get('d'):
                    paths_to_draw.append(element.get('d'))
                
                # collect all 'd' strings (if element is a group)
                for child in element.iter():
                    if child.tag.endswith('path') and child.get('d'):
                        paths_to_draw.append(child.get('d'))
                
                # Stitch all into one master path
                for path_string in set(paths_to_draw):
                    self.svg_to_qpath(path_string, master_qpath)

                # create the item
                if not master_qpath.isEmpty():
                    item = CountryItem(country_obj, master_qpath)
                    item.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache) # need modify
                    self.scene.addItem(item)
                    self.country_items[country_code] = item

        # Fit the view
        self.setSceneRect(self.scene.itemsBoundingRect())
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def highlight_country(self, country_code, color_name="green"):
        # Find a CountryItem in the scene by its country code and permanently change its color.
        # Visually represent correctly guessed countries.
        target_code = country_code.lower()
        
        # Iterate through all items currently drawn on the QGraphicsScene
        for item in self.scene.items():
            # Verify the item is a CountryItem before attempting to access custom properties
            if isinstance(item, CountryItem):
                if item.country_data.code == target_code:
                    item.change_color(color_name)
                    # Break out of the loop once done
                    break

    def get_country_path(self, country_code):
        """Retrieves the QPainterPath for a specific country code."""
        # Find the CountryItem associated with this code
        item = self.country_items.get(country_code)
        if item:
            return item.path() # Returns the QPainterPath
        return None

    def wheelEvent(self, event):
        # Allow zooming in and out with the mouse wheel.
        # Define how fast the map zooms
        zoom_in_factor = 1.15
        zoom_out_factor = 1.0 / zoom_in_factor
        min_zoom = 0.5
        max_zoom = 4

        # Current scale factor
        current_zoom = self.transform().m11()

        # event.angleDelta().y() is positive if scrolling up (zoom in)
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        # Calculate hypothetical new zoom
        new_zoom = current_zoom * zoom_factor

        # Clamp the zoom factor if it exceeds limits
        if new_zoom < min_zoom:
            zoom_factor = min_zoom / current_zoom
        elif new_zoom > max_zoom:
            zoom_factor = max_zoom / current_zoom
            
        # Apply the scaling to the view
        self.scale(zoom_factor, zoom_factor)

    def mousePressEvent(self, event):
        # Detect clicks and send the country code
        super().mousePressEvent(event)
        
        # Check if the user used the left mouse button
        if event.button() == Qt.MouseButton.LeftButton:
            
            # Find the item at the pixel the user clicked
            clicked_item = self.itemAt(event.pos())
            
            # Check if they actually clicked a CountryItem
            if isinstance(clicked_item, CountryItem):
                
                # Extract the country code
                country_code = clicked_item.country_data.code
                
                # send signal for MainWindow
                self.country_clicked.emit(country_code)

    def mouseReleaseEvent(self, event):
        # Detect a true click (not a drag) and send the country code
        super().mouseReleaseEvent(event)
        
        if event.button() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_start_pos'):
            # Calculate the distance the mouse moved between press and release
            move_distance = (event.pos() - self.drag_start_pos).manhattanLength()
            
            # If the mouse moved less than 5 pixels, treat it as a deliberate click
            if move_distance < 5:
                clicked_item = self.itemAt(event.pos())
                
                if isinstance(clicked_item, CountryItem):
                    country_code = clicked_item.country_data.code
                    self.country_clicked.emit(country_code)