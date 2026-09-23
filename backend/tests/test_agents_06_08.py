"""Regressions for offline learner scenarios, not real external workflows."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_agents_06_08 import (
    EVALUATORS, evaluate_briefing, evaluate_reconciliation, evaluate_support,
    load_scenarios, validate_authoring, verify_scenarios,
)


class Agents0608Tests(unittest.TestCase):
    def fixture(self, unit_id, scenario_id):
        return deepcopy(next(item["input"] for item in load_scenarios(unit_id) if item["scenario_id"] == scenario_id))

    def test_authored_units_have_complete_guided_practices(self):
        result = validate_authoring()
        self.assertEqual(set(result), set(EVALUATORS))
        self.assertEqual(result["agents-06"]["scenarios"], 6)

    def test_all_scenarios_match_exact_results_without_mutating_inputs(self):
        self.assertEqual(verify_scenarios(), {"agents-06": 6, "agents-07": 5, "agents-08": 5})

    def test_unknown_fields_never_become_capabilities(self):
        for unit_id, evaluator in EVALUATORS.items():
            payload = deepcopy(load_scenarios(unit_id)[0]["input"])
            payload["command"] = "inert-marker"
            with self.subTest(unit_id=unit_id), self.assertRaisesRegex(ValueError, "invalid_contract"):
                evaluator(payload)

    def test_support_requires_applicable_citation_and_never_sends(self):
        payload = self.fixture("agents-06", "routine")
        payload["category"], payload["evidence_ids"] = "performance", ["RB-PERF-1"]
        result = evaluate_support(payload)
        self.assertEqual(result["citations"], ["RB-PERF-1"])
        self.assertFalse(result["sent"])
        self.assertTrue(result["requires_review"])
        payload["evidence_ids"] = ["RB-ACCESS-1", "RB-PERF-1"]
        self.assertEqual(evaluate_support(payload)["reason"], "evidence_not_applicable")

    def test_support_rejects_type_confusion(self):
        payload = self.fixture("agents-06", "routine")
        for field, value in (("contains_sensitive", 0), ("category", []), ("evidence_ids", "RB-ACCESS-1")):
            modified = {**payload, field: value}
            with self.subTest(field=field), self.assertRaises(ValueError):
                evaluate_support(modified)

    def test_briefing_does_not_accept_self_asserted_or_denied_review(self):
        payload = self.fixture("agents-07", "reviewed-draft")
        payload["approval"]["reviewer"] = "assistant"
        self.assertEqual(evaluate_briefing(payload)["reason"], "reviewer_not_allowed")
        payload["approval"]["reviewer"] = "synthetic-reviewer"
        payload["approval"]["decision"] = "denied"
        result = evaluate_briefing(payload)
        self.assertEqual(result["reason"], "approval_denied")
        self.assertFalse(result["publication_allowed"])

    def test_unknown_fact_cannot_be_laundered_through_briefing_or_approval(self):
        payload = self.fixture("agents-07", "reviewed-draft")
        payload["provided_fact_ids"].append("F-GUARANTEE")
        payload["draft_claim_ids"].append("F-GUARANTEE")
        self.assertEqual(evaluate_briefing(payload)["reason"], "unsupported_claim")
        payload = self.fixture("agents-07", "reviewed-draft")
        payload["approval"]["publish"] = True
        with self.assertRaisesRegex(ValueError, "invalid_contract"):
            evaluate_briefing(payload)

    def test_reconciliation_rejects_boolean_float_negative_and_oversized_cents(self):
        for cents in (True, 12.5, -1, 1_000_000_001, "1250"):
            payload = self.fixture("agents-08", "matched")
            payload["ledger"][0]["cents"] = cents
            with self.subTest(cents=cents), self.assertRaisesRegex(ValueError, "invalid_cents"):
                evaluate_reconciliation(payload)

    def test_reconciliation_missing_ledger_and_empty_input_are_distinct(self):
        payload = self.fixture("agents-08", "matched")
        payload["ledger"] = []
        self.assertEqual(evaluate_reconciliation(payload)["exceptions"], [{"transaction_id": "R-100", "reason": "missing_ledger"}])
        payload["statement"] = []
        self.assertEqual(evaluate_reconciliation(payload)["reason"], "no_records")

    def test_duplicate_amounts_cannot_cancel_each_other(self):
        payload = self.fixture("agents-08", "matched")
        payload["ledger"] = [{"transaction_id": "R-100", "cents": 625, "currency": "BRL"}] * 2
        result = evaluate_reconciliation(payload)
        self.assertEqual(result["matched_ids"], [])
        self.assertEqual(result["exceptions"][0]["reason"], "duplicate_id")
        self.assertFalse(result["financial_action_allowed"])

    def test_reconciliation_bounds_currency_and_record_count(self):
        payload = self.fixture("agents-08", "matched")
        payload["ledger"][0]["currency"] = "USD"
        with self.assertRaisesRegex(ValueError, "invalid_currency"):
            evaluate_reconciliation(payload)
        payload = self.fixture("agents-08", "matched")
        payload["ledger"] *= 21
        with self.assertRaisesRegex(ValueError, "invalid_record_limit"):
            evaluate_reconciliation(payload)

    def test_unit_lookup_does_not_accept_paths(self):
        for unit_id in ("../agents-06", "agents-09", "/agents-06"):
            with self.subTest(unit_id=unit_id), self.assertRaisesRegex(ValueError, "unknown_unit"):
                load_scenarios(unit_id)


if __name__ == "__main__":
    unittest.main()
