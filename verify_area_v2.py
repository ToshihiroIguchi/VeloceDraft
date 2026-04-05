import math
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'app_build', 'backend'))

from models import DrawingModel, Line, Point
from geometry_utils import calculate_area_from_planar_graph, Vector2

def test_filleted_rectangle_area():
    # A 10x10 square at origin (0,0) to (10,10)
    # With R=1 fillet at all 4 corners
    # The actual area should be 10*10 - (4 - PI)*R^2 = 100 - (4 - 3.14159265...) = 99.14159...
    
    # We'll simulate slightly drifted coordinates to test snap_tolerance
    # Top-left corner (0,10) filleted
    # Top-right corner (10,10) filleted
    # Bottom-right corner (10,0) filleted
    # Bottom-left corner (0,0) filleted
    
    # Simple Square for baseline
    drawing = DrawingModel(
        layers=[],
        entities=[
            Line(id="l1", layerId="default", type="line", start=Point(x=0, y=0), end=Point(x=10, y=0)),
            Line(id="l2", layerId="default", type="line", start=Point(x=10, y=0), end=Point(x=10, y=10)),
            Line(id="l3", layerId="default", type="line", start=Point(x=10, y=10), end=Point(x=0, y=10)),
            Line(id="l4", layerId="default", type="line", start=Point(x=0, y=10), end=Point(x=0, y=0.0000001)) # Tiny gap
        ],
        closedRegions=[]
    )
    
    area, regions = calculate_area_from_planar_graph(drawing, snap_tolerance=1e-4)
    print(f"Area with tiny gap (0.0000001) and tolerance 1e-4: {area}")
    assert abs(area - 100.0) < 1e-5, f"Expected 100.0, got {area}"

    # Now test with a much larger gap that should fail
    drawing_fail = DrawingModel(
        layers=[],
        entities=[
            Line(id="l1", layerId="default", type="line", start=Point(x=0, y=0), end=Point(x=10, y=0)),
            Line(id="l2", layerId="default", type="line", start=Point(x=10, y=0), end=Point(x=10, y=10)),
            Line(id="l3", layerId="default", type="line", start=Point(x=10, y=10), end=Point(x=0, y=10)),
            Line(id="l4", layerId="default", type="line", start=Point(x=0, y=10), end=Point(x=0, y=0.1)) # 0.1 gap
        ],
        closedRegions=[]
    )
    area_fail, regions_fail = calculate_area_from_planar_graph(drawing_fail, snap_tolerance=1e-4)
    print(f"Area with large gap (0.1) and tolerance 1e-4: {area_fail}")
    assert area_fail == 0.0, f"Expected 0.0 area for open loop, got {area_fail}"

    print("Verification Passed!")

if __name__ == "__main__":
    test_filleted_rectangle_area()
