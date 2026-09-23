from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_security_04_05 import (
    INCIDENT_EXPECTED,
    SUPPLY_EXPECTED,
    _load_unit_fixtures,
    evaluate_incident_scenario,
    evaluate_supply_scenario,
    validate_authored_units,
    validate_incident_scenario,
    validate_supply_scenario,
    verify_incident_fixtures,
    verify_security_01_03_regressions,
    verify_supply_fixtures,
)


class Security0405Tests(unittest.TestCase):
    def test_authored_units_match_published_catalog(self):
        result = validate_authored_units()
        self.assertEqual(set(result["units"]), {"security-04", "security-05"})
        self.assertEqual(result["available_units"], 50)
        self.assertEqual(result["planned_units"], 0)
        self.assertEqual(result["legacy_lessons"], 30)
        for unit in result["units"].values():
            self.assertEqual(unit["catalog_status"], "available")
            self.assertEqual(unit["authored_locale"], "pt-BR")
            self.assertEqual(unit["planned_locales"], ["en", "es"])

    def test_supply_fixtures_have_expected_approve_block_review_matrix(self):
        result = verify_supply_fixtures()
        self.assertEqual(result["approved"], 1)
        self.assertEqual(result["blocked"], 4)
        self.assertEqual(result["review"], 1)
        self.assertEqual(result["image_downloads"], 0)
        self.assertEqual(result["scanner_invocations"], 0)
        for scenario_id, (decision, codes) in SUPPLY_EXPECTED.items():
            self.assertEqual(result["scenarios"][scenario_id], {"decision": decision, "codes": codes})

    def test_supply_variations_block_missing_control_and_subject_mismatch(self):
        policy, scenarios = _load_unit_fixtures("security-04")
        approved = next(item for item in scenarios if item["scenario_id"] == "approve-pinned-fixture")
        missing_control = deepcopy(approved)
        missing_control["scenario_id"] = "variation-missing-control"
        missing_control["manifest"]["runtime_controls"]["resource_limits_declared"] = False
        report = evaluate_supply_scenario(policy, missing_control)
        self.assertEqual(report["decision"], "block")
        self.assertEqual(report["findings"][0]["code"], "runtime_control_missing:resource_limits_declared")

        mismatch = deepcopy(approved)
        mismatch["scenario_id"] = "variation-subject-mismatch"
        mismatch["manifest"]["provenance"]["subject_digest"] = "sha256:" + "f" * 64
        report = evaluate_supply_scenario(policy, mismatch)
        self.assertEqual(report["decision"], "block")
        self.assertEqual(report["findings"][0]["code"], "provenance_subject_mismatch")

    def test_supply_reports_are_minimal_and_do_not_echo_manifest_or_components(self):
        policy, scenarios = _load_unit_fixtures("security-04")
        for scenario in scenarios:
            report = evaluate_supply_scenario(policy, scenario)
            serialized = json.dumps(report, ensure_ascii=False, sort_keys=True)
            self.assertEqual(set(report), {"scenario_id", "decision", "findings"})
            self.assertNotIn(scenario["manifest"]["image"]["reference"], serialized)
            for component in scenario["sbom"]["components"]:
                self.assertNotIn(component["name"], serialized)

    def test_supply_shape_rejects_extra_fields(self):
        _, scenarios = _load_unit_fixtures("security-04")
        malformed = deepcopy(scenarios[0])
        malformed["manifest"]["command"] = "not-allowed"
        with self.assertRaisesRegex(ValueError, "Manifesto sintético"):
            validate_supply_scenario(malformed)

    def test_incident_fixtures_accept_one_and_reject_five_before_state(self):
        result = verify_incident_fixtures()
        self.assertEqual(result["completed"], 1)
        self.assertEqual(result["rejected"], 5)
        self.assertTrue(result["origin_unchanged"])
        self.assertEqual(result["repeatable_resets"], 2)
        self.assertEqual(result["network_calls"], 0)
        self.assertEqual(result["child_processes"], 0)
        self.assertEqual(result["real_restores"], 0)
        self.assertEqual(result["external_writes"], 0)
        for scenario_id, (decision, reasons) in INCIDENT_EXPECTED.items():
            self.assertEqual(result["scenarios"][scenario_id]["decision"], decision)
            if reasons:
                self.assertEqual(result["scenarios"][scenario_id]["reasons"], reasons)

    def test_incident_origin_is_immutable_and_reset_is_repeatable(self):
        policy, scenarios = _load_unit_fixtures("security-05")
        accepted = next(item for item in scenarios if item["scenario_id"] == "recover-authorized-copy")
        origin_before = deepcopy(accepted["incident"]["source_snapshot"])
        report, session = evaluate_incident_scenario(policy, accepted)
        self.assertEqual(report["decision"], "complete")
        self.assertEqual(accepted["incident"]["source_snapshot"], origin_before)
        self.assertTrue(report["origin_unchanged"])
        self.assertNotEqual(accepted["incident"]["source_id"], session.state["destination"])
        first = session.reset()
        second = session.reset()
        self.assertEqual(first, second)
        self.assertEqual(first["timeline"], [])
        self.assertIsNone(first["destination"])
        self.assertIsNone(first["recovered_snapshot"])

    def test_incident_rejections_do_not_transition_or_echo_excess_evidence(self):
        policy, scenarios = _load_unit_fixtures("security-05")
        for scenario in scenarios:
            if scenario["scenario_id"] == "recover-authorized-copy":
                continue
            report, session = evaluate_incident_scenario(policy, scenario)
            serialized = json.dumps(report, ensure_ascii=False, sort_keys=True)
            self.assertEqual(report["decision"], "reject")
            self.assertEqual(report["completed_stages"], [])
            self.assertIsNone(session)
            self.assertNotIn("CONTEUDO-INERTE-QUE-NAO-DEVE-SER-PERSISTIDO", serialized)
            self.assertNotIn("source_snapshot", serialized)

    def test_incident_variations_reject_unapproved_containment_and_empty_prevention(self):
        policy, scenarios = _load_unit_fixtures("security-05")
        accepted = next(item for item in scenarios if item["scenario_id"] == "recover-authorized-copy")
        containment = deepcopy(accepted)
        containment["scenario_id"] = "variation-containment"
        containment["containment"]["action"] = "desligar-producao"
        report, session = evaluate_incident_scenario(policy, containment)
        self.assertEqual(report["reasons"], ["containment_action_not_allowed"])
        self.assertIsNone(session)

        malformed = deepcopy(accepted)
        malformed["prevention"]["control"] = ""
        with self.assertRaisesRegex(ValueError, "prevention.control"):
            validate_incident_scenario(malformed)

    def test_security_01_03_contracts_remain_green(self):
        result = verify_security_01_03_regressions()
        self.assertEqual(result["authored_units"], ["security-01", "security-02", "security-03"])
        self.assertEqual(result["access_scenarios"], 4)
        self.assertEqual(result["evidence_rejections"], 4)
        self.assertEqual(result["hardening_acceptances"], 1)
        self.assertEqual(result["hardening_rejections"], 9)
        self.assertEqual(result["common_policy"], "allow")
        self.assertEqual(result["external_actions"], 0)


if __name__ == "__main__":
    unittest.main()
