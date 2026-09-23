"""Offline reference checks for fixed Data 04-06 fixtures; no app API imports."""
import argparse
from contextlib import closing
import hashlib
import json
import math
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
UNITS = ('data-04', 'data-05', 'data-06')
HEADINGS = ('Objetivo observável', 'Contexto e limites', 'Exemplo sintético',
            'Exercício', 'Pistas', 'Solução comentada', 'Critério de conclusão',
            'Variação', 'Referências primárias')


def load_json(path):
    with path.open('rb') as stream:
        raw = stream.read(65537)
    if len(raw) > 65536:
        raise ValueError('file_too_large')
    return json.loads(raw.decode('utf-8-sig'))


def fixture(unit_id):
    if unit_id not in UNITS:
        raise ValueError('unknown_unit')
    value = load_json(ROOT / 'backend/content/fixtures' / unit_id / 'scenario.json')
    if (value.get('unit_id') != unit_id or value.get('schema_version') != '1.0'
            or value.get('origin') != 'synthetic'):
        raise ValueError('fixture_identity')
    return value


def snapshot(connection):
    """Canonical known-table content, not an authenticity or schema certificate."""
    value = {
        'services': connection.execute('SELECT id FROM services ORDER BY id').fetchall(),
        'incidents': connection.execute(
            'SELECT id, service_id, state FROM incidents ORDER BY id').fetchall(),
    }
    digest = hashlib.sha256(json.dumps(value, sort_keys=True).encode('utf-8')).hexdigest()
    return value, digest


def copy_to_empty(source, target):
    """Native SQLite backup, only between reviewed caller-created connections."""
    if source is target:
        raise ValueError('same_database')
    if source.in_transaction or target.in_transaction:
        raise ValueError('transaction_not_closed')
    if target.execute("SELECT COUNT(*) FROM sqlite_master").fetchone()[0]:
        raise ValueError('destination_not_empty')
    source.backup(target)


def transaction_restore_demo():
    scenario = fixture('data-04')
    with closing(sqlite3.connect(':memory:')) as source, \
            closing(sqlite3.connect(':memory:')) as target:
        source.execute('PRAGMA foreign_keys = ON')
        target.execute('PRAGMA foreign_keys = ON')
        source.executescript('''
            CREATE TABLE services(id TEXT PRIMARY KEY NOT NULL);
            CREATE TABLE incidents(
                id TEXT PRIMARY KEY NOT NULL,
                service_id TEXT NOT NULL REFERENCES services(id),
                state TEXT NOT NULL CHECK(state IN ('aberto', 'resolvido')));
        ''')
        source.executemany('INSERT INTO services VALUES (?)', scenario['services'])
        source.executemany('INSERT INTO incidents VALUES (?, ?, ?)', scenario['incidents'])
        source.commit()
        baseline = snapshot(source)
        try:
            source.execute("UPDATE incidents SET state='resolvido' WHERE id='inc-100'")
            source.execute("INSERT INTO incidents VALUES ('inc-200', 'missing-service', 'aberto')")
        except sqlite3.IntegrityError:
            source.rollback()
        else:
            source.rollback()
            raise AssertionError('invalid_fk_was_accepted')
        if snapshot(source) != baseline:
            raise AssertionError('rollback_changed_source')
        copy_to_empty(source, target)
        matching = snapshot(target) == baseline
        valid_fk = target.execute('PRAGMA foreign_key_check').fetchall() == []
        target.execute("UPDATE incidents SET state='resolvido' WHERE id='inc-100'")
        target.commit()
        return {
            'after_rollback': source.execute(
                "SELECT state FROM incidents WHERE id='inc-100'").fetchone()[0],
            'backup_destination': 'nova_conexao',
            'source_unchanged': snapshot(source) == baseline,
            'rows_and_checksum_match': matching,
            'foreign_keys_valid': valid_fk,
            'postgresql_verified': False,
        }


def vector(value):
    if (type(value) is not list or len(value) != 2
            or any(type(n) not in (int, float) or not -1000 <= n <= 1000
                   or not math.isfinite(n) for n in value)):
        raise ValueError('invalid_vector')
    return value


