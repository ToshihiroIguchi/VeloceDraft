import math
import uuid
from typing import List, Tuple, Dict, Set
from models import Point, Entity, DrawingModel, Line, ClosedRegion

class Vector2:
    def __init__(self, x: float, y: float):
        self.x = round(float(x), 6)
        self.y = round(float(y), 6)
        
    def __eq__(self, other):
        if not isinstance(other, Vector2):
            return False
        return self.x == other.x and self.y == other.y
        
    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"V({self.x}, {self.y})"

    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def unit(self):
        l = self.length()
        if l < 1e-9: return Vector2(0, 0)
        return Vector2(self.x / l, self.y / l)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

def get_segments(drawing: DrawingModel) -> List[Tuple[Vector2, Vector2]]:
    segments = []
    entities = drawing.entities

    for entity in entities:
        if entity.type == "line":
            segments.append((Vector2(entity.start.x, entity.start.y), Vector2(entity.end.x, entity.end.y)))
        elif entity.type == "rect":
            c, w, h = entity.center, entity.width, entity.height
            p1 = Vector2(c.x - w/2, c.y - h/2)
            p2 = Vector2(c.x + w/2, c.y - h/2)
            p3 = Vector2(c.x + w/2, c.y + h/2)
            p4 = Vector2(c.x - w/2, c.y + h/2)
            segments.extend([(p1, p2), (p2, p3), (p3, p4), (p4, p1)])
        elif entity.type == "roundedRect":
            c, w, h, r = entity.center, entity.width, entity.height, entity.rx
            # Approximate corners with 2 segments each for now (MVP)
            # Better would be 4-8 segments for circle arcs
            p1 = Vector2(c.x - w/2 + r, c.y - h/2)
            p2 = Vector2(c.x + w/2 - r, c.y - h/2)
            p3 = Vector2(c.x + w/2, c.y - h/2 + r)
            p4 = Vector2(c.x + w/2, c.y + h/2 - r)
            p5 = Vector2(c.x + w/2 - r, c.y + h/2)
            p6 = Vector2(c.x - w/2 + r, c.y + h/2)
            p7 = Vector2(c.x - w/2, c.y + h/2 - r)
            p8 = Vector2(c.x - w/2, c.y - h/2 + r)
            segments.extend([(p1, p2), (p2, p3), (p3, p4), (p4, p5), (p5, p6), (p6, p7), (p7, p8), (p8, p1)])
        elif entity.type == "electrodeArray":
            source = next((e for e in entities if e.id == entity.sourceId), None)
            if source:
                for ix in range(entity.countX):
                    for iy in range(entity.countY):
                        offsetX = entity.origin.x + (ix * entity.pitchX)
                        if iy % 2 == 1:
                            offsetX += getattr(entity, "staggerX", 0)
                        offsetY = entity.origin.y + (iy * entity.pitchY)
                        sc = source.center
                        # Recursively handle arrayed entity (ignoring nested arrays for simplicity)
                        temp_e = source.copy(update={"center": Point(x=sc.x + offsetX, y=sc.y + offsetY)})
                        # Extract segments manually for this temp entity
                        if temp_e.type == "rect":
                            c, w, h = temp_e.center, temp_e.width, temp_e.height
                            p1 = Vector2(c.x - w/2, c.y - h/2)
                            p2 = Vector2(c.x + w/2, c.y - h/2)
                            p3 = Vector2(c.x + w/2, c.y + h/2)
                            p4 = Vector2(c.x - w/2, c.y + h/2)
                            segments.extend([(p1, p2), (p2, p3), (p3, p4), (p4, p1)])
                        elif temp_e.type == "roundedRect":
                            c, w, h, r = temp_e.center, temp_e.width, temp_e.height, temp_e.rx
                            p1 = Vector2(c.x - w/2 + r, c.y - h/2); p2 = Vector2(c.x + w/2 - r, c.y - h/2)
                            p3 = Vector2(c.x + w/2, c.y - h/2 + r); p4 = Vector2(c.x + w/2, c.y + h/2 - r)
                            p5 = Vector2(c.x + w/2 - r, c.y + h/2); p6 = Vector2(c.x - w/2 + r, c.y + h/2)
                            p7 = Vector2(c.x - w/2, c.y + h/2 - r); p8 = Vector2(c.x - w/2, c.y - h/2 + r)
                            segments.extend([(p1, p2), (p2, p3), (p3, p4), (p4, p5), (p5, p6), (p6, p7), (p7, p8), (p8, p1)])
        elif entity.type == "arc":
            c, r, s, e = entity.center, entity.radius, entity.startAngle, entity.endAngle
            # Approximate arc with 8 segments
            num_segments = 8
            s_rad = math.radians(s)
            e_rad = math.radians(e)
            
            # Decide direction (shortest arc)
            diff = (e_rad - s_rad) % (2 * math.pi)
            if diff > math.pi: diff -= 2 * math.pi
            
            pts = []
            for i in range(num_segments + 1):
                ang = s_rad + (diff * i / num_segments)
                pts.append(Vector2(c.x + r * math.cos(ang), c.y + r * math.sin(ang)))
            
            for i in range(num_segments):
                segments.append((pts[i], pts[i+1]))

    return segments

