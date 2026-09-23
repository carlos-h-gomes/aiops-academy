from __future__ import annotations

from copy import deepcopy
import ast
from pathlib import Path
import sys
import unittest


LAB_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB_ROOT / "src"))

from development_triage import DevelopmentTriage, PolicyViolation  # noqa: E402


def reviewer_approval(proposal) -> dict:
    """Synthetic input representing a reviewer decision made outside the controller."""
    return {
        "issuer": "human-reviewer",
        "status": "approved",
        "scenario_id": proposal.scenario_id,
        "action": "accept-diff",
        "target": "ephemeral-diff",
        "artifact_version": proposal.artifact_version,
        "diff_sha256": proposal.diff_sha256,
    }


class DevelopmentTriageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = DevelopmentTriage()
        self.before = self.controller.fixture_snapshot()

    def tearDown(self) -> None:
        self.assertEqual(self.controller.fixture_snapshot(), self.before)
        self.controller.close()

    def test_allowlist_accepts_only_four_named_fixture_files(self):
        self.assertIn("BUG-1042", self.controller.read_fixture("ticket.json"))
        for denied in (
            "policy.json",
            "../policy.json",
            "repository/src/../tests/test_totals.py",
            str((LAB_ROOT / "README.md").resolve()),
        ):
            with self.subTest(denied=denied):
                with self.assertRaisesRegex(PolicyViolation, "fixture_not_allowlisted"):
                    self.controller.read_fixture(denied)

    def test_diff_and_candidate_exist_only_in_owned_temporary_area(self):
        proposal = self.controller.prepare()
        self.assertTrue(proposal.diff_path.is_relative_to(self.controller.workspace))
        self.assertTrue(proposal.candidate_path.is_relative_to(self.controller.workspace))
        self.assertTrue(proposal.diff_path.is_file())
        self.assertTrue(proposal.candidate_path.is_file())
        diff = proposal.diff_path.read_text(encoding="utf-8")
        self.assertIn("--- a/repository/src/totals.py", diff)
        self.assertIn("+++ b/repository/src/totals.py", diff)
        self.assertIn("+    return (subtotal_cents * (100 - discount_percent) + 50) // 100", diff)
        self.assertFalse((LAB_ROOT / "proposal.diff").exists())
        self.assertEqual(self.controller.fixture_snapshot(), self.before)

    def test_approval_is_required_and_bound_to_exact_diff(self):
        proposal = self.controller.prepare()
        self.assertEqual(
            self.controller.accept(proposal, None),
            {"decision": "hold", "reason": "approval_missing", "accepted": False},
        )
        wrong = reviewer_approval(proposal)
        wrong["diff_sha256"] = "0" * 64
        self.assertEqual(
            self.controller.accept(proposal, wrong),
            {"decision": "block", "reason": "approval_not_bound_to_diff", "accepted": False},
        )
        denied = reviewer_approval(proposal)
        denied["status"] = "denied"
        self.assertEqual(
            self.controller.accept(proposal, denied),
            {"decision": "block", "reason": "approval_denied", "accepted": False},
        )
        accepted = self.controller.accept(proposal, reviewer_approval(proposal))
        self.assertEqual((accepted["decision"], accepted["accepted"]), ("accepted", True))
        acceptance_path = Path(accepted["acceptance_path"])
        self.assertTrue(acceptance_path.is_relative_to(self.controller.workspace))
        self.assertTrue(acceptance_path.is_file())
        self.assertEqual(self.controller.fixture_snapshot(), self.before)

    def test_changed_diff_cannot_reuse_previous_approval(self):
        proposal = self.controller.prepare()
        approval = reviewer_approval(proposal)
        proposal.diff_path.write_text("changed after review\n", encoding="utf-8")
        self.assertEqual(
            self.controller.accept(proposal, approval),
            {"decision": "block", "reason": "diff_changed_after_review", "accepted": False},
        )

    def test_reset_removes_known_artifacts_and_reproduces_same_diff(self):
        first = self.controller.prepare()
        self.controller.accept(first, reviewer_approval(first))
        self.controller.reset()
        for relative in (
            "proposal.diff",
            "candidate/repository/src/totals.py",
            "acceptance.json",
        ):
            self.assertFalse((self.controller.workspace / relative).exists())
        second = self.controller.prepare()
        self.assertEqual(second.diff_sha256, first.diff_sha256)
        self.assertEqual(self.controller.fixture_snapshot(), self.before)

    def test_controller_has_no_process_network_dynamic_execution_or_git_adapter(self):
        source_path = LAB_ROOT / "src" / "development_triage.py"
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(source_path))
        imported = {
            alias.name.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module and node.module != "__future__"
        )
        self.assertEqual(imported, {"dataclasses", "difflib", "hashlib", "json", "pathlib", "tempfile"})
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        self.assertTrue(names.isdisjoint({"eval", "exec", "compile", "system", "popen"}))
        for forbidden in ("subprocess", "socket", "urllib", "requests", "gitpython"):
            self.assertNotIn(forbidden, source.casefold())

    def test_close_removes_the_owned_temporary_directory(self):
        controller = DevelopmentTriage()
        workspace = controller.workspace
        controller.prepare()
        controller.close()
        self.assertFalse(workspace.exists())


if __name__ == "__main__":
    unittest.main()
