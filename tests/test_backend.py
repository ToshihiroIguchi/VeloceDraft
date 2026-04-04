import pytest
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app_build", "backend"))

from models import DrawingModel, RoundedRect, Point, ElectrodeArray

def test_area_calculation_rect():
    # Simple Rect (RoundedRect with r=0)
    rect = RoundedRect(
        id="1", layerId="L1", type="roundedRect",
        center=Point(x=10, y=10), width=100, height=50, rx=0, ry=0, visible=True
    )
    # Area should be 100 * 50 = 5000
    from main import _get_entity_area
    assert _get_entity_area(rect) == 5000

def test_area_calculation_rounded():
    # Rounded Rect with r=10
    rect = RoundedRect(
        id="1", layerId="L1", type="roundedRect",
        center=Point(x=10, y=10), width=100, height=50, rx=10, ry=10, visible=True
    )
    # Area = 100*50 - (4-PI)*10^2 = 5000 - (0.8584)*100 = 4914.16
    from main import _get_entity_area
    area = _get_entity_area(rect)
    assert 4914 < area < 4915

from models import DrawingModel, RoundedRect, Point, ElectrodeArray, Line, Rect

def test_area_calculation_rect_entities():
    # Test using the actual calculate_area_from_planar_graph logic
    from geometry_utils import calculate_area_from_planar_graph
    rect = Rect(id="r1", layerId="L1", type="rect", center=Point(x=50, y=50), width=100, height=100, visible=True)
    drawing = DrawingModel(layers=[], entities=[rect], closedRegions=[])
    assert calculate_area_from_planar_graph(drawing) == 10000

def test_area_calculation_separate_lines():
    from geometry_utils import calculate_area_from_planar_graph
    # 4 lines forming a 100x100 square
    l1 = Line(id="l1", layerId="L1", type="line", start=Point(x=0, y=0), end=Point(x=100, y=0), visible=True)
    l2 = Line(id="l2", layerId="L1", type="line", start=Point(x=100, y=0), end=Point(x=100, y=100), visible=True)
    l3 = Line(id="l3", layerId="L1", type="line", start=Point(x=100, y=100), end=Point(x=0, y=100), visible=True)
    l4 = Line(id="l4", layerId="L1", type="line", start=Point(x=0, y=100), end=Point(x=0, y=0), visible=True)
    
    drawing = DrawingModel(layers=[], entities=[l1, l2, l3, l4], closedRegions=[])
    area = calculate_area_from_planar_graph(drawing)
    assert area == 10000

def test_area_calculation_overlapping_rects():
    from geometry_utils import calculate_area_from_planar_graph
    # Two 100x100 squares overlapping by 50x100
    # Total area should be 150*100 = 15000 if union, or 10000+10000 if summed.
    # Our Planar Graph logic returns the area of all interior faces.
    # Overlapping rects will create 3 faces: two 50x100 and one 50x100 intersection.
    # Sum should be 15000.
    r1 = Rect(id="r1", layerId="L1", type="rect", center=Point(x=50, y=50), width=100, height=100, visible=True)
    r2 = Rect(id="r2", layerId="L1", type="rect", center=Point(x=100, y=50), width=100, height=100, visible=True)
    drawing = DrawingModel(layers=[], entities=[r1, r2], closedRegions=[])
    area = calculate_area_from_planar_graph(drawing)
    assert area == 15000

if __name__ == "__main__":
    pytest.main([__file__])

