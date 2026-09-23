from copy import deepcopy
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_security_01_02 import (
    EvidenceRejected,
    EXPECTED_ACCESS_SCENARIOS,
    EXPECTED_EVIDENCE_REJECTIONS,
    _load_security_01_fixture,
    _load_security_02_fixture,
    evaluate_access,
    validate_authored_units,
    validate_redacted_evidence,
    verify_access_scenarios,
    verify_evidence_fixture,
)


class Security0102AuthoringTests(unittest.TestCase):
    def test_authored_portuguese_units_match_planned_catalog(self):
        result = validate_authored_units()
        self.assertEqual(result["available_units"], 50)
        self.assertEqual(result["planned_security_units"], 6)
        self.assertEqual(result["legacy_lessons"], 30)
        self.assertEqual(set(result["units"]), {"security-01", "security-02"})
        self.assertEqual(result["units"]["security-01"]["catalog_status"], "available")
        self.assertEqual(result["units"]["security-02"]["catalog_status"], "available")
        for unit in result["units"].values():
            self.assertEqual(unit["authored_locale"], "pt-BR")
            self.assertEqual(unit["planned_locales"], ["en", "es"])

    def test_four_access_scenarios_match_expected_decisions(self):
        result = verify_access_scenarios()
        self.assertEqual(result["scenario_count"], 4)
        self.assertEqual(result["decisions"], {
            scenario_id: expected["decision"]
            for scenario_id, expected in EXPECTED_ACCESS_SCENARIOS.items()
        })
        self.assertEqual(result["external_actions"], 0)

    def test_read_and_change_require_separate_explicit_grants(self):
        policy, _ = _load_security_01_fixture()
        for action in ("ler", "alterar"):
            with self.subTest(action=action):
                self.assertEqual(
                    evaluate_access(policy, "ana-sre", action, "runbook-alpha"),
                    {"decision": "allow", "reason": "explicit_permission"},
                )
        without_change = deepcopy(policy)
        without_change["grants"] = [
            grant for grant in without_change["grants"] if grant["action"] != "alterar"
        ]
        self.assertEqual(
            evaluate_access(without_change, "ana-sre", "alterar", "runbook-alpha"),
            {"decision": "deny", "reason": "missing_explicit_permission"},
        )

    def test_absence_cross_scope_and_escalation_are_denied(self):
        policy, _ = _load_security_01_fixture()
        cases = [
            ("bia-estagiaria", "ler", "runbook-alpha", "missing_explicit_permission"),
            ("ana-sre", "ler", "runbook-beta", "cross_scope"),
            ("ana-sre", "administrar", "runbook-alpha", "escalation_attempt"),
        ]
        for subject, action, resource, reason in cases:
            with self.subTest(reason=reason):
                self.assertEqual(
                    evaluate_access(policy, subject, action, resource),
                    {"decision": "deny", "reason": reason},
                )

    def test_redacted_output_is_accepted_without_raw_values(self):
        policy, source, valid_output, _ = _load_security_02_fixture()
        self.assertEqual(validate_redacted_evidence(policy, source, valid_output), "accepted")
        serialized = str(valid_output)
        self.assertNotIn(source["secret_marker"], serialized)
        self.assertNotIn(source["study_record"], serialized)
        self.assertEqual(set(valid_output), set(policy["allowed_output_fields"]))

    def test_leaks_missing_redaction_and_extra_field_are_rejected(self):
        result = verify_evidence_fixture()
        self.assertEqual(result["valid_output"], "accepted")
        self.assertEqual(result["rejected_outputs"], EXPECTED_EVIDENCE_REJECTIONS)
        self.assertEqual(result["raw_values_emitted"], 0)
        self.assertEqual(result["external_actions"], 0)

    def test_rejection_message_contains_only_safe_code(self):
        policy, source, _, invalid_paths = _load_security_02_fixture()
        from validate_security_01_02 import _load_json

        for fixture_id, expected_code in EXPECTED_EVIDENCE_REJECTIONS.items():
            with self.subTest(fixture_id=fixture_id):
                with self.assertRaises(EvidenceRejected) as caught:
                    validate_redacted_evidence(policy, source, _load_json(invalid_paths[fixture_id]))
                self.assertEqual(str(caught.exception), expected_code)
                self.assertNotIn(source["secret_marker"], str(caught.exception))
                self.assertNotIn(source["study_record"], str(caught.exception))


if __name__ == "__main__":
    unittest.main()
