"""Offline reference evaluators and authoring checks for agents-06..08.

Inputs are closed synthetic objects, never commands, paths, or network targets.
Runtime integration belongs in the application service layer, not this script.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
UNIT_IDS = ("agents-06", "agents-07", "agents-08")
PUBLISHED_DURATIONS = {
    "agents-06": {"essential": 75, "complete": 120},
    "agents-07": {"essential": 75, "complete": 120},
    "agents-08": {"essential": 75, "complete": 120},
}
HEADINGS = ("Objetivo observável", "Contexto e limites", "Exemplo sintético", "Exercício", "Pistas", "Solução comentada", "Critério de conclusão", "Variação", "Referências primárias")
RUNBOOKS = {
    "access": ("RB-ACCESS-1", "Verifique o estado sintético da conta e encaminhe recuperação ao responsável."),
    "performance": ("RB-PERF-1", "Compare latência e erros da amostra sintética antes de sugerir diagnóstico."),
}
FACTS = {"F-DATE": "Data: 12 de outubro de 2030.", "F-FORMAT": "Formato: oficina online.", "F-DURATION": "Duração: 60 minutos."}


def _closed(value: object, fields: set[str]) -> dict:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError("invalid_contract")
    return value


def _identifier(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,47}", value):
        raise ValueError("invalid_identifier")
    return value


def _identifiers(value: object, maximum: int = 8) -> list[str]:
    if not isinstance(value, list) or len(value) > maximum:
        raise ValueError("invalid_identifier_list")
    for item in value:
        _identifier(item)
    if len(set(value)) != len(value):
        raise ValueError("duplicate_identifier")
    return value


def _result(decision: str, reason: str, **details: object) -> dict:
    return {"decision": decision, "reason": reason, **details, "external_effects": 0}


def evaluate_support(payload: dict) -> dict:
    """Prepare only a fixed, cited draft or a typed refusal/escalation."""
    _closed(payload, {"ticket_id", "category", "evidence_ids", "impact", "contains_sensitive", "requested_action"})
    _identifier(payload["ticket_id"])
    _identifier(payload["category"])
    _identifier(payload["impact"])
    if payload["category"] not in RUNBOOKS or payload["impact"] not in ("low", "high"):
        raise ValueError("invalid_ticket_classification")
    if type(payload["contains_sensitive"]) is not bool:
        raise ValueError("invalid_sensitive_flag")
    evidence = _identifiers(payload["evidence_ids"])
    _identifier(payload["requested_action"])
    details = {"draft": None, "citations": [], "requires_review": True, "sent": False}
    if payload["requested_action"] != "draft":
        return _result("block", "external_action_forbidden", **details)
    if payload["contains_sensitive"] or payload["impact"] == "high":
        return _result("hold", "human_review_required", **details)
    runbook, draft = RUNBOOKS[payload["category"]]
    if not evidence:
        return _result("hold", "evidence_missing", **details)
    if evidence != [runbook]:
        return _result("hold", "evidence_not_applicable", **details)
    details.update(draft=draft, citations=[runbook])
    return _result("draft_ready", "cited_draft_requires_review", **details)


def evaluate_briefing(payload: dict) -> dict:
    """Check fixed fact IDs and a synthetic version-bound editorial decision."""
    _closed(payload, {"brief_id", "provided_fact_ids", "draft_claim_ids", "artifact_version", "approval", "requested_action"})
    _identifier(payload["brief_id"])
    _identifier(payload["artifact_version"])
    _identifier(payload["requested_action"])
    facts = _identifiers(payload["provided_fact_ids"])
    claims = _identifiers(payload["draft_claim_ids"])
    approval = payload["approval"]
    if approval is not None:
        _closed(approval, {"reviewer", "decision", "artifact_version"})
        for field in ("reviewer", "artifact_version"):
            _identifier(approval[field])
        if approval["decision"] not in ("approved", "denied"):
            raise ValueError("invalid_approval_decision")
    details = {"draft": None, "supported_claims": [], "publication_allowed": False}
    if payload["requested_action"] != "draft":
        return _result("block", "external_action_forbidden", **details)
    if not claims:
        return _result("hold", "claims_missing", **details)
    if any(fact not in FACTS for fact in facts) or any(claim not in facts or claim not in FACTS for claim in claims):
        return _result("block", "unsupported_claim", **details)
    details.update(draft=" ".join(FACTS[claim] for claim in claims), supported_claims=list(claims))
    if approval is None:
        return _result("hold", "approval_missing", **details)
    if approval["reviewer"] != "synthetic-reviewer":
        return _result("block", "reviewer_not_allowed", **details)
    if approval["decision"] == "denied":
        return _result("block", "approval_denied", **details)
    if approval["artifact_version"] != payload["artifact_version"]:
        return _result("block", "approval_version_mismatch", **details)
    return _result("reviewed_draft", "synthetic_review_bound", **details)


def _records(value: object) -> dict[str, list[int]]:
    if not isinstance(value, list) or len(value) > 20:
        raise ValueError("invalid_record_limit")
    indexed: dict[str, list[int]] = {}
    for record in value:
        _closed(record, {"transaction_id", "cents", "currency"})
        identity = _identifier(record["transaction_id"])
        if type(record["cents"]) is not int or not 0 <= record["cents"] <= 1_000_000_000:
            raise ValueError("invalid_cents")
        if record["currency"] != "BRL":
            raise ValueError("invalid_currency")
        indexed.setdefault(identity, []).append(record["cents"])
    return indexed


def evaluate_reconciliation(payload: dict) -> dict:
    """Compare unique synthetic keys using integer cents; never settle funds."""
    _closed(payload, {"batch_id", "ledger", "statement", "requested_action"})
    _identifier(payload["batch_id"])
    _identifier(payload["requested_action"])
    ledger, statement = _records(payload["ledger"]), _records(payload["statement"])
    details = {"matched_ids": [], "exceptions": [], "financial_action_allowed": False}
    if payload["requested_action"] != "reconcile":
        return _result("block", "external_action_forbidden", **details)
    if not ledger and not statement:
        return _result("hold", "no_records", **details)
    for identity in sorted(set(ledger) | set(statement)):
        left, right = ledger.get(identity, []), statement.get(identity, [])
        if len(left) > 1 or len(right) > 1:
            details["exceptions"].append({"transaction_id": identity, "reason": "duplicate_id", "ledger_count": len(left), "statement_count": len(right)})
        elif not left:
            details["exceptions"].append({"transaction_id": identity, "reason": "missing_ledger"})
        elif not right:
            details["exceptions"].append({"transaction_id": identity, "reason": "missing_statement"})
        elif left[0] != right[0]:
            details["exceptions"].append({"transaction_id": identity, "reason": "amount_mismatch", "delta_cents": right[0] - left[0]})
        else:
            details["matched_ids"].append(identity)
    if details["exceptions"]:
        return _result("review", "exceptions_require_review", **details)
    return _result("balanced", "sample_matches", **details)


EVALUATORS = {"agents-06": evaluate_support, "agents-07": evaluate_briefing, "agents-08": evaluate_reconciliation}


def _load(path: Path) -> dict:
    if path.stat().st_size > 100_000:
        raise ValueError("content_too_large")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("object_required")
    return value


def load_scenarios(unit_id: str) -> list[dict]:
    if unit_id not in EVALUATORS:
        raise ValueError("unknown_unit")
    value = _load(ROOT / "backend/content/fixtures" / unit_id / "scenarios.json")
    _closed(value, {"schema_version", "unit_id", "scenarios"})
    if value["schema_version"] != "1.0" or value["unit_id"] != unit_id:
        raise ValueError("fixture_identity_invalid")
    if not isinstance(value["scenarios"], list) or not 5 <= len(value["scenarios"]) <= 8:
        raise ValueError("fixture_scenario_count")
    seen = set()
    for scenario in value["scenarios"]:
        _closed(scenario, {"scenario_id", "label", "input", "expected"})
        _identifier(scenario["scenario_id"])
        if scenario["scenario_id"] in seen or not isinstance(scenario["label"], str) or not scenario["label"].strip():
            raise ValueError("fixture_scenario_identity")
        seen.add(scenario["scenario_id"])
    return value["scenarios"]


def validate_authoring() -> dict:
    results = {}
    for unit_id in UNIT_IDS:
        unit = _load(ROOT / "backend/content/planned-units" / f"{unit_id}.json")
        if unit["id"] != unit_id or unit["track_id"] != "agents" or unit["status"] != "available" or unit["duration_minutes"] != PUBLISHED_DURATIONS[unit_id]:
            raise ValueError("authoring_identity_invalid")
        if unit["prerequisites"] != [f"agents-{int(unit_id[-2:])-1:02d}"]:
            raise ValueError("authoring_prerequisite_invalid")
        if unit["translations"] != [{"locale": "pt-BR", "authoring_status": "authored"}, {"locale": "en", "authoring_status": "planned"}, {"locale": "es", "authoring_status": "planned"}]:
            raise ValueError("authoring_translation_invalid")
        body = unit["body"]
        positions = []
        for heading in HEADINGS:
            marker = "## " + heading
            if body.count(marker) != 1:
                raise ValueError("authoring_heading_invalid")
            positions.append(body.index(marker))
        if positions != sorted(positions):
            raise ValueError("authoring_heading_order")
        steps = re.findall(r"(?m)^(\d+)\. ", body[positions[3]:positions[4]])
        if len(steps) < 5 or steps != [str(i) for i in range(1, len(steps) + 1)]:
            raise ValueError("authoring_steps_invalid")
        if len(unit["sources"]) < 2 or any(not source["url"].startswith("https://") for source in unit["sources"]):
            raise ValueError("authoring_sources_invalid")
        expected_manifest = {"scenarios": f"backend/content/fixtures/{unit_id}/scenarios.json", "evaluator": "scripts/validate_agents_06_08.py"}
        if unit["fixture"] != expected_manifest:
            raise ValueError("authoring_fixture_manifest")
        results[unit_id] = {"exercise_steps": len(steps), "scenarios": len(load_scenarios(unit_id))}
    return results


def verify_scenarios() -> dict:
    results = {}
    for unit_id, evaluator in EVALUATORS.items():
        scenarios = load_scenarios(unit_id)
        for scenario in scenarios:
            original = deepcopy(scenario["input"])
            result = evaluator(scenario["input"])
            if result != scenario["expected"] or scenario["input"] != original or evaluator(original) != result:
                raise AssertionError(f"scenario_failed:{unit_id}:{scenario['scenario_id']}")
        results[unit_id] = len(scenarios)
    return results


def main() -> None:
    print(json.dumps({"authoring": validate_authoring(), "scenarios": verify_scenarios()}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
