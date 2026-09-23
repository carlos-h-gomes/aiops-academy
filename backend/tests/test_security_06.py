from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_security_06 import (
    EXPECTED_SCENARIOS,
    _load_fixtures,
    evaluate_request,
    validate_policy,
    validate_request_schema,
    validate_security_06_authoring,
    verify_policy_fixtures,
    verify_security_01_05_regressions,
)


class Security06AgentPolicyTests(unittest.TestCase):
    def test_authoring_is_complete_and_catalog_is_published(self):
        result = validate_security_06_authoring()
        self.assertEqual(result["unit"], "security-06")
        self.assertEqual(result["catalog_status"], "available")
        self.assertEqual(result["authored_locale"], "pt-BR")
        self.assertEqual(result["planned_locales"], ["en", "es"])
        self.assertEqual(result["dated_primary_sources"], 4)
        self.assertEqual(result["available_units"], 50)
        self.assertEqual(result["planned_units"], 0)
        self.assertEqual(result["legacy_lessons"], 30)

    def test_schema_closes_request_and_all_text_channels(self):
        schema, _, _ = _load_fixtures()
        validate_request_schema(schema)
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(schema["properties"]))
        self.assertEqual(
            {
                "user_input",
                "retrieved_context",
                "tool_output",
            },
            {
                field
                for field, definition in schema["properties"].items()
                if definition == {"$ref": "#/$defs/untrustedText"}
            },
        )

    def test_policy_has_no_runtime_capability(self):
        _, policy, _ = _load_fixtures()
        validate_policy(policy)
        self.assertEqual(policy["allowed_operations"], ["read_fixture"])
        self.assertEqual(policy["allowed_tools"], ["fixture_reader"])
        self.assertTrue(all(value is False for value in policy["capability_statement"].values()))

    def test_fixture_matrix_allows_one_and_denies_fourteen(self):
        result = verify_policy_fixtures()
        self.assertEqual(set(result["scenarios"]), set(EXPECTED_SCENARIOS))
        self.assertEqual(result["allowed"], 1)
        self.assertEqual(result["denied"], 14)
        self.assertEqual(result["schema_extra_fields_allowed"], 0)
        self.assertEqual(result["input_mutations"], 0)
        for key in ("tool_invocations", "network_calls", "child_processes", "external_writes"):
            self.assertEqual(result[key], 0)

    def test_extra_and_missing_fields_are_denied_by_schema(self):
        schema, policy, scenarios = _load_fixtures()
        allowed = next(item["request"] for item in scenarios if item["scenario_id"] == "allow-authorized-read")

        extra = deepcopy(allowed)
        extra["command"] = "INERT-NOT-A-COMMAND"
        report = evaluate_request(policy, schema, extra)
        self.assertEqual((report["decision"], report["reason"]), ("deny", "schema_extra_field"))

        missing = deepcopy(allowed)
        del missing["approval_id"]
        report = evaluate_request(policy, schema, missing)
        self.assertEqual(
            (report["decision"], report["reason"]),
            ("deny", "schema_required_field_missing"),
        )

    def test_wrong_types_and_oversized_text_are_denied(self):
        schema, policy, scenarios = _load_fixtures()
        allowed = next(item["request"] for item in scenarios if item["scenario_id"] == "allow-authorized-read")

        wrong_type = deepcopy(allowed)
        wrong_type["subject"] = ["learner-agent"]
        report = evaluate_request(policy, schema, wrong_type)
        self.assertEqual(report["reason"], "schema_identifier_invalid")

        oversized = deepcopy(allowed)
        oversized["retrieved_context"] = "x" * 501
        report = evaluate_request(policy, schema, oversized)
        self.assertEqual(report["reason"], "schema_untrusted_text_invalid")

    def test_all_text_channels_are_untrusted_and_override_attempts_are_inert(self):
        schema, policy, scenarios = _load_fixtures()
        scenario_ids = {
            "deny-user-prompt-injection",
            "deny-retrieved-prompt-injection",
            "deny-tool-output-prompt-injection",
        }
        selected = [item for item in scenarios if item["scenario_id"] in scenario_ids]
        self.assertEqual(len(selected), 3)
        policy_before = deepcopy(policy)
        for scenario in selected:
            request_before = deepcopy(scenario["request"])
            report = evaluate_request(policy, schema, scenario["request"])
            self.assertEqual((report["decision"], report["reason"]), ("deny", "text_policy_override_attempt"))
            self.assertTrue(any(flag.startswith("policy_override_attempt:") for flag in report["flags"]))
            self.assertEqual(scenario["request"], request_before)
        self.assertEqual(policy, policy_before)

    def test_text_claim_does_not_replace_structured_authorization(self):
        schema, policy, scenarios = _load_fixtures()
        scenario = next(item for item in scenarios if item["scenario_id"] == "deny-missing-authorization")
        self.assertIn("autorizado", scenario["request"]["user_input"])
        report = evaluate_request(policy, schema, scenario["request"])
        self.assertEqual((report["decision"], report["reason"]), ("deny", "authorization_missing"))

    def test_sensitive_marker_is_never_echoed(self):
        schema, policy, scenarios = _load_fixtures()
        scenario = next(item for item in scenarios if item["scenario_id"] == "deny-false-sensitive-data")
        marker = policy["content_controls"]["sensitive_markers"][0]
        report = evaluate_request(policy, schema, scenario["request"])
        serialized = json.dumps(report, ensure_ascii=False, sort_keys=True)
        self.assertEqual(report["reason"], "sensitive_data_in_untrusted_text")
        self.assertNotIn(marker, serialized)
        self.assertIn("sensitive_marker:retrieved_context", report["flags"])

    def test_tool_scope_authorization_and_approval_denials_are_typed(self):
        schema, policy, scenarios = _load_fixtures()
        expected = {
            "deny-tool-not-allowed": "tool_not_allowed",
            "deny-target-out-of-scope": "target_out_of_scope",
            "deny-expired-authorization": "authorization_expired",
            "deny-authorization-mismatch": "authorization_not_bound_to_request",
            "deny-missing-approval": "approval_missing",
            "deny-expired-approval": "approval_expired",
            "deny-approval-mismatch": "approval_not_bound_to_request",
        }
        for scenario in scenarios:
            if scenario["scenario_id"] in expected:
                report = evaluate_request(policy, schema, scenario["request"])
                self.assertEqual(report["reason"], expected[scenario["scenario_id"]])
                self.assertEqual(report["decision"], "deny")

    def test_policy_rejects_extra_configuration(self):
        _, policy, _ = _load_fixtures()
        tampered = deepcopy(policy)
        tampered["prompt_can_override"] = True
        with self.assertRaisesRegex(ValueError, "contrato estrito"):
            validate_policy(tampered)

    def test_security_01_05_contracts_remain_green(self):
        result = verify_security_01_05_regressions()
        self.assertEqual(
            result["authored_units"],
            ["security-01", "security-02", "security-03", "security-04", "security-05"],
        )
        self.assertEqual(result["security_01_03_external_actions"], 0)
        self.assertEqual(result["security_04_05_external_actions"], 0)
        self.assertEqual((result["supply_approved"], result["supply_blocked"], result["supply_review"]), (1, 4, 1))
        self.assertEqual((result["incident_completed"], result["incident_rejected"]), (1, 5))


if __name__ == "__main__":
    unittest.main()
