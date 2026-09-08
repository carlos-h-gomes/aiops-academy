"""Run a reviewed argument list with a minimized environment through Harness."""
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
keep = ('PATH', 'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'COMSPEC', 'PATHEXT', 'USERPROFILE', 'LOCALAPPDATA', 'APPDATA', 'PROGRAMFILES', 'PROGRAMFILES(X86)')
env = {k: v for k, v in os.environ.items() if k.upper() in keep}
env.update(PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PIP_DISABLE_PIP_VERSION_CHECK='1', npm_config_update_notifier='false', npm_config_fund='false')
args = sys.argv[1:]
if len(args) < 2:
    raise SystemExit('Usage: bounded.py SECONDS COMMAND [ARGS]')
raise SystemExit(subprocess.call([sys.executable, str(root / 'scripts/safe_exec.py'), '--timeout', args[0], '--tail-lines', '50', '--label', 'academy-check', '--', *args[1:]], env=env))
