"""Exactly 12 bounded loopback requests; child always terminated."""
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request
import urllib.error

env={k:v for k,v in os.environ.items() if k.upper() in ('SYSTEMROOT','WINDIR','PATH','TEMP','TMP')}
env['PYTHONIOENCODING']='utf-8'
child=subprocess.Popen([sys.executable,'-u',str(Path(__file__).with_name('service.py')),'--port','0','--seconds','15'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env)
try:
    line=child.stdout.readline()
    info=json.loads(line);base=f'http://127.0.0.1:{info["port"]}'
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    results={}
    for scenario in ('healthy','degraded'):
        statuses=[]
        for _ in range(5):
            try:
                with opener.open(base+'/quotes?scenario='+scenario,timeout=2) as response:statuses.append(response.status)
            except urllib.error.HTTPError as error:statuses.append(error.code);error.close()
        results[scenario]=dict(requests=5,errors=sum(s>=500 for s in statuses))
    with opener.open(base+'/health',timeout=2) as response:assert response.status==200
    with opener.open(base+'/metrics',timeout=2) as response:metrics=response.read(4096).decode()
    assert results['healthy']['errors']==0 and results['degraded']['errors']==5
    assert 'requests_total 10' in metrics and 'errors_total 5' in metrics
    print(json.dumps(dict(passed=True,results=results,requests=12,loopback_only=True),indent=2))
finally:
    child.terminate()
    try:child.communicate(timeout=3)
    except subprocess.TimeoutExpired:child.kill();child.communicate(timeout=3)
