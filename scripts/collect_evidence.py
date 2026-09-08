"""Bounded verification of reviewed local code, content and dependency inventory."""
import ast
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
results=[]
commands=[
 [str(ROOT/'.venv/Scripts/python.exe'),'-m','unittest','discover','-s','backend/tests','-v'],
 [sys.executable,'labs/real/python/check.py','--solution'],
 [sys.executable,'labs/real/http_lab/bench.py'],
]
for cmd in commands:
    run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=60)
    results.append({'command':cmd,'exit':run.returncode,'output':(run.stdout+run.stderr)[-16000:]})
    if run.returncode:raise RuntimeError('Verification failed: '+str(cmd))
sources=list((ROOT/'backend/app').rglob('*.py'))
for path in sources:
    tree=ast.parse(path.read_text(encoding='utf-8'))
    forbidden=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in ('eval','exec','compile','__import__')]
    assert not forbidden,path
    assert not re.search(r'\b(subprocess|pickle|os\.system)\b',path.read_text(encoding='utf-8')),path
results.append({'command':'Focused static checks: backend AST and process/deserialization sinks','exit':0,'output':f'{len(sources)} Python files; no eval/exec/compile/dynamic imports, subprocess, pickle or os.system. Not a general SAST certification.'})
course=json.loads((ROOT/'backend/content/course.json').read_text(encoding='utf-8'))
manuals=json.loads((ROOT/'backend/content/manuals.json').read_text(encoding='utf-8'))
assert len(course['lessons'])==30
assert sum(m.get('category','core')=='core' for m in manuals)==12
counts={'lessons':30,'questions':sum(len(l['quiz']) for l in course['lessons']),'manuals':len(manuals),'lesson_words':sum(len(l['body'].split()) for l in course['lessons']),'manual_words':sum(len(m['body'].split()) for m in manuals)}
results.append({'command':'Content inventory','exit':0,'output':counts})
(ROOT/'artifacts/tests.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
components=[]
for line in (ROOT/'backend/requirements.txt').read_text().splitlines():
    if '==' in line:
        name,version=line.split('==');components.append({'type':'library','name':name,'version':version,'purl':f'pkg:pypi/{name}@{version}'})
lock=json.loads((ROOT/'frontend/package-lock.json').read_text())
for location,p in lock['packages'].items():
    if not location or 'version' not in p:continue
    name=location.split('node_modules/')[-1];components.append({'type':'library','name':name,'version':p['version'],'purl':f'pkg:npm/{name.replace("@","%40")}@{p["version"]}'})
(ROOT/'artifacts/sbom.cdx.json').write_text(json.dumps({'bomFormat':'CycloneDX','specVersion':'1.6','version':1,'metadata':{'component':{'type':'application','name':'aiops-academy','version':course['version']}},'components':components},indent=2),encoding='utf-8')
print(json.dumps({'checks':'passed','counts':counts,'inventory_components':len(components)}))
