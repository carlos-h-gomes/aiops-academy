"""Reproducible local setup; bounded installers, no global package changes."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
def main():
    if sys.version_info<(3,12):raise SystemExit('Use Python 3.12 ou superior (versao suportada).')
    node=shutil.which('node');npm=shutil.which('npm.cmd' if os.name=='nt' else 'npm')
    if not node or not npm:raise SystemExit('Instale Node.js LTS pela fonte oficial e reabra a janela.')
    version=subprocess.check_output([node,'--version'],text=True,timeout=10).strip().lstrip('v')
    major,minor,*_=map(int,version.split('.'))
    if major<22 or (major==22 and minor<12):raise SystemExit('Use Node LTS 22.12+ ou 24+.')
    env={k:v for k,v in os.environ.items() if k.upper() in ('PATH','SYSTEMROOT','WINDIR','TEMP','TMP','COMSPEC','PATHEXT','USERPROFILE','LOCALAPPDATA','APPDATA','PROGRAMFILES','PROGRAMFILES(X86)')}
    env.update(PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PIP_DISABLE_PIP_VERSION_CHECK='1')
    venv=ROOT/'.venv';python=venv/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    commands=[]
    if not python.exists():commands.append(([sys.executable,'-m','venv',str(venv)],ROOT,60))
    commands.extend([([str(python),'-m','pip','install','--only-binary=:all:','-r','backend/requirements.txt'],ROOT,240),([npm,'ci','--ignore-scripts','--no-audit','--no-fund'],ROOT/'frontend',240),([npm,'run','build'],ROOT/'frontend',120),([str(python),'scripts/package_kit.py'],ROOT,30)])
    for args,cwd,timeout in commands:
        print('Preparando dependencias locais...' if 'build' not in args else 'Compilando interface...',flush=True)
        subprocess.run([sys.executable,str(ROOT/'scripts/safe_exec.py'),'--timeout',str(timeout),'--label','preparacao','--',*args],cwd=cwd,env=env,stdin=subprocess.DEVNULL,check=True,timeout=timeout+15)
    print('Preparacao concluida. Execute iniciar.cmd.')
if __name__=='__main__':
    try:main()
    except (subprocess.CalledProcessError,subprocess.TimeoutExpired,OSError) as e:raise SystemExit(f'Preparacao interrompida: {e}')
