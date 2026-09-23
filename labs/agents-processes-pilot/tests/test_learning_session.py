from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from learning_session import main, render, run_session


class LearningSessionTests(unittest.TestCase):
    def test_review_exposes_evidence_diff_and_requires_explicit_decision(self):
        result = run_session()
        self.assertEqual(result["decision"]["decision"], "hold")
        self.assertIn("BUG-1042", result["ticket"]["ticket_id"])
        self.assertIn("def ", result["source"])
        self.assertIn("+++ b/repository/src/totals.py", result["diff"])
        self.assertTrue(result["fixture_unchanged"] and result["workspace_removed"])
        self.assertNotIn("acceptance.json", result["ephemeral_artifacts"])
        self.assertNotIn("acceptance_path", result["decision"])

    def test_approve_requires_the_hash_supplied_by_reviewer(self):
        reviewed = run_session()
        accepted = run_session("approve", reviewed["diff_sha256"])
        self.assertTrue(accepted["decision"]["accepted"])
        self.assertIn("acceptance.json", accepted["ephemeral_artifacts"])
        self.assertTrue(accepted["workspace_removed"] and accepted["fixture_unchanged"])
        blocked = run_session("approve", "0" * 64)
        self.assertEqual(blocked["decision"]["reason"], "approval_not_bound_to_diff")
        self.assertNotIn("acceptance.json", blocked["ephemeral_artifacts"])
        self.assertIn("review novamente", render(blocked))

    def test_reject_does_not_create_acceptance(self):
        result = run_session("reject")
        self.assertEqual(result["decision"]["reason"], "approval_denied")
        self.assertNotIn("acceptance.json", result["ephemeral_artifacts"])

    def test_reset_is_repeatable_and_paths_are_closed(self):
        result = run_session("reset")
        self.assertEqual(result["reset_count"], 2)
        self.assertTrue(result["same_diff_after_reset"] and result["workspace_removed"])
        result = run_session("check-paths")
        self.assertEqual(len(result["denied_paths"]), 3)
        self.assertTrue(result["workspace_removed"] and result["fixture_unchanged"])

    def test_invalid_approval_does_not_open_a_workspace(self):
        for value in (None, "", "abc", "a" * 65, "A" * 64, "../anything"):
            with self.subTest(value=value), patch("learning_session.DevelopmentTriage") as controller:
                with self.assertRaises(ValueError):
                    run_session("approve", value)
                controller.assert_not_called()
        with self.assertRaises(ValueError):
            run_session("review", "0" * 64)

    def test_cli_readable_default_json_and_usage_error(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main([]), 0)
        for phrase in ("Ticket e evidências", "Diff para revisão", "hold / approval_missing", "diretório temporários removidos"):
            self.assertIn(phrase, output.getvalue())
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["review", "--json"]), 0)
        self.assertEqual(json.loads(output.getvalue())["action"], "review")
        error = io.StringIO()
        with redirect_stderr(error):
            self.assertEqual(main(["approve"]), 2)
        self.assertIn("--reviewed-hash", error.getvalue())

    def test_runtime_failure_is_safe_and_does_not_echo_host_paths(self):
        error = io.StringIO()
        with patch("learning_session.run_session", side_effect=OSError("sensitive host path")), redirect_stderr(error):
            self.assertEqual(main([]), 1)
        self.assertNotIn("sensitive", error.getvalue())
        self.assertIn("não desative", error.getvalue())