def ranking(documents, query, audience):
    vector(query)
    if audience not in ('student', 'instructor'):
        raise ValueError('invalid_audience')
    if type(documents) is not list or len(documents) > 100:
        raise ValueError('invalid_documents')
    seen, candidates = set(), []
    for document in documents:
        if (type(document) is not dict
                or set(document) != {'id', 'audience', 'current', 'vector', 'text'}
                or type(document['id']) is not str or not 1 <= len(document['id']) <= 64
                or document['id'] in seen
                or document['audience'] not in ('student', 'instructor')
                or type(document['current']) is not bool
                or type(document['text']) is not str or len(document['text']) > 2000):
            raise ValueError('invalid_document')
        seen.add(document['id'])
        vector(document['vector'])
        if document['audience'] == audience and document['current']:
            distance = sum((a - b) ** 2 for a, b in zip(query, document['vector']))
            candidates.append((distance, document['id']))
    return [identity for _, identity in sorted(candidates)]


def rag_decision(scenario, case):
    """Closed authored claims only; document prose is never parsed as policy."""
    if (type(case) is not dict or set(case) != {'id', 'claim', 'citations'}
            or type(case['claim']) is not str or not 1 <= len(case['claim']) <= 64
            or type(case['citations']) is not list or len(case['citations']) > 8):
        raise ValueError('invalid_case')
    eligible = {d['id']: d for d in scenario['documents']
                if d['audience'] == scenario['audience'] and d['current']}
    supported = False
    for citation in case['citations']:
        if (type(citation) is not dict or set(citation) != {'id', 'version'}
                or type(citation['id']) is not str or not 1 <= len(citation['id']) <= 64
                or type(citation['version']) is not int or citation['version'] < 1):
            raise ValueError('invalid_citation')
        document = eligible.get(citation['id'])
        if document is None or document['version'] != citation['version']:
            return 'abster'
        if case['claim'] not in document['claims']:
            return 'abster'
        supported = True
    return 'responder' if supported else 'abster'


def grade(unit_id, answers):
    expected = fixture(unit_id)['expected']
    if type(answers) is not dict or set(answers) != set(expected):
        raise ValueError('answer_fields')
    wrong = [key for key, wanted in expected.items()
             if type(answers[key]) is not type(wanted) or answers[key] != wanted]
    return {'unit': unit_id, 'correct': len(expected) - len(wrong),
            'total': len(expected), 'review_fields': wrong, 'origin': 'synthetic'}


def validate(unit_id):
    scenario = fixture(unit_id)
    unit = load_json(ROOT / 'backend/content/planned-units' / f'{unit_id}.json')
    if (unit['id'] != unit_id or unit['status'] != 'available'
            or unit['duration_minutes'] is None):
        raise ValueError('published_contract_changed')
    positions = []
    for heading in HEADINGS:
        marker = f'## {heading}\n'
        if unit['body'].count(marker) != 1:
            raise ValueError('heading_invalid')
        positions.append(unit['body'].index(marker))
    if positions != sorted(positions):
        raise ValueError('heading_order')
    for path in unit['fixture'].values():
        if not (ROOT / path).is_file():
            raise ValueError('fixture_missing')
    if unit_id == 'data-04':
        actual = transaction_restore_demo()
    elif unit_id == 'data-05':
        order = ranking(scenario['documents'], scenario['query_vector'], scenario['audience'])
        actual = {'ranking': order, 'restricted_returned': 'rb-admin' in order,
                  'stale_returned': 'rb-old' in order, 'filter_stage': 'antes_do_ranking',
                  'similarity_proves_truth': False, 'pgvector_verified': False}
    else:
        actual = {case['id']: rag_decision(scenario, case) for case in scenario['cases']}
    result = grade(unit_id, actual)
    if result['correct'] != result['total']:
        raise AssertionError('reference_mismatch')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unit', required=True, choices=UNITS)
    parser.add_argument('--submission', action='store_true', help='Read the fixed unit submission.json')
    args = parser.parse_args()
    try:
        result = validate(args.unit)
        if args.submission:
            result = grade(args.unit, load_json(
                ROOT / 'backend/content/fixtures' / args.unit / 'submission.json'))
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result['correct'] == result['total'] else 1
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        print('Entrada inválida ou ausente; confira o modelo e o limite de 64 KiB.')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
