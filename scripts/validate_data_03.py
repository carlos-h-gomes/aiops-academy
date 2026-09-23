"""Grade a bounded synthetic EXPLAIN exercise; never run SQL or claim runtime."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'backend/content/fixtures/data-03'
FIELDS = {'node', 'estimated_rows', 'actual_rows_per_loop', 'loops', 'rows_removed_per_loop'}
REFERENCE = {
    'before_estimate_factor': 10,
    'repeated_rows_total': 12,
    'index_columns': ['incidente_id', 'ocorrido_em'],
    'cost_is_milliseconds': False,
    'runtime_verified': False,
    'speedup_proven': False,
    'write_overhead': True,
    'buffers_available': False,
}


def load_json(path):
    # Local authored files only. Bound bytes before parsing, including submissions.
    with path.open('rb') as stream:
        raw = stream.read(65537)
    if len(raw) > 65536:
        raise ValueError('file_too_large')
    return json.loads(raw.decode('utf-8-sig'))


def summarize(node):
    if not isinstance(node, dict) or set(node) != FIELDS:
        raise ValueError('node_fields')
    if node['node'] not in ('Seq Scan', 'Index Scan'):
        raise ValueError('node_type')
    for key in FIELDS - {'node'}:
        value = node[key]
        if type(value) not in (int, float) or not 0 <= value <= 1000000:
            raise ValueError('metric_invalid')
    loops = node['loops']
    if type(loops) is not int:
        raise ValueError('loops_not_integer')
    actual = node['actual_rows_per_loop']
    return {
        'rows_total': actual * loops,
        'estimate_factor': node['estimated_rows'] / actual if actual > 0 and loops > 0 else None,
        'executed': loops > 0,
    }


def validate_scenario(scenario):
    if not isinstance(scenario, dict) or set(scenario) != {
        'schema_version', 'origin', 'runtime_verified', 'description', 'before', 'after', 'repeated_node'
    }:
        raise ValueError('scenario_fields')
    if (scenario['schema_version'] != '1.0' or scenario['origin'] != 'synthetic'
            or scenario['runtime_verified'] is not False or not isinstance(scenario['description'], str)
            or not scenario['description'].strip()):
        raise ValueError('synthetic_provenance_required')
    return {key: summarize(scenario[key]) for key in ('before', 'after', 'repeated_node')}


def grade(answers):
    if not isinstance(answers, dict) or set(answers) != set(REFERENCE):
        raise ValueError('answer_fields')
    wrong = []
    for key, expected in REFERENCE.items():
        value = answers[key]
        if type(expected) is bool:
            correct = type(value) is bool and value == expected
        elif type(expected) is int:
            correct = type(value) in (int, float) and value == expected
        else:
            correct = type(value) is list and value == expected
        if not correct:
            wrong.append(key)
    return {'correct': len(REFERENCE) - len(wrong), 'total': len(REFERENCE), 'review_fields': wrong,
            'runtime_verified': False}


def validate():
    scenario = load_json(FIXTURE / 'scenario.json')
    metrics = validate_scenario(scenario)
    if metrics['before']['estimate_factor'] != REFERENCE['before_estimate_factor']:
        raise ValueError('reference_factor_mismatch')
    if metrics['repeated_node']['rows_total'] != REFERENCE['repeated_rows_total']:
        raise ValueError('reference_loops_mismatch')
    if (scenario['before']['node'] != 'Seq Scan' or scenario['after']['node'] != 'Index Scan'
            or metrics['before']['rows_total'] != 10 or metrics['after']['rows_total'] != 10):
        raise ValueError('scenario_outcome_mismatch')
    unit = load_json(ROOT / 'backend/content/planned-units/data-03.json')
    # Catalog exceeds the bounded exercise file size; it is repository-owned content.
    catalog = json.loads((ROOT / 'backend/content/curriculum.json').read_text(encoding='utf-8'))
    entry = next(u for u in catalog['units'] if u['id'] == 'data-03')
    for key in ('id', 'track_id', 'order', 'title', 'summary', 'status', 'prerequisites', 'competencies'):
        if unit[key] != entry[key]:
            raise ValueError('catalog_mismatch')
    if unit['status'] != 'available' or unit['duration_minutes'] is None:
        raise ValueError('availability_changed')
    if unit['translations'] != [{'locale': loc, 'authoring_status': status} for loc, status in
                                [('pt-BR', 'authored'), ('en', 'planned'), ('es', 'planned')]]:
        raise ValueError('translations_changed')
    headings = ('Objetivo observável', 'Contexto e limites', 'Exemplo sintético', 'Exercício',
                'Pistas', 'Solução comentada', 'Critério de conclusão', 'Variação', 'Referências primárias')
    positions = []
    for heading in headings:
        marker = f'## {heading}\n'
        if unit['body'].count(marker) != 1:
            raise ValueError('heading_invalid')
        positions.append(unit['body'].index(marker))
    if positions != sorted(positions):
        raise ValueError('heading_order')
    for path in unit['fixture'].values():
        if not (ROOT / path).is_file():
            raise ValueError('fixture_missing')
    if len(unit['sources']) != 3 or any(s['reviewed_on'] != '2026-09-16' for s in unit['sources']):
        raise ValueError('sources_invalid')
    return {'unit': 'data-03', 'status': 'available', 'origin': 'synthetic', **grade(REFERENCE)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--submission', action='store_true', help='Grade fixed data-03/submission.json')
    args = parser.parse_args()
    try:
        result = validate()
        if args.submission:
            result = grade(load_json(FIXTURE / 'submission.json'))
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result['correct'] == result['total'] else 1
    except (ValueError, OSError, RecursionError):
        print('Invalid or missing exercise input; check the template and 64 KiB limit.')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
