import xml.etree.ElementTree as ET
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPainterPath
from CountryItem import CountryItem
from svg.path import parse_path, Move, Line, CubicBezier, QuadraticBezier, Arc, Close

class MapView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setBackgroundBrush(Qt.GlobalColor.blue)

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
                    q_path.lineTo(segment.end.real, segment.end.imag)
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
                    self.scene.addItem(item)

        # Fit the view
        self.setSceneRect(self.scene.itemsBoundingRect())
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event):
        # Allow zooming in and out with the mouse wheel.
        # Define how fast the map zooms
        zoom_in_factor = 1.15
        zoom_out_factor = 1.0 / zoom_in_factor

        # event.angleDelta().y() is positive if scrolling up (zoom in)
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        # Apply the scaling to the view
        self.scale(zoom_factor, zoom_factor)