from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal

class Point(BaseModel):
    x: float
    y: float

class EntityBase(BaseModel):
    id: str
    layerId: str
    visible: bool = True

class RoundedRect(EntityBase):
    type: Literal["roundedRect"]
    center: Point
    width: float
    height: float
    rx: float
    ry: float

class Rect(EntityBase):
    type: Literal["rect"]
    center: Point
    width: float
    height: float

class ElectrodeArray(EntityBase):
    type: Literal["electrodeArray"]
    sourceId: str
    origin: Point
    countX: int
    countY: int = 1
    pitchX: float
    pitchY: float = 0.0

class Line(EntityBase):
    type: Literal["line"]
    start: Point
    end: Point

Entity = Union[RoundedRect, Rect, ElectrodeArray, Line]

class Layer(BaseModel):
    id: str
    name: str
    visible: bool

class ClosedRegion(BaseModel):
    id: str
    boundarySegments: List[dict] # Simplified for now
    area: float
    sourceEntityIds: List[str]
    containsArcs: bool

class DrawingModel(BaseModel):
    layers: List[Layer]
    entities: List[Entity]
    closedRegions: List[ClosedRegion]
