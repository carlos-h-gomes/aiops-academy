"""Deterministic, fixture-only bug triage for the private agents-05 lesson."""
from __future__ import annotations

from dataclasses import dataclass
import difflib
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory


LAB_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = (LAB_ROOT / "fixtures" / "development").resolve()
POLICY_PATH = FIXTURE_ROOT / "policy.json"
POLICY_FIELDS = {
    "schema_version",
    "policy_id",
    "scenario_id",
    "artifact_version",
    "allowlisted_reads",
    "ephemeral_writes",
    "approval",
    "capabilities",
}
APPROVAL_FIELDS = {
    "issuer",
    "status",
    "scenario_id",
    "action",
    "target",
    "artifact_version",
    "diff_sha256",
}
EXPECTED_READS = {
    "ticket.json",
    "proposal.json",
    "repository/src/totals.py",
    "repository/tests/test_totals.py",
}
EXPECTED_WRITES = {
    "proposal.diff",
    "candidate/repository/src/totals.py",
    "acceptance.json",
}
EXPECTED_CAPABILITIES = {
    "fixture_read": True,
    "ephemeral_diff_write": True,
    "fixture_write": False,
    "git": False,
    "shell": False,
    "child_process": False,
    "network": False,
    "secret_input": False,
    "external_write": False,
}


class PolicyViolation(ValueError):
    """A closed policy or path boundary was violated."""


@dataclass(frozen=True)
class TriageProposal:
    scenario_id: str
    ticket_id: str
    artifact_version: str
    hypothesis: str
    evidence: tuple[str, ...]
    proposed_tests: tuple[str, ...]
    diff_sha256: str
    diff_path: Path
    candidate_path: Path


