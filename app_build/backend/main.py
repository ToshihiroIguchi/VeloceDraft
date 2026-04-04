import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from models import DrawingModel, Entity, RoundedRect, ElectrodeArray, Rect, Line
import io
import uuid
import logging

logging.basicConfig(filename='backend.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="VeloceDraft API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/dxf/export")
async def export_dxf(drawing: DrawingModel):
    doc = _create_dxf_doc(drawing)
    out = io.StringIO()
    doc.write(out)
    return Response(content=out.getvalue(), media_type="application/dxf", headers={"Content-Disposition": "attachment; filename=export.dxf"})

@app.post("/api/svg/export")
async def export_svg(drawing: DrawingModel):
    logger.info(f"Exporting SVG with {len(drawing.entities)} entities")
    try:
        doc = _create_dxf_doc(drawing)
        msp = doc.modelspace()
        ctx = RenderContext(doc)
        
        fig = plt.figure()
        # Create axes that cover the whole figure
        ax = fig.add_axes([0, 0, 1, 1])
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        ax.set_axis_off()
        
        backend = MatplotlibBackend(ax)
        Frontend(ctx, backend).draw_layout(msp)
        
        buf = io.BytesIO()
        fig.savefig(buf, format='svg', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        svg_content = buf.getvalue().decode('utf-8')
            
        logger.info("SVG generated successfully via Matplotlib")
        return Response(
            content=svg_content, 
            media_type="image/svg+xml", 
            headers={"Content-Disposition": "attachment; filename=export.svg"}
        )
    except Exception as e:
        logger.error(f"MATPLOTLIB SVG FAILED: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": f"MATPLOTLIB SVG FAILED: {str(e)}"})

@app.post("/api/pdf/export")
async def export_pdf(drawing: DrawingModel):
    doc = _create_dxf_doc(drawing)
    msp = doc.modelspace()
    ctx = RenderContext(doc)
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    backend = MatplotlibBackend(ax)
    Frontend(ctx, backend).draw_layout(msp)
    
    buf = io.BytesIO()
    fig.savefig(buf, format='pdf')
    plt.close(fig)
    return Response(content=buf.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=export.pdf"})

def _create_dxf_doc(drawing: DrawingModel):
    doc = ezdxf.new('R2010')
    
    # Set units
    unit_map = {"unitless": 0, "inch": 1, "mm": 4, "um": 13}
    unit_code = unit_map.get(drawing.unit, 0)
    doc.header['$INSUNITS'] = unit_code
    
    msp = doc.modelspace()
    # Handle non-line entities first
    for entity in drawing.entities:
        if entity.type == "roundedRect":
            _add_rounded_rect(msp, entity)
        elif entity.type == "rect":
            _add_rect(msp, entity)
        elif entity.type == "electrodeArray":
            source = next((e for e in drawing.entities if e.id == entity.sourceId), None)
            if source:
                for ix in range(entity.countX):
                    for iy in range(entity.countY):
                        offsetX = entity.origin.x + (ix * entity.pitchX)
                        if iy % 2 == 1:
                            offsetX += entity.staggerX
                        offsetY = entity.origin.y + (iy * entity.pitchY)
                        sc = source.center
                        shifted_entity = source.copy(update={"center": Point(x=sc.x + offsetX, y=sc.y + offsetY)})
                        if source.type == "roundedRect":
                            _add_rounded_rect(msp, shifted_entity)
                        elif source.type == "arc":
                             msp.add_arc((shifted_entity.center.x, shifted_entity.center.y), shifted_entity.radius, shifted_entity.startAngle, shifted_entity.endAngle)
                        else:
                             _add_rect(msp, shifted_entity)
    
    # Process regular entities
    for entity in drawing.entities:
        if entity.type == "arc":
             msp.add_arc((entity.center.x, entity.center.y), entity.radius, entity.startAngle, entity.endAngle)
    
    # Collect and join all line entities
    lines = [e for e in drawing.entities if e.type == "line"]
    if lines:
        from geometry_utils import join_line_entities, dist
        joined_paths = join_line_entities(lines)
        for path in joined_paths:
            points = [(p.x, p.y) for p in path]
            is_closed = False
            if len(path) > 2 and dist(path[0], path[-1]) < 1e-6:
                is_closed = True
                points = points[:-1] # Remove last point for closed polyline
            msp.add_lwpolyline(points, close=is_closed)
            
    return doc

def _add_rect(msp, entity):
    c, w, h = entity.center, entity.width, entity.height
    msp.add_lwpolyline([
        (c.x - w/2, c.y - h/2), (c.x + w/2, c.y - h/2),
        (c.x + w/2, c.y + h/2), (c.x - w/2, c.y + h/2)
    ], close=True)

def _add_rounded_rect(msp, entity):
    c, w, h, r = entity.center, entity.width, entity.height, entity.rx
    # Simplified approximation for DXF MVP
    points = [
        (c.x - w/2 + r, c.y - h/2), (c.x + w/2 - r, c.y - h/2),
        (c.x + w/2, c.y - h/2 + r), (c.x + w/2, c.y + h/2 - r),
        (c.x + w/2 - r, c.y + h/2), (c.x - w/2 + r, c.y + h/2),
        (c.x - w/2, c.y + h/2 - r), (c.x - w/2, c.y - h/2 + r)
    ]
    msp.add_lwpolyline(points, close=True)

from geometry_utils import calculate_area_from_planar_graph, fillet_geometry

@app.post("/api/area/calculate")
async def calculate_area(drawing: DrawingModel):
    total_area = calculate_area_from_planar_graph(drawing)
    return {"area": total_area}


def _get_entity_area(e):
    w, h, r = getattr(e, "width", 0), getattr(e, "height", 0), getattr(e, "rx", 0)
    return w * h - (4 - 3.14159265) * (r * r)

@app.post("/api/dxf/import")
async def import_dxf(file: UploadFile = File(...)):
    content = await file.read()
    try:
        doc = ezdxf.readb(io.BytesIO(content))
        msp = doc.modelspace()
        entities = []
        for e in msp:
            if e.dxftype() == 'LWPOLYLINE':
                # Convert to simple rect if 4-8 points
                points = e.get_points()
                if len(points) >= 4:
                    xs = [p[0] for p in points]
                    ys = [p[1] for p in points]
                    min_x, max_x = min(xs), max(xs)
                    min_y, max_y = min(ys), max(ys)
                    entities.append({
                        "id": str(uuid.uuid4()),
                        "layerId": "layer1",
                        "type": "rect",
                        "center": {"x": (min_x + max_x)/2, "y": (min_y + max_y)/2},
                        "width": max_x - min_x,
                        "height": max_y - min_y,
                        "visible": True
					})
        return {
            "layers": [{"id": "layer1", "name": "Imported", "visible": True}],
            "entities": entities,
            "closedRegions": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fillet")
async def fillet_lines(input_data: dict):
    line1_dict = input_data.get("line1")
    line2_dict = input_data.get("line2")
    radius = input_data.get("radius", 10.0)
    
    if not line1_dict or not line2_dict:
        raise HTTPException(status_code=400, detail="Missing line data")
        
    line1 = Line(**line1_dict)
    line2 = Line(**line2_dict)
    
    res = fillet_geometry(line1, line2, radius)
    if not res:
        return {"message": "Fillet failed (lines might be parallel or invalid)", "entities": []}
    
    trimmed1, trimmed2, arc_dict = res
    
    return {
        "message": f"Fillet applied with R={radius}",
        "entities": [trimmed1.model_dump(), trimmed2.model_dump(), arc_dict],
        "originalIds": [line1.id, line2.id]
    }
