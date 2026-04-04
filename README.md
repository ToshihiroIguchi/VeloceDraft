# VeloceDraft

VeloceDraft is a specialized 2D CAD application designed specifically for **MLCC (Multi-Layer Ceramic Capacitor)** electrode pattern editing. It bridges the gap between high-end CAD software and manual drafting by providing a parametric, lightweight, and manufacturing-ready environment.

![Header Screenshot](file:///c:/Users/toshi/python/VeloceDraft/production_artifacts/browser_screenshots/03_entities.png)

## Core Features

-   **Parametric Rounded Rects**: First-class support for electrode shapes with adjustable corner radii (rx, ry).
-   **Electrode Array Generator**: One-click generation of 1D/2D electrode patterns with configurable counts and pitches.
-   **High-Precision Calculation**: Built-in backend for accurate geometric area calculation, accounting for corner arc segments.
-   **Distance Overlays**: Real-time relative coordinate tracking (`dx`, `dy`) during move and draw operations.
-   **Multi-Format Export**: 
    -   **DXF**: Manufacturing-ready vector data (LWPOLYLINE) powered by `ezdxf`.
    -   **SVG**: For documentation and web integration.
    -   **PDF**: High-fidelity vector rendering via Matplotlib.
-   **Layer Management**: Simple visibility control for organized drafting.

## Tech Stack

-   **Frontend**: React 18, TypeScript, Fabric.js (Canvas Engine), Lucide React (Icons), Vite (Build Tool).
-   **Backend**: FastAPI, Uvicorn, Pydantic (Data Validation).
-   **Geometry Engine**: `ezdxf` (DXF I/O), `matplotlib` (Rendering).
-   **E2E Testing**: Playwright (Browser Automation).

## Development Setup

### 1. Prerequisite
-   Python 3.12+
-   Node.js 18+

### 2. Environment Setup
```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install fastapi uvicorn ezdxf matplotlib pydantic playwright
npm install
```

### 3. Running Locally
Use the provided script to start both the Frontend and Backend:
```powershell
./scripts/dev-up.ps1
```
-   **Frontend**: http://localhost:5173
-   **Backend**: http://localhost:8000

## API Documentation
The backend provides several endpoints for geometry processing:
-   `POST /api/area/calculate`: Computes total area of drawing entities.
-   `POST /api/dxf/export`: Generates a physical DXF file.
-   `POST /api/pdf/export`: Generates a high-quality PDF.
-   `POST /api/fillet`: Calculates line-line fillet intersections.

## License
MIT License - Copyright (c) 2026 VeloceDraft Team
