from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_security_03 import (
    INVALID_FIXTURE_CODES,
    _load_json,
    _load_security_03_fixture,
    evaluate_topology,
    validate_security_03_authoring,
    validate_topology_shape,
    verify_common_policy,
    verify_security_01_02_regressions,
    verify_topology_fixtures,
)


class Security03HardeningTests(unittest.TestCase):
    def test_authored_unit_matches_published_catalog(self):
        result = validate_security_03_authoring()
        self.assertEqual(result["unit"], "security-03")
        self.assertEqual(result["catalog_status"], "available")
        self.assertEqual(result["catalog_translations"], ["available", "planned", "planned"])
        self.assertEqual(result["available_units"], 50)
        self.assertEqual(result["planned_units"], 0)
        self.assertEqual(result["legacy_lessons"], 30)

    def test_common_policy_reuses_identity_and_handling_contracts(self):
        result = verify_common_policy()
        self.assertEqual(result["identity_import"], "validated")
        self.assertEqual(result["handling_import"], "validated")
        self.assertEqual(result["authorization"], "allow")
        self.assertEqual(result["protected_fields"], 2)
        self.assertEqual(result["external_actions"], 0)

    def test_static_fixtures_accept_one_and_deny_each_risk(self):
        result = verify_topology_fixtures()
        self.assertEqual(result["accepted"], 1)
        self.assertEqual(result["rejected"], INVALID_FIXTURE_CODES)
        self.assertEqual(result["runtime_tools"], 0)
        self.assertEqual(result["external_actions"], 0)

    def test_isolated_topology_accepts_loopback_or_no_publisher(self):
        policy, valid, _ = _load_security_03_fixture()
        self.assertEqual(evaluate_topology(policy, valid)["decision"], "accept")
        without_publisher = deepcopy(valid)
        without_publisher["scenario_id"] = "accept-without-publisher"
        without_publisher["service"]["network"]["publications"] = []
        self.assertEqual(
            evaluate_topology(policy, without_publisher),
            {
                "scenario_id": "accept-without-publisher",
                "decision": "accept",
                "reasons": ["hardening_policy_satisfied"],
            },
        )

    def test_identity_secret_root_and_fixed_route_fail_closed(self):
        policy, valid, _ = _load_security_03_fixture()
        mutations = [
            ("identity", ("authorization", "subject"), "bia-estagiaria", "identity_not_authorized"),
            ("secret", ("service", "secrets"), ["DEMO-INERTE-NAO-USAR"], "secret_distribution"),
            ("root", ("service", "process", "user"), "root", "root_process"),
            (
                "destination",
                ("service", "network", "egress", "destinations"),
                ["user-selected-host"],
                "unapproved_egress_destination",
            ),
        ]
        for case_id, path, value, expected in mutations:
            with self.subTest(case_id=case_id):
                candidate = deepcopy(valid)
                candidate["scenario_id"] = f"deny-{case_id}"
                target = candidate
                for segment in path[:-1]:
                    target = target[segment]
                target[path[-1]] = value
                report = evaluate_topology(policy, candidate)
                self.assertEqual(report["decision"], "deny")
                self.assertIn(expected, report["reasons"])

    def test_reports_are_minimal_and_do_not_echo_protected_values(self):
        policy, valid, invalid_paths = _load_security_03_fixture()
        handling_source = _load_json(ROOT / "backend/content/fixtures/security-02/source-record.json")
        reports = [evaluate_topology(policy, valid)] + [
            evaluate_topology(policy, _load_json(path)) for path in invalid_paths.values()
        ]
        for report in reports:
            serialized = json.dumps(report, ensure_ascii=False, sort_keys=True)
            self.assertEqual(set(report), {"scenario_id", "decision", "reasons"})
            self.assertNotIn("secret_marker", serialized)
            self.assertNotIn("study_record", serialized)
            self.assertNotIn(handling_source["secret_marker"], serialized)
            self.assertNotIn(handling_source["study_record"], serialized)

    def test_malformed_or_extra_fields_are_rejected_before_decision(self):
        _, valid, _ = _load_security_03_fixture()
        malformed = deepcopy(valid)
        malformed["service"]["image"] = "not-allowed"
        with self.assertRaisesRegex(ValueError, "Serviço fora do contrato"):
            validate_topology_shape(malformed)

    def test_security_01_02_contracts_remain_green(self):
        result = verify_security_01_02_regressions()
        self.assertEqual(result["authored_units"], ["security-01", "security-02"])
        self.assertEqual(result["access_scenarios"], 4)
        self.assertEqual(result["evidence_rejections"], 4)
        self.assertEqual(result["external_actions"], 0)


if __name__ == "__main__":
    unittest.main()
