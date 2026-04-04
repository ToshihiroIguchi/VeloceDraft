# VeloceDraft AGENTS SSOT

This document is the Single Source of Truth for Autonomous AI Agents working on VeloceDraft.

## 1. Project Philosophy
- **No Reinventing the Wheel**: Prioritize existing stable libraries (e.g., Fabric.js, ezdxf).
- **MLCC Strict Scope**: The CAD is specialized for MLCC electrodes. No general-purpose features.
- **No Feature Creep**: Build only what is needed for MVP (e.g., Rounded Rect, Parameteric Arrays, basic Area calculation).

## 2. Language Policy
- Code, docstrings, variable names, and commit formatting must be in **English**.
- Internal Design Documents, Plans, and Final Reports (including files in `production_artifacts/` and `.agents/`) must be in **Japanese**.

## 3. Toolchain
- **Python**: Run in venv explicitly. Pass python executable directly, do not use `source activate`. (`.\.venv\Scripts\python.exe` / `./.venv/bin/python`)
- **Frontend**: Vite + React 18 + TS + Fabric.js.
- **Backend**: FastAPI + Uvicorn + Pydantic + ezdxf.
- **E2E**: Playwright (for automated browser validation and screenshot generation).
- **NO WASM**.

## 4. Work Directives
- **Zero Interruption Rule**: Do NOT stop for routine confirmations. Complete the implementation autonomously based on this SSoT and SSoT documentation.
- The sole Source of Truth for geometries is the Internal JSON Model (`DrawingModel`), NOT the Canvas representation.