def intersect(s1_start, s1_end, s2_start, s2_end):
    # Line intersection formula
    x1, y1 = s1_start.x, s1_start.y
    x2, y2 = s1_end.x, s1_end.y
    x3, y3 = s2_start.x, s2_start.y
    x4, y4 = s2_end.x, s2_end.y
    
    denom = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)
    if abs(denom) < 1e-9: return None # Parallel
    
    ua = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / denom
    ub = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / denom
    
    if 0 <= ua <= 1 and 0 <= ub <= 1:
        return Vector2(x1 + ua*(x2-x1), y1 + ua*(y2-y1))
    return None

def split_segments(segments: List[Tuple[Vector2, Vector2]]) -> List[Tuple[Vector2, Vector2]]:
    # 1. Collect all points (start/end + intersections)
    all_points_on_segments = {s: {s[0], s[1]} for s in segments}
    
    for i in range(len(segments)):
        for j in range(i + 1, len(segments)):
            s1, s2 = segments[i], segments[j]
            p = intersect(s1[0], s1[1], s2[0], s2[1])
            if p:
                all_points_on_segments[s1].add(p)
                all_points_on_segments[s2].add(p)
                
    # 2. Decompose segments into atomic parts
    atomic_segments = []
    for s, pts in all_points_on_segments.items():
        # Sort points along the segment to create sequential sub-segments
        # if vertical, sort by y, else sort by x
        pts_list = list(pts)
        if abs(s[0].x - s[1].x) < 1e-9:
            pts_list.sort(key=lambda p: p.y)
        else:
            pts_list.sort(key=lambda p: p.x)
            
        for k in range(len(pts_list) - 1):
            if pts_list[k] != pts_list[k+1]:
                atomic_segments.append((pts_list[k], pts_list[k+1]))
                
    return atomic_segments

