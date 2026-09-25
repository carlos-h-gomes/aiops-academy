"""SQLite persistence with atomic read-modify-write and separate namespaces."""
import json
import os
import sqlite3
from datetime import date
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DB = Path(os.environ.get('ACADEMY_DB',str(ROOT / 'data/academy.sqlite3')))

@contextmanager
def transaction():
    DB.parent.mkdir(parents=True,exist_ok=True)
    connection=sqlite3.connect(DB,timeout=5)
    try:
        connection.execute('CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        connection.execute('BEGIN IMMEDIATE')
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

def read(connection,key,default=None):
    row=connection.execute('SELECT value FROM state WHERE key=?',(key,)).fetchone()
    return json.loads(row[0]) if row else default

def write(connection,key,value):
    connection.execute('INSERT INTO state(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(key,json.dumps(value,ensure_ascii=False,allow_nan=False)))

def default_progress():
    return dict(settings=dict(start_date=date.today().isoformat(),daily_hours=1),notes={},completed=[],quizzes={},labs={},reviews={},unit_progress={})

def hydrate_progress(value):
    """Additive compatibility for pre-unit-progress local backups and databases."""
    if not isinstance(value,dict):
        raise ValueError('Progresso local inválido.')
    default=default_progress()
    hydrated={**default,**value}
    if not isinstance(hydrated['unit_progress'],dict):
        raise ValueError('Progresso das unidades inválido.')
    return hydrated

def progress():
    with transaction() as db:
        value=read(db,'progress')
        if value is None:
            value=default_progress()
            write(db,'progress',value)
        return hydrate_progress(value)

def update_progress(fn):
    with transaction() as db:
        value=hydrate_progress(read(db,'progress',default_progress()))
        result=fn(value)
        write(db,'progress',value)
        return value if result is None else result

def session_create(value):
    import uuid
    with transaction() as db:
        count=db.execute("SELECT count(*) FROM state WHERE key LIKE 'session:%'").fetchone()[0]
        if count >= 500:
            db.execute("DELETE FROM state WHERE rowid IN (SELECT rowid FROM state WHERE key LIKE 'session:%' ORDER BY rowid LIMIT 100)")
        sid=uuid.uuid4().hex
        write(db,'session:'+sid,value)
        return sid

def session_update(sid,fn):
    with transaction() as db:
        value=read(db,'session:'+sid)
        if value is None:
            raise ValueError('Sessão ausente ou expirada. Inicie um novo laboratório.')
        result=fn(value)
        write(db,'session:'+sid,value)
        return result
