from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "scripts"))

from app.services.agent_controller import ControllerState, execute, validate_policy, validate_result
from validate_agents_01_04 import (
    EXPECTED_SCENARIOS,
    load_contract,
    validate_authoring,
    validate_schemas,
    verify_idempotency_and_resume,
    verify_negative_mutations,
    verify_scenarios,
    verify_security_regression,
)


class Agents0104ControllerTests(unittest.TestCase):
    def setUp(self):
        self.request_schema, self.result_schema, self.policy, self.fixtures, self.scenarios = load_contract()
        self.by_id = {item["scenario_id"]: item["request"] for item in self.scenarios}

    def test_four_authored_units_preserve_the_current_catalog_boundary(self):
        result = validate_authoring()
        self.assertEqual(set(result["units"]), {"agents-01", "agents-02", "agents-03", "agents-04"})
        self.assertEqual((result["available"], result["planned"], result["legacy_lessons"]), (50, 0, 30))
        self.assertTrue(all(item["hints"] <= 2 for item in result["units"].values()))

    def test_request_and_result_schemas_are_closed(self):
        result = validate_schemas()
        self.assertEqual(result, {"request_fields": 12, "result_fields": 12, "extra_fields_allowed": 0})

    def test_policy_is_fixture_only_and_has_no_external_capability(self):
        validate_policy(self.policy)
        self.assertEqual(set(self.policy["allowed_actions"]), {"classify_process", "inspect_layers"})
        self.assertTrue(self.policy["capabilities"]["fixture_only"])
        for key in ("shell", "url_input", "network", "child_process", "external_write", "external_approval"):
            self.assertFalse(self.policy["capabilities"][key])

    def test_rule_agent_and_refusal_decisions_are_deterministic(self):
        result = verify_scenarios()
        self.assertEqual(set(result["scenarios"]), set(EXPECTED_SCENARIOS))
        self.assertEqual(result["external_effects"], 0)

    def test_extra_field_wrong_type_shell_and_external_target_are_denied(self):
        result = verify_negative_mutations()
        self.assertEqual(
            set(result),
            {
                "schema_extra_field",
                "action_not_allowed",
                "tool_not_allowed",
                "target_not_allowed",
                "fixture_not_allowed",
                "step_budget_exceeded",
                "schema_step_budget_invalid",
            },
        )
        self.assertTrue(all(state == "blocked" for state in result.values()))

        missing = deepcopy(self.by_id["classify-rule"])
        del missing["approval_id"]
        report = execute(self.policy, self.fixtures, missing, ControllerState())
        self.assertEqual(report["reason"], "schema_required_field_missing")

        invalid_id = deepcopy(self.by_id["classify-rule"])
        invalid_id["request_id"] = ["invalid"]
        report = execute(self.policy, self.fixtures, invalid_id, ControllerState())
        self.assertEqual(report["request_id"], "invalid-request")
        validate_result(report)

    def test_idempotent_repetition_does_not_duplicate_simulated_effect(self):
        state = ControllerState()
        request = deepcopy(self.by_id["classify-rule"])
        first = execute(self.policy, self.fixtures, request, state)
        second = execute(self.policy, self.fixtures, request, state)
        self.assertFalse(first["idempotent"])
        self.assertTrue(second["idempotent"])
        self.assertEqual(first["counters"]["simulated_effects"], 1)
        self.assertEqual(second["counters"]["simulated_effects"], 1)
        self.assertEqual(state.effect_counts["idem-rule"], 1)

    def test_missing_approval_holds_and_safe_resume_completes(self):
        result = verify_idempotency_and_resume()
        self.assertEqual(result["repeated_effects"], 1)
        self.assertEqual(result["resume_effects"], 1)
        self.assertEqual(result["resume_transitions"], 5)

    def test_expired_and_denied_approvals_are_distinct_blocks(self):
        for scenario_id, reason in (
            ("approval-expired-block", "approval_expired"),
            ("approval-denied-block", "approval_denied"),
        ):
            report = execute(self.policy, self.fixtures, deepcopy(self.by_id[scenario_id]), ControllerState())
            self.assertEqual((report["decision"], report["state"], report["reason"]), ("block", "blocked", reason))
            self.assertEqual(report["counters"]["tool_invocations"], 0)

    def test_approval_mismatch_is_denied(self):
        request = deepcopy(self.by_id["approval-missing-hold"])
        request["approval_id"] = "approval-layer-valid"
        request["idempotency_key"] = "idem-other-intent"
        report = execute(self.policy, self.fixtures, request, ControllerState())
        self.assertEqual(report["reason"], "approval_not_bound_to_request")

    def test_step_budget_and_policy_ceiling_are_enforced_before_tool(self):
        for budget, reason in ((1, "step_budget_exceeded"), (5, "step_budget_above_policy")):
            request = deepcopy(self.by_id["classify-rule"])
            request["step_budget"] = budget
            request["idempotency_key"] = f"idem-budget-{budget}"
            report = execute(self.policy, self.fixtures, request, ControllerState())
            self.assertEqual(report["reason"], reason)
            self.assertEqual(report["counters"]["tool_invocations"], 0)

    def test_idempotency_key_conflict_is_blocked(self):
        state = ControllerState()
        first = deepcopy(self.by_id["classify-rule"])
        execute(self.policy, self.fixtures, first, state)
        conflict = deepcopy(first)
        conflict["fixture_id"] = "process-ambiguous"
        conflict["request_id"] = "idempotency-conflict"
        report = execute(self.policy, self.fixtures, conflict, state)
        self.assertEqual((report["decision"], report["reason"]), ("block", "idempotency_conflict"))
        self.assertEqual(state.effect_counts["idem-rule"], 1)

    def test_every_result_is_schema_shaped_and_external_counters_stay_zero(self):
        for request in self.by_id.values():
            report = execute(self.policy, self.fixtures, deepcopy(request), ControllerState())
            validate_result(report)
            self.assertEqual(report["counters"]["network_calls"], 0)
            self.assertEqual(report["counters"]["child_processes"], 0)
            self.assertEqual(report["counters"]["external_writes"], 0)
            serialized = json.dumps(report, ensure_ascii=False)
            self.assertNotIn("http://", serialized)
            self.assertNotIn("https://", serialized)

    def test_security_06_static_policy_remains_green(self):
        self.assertEqual(
            verify_security_regression(),
            {"security_06_allowed": 1, "security_06_denied": 14, "external_effects": 0},
        )


if __name__ == "__main__":
    unittest.main()
