"""Deterministic, fixture-only controller for the private agents-01..04 practice."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import re


IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")
REQUEST_ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
VERSION = re.compile(r"^[0-9]+\.[0-9]+$")
REQUEST_FIELDS = {
    "schema_version",
    "request_id",
    "scenario_version",
    "subject",
    "action",
    "target",
    "tool",
    "fixture_id",
    "approval_id",
    "idempotency_key",
    "step_budget",
    "artifact_version",
}
RESULT_FIELDS = {
    "schema_version",
    "request_id",
    "decision",
    "reason",
    "state",
    "policy_id",
    "fixture_version",
    "idempotent",
    "steps_used",
    "transitions",
    "result",
    "counters",
}
BOUND_FIELDS = (
    "subject",
    "action",
    "target",
    "tool",
    "fixture_id",
    "artifact_version",
    "idempotency_key",
)


class ContractError(ValueError):
    """A typed contract failure that does not echo rejected content."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class ControllerState:
    """Ephemeral state; no filesystem, process, network, or external persistence."""

    def __init__(self) -> None:
        self.records: dict[str, dict] = {}
        self.effect_counts: dict[str, int] = {}


def _timestamp(value: str, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"invalid_timestamp:{field}")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"invalid_timestamp:{field}") from exc


def _identifier(value, code: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ContractError(code)
    return value


def validate_request(request: dict) -> None:
    if not isinstance(request, dict):
        raise ContractError("schema_type_invalid")
    if set(request) - REQUEST_FIELDS:
        raise ContractError("schema_extra_field")
    if REQUEST_FIELDS - set(request):
        raise ContractError("schema_required_field_missing")
    if request["schema_version"] != "1.0":
        raise ContractError("schema_version_invalid")
    if not isinstance(request["request_id"], str) or not REQUEST_ID.fullmatch(request["request_id"]):
        raise ContractError("schema_request_id_invalid")
    if not isinstance(request["scenario_version"], str) or not VERSION.fullmatch(request["scenario_version"]):
        raise ContractError("schema_scenario_version_invalid")
    for field in ("subject", "action", "target", "tool", "fixture_id", "idempotency_key"):
        _identifier(request[field], f"schema_{field}_invalid")
    if request["approval_id"] is not None:
        _identifier(request["approval_id"], "schema_approval_id_invalid")
    if not isinstance(request["artifact_version"], str) or not VERSION.fullmatch(request["artifact_version"]):
        raise ContractError("schema_artifact_version_invalid")
    if type(request["step_budget"]) is not int or not 1 <= request["step_budget"] <= 16:
        raise ContractError("schema_step_budget_invalid")


def validate_policy(policy: dict) -> None:
    fields = {
        "schema_version",
        "policy_id",
        "evaluation_time",
        "request_schema",
        "result_schema",
        "allowed_actions",
        "subjects",
        "targets",
        "approvals",
        "budgets",
        "state_transitions",
        "capabilities",
    }
    if not isinstance(policy, dict) or set(policy) != fields:
        raise ValueError("policy_contract_invalid")
    if policy["schema_version"] != "1.0" or policy["policy_id"] != "agents-01-04-controller-policy-v1":
        raise ValueError("policy_identity_invalid")
    _timestamp(policy["evaluation_time"], "evaluation_time")
    if policy["request_schema"] != "control-request.schema.json" or policy["result_schema"] != "control-result.schema.json":
        raise ValueError("policy_schema_pointer_invalid")
    expected_actions = {
        "classify_process": {
            "tool": "fixture_classifier",
            "target": "process-intake",
            "step_cost": 2,
            "approval_required": False,
        },
        "inspect_layers": {
            "tool": "fixture_reader",
            "target": "agent-layers",
            "step_cost": 1,
            "approval_required": True,
        },
    }
    if policy["allowed_actions"] != expected_actions:
        raise ValueError("policy_action_allowlist_invalid")
    expected_subject = {
        "learner-agent": {"allowed_actions": ["classify_process", "inspect_layers"]}
    }
    if policy["subjects"] != expected_subject:
        raise ValueError("policy_subjects_invalid")
    expected_targets = {
        "process-intake": {
            "allowed_fixtures": [
                "process-routine",
                "process-ambiguous",
                "process-high-impact",
                "process-incomplete",
            ]
        },
        "agent-layers": {"allowed_fixtures": ["layers-v1"]},
    }
    if policy["targets"] != expected_targets:
        raise ValueError("policy_targets_invalid")
    if policy["budgets"] != {"max_steps": 4}:
        raise ValueError("policy_budget_invalid")
    expected_transitions = {
        "received": ["validating"],
        "validating": ["blocked", "held", "ready"],
        "held": ["validating"],
        "ready": ["blocked", "completed"],
        "blocked": ["blocked"],
        "completed": ["completed"],
    }
    if policy["state_transitions"] != expected_transitions:
        raise ValueError("policy_transitions_invalid")
    expected_capabilities = {
        "fixture_only": True,
        "shell": False,
        "url_input": False,
        "network": False,
        "child_process": False,
        "external_write": False,
        "external_approval": False,
    }
    if policy["capabilities"] != expected_capabilities:
        raise ValueError("policy_capabilities_invalid")
    if not isinstance(policy["approvals"], list) or len(policy["approvals"]) != 3:
        raise ValueError("policy_approvals_invalid")
    approval_fields = {"approval_id", "issuer", "status", *BOUND_FIELDS, "expires_at"}
    ids = []
    for approval in policy["approvals"]:
        if not isinstance(approval, dict) or set(approval) != approval_fields:
            raise ValueError("policy_approval_contract_invalid")
        for field in ("approval_id", "issuer", *(item for item in BOUND_FIELDS if item != "artifact_version")):
            _identifier(approval[field], "policy_approval_identifier_invalid")
        if not isinstance(approval["artifact_version"], str) or not VERSION.fullmatch(approval["artifact_version"]):
            raise ValueError("policy_approval_artifact_version_invalid")
        if approval["issuer"] != "human-reviewer" or approval["status"] not in {"approved", "denied"}:
            raise ValueError("policy_approval_authority_invalid")
        _timestamp(approval["expires_at"], "approval.expires_at")
        ids.append(approval["approval_id"])
    if len(ids) != len(set(ids)):
        raise ValueError("policy_approval_duplicate")


def validate_fixtures(fixtures: dict) -> None:
    if not isinstance(fixtures, dict) or set(fixtures) != {"schema_version", "fixtures"}:
        raise ValueError("fixture_set_invalid")
    if fixtures["schema_version"] != "1.0" or not isinstance(fixtures["fixtures"], list):
        raise ValueError("fixture_set_version_invalid")
    expected_ids = {
        "process-routine",
        "process-ambiguous",
        "process-high-impact",
        "process-incomplete",
        "layers-v1",
    }
    seen = set()
    for fixture in fixtures["fixtures"]:
        common = {"fixture_id", "fixture_version", "kind", "payload"}
        if not isinstance(fixture, dict) or set(fixture) != common:
            raise ValueError("fixture_contract_invalid")
        _identifier(fixture["fixture_id"], "fixture_identifier_invalid")
        if fixture["fixture_version"] != "1.0" or fixture["kind"] not in {"process_request", "layer_map"}:
            raise ValueError("fixture_identity_invalid")
        payload = fixture["payload"]
        if fixture["kind"] == "process_request":
            if not isinstance(payload, dict) or set(payload) != {
                "impact",
                "ambiguity",
                "inputs_complete",
                "owner",
                "preset_response",
            }:
                raise ValueError("process_fixture_contract_invalid")
            if payload["impact"] not in {"low", "medium", "high"}:
                raise ValueError("process_fixture_impact_invalid")
            if payload["ambiguity"] not in {"low", "high"} or type(payload["inputs_complete"]) is not bool:
                raise ValueError("process_fixture_decision_input_invalid")
            if payload["owner"] not in {"operations", "human-reviewer"}:
                raise ValueError("process_fixture_owner_invalid")
            _identifier(payload["preset_response"], "process_fixture_response_invalid")
        else:
            if payload != {
                "layers": ["model", "assistant", "orchestrator", "state", "tool"],
                "preset_response": "layer-map-available",
            }:
                raise ValueError("layer_fixture_contract_invalid")
        seen.add(fixture["fixture_id"])
    if seen != expected_ids or len(seen) != len(fixtures["fixtures"]):
        raise ValueError("fixture_inventory_invalid")


def _transition(policy: dict, transitions: list[dict], source: str, target: str, reason: str) -> None:
    if target not in policy["state_transitions"].get(source, []):
        raise AssertionError(f"invalid_transition:{source}:{target}")
    transitions.append({"from": source, "to": target, "reason": reason})


def _binding(request: dict) -> dict:
    return {field: request[field] for field in BOUND_FIELDS}


def _find_fixture(fixtures: dict, fixture_id: str) -> dict | None:
    return next((item for item in fixtures["fixtures"] if item["fixture_id"] == fixture_id), None)


def _blank_result() -> dict:
    return {"classification": None, "response_code": None, "artifact_ref": None}


def _counters(tool_invocations: int = 0, simulated_effects: int = 0) -> dict:
    return {
        "tool_invocations": tool_invocations,
        "simulated_effects": simulated_effects,
        "network_calls": 0,
        "child_processes": 0,
        "external_writes": 0,
    }


def _report(
    policy: dict,
    request_id: str,
    decision: str,
    reason: str,
    state: str,
    transitions: list[dict],
    *,
    fixture_version: str | None = None,
    steps_used: int = 0,
    result: dict | None = None,
    counters: dict | None = None,
) -> dict:
    report = {
        "schema_version": "1.0",
        "request_id": request_id,
        "decision": decision,
        "reason": reason,
        "state": state,
        "policy_id": policy.get("policy_id", "invalid-policy"),
        "fixture_version": fixture_version,
        "idempotent": False,
        "steps_used": steps_used,
        "transitions": transitions,
        "result": result or _blank_result(),
        "counters": counters or _counters(),
    }
    validate_result(report)
    return report


def validate_result(report: dict) -> None:
    if not isinstance(report, dict) or set(report) != RESULT_FIELDS:
        raise ValueError("result_contract_invalid")
    if report["schema_version"] != "1.0" or report["decision"] not in {"ready", "hold", "block"}:
        raise ValueError("result_decision_invalid")
    if not isinstance(report["request_id"], str) or not REQUEST_ID.fullmatch(report["request_id"]):
        raise ValueError("result_request_id_invalid")
    for field in ("reason", "policy_id"):
        _identifier(report[field], f"result_{field}_invalid")
    if report["state"] not in {"held", "blocked", "completed"}:
        raise ValueError("result_state_invalid")
    if type(report["idempotent"]) is not bool or type(report["steps_used"]) is not int:
        raise ValueError("result_scalar_invalid")
    if report["fixture_version"] is not None and not VERSION.fullmatch(report["fixture_version"]):
        raise ValueError("result_fixture_version_invalid")
    if not isinstance(report["transitions"], list) or not report["transitions"]:
        raise ValueError("result_transitions_invalid")
    for item in report["transitions"]:
        if not isinstance(item, dict) or set(item) != {"from", "to", "reason"}:
            raise ValueError("result_transition_contract_invalid")
        for value in item.values():
            _identifier(value, "result_transition_identifier_invalid")
    result = report["result"]
    if not isinstance(result, dict) or set(result) != {"classification", "response_code", "artifact_ref"}:
        raise ValueError("result_payload_invalid")
    if result["classification"] not in {None, "rule", "limited_agent", "refusal"}:
        raise ValueError("result_classification_invalid")
    for field in ("response_code", "artifact_ref"):
        if result[field] is not None:
            _identifier(result[field], f"result_{field}_invalid")
    expected_counters = {
        "tool_invocations",
        "simulated_effects",
        "network_calls",
        "child_processes",
        "external_writes",
    }
    if not isinstance(report["counters"], dict) or set(report["counters"]) != expected_counters:
        raise ValueError("result_counters_invalid")
    if any(type(value) is not int or value < 0 for value in report["counters"].values()):
        raise ValueError("result_counter_value_invalid")
    if any(report["counters"][key] != 0 for key in ("network_calls", "child_processes", "external_writes")):
        raise ValueError("result_external_effect_invalid")


def _deny(policy: dict, request_id: str, transitions: list[dict], reason: str) -> dict:
    source = transitions[-1]["to"]
    _transition(policy, transitions, source, "blocked", reason)
    return _report(policy, request_id, "block", reason, "blocked", transitions)


def _approval_decision(policy: dict, request: dict) -> tuple[str, str | None]:
    if request["approval_id"] is None:
        return "hold", "approval_missing"
    approval = next(
        (item for item in policy["approvals"] if item["approval_id"] == request["approval_id"]),
        None,
    )
    if approval is None:
        return "block", "approval_unknown"
    if any(approval[field] != request[field] for field in BOUND_FIELDS):
        return "block", "approval_not_bound_to_request"
    if approval["status"] != "approved":
        return "block", "approval_denied"
    if _timestamp(approval["expires_at"], "approval.expires_at") <= _timestamp(
        policy["evaluation_time"], "evaluation_time"
    ):
        return "block", "approval_expired"
    return "ready", None


def _run_adapter(action: str, fixture: dict) -> tuple[dict, bool]:
    if action == "classify_process":
        payload = fixture["payload"]
        if not payload["inputs_complete"] or payload["impact"] == "high":
            classification = "refusal"
        elif payload["ambiguity"] == "high":
            classification = "limited_agent"
        else:
            classification = "rule"
        return {
            "classification": classification,
            "response_code": payload["preset_response"],
            "artifact_ref": None,
        }, classification != "refusal"
    if action == "inspect_layers":
        return {
            "classification": "rule",
            "response_code": fixture["payload"]["preset_response"],
            "artifact_ref": "layers-v1-1",
        }, True
    raise AssertionError("adapter_not_allowlisted")


def execute(policy: dict, fixtures: dict, request: dict, state: ControllerState | None = None) -> dict:
    """Evaluate one structured request and invoke only an internal fixture adapter."""
    state = state or ControllerState()
    validate_policy(policy)
    validate_fixtures(fixtures)
    candidate_request_id = request.get("request_id") if isinstance(request, dict) else None
    request_id = (
        candidate_request_id
        if isinstance(candidate_request_id, str) and REQUEST_ID.fullmatch(candidate_request_id)
        else "invalid-request"
    )
    transitions: list[dict] = []
    _transition(policy, transitions, "received", "validating", "request_received")
    try:
        validate_request(request)
    except ContractError as exc:
        return _deny(policy, request_id, transitions, exc.code)

    key = request["idempotency_key"]
    existing = state.records.get(key)
    if existing is not None:
        if existing["binding"] != _binding(request):
            return _deny(policy, request_id, transitions, "idempotency_conflict")
        previous = existing["report"]
        if previous["state"] in {"completed", "blocked"}:
            replay = deepcopy(previous)
            replay["idempotent"] = True
            replay["transitions"] = [
                {"from": previous["state"], "to": previous["state"], "reason": "idempotent_replay"}
            ]
            validate_result(replay)
            return replay
        transitions = deepcopy(previous["transitions"])
        _transition(policy, transitions, "held", "validating", "approval_resume")

    subject = policy["subjects"].get(request["subject"])
    if subject is None:
        report = _deny(policy, request_id, transitions, "subject_unknown")
    elif request["action"] not in policy["allowed_actions"] or request["action"] not in subject["allowed_actions"]:
        report = _deny(policy, request_id, transitions, "action_not_allowed")
    else:
        action = policy["allowed_actions"][request["action"]]
        if request["tool"] != action["tool"]:
            report = _deny(policy, request_id, transitions, "tool_not_allowed")
        elif request["target"] != action["target"]:
            report = _deny(policy, request_id, transitions, "target_not_allowed")
        elif request["step_budget"] > policy["budgets"]["max_steps"]:
            report = _deny(policy, request_id, transitions, "step_budget_above_policy")
        elif action["step_cost"] > request["step_budget"]:
            report = _deny(policy, request_id, transitions, "step_budget_exceeded")
        elif request["fixture_id"] not in policy["targets"][request["target"]]["allowed_fixtures"]:
            report = _deny(policy, request_id, transitions, "fixture_not_allowed")
        else:
            fixture = _find_fixture(fixtures, request["fixture_id"])
            if fixture is None or fixture["fixture_version"] != request["scenario_version"]:
                report = _deny(policy, request_id, transitions, "fixture_version_mismatch")
            elif request["artifact_version"] != fixture["fixture_version"]:
                report = _deny(policy, request_id, transitions, "artifact_version_mismatch")
            else:
                approval_decision, approval_reason = (
                    _approval_decision(policy, request)
                    if action["approval_required"]
                    else ("ready", None)
                )
                if approval_decision == "hold":
                    _transition(policy, transitions, "validating", "held", approval_reason)
                    report = _report(
                        policy,
                        request_id,
                        "hold",
                        approval_reason,
                        "held",
                        transitions,
                        fixture_version=fixture["fixture_version"],
                    )
                elif approval_decision == "block":
                    report = _deny(policy, request_id, transitions, approval_reason)
                else:
                    _transition(policy, transitions, "validating", "ready", "policy_satisfied")
                    result, effect_allowed = _run_adapter(request["action"], fixture)
                    if not effect_allowed:
                        _transition(policy, transitions, "ready", "blocked", "process_refused")
                        report = _report(
                            policy,
                            request_id,
                            "block",
                            "process_refused",
                            "blocked",
                            transitions,
                            fixture_version=fixture["fixture_version"],
                            steps_used=action["step_cost"],
                            result=result,
                            counters=_counters(tool_invocations=1),
                        )
                    else:
                        _transition(policy, transitions, "ready", "completed", "fixture_operation_completed")
                        state.effect_counts[key] = state.effect_counts.get(key, 0) + 1
                        report = _report(
                            policy,
                            request_id,
                            "ready",
                            "policy_satisfied",
                            "completed",
                            transitions,
                            fixture_version=fixture["fixture_version"],
                            steps_used=action["step_cost"],
                            result=result,
                            counters=_counters(
                                tool_invocations=1,
                                simulated_effects=state.effect_counts[key],
                            ),
                        )
    state.records[key] = {"binding": _binding(request), "report": deepcopy(report)}
    return report
