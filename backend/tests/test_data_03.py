from copy import deepcopy
from contextlib import redirect_stdout
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from validate_data_03 import FIXTURE, REFERENCE, grade, load_json, main, summarize, validate, validate_scenario


class Data03Tests(unittest.TestCase):
    def test_authoring_and_reference(self):
        result = validate()
        self.assertEqual(result['correct'], 8)
        self.assertIs(result['runtime_verified'], False)

    def test_loops_multiply_rows_not_estimate_factor(self):
        node = load_json(FIXTURE / 'scenario.json')['repeated_node']
        result = summarize(node)
        self.assertEqual(result['rows_total'], 12)
        self.assertAlmostEqual(result['estimate_factor'], 2 / 3)

    def test_zero_rows_and_unexecuted_node_have_no_ratio(self):
        node = load_json(FIXTURE / 'scenario.json')['before']
        node['actual_rows_per_loop'] = 0
        self.assertIsNone(summarize(node)['estimate_factor'])
        node['loops'] = 0
        self.assertFalse(summarize(node)['executed'])

    def test_invalid_metrics_rejected(self):
        node = load_json(FIXTURE / 'scenario.json')['before']
        for value in (-1, float('nan'), float('inf'), True, '10', None, 1000001, 10 ** 1000):
            with self.subTest(value=value):
                changed = {**node, 'estimated_rows': value}
                with self.assertRaises(ValueError):
                    summarize(changed)
        with self.assertRaises(ValueError):
            summarize({**node, 'loops': 1.5})

    def test_missing_fields_are_not_zero(self):
        node = load_json(FIXTURE / 'scenario.json')['before']
        del node['actual_rows_per_loop']
        with self.assertRaises(ValueError):
            summarize(node)

    def test_runtime_provenance_cannot_be_promoted(self):
        scenario = load_json(FIXTURE / 'scenario.json')
        for field, value in (('origin', 'captured'), ('runtime_verified', True)):
            changed = deepcopy(scenario)
            changed[field] = value
            with self.assertRaises(ValueError):
                validate_scenario(changed)

    def test_each_wrong_answer_is_identified(self):
        for key in REFERENCE:
            answers = deepcopy(REFERENCE)
            answers[key] = None
            self.assertEqual(grade(answers)['review_fields'], [key])

    def test_numeric_booleans_and_benchmark_claims_are_wrong(self):
        answers = {**REFERENCE, 'before_estimate_factor': True, 'cost_is_milliseconds': 0,
                   'speedup_proven': True, 'buffers_available': True}
        self.assertEqual(grade(answers)['correct'], 4)

    def test_wrong_index_order_and_unknown_fields(self):
        answers = {**REFERENCE, 'index_columns': ['ocorrido_em', 'incidente_id']}
        self.assertIn('index_columns', grade(answers)['review_fields'])
        with self.assertRaises(ValueError):
            grade({**REFERENCE, 'unexpected': True})

    def test_file_size_bound_and_invalid_json(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'submission.json'
            path.write_bytes(b' ' * 65537)
            with self.assertRaises(ValueError):
                load_json(path)
            path.write_text('{', encoding='utf-8')
            with self.assertRaises(ValueError):
                load_json(path)

    def test_unfilled_template_is_not_success(self):
        result = grade(load_json(FIXTURE / 'answer-template.json'))
        self.assertEqual(result['correct'], 0)

    def test_large_answer_is_wrong_without_float_overflow(self):
        result = grade({**REFERENCE, 'before_estimate_factor': 10 ** 1000})
        self.assertEqual(result['review_fields'], ['before_estimate_factor'])

    def test_submission_exit_codes_and_feedback(self):
        for answers, expected_exit in ((REFERENCE, 0), ({**REFERENCE, 'speedup_proven': True}, 1), ({}, 2)):
            with patch('sys.argv', ['validate_data_03.py', '--submission']), \
                 patch('validate_data_03.validate', return_value={}), \
                 patch('validate_data_03.load_json', return_value=answers), \
                 redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(), expected_exit)
                if expected_exit == 1:
                    self.assertIn('speedup_proven', output.getvalue())


if __name__ == '__main__':
    unittest.main()
