"""Validate private agents-01..04 authoring and the local deterministic controller."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.agent_controller import (  # noqa: E402
    ControllerState,
    REQUEST_FIELDS,
    RESULT_FIELDS,
    execute,
    validate_fixtures,
    validate_policy,
    validate_request,
    validate_result,
)
from validate_security_01_02 import _load_json, _safe_source, _strict_nonempty_text  # noqa: E402
from validate_security_06 import verify_policy_fixtures as verify_security_06_policy  # noqa: E402


CATALOG_PATH = ROOT / "backend/content/curriculum.json"
COURSE_PATH = ROOT / "backend/content/course.json"
FIXTURE_ROOT = ROOT / "backend/content/fixtures/agents-01-04"
PLANNED_ROOT = ROOT / "backend/content/planned-units"
UNIT_FIELDS = {
    "schema_version",
    "id",
    "track_id",
    "order",
    "title",
    "summary",
    "status",
    "prerequisites",
    "competencies",
    "duration_minutes",
    "translations",
    "body",
    "fixture",
    "sources",
}
HEADINGS = (
    "## Objetivo observável",
    "## Contexto e limites",
    "## Exemplo sintético",
    "## Exercício",
    "## Pistas",
    "## Solução comentada",
    "## Critério de conclusão",
    "## Variação",
    "## Referências primárias",
)
EXPECTED_IDENTITIES = {
    "agents-01": (1, "Processos, regras e agentes", ["infra-06"]),
    "agents-02": (2, "Modelos, assistentes e ferramentas", ["agents-01"]),
    "agents-03": (3, "Saídas estruturadas e ferramentas", ["agents-02"]),
    "agents-04": (4, "Estado, avaliação e aprovação", ["agents-03"]),
}
PUBLISHED = {
    "agents-01": ("2026.09.20.1", {"essential": 75, "complete": 120}),
    "agents-02": ("2026.09.21.1", {"essential": 75, "complete": 120}),
    "agents-03": ("2026.09.21.1", {"essential": 90, "complete": 150}),
    "agents-04": ("2026.09.21.1", {"essential": 90, "complete": 150}),
}
REQUIRED_TERMS = {
    "agents-01": ("regra determinística", "assistência limitada", "recusa", "responsável", "impacto alto"),
    "agents-02": ("modelo", "assistente", "orquestrador", "estado", "ferramenta", "saída plausível"),
    "agents-03": ("schema", "campo extra", "ferramenta", "alvo", "command", "url"),
    "agents-04": ("idempotência", "orçamento", "aprovação", "expirada", "negada", "retomada"),
}
EXPECTED_SCENARIOS = {
    "classify-rule": ("ready", "completed", "policy_satisfied", "rule"),
    "classify-limited-agent": ("ready", "completed", "policy_satisfied", "limited_agent"),
    "classify-high-impact-refusal": ("block", "blocked", "process_refused", "refusal"),
    "classify-incomplete-refusal": ("block", "blocked", "process_refused", "refusal"),
    "approval-missing-hold": ("hold", "held", "approval_missing", None),
    "approval-expired-block": ("block", "blocked", "approval_expired", None),
    "approval-denied-block": ("block", "blocked", "approval_denied", None),
}


def _fixture_path(name: str) -> Path:
    path = (FIXTURE_ROOT / name).resolve()
    if not path.is_relative_to(FIXTURE_ROOT.resolve()) or path.suffix != ".json" or not path.is_file():
        raise ValueError(f"agents fixture path invalid:{name}")
    return path


def load_contract() -> tuple[dict, dict, dict, dict, list[dict]]:
    request_schema = _load_json(_fixture_path("control-request.schema.json"))
    result_schema = _load_json(_fixture_path("control-result.schema.json"))
    policy = _load_json(_fixture_path("policy.json"))
    fixtures = _load_json(_fixture_path("fixtures.json"))
    scenarios = _load_json(_fixture_path("scenarios.json"))
    if not isinstance(scenarios, dict) or set(scenarios) != {"schema_version", "scenarios"}:
        raise ValueError("scenario_set_invalid")
    if scenarios["schema_version"] != "1.0" or not isinstance(scenarios["scenarios"], list):
        raise ValueError("scenario_set_version_invalid")
    return request_schema, result_schema, policy, fixtures, scenarios["scenarios"]


def validate_authoring() -> dict:
    catalog = _load_json(CATALOG_PATH, 1_000_000)
    course = _load_json(COURSE_PATH, 2_000_000)
    translations = [
        {"locale": "pt-BR", "authoring_status": "authored"},
        {"locale": "en", "authoring_status": "planned"},
        {"locale": "es", "authoring_status": "planned"},
    ]
    fixture_manifest = {
        "schema": "backend/content/fixtures/agents-01-04/control-request.schema.json",
        "result_schema": "backend/content/fixtures/agents-01-04/control-result.schema.json",
        "policy": "backend/content/fixtures/agents-01-04/policy.json",
        "data": "backend/content/fixtures/agents-01-04/fixtures.json",
        "scenarios": "backend/content/fixtures/agents-01-04/scenarios.json",
    }
    results = {}
    for unit_id, (order, title, prerequisites) in EXPECTED_IDENTITIES.items():
        unit = _load_json(PLANNED_ROOT / f"{unit_id}.json")
        if not isinstance(unit, dict) or set(unit) != UNIT_FIELDS:
            raise ValueError(f"authoring_contract_invalid:{unit_id}")
        expected_status = "available"
        expected_duration = PUBLISHED[unit_id][1]
        if (
            unit["schema_version"] != "1.0"
            or unit["id"] != unit_id
            or unit["track_id"] != "agents"
            or unit["order"] != order
            or unit["title"] != title
            or unit["status"] != expected_status
            or unit["prerequisites"] != prerequisites
            or unit["duration_minutes"] != expected_duration
            or unit["translations"] != translations
            or unit["fixture"] != fixture_manifest
        ):
            raise ValueError(f"authoring_identity_invalid:{unit_id}")
        _strict_nonempty_text(unit["summary"], f"{unit_id}.summary")
        if not isinstance(unit["competencies"], list) or len(unit["competencies"]) != 2:
            raise ValueError(f"authoring_competencies_invalid:{unit_id}")
        body = unit["body"]
        positions = []
        for heading in HEADINGS:
            if body.count(heading) != 1:
                raise ValueError(f"authoring_heading_invalid:{unit_id}:{heading}")
            positions.append(body.index(heading))
        if positions != sorted(positions):
            raise ValueError(f"authoring_heading_order_invalid:{unit_id}")
        exercise = body[body.index("## Exercício") : body.index("## Pistas")]
        steps = re.findall(r"(?m)^(\d+)\. ", exercise)
        if len(steps) < 3 or steps != [str(index) for index in range(1, len(steps) + 1)]:
            raise ValueError(f"authoring_exercise_invalid:{unit_id}")
        hints = body[body.index("## Pistas") : body.index("## Solução comentada")]
        hint_numbers = re.findall(r"\*\*Pista (\d+) —", hints)
        if not 1 <= len(hint_numbers) <= 2 or hint_numbers != [str(index) for index in range(1, len(hint_numbers) + 1)]:
            raise ValueError(f"authoring_hints_invalid:{unit_id}")
        missing = [term for term in REQUIRED_TERMS[unit_id] if term.casefold() not in body.casefold()]
        if missing:
            raise ValueError(f"authoring_terms_missing:{unit_id}:{missing}")
        if not isinstance(unit["sources"], list) or len(unit["sources"]) < 3:
            raise ValueError(f"authoring_sources_invalid:{unit_id}")
        for source in unit["sources"]:
            _safe_source(source)
            if source["reviewed_on"] != "2026-09-11":
                raise ValueError(f"authoring_source_date_invalid:{unit_id}")
        published = [item for item in catalog["units"] if item["id"] == unit_id]
        if len(published) != 1:
            raise ValueError(f"catalog_identity_invalid:{unit_id}")
        published = published[0]
        for field in ("id", "track_id", "order", "title", "summary", "status", "prerequisites", "competencies"):
            if published[field] != unit[field]:
                raise ValueError(f"catalog_authoring_mismatch:{unit_id}:{field}")
        expected_public_translations = [
            {"locale": "pt-BR", "status": "available", "content_version": PUBLISHED[unit_id][0]},
            {"locale": "en", "status": "planned", "content_version": None},
            {"locale": "es", "status": "planned", "content_version": None},
        ]
        if (
            published["status"] != "available"
            or published["content_version"] != PUBLISHED[unit_id][0]
            or published["lesson_day"] is not None
            or published["duration_minutes"] != PUBLISHED[unit_id][1]
            or published["practice"] is None
            or published["practice"]["kind"] != "guided_fixture"
            or not published["sources"]
            or published["verified_tool_versions"]
            or published["translations"] != expected_public_translations
        ):
            raise ValueError(f"catalog_published_lesson_invalid:{unit_id}")
        results[unit_id] = {"sources": len(unit["sources"]), "exercise_steps": len(steps), "hints": len(hint_numbers)}
    available = sum(item["status"] == "available" for item in catalog["units"])
    planned = sum(item["status"] == "planned" for item in catalog["units"])
    if len(catalog["units"]) != 50 or (available, planned) != (50, 0):
        raise ValueError("catalog_counts_changed")
    if [lesson["day"] for lesson in course["lessons"]] != list(range(1, 31)):
        raise ValueError("legacy_lessons_changed")
    return {"units": results, "available": available, "planned": planned, "legacy_lessons": 30}


def validate_schemas() -> dict:
    request_schema, result_schema, _, _, _ = load_contract()
    request_top = {"$schema", "$id", "title", "type", "additionalProperties", "required", "properties", "$defs"}
    result_top = request_top
    if set(request_schema) != request_top or set(result_schema) != result_top:
        raise ValueError("schema_topology_invalid")
    if request_schema["additionalProperties"] is not False or set(request_schema["required"]) != REQUEST_FIELDS or set(request_schema["properties"]) != REQUEST_FIELDS:
        raise ValueError("request_schema_not_closed")
    if result_schema["additionalProperties"] is not False or set(result_schema["required"]) != RESULT_FIELDS or set(result_schema["properties"]) != RESULT_FIELDS:
        raise ValueError("result_schema_not_closed")
    if any(
        result_schema["properties"][field]["additionalProperties"] is not False
        for field in ("result", "counters")
    ):
        raise ValueError("result_nested_schema_not_closed")
    transition = result_schema["properties"]["transitions"]["items"]
    if transition["additionalProperties"] is not False:
        raise ValueError("transition_schema_not_closed")
    return {"request_fields": len(REQUEST_FIELDS), "result_fields": len(RESULT_FIELDS), "extra_fields_allowed": 0}


def verify_scenarios() -> dict:
    _, _, policy, fixtures, scenarios = load_contract()
    validate_policy(policy)
    validate_fixtures(fixtures)
    if {item.get("scenario_id") for item in scenarios} != set(EXPECTED_SCENARIOS):
        raise ValueError("scenario_inventory_invalid")
    results = {}
    for scenario in scenarios:
        if not isinstance(scenario, dict) or set(scenario) != {"scenario_id", "request", "expected"}:
            raise ValueError("scenario_contract_invalid")
        expected = EXPECTED_SCENARIOS[scenario["scenario_id"]]
        if scenario["expected"] != dict(zip(("decision", "state", "reason", "classification"), expected)):
            raise ValueError(f"scenario_expected_invalid:{scenario['scenario_id']}")
        before = deepcopy(scenario["request"])
        report = execute(policy, fixtures, scenario["request"], ControllerState())
        actual = (report["decision"], report["state"], report["reason"], report["result"]["classification"])
        if actual != expected:
            raise AssertionError(f"scenario_result_invalid:{scenario['scenario_id']}:{actual}")
        if scenario["request"] != before:
            raise AssertionError("controller_mutated_request")
        if any(report["counters"][key] for key in ("network_calls", "child_processes", "external_writes")):
            raise AssertionError("external_effect_detected")
        results[scenario["scenario_id"]] = report["reason"]
    return {"scenarios": results, "external_effects": 0}


def verify_idempotency_and_resume() -> dict:
    _, _, policy, fixtures, scenarios = load_contract()
    by_id = {item["scenario_id"]: item["request"] for item in scenarios}
    state = ControllerState()
    first = execute(policy, fixtures, deepcopy(by_id["classify-rule"]), state)
    repeated = execute(policy, fixtures, deepcopy(by_id["classify-rule"]), state)
    if first["counters"]["simulated_effects"] != 1 or repeated["counters"]["simulated_effects"] != 1 or not repeated["idempotent"]:
        raise AssertionError("idempotency_failed")
    resume_state = ControllerState()
    pending = deepcopy(by_id["approval-missing-hold"])
    held = execute(policy, fixtures, pending, resume_state)
    pending["approval_id"] = "approval-layer-valid"
    resumed = execute(policy, fixtures, pending, resume_state)
    replay = execute(policy, fixtures, pending, resume_state)
    if (held["decision"], resumed["state"], replay["idempotent"]) != ("hold", "completed", True):
        raise AssertionError("safe_resume_failed")
    if resumed["counters"]["simulated_effects"] != 1 or replay["counters"]["simulated_effects"] != 1:
        raise AssertionError("resume_duplicated_effect")
    return {"repeated_effects": 1, "resume_effects": 1, "resume_transitions": len(resumed["transitions"])}


def verify_negative_mutations() -> dict:
    _, _, policy, fixtures, scenarios = load_contract()
    base = deepcopy(next(item["request"] for item in scenarios if item["scenario_id"] == "classify-rule"))
    cases = {}
    mutations = {
        "schema_extra_field": ("command", "inert-not-a-command"),
        "action_not_allowed": ("action", "external_action"),
        "tool_not_allowed": ("tool", "shell"),
        "target_not_allowed": ("target", "external-target"),
        "fixture_not_allowed": ("fixture_id", "layers-v1"),
        "step_budget_exceeded": ("step_budget", 1),
    }
    for reason, (field, value) in mutations.items():
        request = deepcopy(base)
        request["request_id"] = f"deny-{reason.replace('_', '-')}"
        request["idempotency_key"] = f"idem-{reason.replace('_', '-')}"
        request[field] = value
        report = execute(policy, fixtures, request, ControllerState())
        if (report["decision"], report["reason"]) != ("block", reason):
            raise AssertionError(f"negative_mutation_failed:{reason}:{report['reason']}")
        cases[reason] = report["state"]
    wrong_type = deepcopy(base)
    wrong_type["step_budget"] = "2"
    report = execute(policy, fixtures, wrong_type, ControllerState())
    if report["reason"] != "schema_step_budget_invalid":
        raise AssertionError("schema_type_mutation_failed")
    cases["schema_step_budget_invalid"] = report["state"]
    return cases


def verify_security_regression() -> dict:
    result = verify_security_06_policy()
    if (result["allowed"], result["denied"]) != (1, 14):
        raise AssertionError("security_06_regression")
    return {"security_06_allowed": 1, "security_06_denied": 14, "external_effects": 0}


def main() -> None:
    result = {
        "authoring": validate_authoring(),
        "schemas": validate_schemas(),
        "controller": verify_scenarios(),
        "idempotency-and-resume": verify_idempotency_and_resume(),
        "negative-mutations": verify_negative_mutations(),
        "security-06-regression": verify_security_regression(),
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