def _read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PolicyViolation("json_object_required")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DevelopmentTriage:
    """Read an immutable fixture and write only to an owned temporary directory."""

    def __init__(self) -> None:
        self.policy = _read_json(POLICY_PATH)
        self._validate_policy()
        self._temporary = TemporaryDirectory(prefix="agents-05-development-")
        self.workspace = Path(self._temporary.name).resolve()

    def __enter__(self) -> "DevelopmentTriage":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        self._temporary.cleanup()

    def _validate_policy(self) -> None:
        if set(self.policy) != POLICY_FIELDS:
            raise PolicyViolation("policy_contract_invalid")
        if (
            self.policy["schema_version"] != "1.0"
            or self.policy["policy_id"] != "agents-05-development-policy-v1"
            or self.policy["scenario_id"] != "development-v1"
            or self.policy["artifact_version"] != "1.0"
        ):
            raise PolicyViolation("policy_identity_invalid")
        if set(self.policy["allowlisted_reads"]) != EXPECTED_READS:
            raise PolicyViolation("policy_read_allowlist_invalid")
        if set(self.policy["ephemeral_writes"]) != EXPECTED_WRITES:
            raise PolicyViolation("policy_write_allowlist_invalid")
        approval = self.policy["approval"]
        if approval != {
            "required": True,
            "issuer": "human-reviewer",
            "action": "accept-diff",
            "target": "ephemeral-diff",
            "binding_fields": [
                "scenario_id",
                "action",
                "target",
                "artifact_version",
                "diff_sha256",
            ],
        }:
            raise PolicyViolation("policy_approval_invalid")
        if self.policy["capabilities"] != EXPECTED_CAPABILITIES:
            raise PolicyViolation("policy_capabilities_invalid")

    def _fixture_path(self, relative: str) -> Path:
        if not isinstance(relative, str) or relative not in EXPECTED_READS:
            raise PolicyViolation("fixture_not_allowlisted")
        candidate = (FIXTURE_ROOT / relative).resolve()
        if not candidate.is_relative_to(FIXTURE_ROOT) or not candidate.is_file():
            raise PolicyViolation("fixture_path_escape")
        return candidate

    def read_fixture(self, relative: str) -> str:
        return self._fixture_path(relative).read_text(encoding="utf-8")

    def _ephemeral_path(self, relative: str) -> Path:
        if relative not in EXPECTED_WRITES:
            raise PolicyViolation("ephemeral_target_not_allowlisted")
        candidate = (self.workspace / relative).resolve()
        if not candidate.is_relative_to(self.workspace):
            raise PolicyViolation("ephemeral_path_escape")
        return candidate

    def fixture_snapshot(self) -> dict[str, str]:
        return {relative: _sha256(self._fixture_path(relative)) for relative in sorted(EXPECTED_READS)}

    def prepare(self) -> TriageProposal:
        ticket = json.loads(self.read_fixture("ticket.json"))
        proposal = json.loads(self.read_fixture("proposal.json"))
        source_path = proposal.get("source_path")
        test_path = proposal.get("test_path")
        if source_path not in EXPECTED_READS or test_path not in EXPECTED_READS:
            raise PolicyViolation("proposal_path_not_allowlisted")
        if (
            set(ticket) != {
                "schema_version",
                "ticket_id",
                "title",
                "observed",
                "expected",
                "rounding_rule",
                "scope",
                "contains_secret",
            }
            or ticket["schema_version"] != "1.0"
            or ticket["ticket_id"] != "BUG-1042"
            or ticket["scope"] != source_path
            or ticket["contains_secret"] is not False
        ):
            raise PolicyViolation("ticket_contract_invalid")
        if set(proposal) != {
            "schema_version",
            "proposal_id",
            "artifact_version",
            "source_path",
            "test_path",
            "hypothesis",
            "evidence",
            "before",
            "after",
            "proposed_tests",
        }:
            raise PolicyViolation("proposal_contract_invalid")
        if (
            proposal["schema_version"] != "1.0"
            or proposal["proposal_id"] != "proposal-bug-1042-v1"
            or proposal["artifact_version"] != self.policy["artifact_version"]
            or not isinstance(proposal["evidence"], list)
            or len(proposal["evidence"]) != 2
            or not isinstance(proposal["proposed_tests"], list)
            or len(proposal["proposed_tests"]) != 3
        ):
            raise PolicyViolation("proposal_identity_invalid")
        source = self.read_fixture(source_path)
        self.read_fixture(test_path)
        before = proposal["before"]
        after = proposal["after"]
        if not isinstance(before, str) or not isinstance(after, str) or source.count(before) != 1:
            raise PolicyViolation("proposal_replacement_ambiguous")
        candidate = source.replace(before, after, 1)
        diff = "".join(
            difflib.unified_diff(
                source.splitlines(keepends=True),
                candidate.splitlines(keepends=True),
                fromfile=f"a/{source_path}",
                tofile=f"b/{source_path}",
            )
        )
        if not diff:
            raise PolicyViolation("proposal_diff_empty")
        candidate_path = self._ephemeral_path("candidate/repository/src/totals.py")
        diff_path = self._ephemeral_path("proposal.diff")
        candidate_path.parent.mkdir(parents=True, exist_ok=True)
        candidate_path.write_text(candidate, encoding="utf-8", newline="\n")
        diff_path.write_text(diff, encoding="utf-8", newline="\n")
        return TriageProposal(
            scenario_id=self.policy["scenario_id"],
            ticket_id=ticket["ticket_id"],
            artifact_version=proposal["artifact_version"],
            hypothesis=proposal["hypothesis"],
            evidence=tuple(proposal["evidence"]),
            proposed_tests=tuple(proposal["proposed_tests"]),
            diff_sha256=_sha256(diff_path),
            diff_path=diff_path,
            candidate_path=candidate_path,
        )

    def accept(self, proposal: TriageProposal, approval: dict | None) -> dict:
        if approval is None:
            return {"decision": "hold", "reason": "approval_missing", "accepted": False}
        if not isinstance(approval, dict) or set(approval) != APPROVAL_FIELDS:
            return {"decision": "block", "reason": "approval_contract_invalid", "accepted": False}
        expected = {
            "issuer": self.policy["approval"]["issuer"],
            "status": "approved",
            "scenario_id": proposal.scenario_id,
            "action": self.policy["approval"]["action"],
            "target": self.policy["approval"]["target"],
            "artifact_version": proposal.artifact_version,
            "diff_sha256": proposal.diff_sha256,
        }
        if approval["issuer"] != expected["issuer"]:
            return {"decision": "block", "reason": "approval_issuer_invalid", "accepted": False}
        if approval["status"] != "approved":
            return {"decision": "block", "reason": "approval_denied", "accepted": False}
        if approval != expected:
            return {"decision": "block", "reason": "approval_not_bound_to_diff", "accepted": False}
        if (
            not proposal.diff_path.is_relative_to(self.workspace)
            or not proposal.diff_path.is_file()
            or _sha256(proposal.diff_path) != proposal.diff_sha256
        ):
            return {"decision": "block", "reason": "diff_changed_after_review", "accepted": False}
        acceptance = {
            "schema_version": "1.0",
            "scenario_id": proposal.scenario_id,
            "ticket_id": proposal.ticket_id,
            "artifact_version": proposal.artifact_version,
            "diff_sha256": proposal.diff_sha256,
            "issuer": approval["issuer"],
            "decision": "accepted",
            "effect": "ephemeral-record-only",
        }
        acceptance_path = self._ephemeral_path("acceptance.json")
        acceptance_path.write_text(
            json.dumps(acceptance, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return {
            "decision": "accepted",
            "reason": "human_approval_bound_to_diff",
            "accepted": True,
            "acceptance_path": str(acceptance_path),
        }

    def reset(self) -> None:
        for relative in ("acceptance.json", "proposal.diff", "candidate/repository/src/totals.py"):
            path = self._ephemeral_path(relative)
            if path.is_file():
                path.unlink()
        for relative in ("candidate/repository/src", "candidate/repository", "candidate"):
            directory = (self.workspace / relative).resolve()
            if directory.is_relative_to(self.workspace) and directory.is_dir():
                directory.rmdir()


def main() -> None:
    with DevelopmentTriage() as controller:
        proposal = controller.prepare()
        decision = controller.accept(proposal, None)
        print(
            json.dumps(
                {
                    "scenario_id": proposal.scenario_id,
                    "ticket_id": proposal.ticket_id,
                    "artifact_version": proposal.artifact_version,
                    "hypothesis": proposal.hypothesis,
                    "evidence": proposal.evidence,
                    "proposed_tests": proposal.proposed_tests,
                    "diff_sha256": proposal.diff_sha256,
                    "decision": decision,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
