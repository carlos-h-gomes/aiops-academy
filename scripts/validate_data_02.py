"""Verify fixed teaching queries in an ephemeral SQLite database, not PostgreSQL."""
from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'backend/content/fixtures/data-02'
HEADINGS = ('Objetivo observável', 'Contexto e limites', 'Exemplo sintético',
            'Exercício', 'Pistas', 'Solução comentada', 'Critério de conclusão',
            'Variação', 'Referências primárias')


@contextmanager
def database():
    connection = sqlite3.connect(':memory:')
    try:
        connection.execute('PRAGMA foreign_keys = ON')
        for path in (ROOT / 'backend/content/fixtures/data-01/schema.sql',
                     ROOT / 'backend/content/fixtures/data-01/valid.sql',
                     FIXTURE / 'extension.sql'):
            connection.executescript(path.read_text(encoding='utf-8'))
        connection.commit()
        connection.execute('PRAGMA query_only = ON')
        yield connection
    finally:
        connection.close()


def query(connection, name, service, state='ativo'):
    if name not in ('inner', 'left', 'summary'):
        raise ValueError('unknown_query')
    sql = (FIXTURE / f'{name}.sql').read_text(encoding='utf-8')
    return connection.execute(sql, {'servico': service, 'estado': state}).fetchall()


def validate_authoring():
    unit = json.loads((ROOT / 'backend/content/planned-units/data-02.json').read_text(encoding='utf-8'))
    catalog = json.loads((ROOT / 'backend/content/curriculum.json').read_text(encoding='utf-8'))
    entry = next(item for item in catalog['units'] if item['id'] == 'data-02')
    for key in ('id', 'track_id', 'order', 'title', 'summary', 'competencies', 'prerequisites', 'status'):
        if unit[key] != entry[key]:
            raise ValueError(f'catalog_mismatch:{key}')
    if unit['status'] != 'available' or unit['duration_minutes'] is None:
        raise ValueError('published_contract_changed')
    if unit['translations'] != [{'locale': loc, 'authoring_status': status} for loc, status in
                                [('pt-BR', 'authored'), ('en', 'planned'), ('es', 'planned')]]:
        raise ValueError('translation_contract_changed')
    positions = []
    for heading in HEADINGS:
        marker = f'## {heading}\n'
        if unit['body'].count(marker) != 1:
            raise ValueError(f'heading_invalid:{heading}')
        positions.append(unit['body'].index(marker))
    if positions != sorted(positions):
        raise ValueError('heading_order')
    for path in unit['fixture'].values():
        if not (ROOT / path).is_file():
            raise ValueError(f'fixture_missing:{path}')
    if len(unit['sources']) != 2 or any(s['reviewed_on'] != '2026-09-16' for s in unit['sources']):
        raise ValueError('sources_invalid')
    return {'unit': 'data-02', 'status': 'available'}


def validate():
    result = validate_authoring()
    with database() as connection:
        expected = [('inc-100', f'evt-{n:03}', 'rb-quotes-01') for n in (1, 2, 3, 5)]
        checks = (
            (query(connection, 'inner', 'svc-quotes'), expected),
            (query(connection, 'left', 'svc-quotes'), expected + [('inc-300', None, None)]),
            (query(connection, 'left', 'svc-ledger-demo'), [('inc-200', 'evt-004', None)]),
            (query(connection, 'summary', 'svc-quotes'), [('inc-100', 4, 'rb-quotes-01'), ('inc-300', 0, None)]),
            (query(connection, 'summary', "svc-quotes' OR 1=1 --"), []),
        )
        for actual, wanted in checks:
            if actual != wanted:
                raise AssertionError(f'query_result_mismatch:{actual!r}')
    return {**result, 'result_checks': len(checks), 'engine': 'SQLite :memory:'}


if __name__ == '__main__':
    print(json.dumps(validate(), ensure_ascii=False))