def calculate_area_from_planar_graph(drawing: DrawingModel, snap_tolerance: float = 1e-4) -> Tuple[float, List[ClosedRegion]]:
    segments = get_segments(drawing)
    if not segments: return 0.0, []
    
    atomic = split_segments(segments)
    
    # Node merging: map each unique-ish point to a canonical Vector2
    canonical_nodes: Dict[Vector2, Vector2] = {}
    def get_canonical(p: Vector2) -> Vector2:
        for node in canonical_nodes:
            if dist(node, p) < snap_tolerance:
                return node
        canonical_nodes[p] = p
        return p

    # Graph: node -> list of (neighbor_node, angle)
    graph: Dict[Vector2, List[Tuple[Vector2, float]]] = {}
    
    for p1_raw, p2_raw in atomic:
        p1 = get_canonical(p1_raw)
        p2 = get_canonical(p2_raw)
        
        if p1 == p2: continue
        
        angle12 = math.atan2(p2.y - p1.y, p2.x - p1.x)
        angle21 = math.atan2(p1.y - p2.y, p1.x - p2.x)
        
        # Avoid duplicate edges between same canonical nodes
        if not any(nb == p2 for nb, _ in graph.get(p1, [])):
            graph.setdefault(p1, []).append((p2, angle12))
        if not any(nb == p1 for nb, _ in graph.get(p2, [])):
            graph.setdefault(p2, []).append((p1, angle21))
        
    # Sort outgoing edges by angle for each node
    for node in graph:
        graph[node].sort(key=lambda x: x[1])
        
    visited_edges: Set[Tuple[Vector2, Vector2]] = set()
    total_area = 0.0
    regions = []
    
    # Traverse all directed edges exactly once
    for u in graph:
        for v, _ in graph[u]:
            if (u, v) in visited_edges:
                continue
            
            # Start of a face
            face_nodes = []
            curr_u, curr_v = u, v
            
            while (curr_u, curr_v) not in visited_edges:
                visited_edges.add((curr_u, curr_v))
                face_nodes.append(curr_u)
                
                neighbors = graph[curr_v]
                idx = -1
                for i, (nb, ang) in enumerate(neighbors):
                    if nb == curr_u:
                        idx = i
                        break
                
                if idx == -1: break # Should not happen in planar graph
                
                next_node, _ = neighbors[idx - 1]
                curr_u, curr_v = curr_v, next_node
                
            # Shoelace formula for the face
            if len(face_nodes) >= 3:
                area = 0.0
                for i in range(len(face_nodes)):
                    p_i = face_nodes[i]
                    p_j = face_nodes[(i + 1) % len(face_nodes)]
                    area += (p_i.x * p_j.y) - (p_j.x * p_i.y)
                area *= 0.5
                
                if area > 1e-6: # Filter out tiny numerical noise faces
                    total_area += area
                    regions.append(ClosedRegion(
                        id=str(uuid.uuid4()),
                        vertices=[Point(x=p.x, y=p.y) for p in face_nodes],
                        area=round(area, 6),
                        sourceEntityIds=[],
                        containsArcs=False
                    ))
                    
    return round(total_area, 6), regions

def join_line_entities(lines: List[Line], tolerance: float = 1e-6) -> List[List[Vector2]]:
    if not lines: return []
    
    # Each path is a list of points
    paths: List[List[Vector2]] = []
    unused = list(lines)
    
    while unused:
        line = unused.pop(0)
        p1 = Vector2(line.start.x, line.start.y)
        p2 = Vector2(line.end.x, line.end.y)
        curr_path = [p1, p2]
        
        changed = True
        while changed:
            changed = False
            for i, line_i in enumerate(unused):
                pa = Vector2(line_i.start.x, line_i.start.y)
                pb = Vector2(line_i.end.x, line_i.end.y)
                
                # Check connection at start/end of path
                start = curr_path[0]
                end = curr_path[-1]
                
                if dist(end, pa) < tolerance:
                    curr_path.append(pb)
                    unused.pop(i)
                    changed = True
                    break
                elif dist(end, pb) < tolerance:
                    curr_path.append(pa)
                    unused.pop(i)
                    changed = True
                    break
                elif dist(start, pa) < tolerance:
                    curr_path.insert(0, pb)
                    unused.pop(i)
                    changed = True
                    break
                elif dist(start, pb) < tolerance:
                    curr_path.insert(0, pa)
                    unused.pop(i)
                    changed = True
                    break
        paths.append(curr_path)
        
    return paths

def dist(v1: Vector2, v2: Vector2) -> float:
    return math.sqrt((v1.x - v2.x)**2 + (v1.y - v2.y)**2)

