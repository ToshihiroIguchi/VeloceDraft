import sys
import os
sys.path.append(os.path.join(os.getcwd(), "app_build", "backend"))

from models import Line, Point, DrawingModel, Layer
from geometry_utils import batch_fillet_geometry, calculate_area_from_planar_graph

# 1. Create a triangle
pts = [Point(x=100, y=100), Point(x=200, y=100), Point(x=150, y=200), Point(x=100, y=100)]
lines = []
for i in range(len(pts)-1):
    lines.append(Line(id=f"l{i}", layerId="L1", type="line", start=pts[i], end=pts[i+1], visible=True))

# 2. Batch Fillet
radius = 10.0
trimmed, arcs, ids = batch_fillet_geometry(lines, radius)

# 3. Create Model
# Note: ‘arcs’ from batch_fillet_geometry are dicts, need to convert to Arc models if we want to use them properly
from models import Arc
arc_models = []
for a in arcs:
    # Arc model in models.py uses center: Point, etc.
    # arc dict has "center": {"x":..., "y":...}
    arc_models.append(Arc(
        id=a["id"],
        layerId=a["layerId"],
        type="arc",
        center=Point(x=a["center"]["x"], y=a["center"]["y"]),
        radius=a["radius"],
        startAngle=a["startAngle"],
        endAngle=a["endAngle"],
        visible=True
    ))

model = DrawingModel(
    layers=[Layer(id="L1", name="Layer 1", visible=True)],
    entities=trimmed + arc_models,
    closedRegions=[],
    unit="unitless"
)

# 4. Calculate Area
try:
    total_area, regions = calculate_area_from_planar_graph(model)
    print(f"Total Area: {total_area}")
    print(f"Regions found: {len(regions)}")
    for r in regions:
        print(f"Region area: {r.area}")
except Exception as e:
    import traceback
    traceback.print_exc()
