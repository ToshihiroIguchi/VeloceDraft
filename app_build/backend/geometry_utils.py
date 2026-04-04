import math
from typing import List, Tuple, Dict, Set
from models import Point, Entity, DrawingModel

class Vector2:
    def __init__(self, x: float, y: float):
        self.x = round(x, 6)
        self.y = round(y, 6)

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

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
                        offsetY = entity.origin.y + (iy * entity.pitchY)
                        sc = source.center
                        # Recursively handle arrayed entity (ignoring nested arrays for simplicity)
                        temp_e = source.copy(update={"center": {"x": sc.x + offsetX, "y": sc.y + offsetY}})
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

def calculate_area_from_planar_graph(drawing: DrawingModel) -> float:
    segments = get_segments(drawing)
    if not segments: return 0.0
    
    atomic = split_segments(segments)
    
    # Graph: node -> list of (neighbor_node, angle)
    graph: Dict[Vector2, List[Tuple[Vector2, float]]] = {}
    
    for p1, p2 in atomic:
        if p1 == p2: continue
        angle12 = math.atan2(p2.y - p1.y, p2.x - p1.x)
        angle21 = math.atan2(p1.y - p2.y, p1.x - p2.x)
        graph.setdefault(p1, []).append((p2, angle12))
        graph.setdefault(p2, []).append((p1, angle21))
        
    # Sort outgoing edges by angle for each node
    for node in graph:
        graph[node].sort(key=lambda x: x[1])
        
    visited_edges: Set[Tuple[Vector2, Vector2]] = set()
    total_area = 0.0
    
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
                
                # Move to next node: pick the edge from curr_v that is 
                # immediate counter-clockwise from curr_v -> curr_u
                neighbors = graph[curr_v]
                # Angle of curr_v -> curr_u
                rev_angle = math.atan2(curr_u.y - curr_v.y, curr_u.x - curr_v.x)
                
                # Find index of reverse edge in sorted list
                idx = -1
                for i, (nb, ang) in enumerate(neighbors):
                    if nb == curr_u:
                        idx = i
                        break
                
                # The next CCW edge is the one at index - 1
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
                
                # area > 0 means it's a "hole" or internal face (CCW winding)
                # area < 0 for the infinite face (CW winding)
                # Note: Shoelace sign depends on coordinate system and CCW/CW choice.
                # In most math libs, positive is CCW. In Face discovery, inner faces are CCW if picking next CCW.
                if area > 0:
                    total_area += area
                    
    return total_area