def fillet_geometry(line1: Line, line2: Line, radius: float) -> Tuple[Line, Line, dict]:
    """Calculates the trimmed lines and the arc for a fillet operation."""
    p1, p2 = Vector2(line1.start.x, line1.start.y), Vector2(line1.end.x, line1.end.y)
    p3, p4 = Vector2(line2.start.x, line2.start.y), Vector2(line2.end.x, line2.end.y)
    
    # Line intersection
    v1 = p2 - p1
    v2 = p4 - p3
    det = v1.x * v2.y - v1.y * v2.x
    if abs(det) < 1e-9: return None # Parallel

    # Intersection point V
    t = ((p3.x - p1.x) * v2.y - (p3.y - p1.y) * v2.x) / det
    V = p1 + v1 * t
    
    # Directions away from intersection
    # This logic assumes the user wants to fillet the "outside" legs.
    # We pick the endpoint of each line that is furthest from the intersection.
    far1 = p1 if (p1 - V).length() > (p2 - V).length() else p2
    far2 = p3 if (p3 - V).length() > (p4 - V).length() else p4
    
    u = (far1 - V).unit()
    v = (far2 - V).unit()
    
    cos_theta = u.dot(v)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    theta = math.acos(cos_theta)
    
    if theta < 1e-6 or theta > math.pi - 1e-6: return None
    
    # Distance from V to tangent points
    d = radius / math.tan(theta / 2)
    
    T1 = V + u * d
    T2 = V + v * d
    
    # Arc Center:
    # The center C is at distance 'radius' from the lines.
    # The distance from V to C is radius / sin(theta/2).
    # The direction from V to C is (u+v).unit()
    bisector = (u + v).unit()
    dist_to_center = radius / math.sin(theta / 2)
    C = V + bisector * dist_to_center
    
    # Trimming
    trimmed1 = line1.copy(deep=True)
    trimmed1.start = Point(x=T1.x, y=T1.y)
    trimmed1.end = Point(x=far1.x, y=far1.y)
    
    trimmed2 = line2.copy(deep=True)
    trimmed2.start = Point(x=T2.x, y=T2.y)
    trimmed2.end = Point(x=far2.x, y=far2.y)
    
    # Arc Angles
    # Angles in degrees for the frontend/ezdxf
    # atan2 gives (-PI, PI]
    angle1 = math.degrees(math.atan2(T1.y - C.y, T1.x - C.x))
    angle2 = math.degrees(math.atan2(T2.y - C.y, T2.x - C.x))
    
    # We need to ensure we take the "small" arc.
    # Cross product (u x v) tells us if v is CCW from u.
    # In math.atan2, angles increase CCW.
    # Let's just return a dict that the backend will convert to the Arc model.
    
    return trimmed1, trimmed2, {
        "id": str(uuid.uuid4()),
        "layerId": line1.layerId,
        "type": "arc",
        "center": {"x": C.x, "y": C.y},
        "radius": radius,
        "startAngle": angle1,
        "endAngle": angle2,
        "start": {"x": T1.x, "y": T1.y},
        "end": {"x": T2.x, "y": T2.y},
        "visible": True
    }

