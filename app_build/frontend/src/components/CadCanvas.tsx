import React, { useEffect, useRef, useState } from 'react';
import { fabric } from 'fabric';
import { v4 as uuidv4 } from 'uuid';
import type { CadAction } from '../store/cadReducer';
import type { CadState, Point, RoundedRect } from '../model';

interface CadCanvasProps {
  state: CadState;
  dispatch: React.Dispatch<CadAction>;
}

export const CadCanvas: React.FC<CadCanvasProps> = ({ state, dispatch }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [fabricCanvas, setFabricCanvas] = useState<fabric.Canvas | null>(null);

  // Initialize Fabric Canvas
  useEffect(() => {
    if (!canvasRef.current) return;
    const canvas = new fabric.Canvas(canvasRef.current, {
      width: window.innerWidth - 250, // leave space for sidebar
      height: window.innerHeight - 60, // leave space for toolbar
      selection: true,
      preserveObjectStacking: true,
    });
    setFabricCanvas(canvas);

    const handleResize = () => {
      canvas.setDimensions({
        width: window.innerWidth - 250,
        height: window.innerHeight - 60,
      });
      canvas.renderAll();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      canvas.dispose();
    };
  }, []);

  // Sync state.model -> fabric canvas
  useEffect(() => {
    if (!fabricCanvas) return;
    
    // Naive sync: clear and redraw. For MVP this is acceptable.
    // In a real app we would diff the entities.
    fabricCanvas.clear();
    
    state.model.entities.forEach(entity => {
      const layer = state.model.layers.find(l => l.id === entity.layerId);
      if (layer && !layer.visible) return;
      if (!entity.visible) return;

      if (entity.type === 'roundedRect' || entity.type === 'rect') {
        const obj = new fabric.Rect({
          left: entity.center.x - entity.width / 2,
          top: entity.center.y - entity.height / 2,
          width: entity.width,
          height: entity.height,
          rx: entity.type === 'roundedRect' ? (entity as RoundedRect).rx : 0,
          ry: entity.type === 'roundedRect' ? (entity as RoundedRect).ry : 0,
          fill: 'rgba(0, 100, 250, 0.3)',
          stroke: 'blue',
          strokeWidth: 2,
          selectable: state.currentTool === 'select',
        });
        // @ts-ignore
        obj.id = entity.id; 
        fabricCanvas.add(obj);
      }
      
      if (entity.type === 'line') {
        const obj = new fabric.Line([entity.start.x, entity.start.y, entity.end.x, entity.end.y], {
          stroke: 'blue',
          strokeWidth: 2,
          selectable: state.currentTool === 'select',
        });
        // @ts-ignore
        obj.id = entity.id;
        fabricCanvas.add(obj);
      }
      
      if (entity.type === 'electrodeArray') {
        const source = state.model.entities.find(e => e.id === entity.sourceId);
        if (source && (source.type === 'roundedRect' || source.type === 'rect')) {
          for (let i = 0; i < entity.countX; i++) {
            for (let j = 0; j < entity.countY; j++) {
              const obj = new fabric.Rect({
                left: source.center.x - source.width/2 + entity.origin.x + (i * entity.pitchX) + (j % 2 === 1 ? entity.staggerX : 0),
                top: source.center.y - source.height/2 + entity.origin.y + (j * entity.pitchY),
                width: source.width,
                height: source.height,
                rx: source.type === 'roundedRect' ? (source as RoundedRect).rx : 0,
                ry: source.type === 'roundedRect' ? (source as RoundedRect).ry : 0,
                fill: 'rgba(250, 100, 0, 0.3)',
                stroke: 'orange',
                strokeWidth: 2,
                selectable: state.currentTool === 'select',
              });
              // @ts-ignore
              obj.id = `${entity.id}_${i}_${j}`;
              // @ts-ignore
              obj.isPattern = true;
              fabricCanvas.add(obj);
            }
          }
        }
      }

      if (entity.type === 'arc') {
        const arc = entity as any;
        const sRad = arc.startAngle * (Math.PI / 180);
        const eRad = arc.endAngle * (Math.PI / 180);
        const x1 = arc.center.x + arc.radius * Math.cos(sRad);
        const y1 = arc.center.y + arc.radius * Math.sin(sRad);
        const x2 = arc.center.x + arc.radius * Math.cos(eRad);
        const y2 = arc.center.y + arc.radius * Math.sin(eRad);

        // Determine if large arc and sweep flag
        // For fillet we always want the "small" arc (< 180 deg)
        let diff = (arc.endAngle - arc.startAngle) % 360;
        if (diff < -180) diff += 360;
        if (diff > 180) diff -= 360;

        const largeArc = Math.abs(diff) > 180 ? 1 : 0;
        const sweep = diff > 0 ? 1 : 0;

        const pathData = `M ${x1} ${y1} A ${arc.radius} ${arc.radius} 0 ${largeArc} ${sweep} ${x2} ${y2}`;
        
        fabricCanvas.add(new fabric.Path(pathData, {
          fill: 'transparent',
          stroke: 'blue',
          strokeWidth: 2,
          selectable: state.currentTool === 'select',
          // @ts-ignore
          id: arc.id
        }));
      }
    });

    fabricCanvas.renderAll();
  }, [state.model, state.currentTool, fabricCanvas]);

  // Handle Mouse Events for Tools
  useEffect(() => {
    if (!fabricCanvas) return;

    let isDragging = false;
    let startPoint: Point | null = null;
    let activeShape: fabric.Object | null = null;
    let snapIndicator: fabric.Rect | null = null;

    const findSnapPoint = (pointer: Point): Point | null => {
      const threshold = 15 / fabricCanvas.getZoom(); // consistent screen-space threshold
      const entities = state.model.entities;
      const points: Point[] = [];
      entities.forEach(e => {
        if (!e.visible) return;
        const layer = state.model.layers.find(l => l.id === e.layerId);
        if (layer && !layer.visible) return;

        if (e.type === 'line') {
          points.push(e.start, e.end);
        } else if (e.type === 'rect' || e.type === 'roundedRect') {
          const { center, width, height } = e;
          points.push(
            { x: center.x - width / 2, y: center.y - height / 2 },
            { x: center.x + width / 2, y: center.y - height / 2 },
            { x: center.x + width / 2, y: center.y + height / 2 },
            { x: center.x - width / 2, y: center.y + height / 2 }
          );
        } else if (e.type === 'arc') {
          const arc = e as any;
          const sRad = arc.startAngle * (Math.PI / 180);
          const eRad = arc.endAngle * (Math.PI / 180);
          points.push(
            { x: arc.center.x, y: arc.center.y },
            { x: arc.center.x + arc.radius * Math.cos(sRad), y: arc.center.y + arc.radius * Math.sin(sRad) },
            { x: arc.center.x + arc.radius * Math.cos(eRad), y: arc.center.y + arc.radius * Math.sin(eRad) }
          );
        }
      });

      let nearest: Point | null = null;
      let minDist = threshold;

      points.forEach(p => {
        const d = Math.sqrt((p.x - pointer.x)**2 + (p.y - pointer.y)**2);
        if (d < minDist) {
          minDist = d;
          nearest = p;
        }
      });
      return nearest;
    };

    const updateSnapIndicator = (point: Point | null) => {
      if (point) {
        if (!snapIndicator) {
          snapIndicator = new fabric.Rect({
            width: 8 / fabricCanvas.getZoom(),
            height: 8 / fabricCanvas.getZoom(),
            fill: 'transparent',
            stroke: '#00ff00',
            strokeWidth: 2 / fabricCanvas.getZoom(),
            selectable: false,
            evented: false,
            originX: 'center',
            originY: 'center',
          });
          fabricCanvas.add(snapIndicator);
        }
        snapIndicator.set({ left: point.x, top: point.y });
        snapIndicator.bringToFront();
      } else {
        if (snapIndicator) {
          fabricCanvas.remove(snapIndicator);
          snapIndicator = null;
        }
      }
    };

    fabricCanvas.off('mouse:down');
    fabricCanvas.off('mouse:move');
    fabricCanvas.off('mouse:up');

    fabricCanvas.on('mouse:wheel', function(opt) {
      const delta = opt.e.deltaY;
      let zoom = fabricCanvas.getZoom();
      zoom *= 0.999 ** delta;
      if (zoom > 20) zoom = 20;
      if (zoom < 0.01) zoom = 0.01;
      fabricCanvas.zoomToPoint({ x: opt.e.offsetX, y: opt.e.offsetY }, zoom);
      opt.e.preventDefault();
      opt.e.stopPropagation();
    });

    fabricCanvas.on('mouse:down', (opt) => {
      let pointer = fabricCanvas.getPointer(opt.e);
      const snapPoint = findSnapPoint(pointer);
      if (snapPoint) {
        pointer = snapPoint;
      }
      startPoint = { x: pointer.x, y: pointer.y };

      if (state.currentTool === 'pan' && opt.e.altKey) {
        isDragging = true;
        fabricCanvas.selection = false;
      }
      
      if (state.currentTool === 'roundedRect') {
        isDragging = true;
        activeShape = new fabric.Rect({
          left: pointer.x,
          top: pointer.y,
          width: 0,
          height: 0,
          rx: 10,
          ry: 10,
          fill: 'rgba(0, 100, 250, 0.3)',
          stroke: 'blue',
          strokeWidth: 2,
          selectable: false,
        });
        fabricCanvas.add(activeShape);
      }
      
      if (state.currentTool === 'line') {
        isDragging = true;
        activeShape = new fabric.Line([pointer.x, pointer.y, pointer.x, pointer.y], {
          stroke: 'blue',
          strokeWidth: 2,
          selectable: false,
        });
        fabricCanvas.add(activeShape);
      }
    });

    fabricCanvas.on('mouse:move', (opt) => {
      let pointer = fabricCanvas.getPointer(opt.e);
      const snapPoint = findSnapPoint(pointer);
      if (snapPoint) {
        pointer = snapPoint;
      }
      updateSnapIndicator(snapPoint);

      if (isDragging && startPoint) {
        if (state.currentTool === 'pan' && opt.e.altKey) {
          const e = opt.e as MouseEvent;
          const vpt = fabricCanvas.viewportTransform;
          if (vpt) {
            vpt[4] += e.movementX;
            vpt[5] += e.movementY;
            fabricCanvas.requestRenderAll();
          }
        }
        
        if (state.currentTool === 'roundedRect' && activeShape && startPoint) {
          let width = Math.abs(pointer.x - startPoint.x);
          let height = Math.abs(pointer.y - startPoint.y);
          let left = Math.min(pointer.x, startPoint.x);
          let top = Math.min(pointer.y, startPoint.y);

          if (opt.e.shiftKey) {
            const size = Math.max(width, height);
            width = size;
            height = size;
            left = pointer.x < startPoint.x ? startPoint.x - size : startPoint.x;
            top = pointer.y < startPoint.y ? startPoint.y - size : startPoint.y;
          }

          // @ts-ignore
          activeShape.set({ width, height, left, top });
          fabricCanvas.requestRenderAll();
          
          dispatch({
            type: 'UPDATE_DISTANCE_OVERLAY',
            p1: startPoint, 
            p2: { x: pointer.x < startPoint.x ? startPoint.x - width : startPoint.x + width, 
                  y: pointer.y < startPoint.y ? startPoint.y - height : startPoint.y + height }
          });
        }

        if (state.currentTool === 'line' && activeShape && startPoint) {
          let endX = pointer.x;
          let endY = pointer.y;
          if (opt.e.shiftKey) {
            if (Math.abs(pointer.x - startPoint.x) > Math.abs(pointer.y - startPoint.y)) {
              endY = startPoint.y;
            } else {
              endX = startPoint.x;
            }
          }
          // @ts-ignore
          activeShape.set({ x2: endX, y2: endY });
          fabricCanvas.requestRenderAll();
          dispatch({
            type: 'UPDATE_DISTANCE_OVERLAY',
            p1: startPoint, p2: { x: endX, y: endY }
          });
        }
      }
    });

    fabricCanvas.on('mouse:up', (opt) => {
      let pointer = fabricCanvas.getPointer(opt.e);
      const snapPoint = findSnapPoint(pointer);
      if (snapPoint) {
        pointer = snapPoint;
      }
      updateSnapIndicator(null);
      isDragging = false;
      fabricCanvas.selection = true;
      
      if (state.currentTool === 'roundedRect' && activeShape && startPoint) {
        let width = Math.abs(pointer.x - startPoint.x);
        let height = Math.abs(pointer.y - startPoint.y);
        let left = Math.min(pointer.x, startPoint.x);
        let top = Math.min(pointer.y, startPoint.y);

        if (opt.e.shiftKey) {
          const size = Math.max(width, height);
          width = size;
          height = size;
          left = pointer.x < startPoint.x ? startPoint.x - size : startPoint.x;
          top = pointer.y < startPoint.y ? startPoint.y - size : startPoint.y;
        }

        if (width > 5 && height > 5) {
          const newRect: RoundedRect = {
            id: uuidv4(),
            layerId: state.activeLayerId,
            type: 'roundedRect',
            center: {
              x: left + width / 2,
              y: top + height / 2,
            },
            width, height, rx: 10, ry: 10, visible: true
          };
          dispatch({ type: 'ADD_ENTITY', entity: newRect });
        }
        fabricCanvas.remove(activeShape);
        activeShape = null;
        dispatch({ type: 'SET_TOOL', tool: 'select' });
        dispatch({ type: 'UPDATE_DISTANCE_OVERLAY', p1: null, p2: null });
      }

      if (state.currentTool === 'line' && activeShape && startPoint) {
        let endX = pointer.x;
        let endY = pointer.y;
        if (opt.e.shiftKey) {
          if (Math.abs(pointer.x - startPoint.x) > Math.abs(pointer.y - startPoint.y)) {
            endY = startPoint.y;
          } else {
            endX = startPoint.x;
          }
        }
        const dist = Math.sqrt((endX - startPoint.x)**2 + (endY - startPoint.y)**2);
        if (dist > 5) {
          const newLine = {
            id: uuidv4(),
            layerId: state.activeLayerId,
            type: 'line',
            start: { x: startPoint.x, y: startPoint.y },
            end: { x: endX, y: endY },
            visible: true
          };
          // @ts-ignore
          dispatch({ type: 'ADD_ENTITY', entity: newLine });
        }
        fabricCanvas.remove(activeShape);
        activeShape = null;
        dispatch({ type: 'SET_TOOL', tool: 'select' });
        dispatch({ type: 'UPDATE_DISTANCE_OVERLAY', p1: null, p2: null });
      }
    });
    
    // Setup selection syncing
    fabricCanvas.on('selection:created', handleSelection);
    fabricCanvas.on('selection:updated', handleSelection);
    fabricCanvas.on('selection:cleared', () => dispatch({ type: 'SET_SELECTED', entityIds: [] }));

    function handleSelection(opt: fabric.IEvent) {
      // @ts-ignore
      const ids = opt.selected?.map(o => o.id?.split('_')[0]).filter(id => id) || [];
      const uniqueIds = Array.from(new Set(ids));
      dispatch({ type: 'SET_SELECTED', entityIds: uniqueIds });
    }

  }, [fabricCanvas, state.currentTool, state.activeLayerId, dispatch]);

  return (
    <div style={{ flex: 1, position: 'relative' }}>
      <canvas ref={canvasRef} />
      {state.distanceOverlay.active && state.distanceOverlay.p1 && state.distanceOverlay.p2 && (
        <div style={{
          position: 'absolute',
          top: 10, left: 10,
          background: 'rgba(0,0,0,0.7)',
          color: 'white',
          padding: '4px 8px',
          borderRadius: 4,
          pointerEvents: 'none',
          fontSize: '12px'
        }}>
          {(() => {
            const unit = state.model.unit === 'um' ? 'μm' : (state.model.unit === 'unitless' ? '' : ` ${state.model.unit}`);
            return (
              <>
                dx: {Math.abs(state.distanceOverlay.p2.x - state.distanceOverlay.p1.x).toFixed(1)}{unit} | 
                dy: {Math.abs(state.distanceOverlay.p2.y - state.distanceOverlay.p1.y).toFixed(1)}{unit}
              </>
            );
          })()}
        </div>
      )}
    </div>
  );
};
