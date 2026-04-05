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
    area, regions = calculate_area_from_planar_graph(drawing)
    assert area == 10000
    assert len(regions) >= 1

def test_area_calculation_separate_lines():
    from geometry_utils import calculate_area_from_planar_graph
    # 4 lines forming a 100x100 square
    l1 = Line(id="l1", layerId="L1", type="line", start=Point(x=0, y=0), end=Point(x=100, y=0), visible=True)
    l2 = Line(id="l2", layerId="L1", type="line", start=Point(x=100, y=0), end=Point(x=100, y=100), visible=True)
    l3 = Line(id="l3", layerId="L1", type="line", start=Point(x=100, y=100), end=Point(x=0, y=100), visible=True)
    l4 = Line(id="l4", layerId="L1", type="line", start=Point(x=0, y=100), end=Point(x=0, y=0), visible=True)
    
    drawing = DrawingModel(layers=[], entities=[l1, l2, l3, l4], closedRegions=[])
    area, regions = calculate_area_from_planar_graph(drawing)
    assert area == 10000
    assert len(regions) == 1

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
    area, regions = calculate_area_from_planar_graph(drawing)
    assert area == 15000
    assert len(regions) == 3 # Two outer parts and one overlapping part

def test_dxf_export_joined_polyline():
    from main import _create_dxf_doc
    # 4 lines forming a 100x100 square
    l1 = Line(id="l1", layerId="L1", type="line", start=Point(x=0, y=0), end=Point(x=100, y=0), visible=True)
    l2 = Line(id="l2", layerId="L1", type="line", start=Point(x=100, y=0), end=Point(x=100, y=100), visible=True)
    l3 = Line(id="l3", layerId="L1", type="line", start=Point(x=100, y=100), end=Point(x=0, y=100), visible=True)
    l4 = Line(id="l4", layerId="L1", type="line", start=Point(x=0, y=100), end=Point(x=0, y=0), visible=True)
    
    drawing = DrawingModel(layers=[], entities=[l1, l2, l3, l4], closedRegions=[])
    doc = _create_dxf_doc(drawing)
    msp = doc.modelspace()
    
    # Check entities in modelspace
    # In ezdxf, msp is iterable
    entities = list(msp)
    # Should have 1 LWPOLYLINE instead of 4 LINEs
    assert len(entities) == 1
    assert entities[0].dxftype() == 'LWPOLYLINE'
    assert entities[0].is_closed == True
    assert len(entities[0].get_points()) == 4

def test_dxf_unit_header():
    from main import _create_dxf_doc
    # mm -> 4
    drawing = DrawingModel(layers=[], entities=[], closedRegions=[], unit="mm")
    doc = _create_dxf_doc(drawing)
    assert doc.header['$INSUNITS'] == 4

    # um -> 13
    drawing2 = DrawingModel(layers=[], entities=[], closedRegions=[], unit="um")
    doc2 = _create_dxf_doc(drawing2)
    assert doc2.header['$INSUNITS'] == 13

def test_batch_fillet():
    from geometry_utils import batch_fillet_geometry
    # 3 lines forming a U-shape: (0,100)-(0,0)-(100,0)-(100,100)
    l1 = Line(id="l1", layerId="L1", type="line", start=Point(x=0, y=100), end=Point(x=0, y=0), visible=True)
    l2 = Line(id="l2", layerId="L1", type="line", start=Point(x=0, y=0), end=Point(x=100, y=0), visible=True)
    l3 = Line(id="l3", layerId="L1", type="line", start=Point(x=100, y=0), end=Point(x=100, y=100), visible=True)
    
    # Apply R=10
    trimmed, arcs, original_ids = batch_fillet_geometry([l1, l2, l3], 10.0)
    
    # Should have 3 trimmed lines and 2 arcs
    assert len(trimmed) == 3
    assert len(arcs) == 2
    assert len(original_ids) == 3

if __name__ == "__main__":
    pytest.main([__file__])