def batch_fillet_geometry(lines: List[Line], radius: float) -> Tuple[List[Line], List[dict], List[str]]:
    """Applies fillet to all corners in a set of connected lines."""
    if not lines: return [], [], []
    
    # 1. Join lines into paths
    paths = join_line_entities(lines)
    all_trimmed_lines = []
    all_new_arcs = []
    original_ids = [l.id for l in lines]
    
    for path in paths:
        if len(path) < 3:
            # Not enough points for a corner, just recreate original line segments
            # (In a real system, we'd maps paths back to original entity objects)
            for i in range(len(path)-1):
                all_trimmed_lines.append(Line(
                    id=str(uuid.uuid4()), 
                    layerId=lines[0].layerId, 
                    type="line", 
                    start=Point(x=path[i].x, y=path[i].y), 
                    end=Point(x=path[i+1].x, y=path[i+1].y), 
                    visible=True
                ))
            continue
            
        # 2. Process corners sequentially
        # current_pts will be modified during trimming
        current_pts = [Vector2(p.x, p.y) for p in path]
        num_corners = len(current_pts) - 2 # e.g. 3 points = 1 corner
        
        new_path_arcs = []
        
        # We need to check if the path is closed
        is_closed = (current_pts[0] == current_pts[-1])
        if is_closed and len(current_pts) > 3:
            # Special case for closed loop: fillet the final joint too
            # Loop around by prepending the second to last point
            loop_pts = [current_pts[-2]] + current_pts[:-1] + [current_pts[1]]
            # 0: p_{n-1}, 1: p_0, 2: p_1, ..., n-1: p_{n-2}, n: p_{n-1}, n+1: p_0
        else:
            loop_pts = current_pts

        path_arcs = []
        # Temporary storage for trimmed points for each joint
        # joint_i (between seg i and i+1) results in T_end(i) and T_start(i+1)
        trimmed_pts = {i: {"end": loop_pts[i], "start": loop_pts[i]} for i in range(len(loop_pts))}

        for i in range(1, len(loop_pts) - 1):
            p_prev = loop_pts[i-1]
            p_curr = loop_pts[i]
            p_next = loop_pts[i+1]
            
            # Temporary lines for calculation
            l1 = Line(id="temp", layerId="L", type="line", start=Point(x=p_prev.x, y=p_prev.y), end=Point(x=p_curr.x, y=p_curr.y), visible=True)
            l2 = Line(id="temp", layerId="L", type="line", start=Point(x=p_curr.x, y=p_curr.y), end=Point(x=p_next.x, y=p_next.y), visible=True)
            
            res = fillet_geometry(l1, l2, radius)
            if res:
                t1, t2, arc_dict = res
                # t1.start is the tangent point on L1
                # t2.start is the tangent point on L2
                # We need the points furthest from intersection relative to the corner
                # In fillet_geometry, trimmed1.start is the tangent point.
                
                # Check if radius is too big for the segments
                # Distance from corner p_curr to tangent points T1, T2
                d1 = math.sqrt((t1.start.x - p_curr.x)**2 + (t1.start.y - p_curr.y)**2)
                d2 = math.sqrt((t2.start.x - p_curr.x)**2 + (t2.start.y - p_curr.y)**2)
                
                seg1_len = math.sqrt((p_curr.x - p_prev.x)**2 + (p_curr.y - p_prev.y)**2)
                seg2_len = math.sqrt((p_curr.x - p_next.x)**2 + (p_curr.y - p_next.y)**2)
                
                if d1 < seg1_len and d2 < seg2_len:
                    trimmed_pts[i-1]["end"] = Vector2(t1.start.x, t1.start.y)
                    trimmed_pts[i]["start"] = Vector2(t2.start.x, t2.start.y)
                    path_arcs.append(arc_dict)
                else:
                    # R too large for this corner, keep original
                    trimmed_pts[i-1]["end"] = p_curr
                    trimmed_pts[i]["start"] = p_curr
            else:
                # Parallel lines or invalid, skip
                trimmed_pts[i-1]["end"] = p_curr
                trimmed_pts[i]["start"] = p_curr

        # 3. Reconstruct lines from trimmed points
        for i in range(len(loop_pts) - 1):
            p_start = trimmed_pts[i]["start"]
            p_end = trimmed_pts[i]["end"]
            
            # Only add segments with length > tool tolerance
            if math.sqrt((p_end.x - p_start.x)**2 + (p_end.y - p_start.y)**2) > 1e-6:
                all_trimmed_lines.append(Line(
                    id=str(uuid.uuid4()),
                    layerId=lines[0].layerId,
                    type="line",
                    start=Point(x=p_start.x, y=p_start.y),
                    end=Point(x=p_end.x, y=p_end.y),
                    visible=True
                ))
        
        all_new_arcs.extend(path_arcs)
        
    return all_trimmed_lines, all_new_arcs, original_ids
