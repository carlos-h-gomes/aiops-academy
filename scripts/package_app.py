"""Portable source + built UI, without installed runtimes or learner state."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.2.0-beta.3'
PUBLIC_TREE_ROOTS = {'backend', 'frontend', 'cloudflare', 'scripts', 'labs', 'schemas', 'artifacts', '.github'}
PUBLIC_ROOT_FILES = {
    '.editorconfig', '.gitattributes', '.gitignore', 'CHANGELOG.md', 'CONTENT-LICENSE.md',
    'CONTRIBUTING.md', 'iniciar.cmd', 'launcher.py', 'LICENSE', 'preparar.cmd', 'README.md',
    'ROADMAP.md', 'SECURITY.md',
}
PUBLIC_DOCUMENTS = {
    'README.md', 'CONTRIBUTING.md', 'SECURITY.md', 'LICENSE', 'CONTENT-LICENSE.md',
    'CHANGELOG.md', 'ROADMAP.md', 'docs/USER-MANUAL.md',
    'docs/TECHNICAL-DOCUMENTATION.md', 'docs/VALIDATION.md',
    'docs/architecture/DIRECTORY-MAP.md',
}
PUBLIC_DOCS = {name for name in PUBLIC_DOCUMENTS if name.startswith('docs/')}
REMOVED_DOCUMENTS = {
    'docs/planning/GITHUB-SETUP.md',
    'docs/planning/V1-BACKLOG.md', 'docs/planning/V1-PROPOSTA.md',
    'docs/research/AIOPS-ACADEMY-ESTUDO-2026-09-07.md',
}
EXCLUDED_PARTS = {'node_modules', '.venv', '__pycache__', 'workspace', '.git', 'qa', '_qa'}
EXCLUDED_PREFIXES = (
    ('data',),
    ('docs', 'ai'),
    ('cloudflare', 'dist'),
    ('backend', 'content', 'fixtures'),
    ('labs', 'agents-processes-pilot'),
    ('labs', 'observability-pilot'),
)
EXCLUDED_FILES = {'backend/app/services/agent_controller.py'}
EXCLUDED_NAME_PREFIXES = ('test_data_', 'test_security_', 'test_agents_', 'validate_data_', 'validate_security_', 'validate_agents_')
SENSITIVE_SUFFIXES = {'.pyc', '.sqlite3', '.sqlite', '.db', '.log', '.key', '.pem', '.p12'}
ARTIFACT_NAMES = {'aiops-labs-reais.zip', 'kit-manifest.json'}
PUBLISHED_LESSON_PATHS = frozenset({
    *(f'backend/content/planned-units/data-{number:02d}.json' for number in range(1, 7)),
    *(f'backend/content/planned-units/security-{number:02d}.json' for number in range(1, 7)),
    *(f'backend/content/planned-units/agents-{number:02d}.json' for number in range(1, 9)),
})


def _parts(relative_path):
    path = PurePosixPath(str(relative_path).replace('\\', '/'))
    if path.is_absolute() or not path.parts or '..' in path.parts:
        raise ValueError(f'package path must be a safe relative path: {relative_path!r}')
    return path, path.parts, path.as_posix()


def _has_prefix(parts, prefix):
    return parts[:len(prefix)] == prefix


def is_package_path(relative_path):
    """Return whether a simulated relative file path belongs in the package."""
    path, parts, name = _parts(relative_path)
    if set(parts) & EXCLUDED_PARTS:
        return False
    if any(_has_prefix(parts, prefix) for prefix in EXCLUDED_PREFIXES):
        return False
    if _has_prefix(parts, ('backend', 'content', 'planned-units')):
        return name in PUBLISHED_LESSON_PATHS
    if name in EXCLUDED_FILES or path.name.startswith(EXCLUDED_NAME_PREFIXES) or path.name.startswith('.env') or path.suffix.lower() in SENSITIVE_SUFFIXES:
        return False
    if len(parts) == 1:
        return name in PUBLIC_ROOT_FILES
    if parts[0] == 'docs':
        return name in PUBLIC_DOCS
    if parts[0] not in PUBLIC_TREE_ROOTS:
        return False
    if parts[0] == 'artifacts':
        return len(parts) == 2 and path.name in ARTIFACT_NAMES
    return True


def select_package_paths(relative_paths):
    """Select package members from paths supplied by a caller; no filesystem access."""
    return sorted({
        PurePosixPath(str(path).replace('\\', '/')).as_posix()
        for path in relative_paths
        if is_package_path(path)
    })


def assert_selection_boundary(names):
    selected = set(names)
    assert PUBLIC_DOCUMENTS <= selected
    assert PUBLISHED_LESSON_PATHS <= selected
    assert {name for name in selected if name.startswith('docs/')} == PUBLIC_DOCS
    assert not REMOVED_DOCUMENTS & selected
    assert {name for name in selected if name.startswith('artifacts/')} <= {
        f'artifacts/{name}' for name in ARTIFACT_NAMES
    }
    assert not EXCLUDED_FILES & selected
    assert not any(
        any(_has_prefix(PurePosixPath(name).parts, prefix) for prefix in EXCLUDED_PREFIXES)
        for name in selected
    )


def write(z, name, body):
    info = zipfile.ZipInfo(name, date_time=(2026, 9, 6, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    z.writestr(info, body)


def build_package():
    candidates = [p for p in ROOT.rglob('*') if p.is_file()]
    selected_names = select_package_paths(
        (p.relative_to(ROOT).as_posix() for p in candidates),
    )
    paths = [ROOT/name for name in selected_names]
    manifest = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in zip(selected_names, paths)}
    assert {
        'frontend/src/data/types.ts', 'frontend/src/data/curriculum.ts',
        'backend/content/curriculum.json', 'schemas/curriculum.schema.json',
    } <= manifest.keys()
    assert_selection_boundary(manifest)

    published_unit_ids = [PurePosixPath(name).stem for name in sorted(PUBLISHED_LESSON_PATHS)]
    target = ROOT/f'artifacts/aiops-academy-{VERSION}-windows.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, path in zip(selected_names, paths):
            write(z, name, path.read_bytes())
        write(z, 'MANIFEST.json', json.dumps(manifest, sort_keys=True, indent=2).encode())
    with tempfile.TemporaryDirectory(prefix='academy-delivery-') as temp, zipfile.ZipFile(target) as z:
        dest = Path(temp).resolve()
        assert sum(i.file_size for i in z.infolist()) < 20_000_000
        for info in z.infolist():
            path = (dest/info.filename).resolve()
            assert path.is_relative_to(dest) and not path.exists()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(z.read(info))
            if info.filename != 'MANIFEST.json':
                assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest[info.filename]
        env = {k: v for k, v in os.environ.items() if k.upper() in ('SYSTEMROOT', 'WINDIR', 'PATH', 'TEMP', 'TMP')}
        env.update(PYTHONUTF8='1', ACADEMY_DB=str(dest/'data/probe.sqlite3'))
        probe = (
            "import sys;sys.path.insert(0,'backend');from app.main import app;from fastapi.testclient import TestClient;"
            "c=TestClient(app,base_url='http://127.0.0.1');assert c.get('/').status_code==200;"
            "assert len(c.get('/api/v1/course').json()['lessons'])==30;catalog=c.get('/api/v1/curriculum').json();"
            "assert len(catalog['tracks'])==4;assert len(catalog['units'])==50;"
            f"unit_ids={published_unit_ids!r};"
            "assert all(c.get('/api/v1/units/'+unit).status_code==200 for unit in unit_ids);"
            "assert all(c.get('/api/v1/units/'+unit+'/lab').status_code==200 for unit in unit_ids);"
            "assert c.get('/api/v1/kit').status_code==200;assert c.get('/_qa/audit.html').status_code==404;"
            "print('fresh extraction smoke passed')"
        )
        check = subprocess.run([str(ROOT/'.venv/Scripts/python.exe'), '-c', probe], cwd=dest, env=env, capture_output=True, text=True, timeout=20)
        if check.returncode:
            detail = (check.stdout + check.stderr).strip()
            raise RuntimeError(detail[-4000:])
    try:
        source_commit = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, timeout=10
        ).strip()
        if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True, timeout=10).strip():
            source_commit = 'uncommitted'
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        source_commit = 'uncommitted'
    report = {
        'product': 'AIOps Academy',
        'version': VERSION,
        'archive': target.name,
        'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
        'files': len(paths)+1,
        'source_commit': source_commit,
        'target': 'Windows local loopback; Python 3.12+ and Node LTS 22.12+/24+ for preparation',
        'builder': f'Python {platform.python_version()} on {platform.system()} {platform.release()}',
        'lock_sha256': {
            'backend/requirements.txt': hashlib.sha256((ROOT/'backend/requirements.txt').read_bytes()).hexdigest(),
            'frontend/package-lock.json': hashlib.sha256((ROOT/'frontend/package-lock.json').read_bytes()).hexdigest(),
        },
        'fresh_extraction': 'passed',
        'smoke': 'API, UI file, course, kit, QA absence passed with existing verified Python runtime',
        'excluded': ['venv', 'node_modules', 'learner database', 'QA database', 'private docs/ai memory', 'secrets'],
        'install_scope': 'Clean preparation was exercised in a new directory on the same Windows computer; installation on a second computer was not executed.',
    }
    (ROOT/'artifacts/release-manifest.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


def main():
    argparse.ArgumentParser(
        description='Build the curated local beta; only published guided lessons are included and maintenance fixtures/pilots are excluded.'
    ).parse_args()
    build_package()


if __name__ == '__main__':
    main()
