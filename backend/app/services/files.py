"""Allowlisted learning artifacts only; never serve arbitrary user paths."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]

def manuals():
    return json.loads((ROOT/'backend/content/manuals.json').read_text(encoding='utf-8'))

def kit():
    path=ROOT/'artifacts/aiops-labs-reais.zip'
    if not path.is_file():raise ValueError('Kit ainda não foi empacotado. Veja labs/real no diretório do app.')
    return path
