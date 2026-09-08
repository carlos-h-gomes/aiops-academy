"""User launcher for a bounded local study session; existing ports are preserved."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser

ROOT=Path(__file__).resolve().parent
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765);parser.add_argument('--seconds',type=int,default=28800);parser.add_argument('--no-browser',action='store_true');parser.add_argument('--qa',action='store_true');args=parser.parse_args()
    if not 1024<=args.port<=65535 or not 30<=args.seconds<=28800:parser.error('port: 1024..65535; seconds: 30..28800')
    url=f'http://127.0.0.1:{args.port}'
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(url+'/api/v1/health',timeout=1) as response:existing=json.loads(response.read(4096))
        if existing.get('product')=='aiops-academy':
            print('AIOps Academy ja esta aberta em '+url)
            if not args.no_browser:webbrowser.open(url)
            return
    except Exception:pass
    try:
        with socket.socket() as check:check.bind(('127.0.0.1',args.port))
    except OSError:raise SystemExit('Porta ocupada. Preserve o outro programa e use --port 8766.')
    if not (ROOT/'frontend/dist/index.html').is_file():raise SystemExit('Execute preparar.cmd antes de iniciar.')
    env={k:v for k,v in os.environ.items() if k.upper() in ('PATH','SYSTEMROOT','WINDIR','TEMP','TMP','COMSPEC','PATHEXT')}
    env.update(PYTHONUTF8='1',PYTHONIOENCODING='utf-8')
    if args.qa:env.update(ACADEMY_DB=str(ROOT/'artifacts/qa.sqlite3'),ACADEMY_QA='1')
    target='scripts.qa_app:app' if args.qa else 'app.main:app'
    child=subprocess.Popen([sys.executable,'-m','uvicorn',target,'--app-dir',str(ROOT/'backend'),'--host','127.0.0.1','--port',str(args.port),'--no-access-log','--limit-concurrency','32','--timeout-keep-alive','5','--log-level','warning'],cwd=ROOT,env=env,stdin=subprocess.DEVNULL)
    try:
        ready=False
        for _ in range(100):
            if child.poll() is not None:raise RuntimeError('Servidor encerrou durante inicializacao.')
            try:
                with opener.open(url+'/api/v1/health',timeout=.3) as r:
                    ready=json.loads(r.read(4096)).get('product')=='aiops-academy'
                if ready:break
            except Exception:time.sleep(.1)
        if not ready:raise RuntimeError('Servidor nao respondeu em tempo.')
        print(f'AIOps Academy: {url}\nSessao local por ate {args.seconds//60} minutos. Ctrl+C encerra. Seu progresso fica salvo.',flush=True)
        if not args.no_browser:webbrowser.open(url)
        deadline=time.monotonic()+args.seconds
        while time.monotonic()<deadline and child.poll() is None:time.sleep(.25)
    except KeyboardInterrupt:print('Encerrando sessao de estudo.')
    finally:
        if child.poll() is None:child.terminate()
        try:child.wait(timeout=5)
        except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5)
if __name__=='__main__':main()
