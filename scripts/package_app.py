"""Portable source + built UI, without installed runtimes or learner state."""
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile
import sys
import os
import subprocess
import platform

ROOT=Path(__file__).resolve().parents[1]
VERSION='1.2.0-beta.1'
allowed={'backend','frontend','scripts','labs','docs','schemas','artifacts','.github'}
excluded={'node_modules','.venv','__pycache__','workspace','.git'}
artifact_names={'aiops-labs-reais.zip','kit-manifest.json'}
paths=[]
for p in ROOT.rglob('*'):
    rel=p.relative_to(ROOT)
    if rel.parts[0]=='data' or rel.parts[:2]==('docs','ai') or p.name.startswith('.env') or p.suffix in ('.key','.pem','.p12'):continue
    if not p.is_file() or set(rel.parts)&excluded or p.suffix in ('.pyc','.sqlite3','.sqlite','.db'):continue
    if len(rel.parts)>1 and rel.parts[0] not in allowed:continue
    if rel.parts[0]=='artifacts' and not (len(rel.parts)==2 and p.name in artifact_names):continue
    paths.append(p)
paths.sort()
manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
assert {'frontend/src/data/types.ts','frontend/src/data/curriculum.ts','backend/content/curriculum.json','schemas/curriculum.schema.json'} <= manifest.keys()
assert {name for name in manifest if name.startswith('artifacts/')} <= {f'artifacts/{name}' for name in artifact_names}
target=ROOT/f'artifacts/aiops-academy-{VERSION}-windows.zip'
def write(z,name,body):
    info=zipfile.ZipInfo(name,date_time=(2026,9,6,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,body)
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for p in paths:write(z,p.relative_to(ROOT).as_posix(),p.read_bytes())
    write(z,'MANIFEST.json',json.dumps(manifest,sort_keys=True,indent=2).encode())
with tempfile.TemporaryDirectory(prefix='academy-delivery-') as temp,zipfile.ZipFile(target) as z:
    dest=Path(temp).resolve()
    assert sum(i.file_size for i in z.infolist())<20_000_000
    for info in z.infolist():
        p=(dest/info.filename).resolve();assert p.is_relative_to(dest) and not p.exists()
        p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(info))
        if info.filename!='MANIFEST.json':assert hashlib.sha256(p.read_bytes()).hexdigest()==manifest[info.filename]
    env={k:v for k,v in os.environ.items() if k.upper() in ('SYSTEMROOT','WINDIR','PATH','TEMP','TMP')}
    env.update(PYTHONUTF8='1',ACADEMY_DB=str(dest/'data/probe.sqlite3'))
    probe="import sys;sys.path.insert(0,'backend');from app.main import app;from fastapi.testclient import TestClient;c=TestClient(app,base_url='http://127.0.0.1');assert c.get('/').status_code==200;assert len(c.get('/api/v1/course').json()['lessons'])==30;catalog=c.get('/api/v1/curriculum').json();assert len(catalog['tracks'])==4;assert len(catalog['units'])==50;assert c.get('/api/v1/kit').status_code==200;assert c.get('/_qa/audit.html').status_code==404;print('fresh extraction smoke passed')"
    check=subprocess.run([str(ROOT/'.venv/Scripts/python.exe'),'-c',probe],cwd=dest,env=env,capture_output=True,text=True,timeout=20)
    if check.returncode:raise RuntimeError(check.stderr[:1000])
try:
    source_commit=subprocess.check_output(
        ['git','rev-parse','HEAD'],cwd=ROOT,text=True,timeout=10
    ).strip()
except (subprocess.CalledProcessError,subprocess.TimeoutExpired,OSError):
    source_commit='uncommitted'
report={
    'product':'AIOps Academy',
    'version':VERSION,
    'archive':target.name,
    'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
    'files':len(paths)+1,
    'source_commit':source_commit,
    'target':'Windows local loopback; Python 3.12+ and Node LTS 22.12+/24+ for preparation',
    'builder':f'Python {platform.python_version()} on {platform.system()} {platform.release()}',
    'lock_sha256':{
        'backend/requirements.txt':hashlib.sha256((ROOT/'backend/requirements.txt').read_bytes()).hexdigest(),
        'frontend/package-lock.json':hashlib.sha256((ROOT/'frontend/package-lock.json').read_bytes()).hexdigest(),
    },
    'fresh_extraction':'passed',
    'smoke':'API, UI file, course, kit, QA absence passed with existing verified Python runtime',
    'excluded':['venv','node_modules','learner database','QA database','private docs/ai memory','secrets'],
    'install_scope':'Clean preparation was exercised in a new directory on the same Windows computer; installation on a second computer was not executed.',
}
(ROOT/'artifacts/release-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
