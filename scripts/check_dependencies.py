"""Read-only public advisory checks. Sends only locked package names/versions."""
import json
from datetime import date
from pathlib import Path
import subprocess
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
packages=[dict(name=line.split('==')[0],version=line.split('==')[1]) for line in (ROOT/'backend/requirements.txt').read_text().splitlines() if '==' in line]
payload={'queries':[{'package':{'name':p['name'],'ecosystem':'PyPI'},'version':p['version']} for p in packages]}
req=urllib.request.Request('https://api.osv.dev/v1/querybatch',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST')
with urllib.request.urlopen(req,timeout=30) as response:result=json.loads(response.read(2_000_000))
if len(result.get('results',[]))!=len(packages):raise RuntimeError('Incomplete advisory response')
python=[dict(**p,advisories=r.get('vulns',[])) for p,r in zip(packages,result['results'])]
npm=subprocess.run(['npm.cmd','audit','--json'],cwd=ROOT/'frontend',capture_output=True,text=True,timeout=60)
node=json.loads(npm.stdout)
if 'metadata' not in node or npm.returncode not in (0,1):raise RuntimeError('Incomplete npm advisory response')
report=dict(checked=date.today().isoformat(),sources=['https://api.osv.dev','https://registry.npmjs.org'],python=python,npm=node,limits='Known advisories only; not proof of absence of vulnerabilities. Development and transitive npm packages included.')
(ROOT/'artifacts/dependencies.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
count=sum(len(p['advisories']) for p in python)+node['metadata']['vulnerabilities']['total']
print(json.dumps({'python_packages':len(python),'reported_advisories':count,'npm_exit':npm.returncode}))
raise SystemExit(1 if count else 0)
