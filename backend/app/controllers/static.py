"""Only built frontend files are exposed; no source or study database access."""
from pathlib import Path
from fastapi import APIRouter,HTTPException
from fastapi.responses import FileResponse

router=APIRouter()
DIST=Path(__file__).resolve().parents[3]/'frontend/dist'

@router.get('/')
def index():
    if not (DIST/'index.html').is_file():raise HTTPException(503,'Interface ainda não compilada. Execute preparar.cmd.')
    return FileResponse(DIST/'index.html')

@router.get('/favicon.svg')
def icon():return FileResponse(DIST/'favicon.svg')

@router.get('/assets/{path:path}')
def asset(path:str):
    base=(DIST/'assets').resolve()
    candidate=(base/path).resolve()
    if not candidate.is_relative_to(base) or not candidate.is_file():raise HTTPException(404)
    return FileResponse(candidate)
