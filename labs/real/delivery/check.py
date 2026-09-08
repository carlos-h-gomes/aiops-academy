"""Offline tests: python check.py; --solution verifies the reference."""
import argparse
import importlib
import unittest


class DeliveryChecks(unittest.TestCase):
    def setUp(self):
        self.checks = dict(unit='passed', integration='passed', security='passed')

    def test_approved_complete_evidence(self):
        self.assertEqual(code.decide(self.checks, 'approved', True), 'promote')

    def test_waits_for_approval(self):
        self.assertEqual(code.decide(self.checks, 'pending', True), 'hold')

    def test_refusal_and_changed_artifact_block(self):
        self.assertEqual(code.decide(self.checks, 'denied', True), 'block')
        self.assertEqual(code.decide(self.checks, 'approved', False), 'block')

    def test_each_failure_and_missing_result_blocks_before_approval(self):
        for key in self.checks:
            for result in ('failed', 'missing'):
                values = {**self.checks, key:result}
                self.assertEqual(code.decide(values, 'pending', True), 'block')
                self.assertEqual(code.decide(values, 'approved', True), 'block')

    def test_missing_or_unknown_check_is_invalid(self):
        for checks in ({}, {'unit':'passed'}, {**self.checks, 'extra':'passed'}, []):
            with self.assertRaises(ValueError):
                code.decide(checks, 'approved', True)

    def test_wrong_types_and_statuses_are_invalid(self):
        for checks, approval, artifact in [({**self.checks, 'unit':True}, 'approved', True),
                                         ({**self.checks, 'unit':'skipped'}, 'approved', True),
                                         (self.checks, 'yes', True), (self.checks, True, True),
                                         (self.checks, 'approved', 'true'), (self.checks, 'approved', 1)]:
            with self.assertRaises(ValueError):
                code.decide(checks, approval, artifact)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--solution', action='store_true')
    args = parser.parse_args()
    code = importlib.import_module('solution' if args.solution else 'exercise')
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(DeliveryChecks))
    raise SystemExit(0 if result.wasSuccessful() else 1)
