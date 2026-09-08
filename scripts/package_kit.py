"""Deterministic, bounded, source-only exercises; verified fresh extraction."""
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile
import sys

ROOT=Path(__file__).resolve().parents[1]
(ROOT/'artifacts').mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'backend'))
from app.models.catalog import LOGS

kit=ROOT/'labs/real'
(kit/'fixtures').mkdir(exist_ok=True)
(kit/'fixtures/logs.json').write_text(json.dumps(LOGS,ensure_ascii=False,indent=2),encoding='utf-8')
manuals=json.loads((ROOT/'backend/content/manuals.json').read_text(encoding='utf-8'))
(kit/'MANUAL.md').write_text('# Kit AIOps Academy\n\nExercícios locais e roteiros opcionais. Leia cada escopo antes de executar.\n\n'+'\n\n'.join('# '+m['title']+'\n\n'+m['body'] for m in manuals),encoding='utf-8')
for name in ('LICENSE','CONTENT-LICENSE.md'):
    (kit/name).write_bytes((ROOT/name).read_bytes())
paths=sorted(p for p in kit.rglob('*') if p.is_file() and not set(p.parts)&{'__pycache__','.venv','workspace'} and p.suffix!='.pyc')
archive=ROOT/'artifacts/aiops-labs-reais.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in paths:
        info=zipfile.ZipInfo(p.relative_to(kit).as_posix(),date_time=(2026,9,6,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
        z.writestr(info,p.read_bytes())
with tempfile.TemporaryDirectory(prefix='academy-kit-check-') as d,zipfile.ZipFile(archive) as z:
    root=Path(d).resolve()
    assert sum(i.file_size for i in z.infolist())<5_000_000
    for i in z.infolist():
        dest=(root/i.filename).resolve();assert dest.is_relative_to(root) and not dest.exists()
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(i))
        assert dest.read_bytes()==(kit/i.filename).read_bytes()
digest=hashlib.sha256(archive.read_bytes()).hexdigest()
(ROOT/'artifacts/kit-manifest.json').write_text(json.dumps({'archive':archive.name,'sha256':digest,'files':[p.relative_to(kit).as_posix() for p in paths],'fresh_extraction':'passed'},indent=2),encoding='utf-8')
print(f'PASS: {len(paths)} files; SHA256 {digest}')
