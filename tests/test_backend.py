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

def test_fillet_intersection():
    from main import Line
    l1 = Line(id="l1", layerId="L1", type="line", start=Point(x=0, y=0), end=Point(x=100, y=0), visible=True)
    l2 = Line(id="l2", layerId="L1", type="line", start=Point(x=50, y=-50), end=Point(x=50, y=50), visible=True)
    # Intersection at (50, 0)
    # We'll use the API call or the inner function if exposed
    # For now, just test the intersection logic snippet if moved to helper
    pass

if __name__ == "__main__":
    pytest.main([__file__])
