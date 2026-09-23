"""Validate private security-06 authoring and its static agent-policy contract."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import re

from validate_security_01_02 import _load_json, _safe_source, _strict_nonempty_text
from validate_security_04_05 import (
    validate_authored_units as validate_security_04_05_authoring,
    verify_incident_fixtures,
    verify_security_01_03_regressions,
    verify_supply_fixtures,
)


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "backend/content/curriculum.json"
COURSE_PATH = ROOT / "backend/content/course.json"
PLANNED_PATH = ROOT / "backend/content/planned-units/security-06.json"
FIXTURE_ROOT = ROOT / "backend/content/fixtures/security-06"
AUTHORING_FIELDS = {
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
REQUEST_FIELDS = {
    "schema_version",
    "request_id",
    "subject",
    "operation",
    "target",
    "tool",
    "authorization_id",
    "approval_id",
    "user_input",
    "retrieved_context",
    "tool_output",
}
POLICY_FIELDS = {
    "schema_version",
    "policy_id",
    "request_schema",
    "evaluation_time",
    "allowed_operations",
    "allowed_tools",
    "subjects",
    "targets",
    "authorizations",
    "approvals",
    "content_controls",
    "approval_required_for",
    "report_fields",
    "capability_statement",
}
EXPECTED_SCENARIOS = {
    "allow-authorized-read": ("allow", "external_policy_satisfied"),
    "deny-user-prompt-injection": ("deny", "text_policy_override_attempt"),
    "deny-retrieved-prompt-injection": ("deny", "text_policy_override_attempt"),
    "deny-tool-output-prompt-injection": ("deny", "text_policy_override_attempt"),
    "deny-false-sensitive-data": ("deny", "sensitive_data_in_untrusted_text"),
    "deny-tool-not-allowed": ("deny", "tool_not_allowed"),
    "deny-target-out-of-scope": ("deny", "target_out_of_scope"),
    "deny-missing-authorization": ("deny", "authorization_missing"),
    "deny-expired-authorization": ("deny", "authorization_expired"),
    "deny-authorization-mismatch": ("deny", "authorization_not_bound_to_request"),
    "deny-missing-approval": ("deny", "approval_missing"),
    "deny-expired-approval": ("deny", "approval_expired"),
    "deny-approval-mismatch": ("deny", "approval_not_bound_to_request"),
    "deny-operation-not-allowed": ("deny", "operation_not_allowed"),
    "deny-unknown-subject": ("deny", "subject_unknown"),
}
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")
REQUEST_ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
BOUND_FIELDS = ("subject", "operation", "target", "tool")


class RequestRejected(ValueError):
    """A typed denial that never embeds rejected content."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _resolve_fixture(value: str) -> Path:
    _strict_nonempty_text(value, "fixture path")
    candidate = (ROOT / value).resolve()
    if not candidate.is_relative_to(FIXTURE_ROOT.resolve()) or candidate.suffix.lower() != ".json":
        raise ValueError(f"Caminho fora de security-06: {value}")
    if not candidate.is_file():
        raise ValueError(f"Fixture ausente: {value}")
    return candidate


def _parse_timestamp(value: str, field: str) -> datetime:
    _strict_nonempty_text(value, field)
    if not value.endswith("Z"):
        raise ValueError(f"Timestamp deve usar UTC Z: {field}")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"Timestamp inválido: {field}") from exc
    return parsed


def validate_security_06_authoring() -> dict:
    unit = _load_json(PLANNED_PATH)
    catalog = _load_json(CATALOG_PATH, 1_000_000)
    course = _load_json(COURSE_PATH, 2_000_000)
    if not isinstance(unit, dict) or set(unit) != AUTHORING_FIELDS:
        raise ValueError("security-06 não segue o contrato estrito de autoria.")
    if (
        unit["schema_version"] != "1.0"
        or unit["id"] != "security-06"
        or unit["track_id"] != "security"
        or unit["order"] != 6
        or unit["status"] != "available"
        or unit["duration_minutes"] != {"essential": 90, "complete": 150}
        or unit["prerequisites"] != ["security-05"]
    ):
        raise ValueError("Identidade, ordem, estado ou pré-requisito inválido em security-06.")
    for field in ("title", "summary"):
        _strict_nonempty_text(unit[field], f"security-06.{field}")
    if not isinstance(unit["competencies"], list) or not unit["competencies"]:
        raise ValueError("security-06 precisa de competências observáveis.")
    for competency in unit["competencies"]:
        _strict_nonempty_text(competency, "security-06.competencies")
    if unit["translations"] != [
        {"locale": "pt-BR", "authoring_status": "authored"},
        {"locale": "en", "authoring_status": "planned"},
        {"locale": "es", "authoring_status": "planned"},
    ]:
        raise ValueError("Apenas a fonte privada PT-BR pode estar authored.")

    body = unit["body"]
    _strict_nonempty_text(body, "security-06.body")
    positions = []
    for heading in HEADINGS:
        if body.count(heading) != 1:
            raise ValueError(f"Seção ausente ou repetida em security-06: {heading}")
        positions.append(body.index(heading))
    if positions != sorted(positions):
        raise ValueError("Seções editoriais fora da ordem em security-06.")
    exercise = body[body.index("## Exercício") : body.index("## Pistas")]
    steps = re.findall(r"(?m)^(\d+)\. ", exercise)
    if len(steps) < 3 or steps != [str(i) for i in range(1, len(steps) + 1)]:
        raise ValueError("Exercício numerado inválido em security-06.")
    hints = body[body.index("## Pistas") : body.index("## Solução comentada")]
    hint_numbers = re.findall(r"\*\*Pista (\d+) —", hints)
    if not 1 <= len(hint_numbers) <= 2 or hint_numbers != [
        str(i) for i in range(1, len(hint_numbers) + 1)
    ]:
        raise ValueError("security-06 deve conter uma ou duas pistas graduais.")
    required_terms = (
        "prompt injection",
        "user_input",
        "retrieved_context",
        "tool_output",
        "autorização fora do prompt",
        "aprovação",
        "campo extra",
        "ferramenta",
        "alvo fora de escopo",
        "zero ferramenta",
        "zero rede",
        "não detecta toda",
    )
    folded = body.casefold()
    missing_terms = [term for term in required_terms if term.casefold() not in folded]
    if missing_terms:
        raise ValueError(f"security-06 não cobre termos obrigatórios: {missing_terms}")

    fixture = unit["fixture"]
    if not isinstance(fixture, dict) or set(fixture) != {"schema", "policy", "scenarios"}:
        raise ValueError("Manifesto de fixtures incompleto em security-06.")
    for value in fixture.values():
        _resolve_fixture(value)
    if not isinstance(unit["sources"], list) or len(unit["sources"]) < 4:
        raise ValueError("security-06 precisa de quatro fontes primárias.")
    for source in unit["sources"]:
        _safe_source(source)

    matches = [candidate for candidate in catalog["units"] if candidate["id"] == "security-06"]
    if len(matches) != 1:
        raise ValueError("O catálogo deve conter exatamente uma security-06.")
    published = matches[0]
    for field in (
        "id",
        "track_id",
        "order",
        "title",
        "summary",
        "status",
        "prerequisites",
        "competencies",
    ):
        if published[field] != unit[field]:
            raise ValueError(f"A autoria security-06 diverge do catálogo em {field}.")
    published_translations = [
        {"locale": "pt-BR", "status": "available", "content_version": "2026.09.21.1"},
        *[{"locale": locale, "status": "planned", "content_version": None} for locale in ("en", "es")],
    ]
    if (
        published["status"] != "available"
        or published["content_version"] != "2026.09.21.1"
        or published["lesson_day"] is not None
        or published["duration_minutes"] != {"essential": 90, "complete": 150}
        or published["practice"]["kind"] != "guided_fixture"
        or len(published["sources"]) != len(unit["sources"])
        or published["verified_tool_versions"]
        or published["translations"] != published_translations
    ):
        raise ValueError("security-06 não expõe a prática guiada publicada esperada.")
    available = [candidate for candidate in catalog["units"] if candidate["status"] == "available"]
    planned = [candidate for candidate in catalog["units"] if candidate["status"] == "planned"]
    if len(catalog["units"]) != 50 or len(available) != 50 or planned:
        raise ValueError("O recorte deve preservar 30 aulas legadas e 20 aulas guiadas disponíveis.")
    if [lesson["day"] for lesson in course["lessons"]] != list(range(1, 31)):
        raise ValueError("As 30 aulas legadas foram alteradas.")
    return {
        "unit": "security-06",
        "catalog_status": "available",
        "authored_locale": "pt-BR",
        "planned_locales": ["en", "es"],
        "dated_primary_sources": len(unit["sources"]),
        "available_units": len(available),
        "planned_units": len(planned),
        "legacy_lessons": len(course["lessons"]),
    }


def validate_request_schema(schema: dict) -> None:
    if not isinstance(schema, dict):
        raise ValueError("Schema de pedido deve ser objeto.")
    required_top = {"$schema", "$id", "title", "type", "additionalProperties", "required", "properties", "$defs"}
    if set(schema) != required_top:
        raise ValueError("Schema de pedido contém campos inesperados.")
    if (
        schema["$schema"] != "https://json-schema.org/draft/2020-12/schema"
        or schema["type"] != "object"
        or schema["additionalProperties"] is not False
        or set(schema["required"]) != REQUEST_FIELDS
        or len(schema["required"]) != len(REQUEST_FIELDS)
        or set(schema["properties"]) != REQUEST_FIELDS
    ):
        raise ValueError("Schema de pedido não fecha forma e campos obrigatórios.")
    if schema["properties"]["schema_version"] != {"const": "1.0"}:
        raise ValueError("Versão do pedido não está fixada.")
    defs = schema["$defs"]
    if set(defs) != {"identifier", "optionalIdentifier", "untrustedText"}:
        raise ValueError("Definições do schema divergentes.")
    if defs["untrustedText"] != {"type": "string", "maxLength": 500}:
        raise ValueError("Limite textual do schema divergente.")


def _validate_string_list(value, field: str, expected: list[str] | None = None) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError(f"Lista inválida: {field}")
    for item in value:
        _strict_nonempty_text(item, field)
    if len(value) != len(set(value)):
        raise ValueError(f"Lista contém duplicata: {field}")
    if expected is not None and value != expected:
        raise ValueError(f"Lista divergente: {field}")


def _validate_bound_records(records, id_field: str, expected_issuer: str) -> None:
    record_fields = {id_field, "issuer", *BOUND_FIELDS, "expires_at"}
    if not isinstance(records, list) or not records:
        raise ValueError(f"Registros ausentes: {id_field}")
    identifiers = []
    for record in records:
        if not isinstance(record, dict) or set(record) != record_fields:
            raise ValueError(f"Registro fora do contrato: {id_field}")
        for field in (id_field, "issuer", *BOUND_FIELDS):
            _strict_nonempty_text(record[field], f"{id_field}.{field}")
        if record["issuer"] != expected_issuer:
            raise ValueError(f"Emissor não confiável: {id_field}")
        _parse_timestamp(record["expires_at"], f"{id_field}.expires_at")
        identifiers.append(record[id_field])
    if len(identifiers) != len(set(identifiers)):
        raise ValueError(f"ID duplicado: {id_field}")


def validate_policy(policy: dict) -> None:
    if not isinstance(policy, dict) or set(policy) != POLICY_FIELDS:
        raise ValueError("Policy de agentes fora do contrato estrito.")
    if policy["schema_version"] != "1.0" or policy["policy_id"] != "security-06-agent-policy-v1":
        raise ValueError("Identidade da policy divergente.")
    schema_path = _resolve_fixture(policy["request_schema"])
    if schema_path.name != "agent-request.schema.json":
        raise ValueError("Policy aponta para schema inesperado.")
    evaluation_time = _parse_timestamp(policy["evaluation_time"], "evaluation_time")
    _validate_string_list(policy["allowed_operations"], "allowed_operations", ["read_fixture"])
    _validate_string_list(policy["allowed_tools"], "allowed_tools", ["fixture_reader"])

    if set(policy["subjects"]) != {"learner-agent"}:
        raise ValueError("Sujeitos da policy divergentes.")
    subject = policy["subjects"]["learner-agent"]
    if not isinstance(subject, dict) or set(subject) != {
        "allowed_operations",
        "allowed_tools",
        "allowed_scopes",
    }:
        raise ValueError("Contrato do sujeito divergente.")
    _validate_string_list(subject["allowed_operations"], "subject.allowed_operations", ["read_fixture"])
    _validate_string_list(subject["allowed_tools"], "subject.allowed_tools", ["fixture_reader"])
    _validate_string_list(subject["allowed_scopes"], "subject.allowed_scopes", ["training-public"])

    expected_targets = {
        "runbook-public": {"scope": "training-public"},
        "runbook-restricted": {"scope": "training-restricted"},
    }
    if policy["targets"] != expected_targets:
        raise ValueError("Alvos ou escopos da policy divergentes.")
    _validate_bound_records(policy["authorizations"], "authorization_id", "training-policy")
    _validate_bound_records(policy["approvals"], "approval_id", "human-reviewer")
    for record in [*policy["authorizations"], *policy["approvals"]]:
        if record["operation"] not in policy["allowed_operations"]:
            raise ValueError("Registro referencia operação fora da allowlist.")
        if record["tool"] not in policy["allowed_tools"]:
            raise ValueError("Registro referencia ferramenta fora da allowlist.")
        if record["target"] not in policy["targets"]:
            raise ValueError("Registro referencia alvo desconhecido.")
        if record["subject"] not in policy["subjects"]:
            raise ValueError("Registro referencia sujeito desconhecido.")
    if not any(_parse_timestamp(item["expires_at"], "authorization.expires_at") <= evaluation_time for item in policy["authorizations"]):
        raise ValueError("Policy precisa de autorização expirada para o exercício.")
    if not any(_parse_timestamp(item["expires_at"], "approval.expires_at") <= evaluation_time for item in policy["approvals"]):
        raise ValueError("Policy precisa de aprovação expirada para o exercício.")

    controls = policy["content_controls"]
    if not isinstance(controls, dict) or set(controls) != {
        "untrusted_fields",
        "deny_text_fragments",
        "sensitive_markers",
        "maximum_characters_per_field",
    }:
        raise ValueError("Controles de conteúdo fora do contrato.")
    _validate_string_list(
        controls["untrusted_fields"],
        "content_controls.untrusted_fields",
        ["user_input", "retrieved_context", "tool_output"],
    )
    _validate_string_list(controls["deny_text_fragments"], "content_controls.deny_text_fragments")
    _validate_string_list(controls["sensitive_markers"], "content_controls.sensitive_markers")
    if controls["maximum_characters_per_field"] != 500:
        raise ValueError("Limite textual da policy diverge do schema.")
    _validate_string_list(policy["approval_required_for"], "approval_required_for", ["read_fixture"])
    expected_report_fields = [
        "request_id",
        "decision",
        "reason",
        "policy_id",
        "flags",
        "tool_invocations",
        "network_calls",
        "child_processes",
        "external_writes",
    ]
    if policy["report_fields"] != expected_report_fields:
        raise ValueError("Allowlist do relatório divergente.")
    if policy["capability_statement"] != {
        "tool_adapter_exists": False,
        "network_enabled": False,
        "process_execution_enabled": False,
        "external_writes_enabled": False,
    }:
        raise ValueError("O contrato estático não pode declarar capacidade real.")


def validate_request_shape(request: dict, schema: dict) -> None:
    validate_request_schema(schema)
    if not isinstance(request, dict):
        raise RequestRejected("schema_type_invalid")
    extras = set(request) - REQUEST_FIELDS
    if extras:
        raise RequestRejected("schema_extra_field")
    missing = REQUEST_FIELDS - set(request)
    if missing:
        raise RequestRejected("schema_required_field_missing")
    if request["schema_version"] != "1.0":
        raise RequestRejected("schema_version_invalid")
    if not isinstance(request["request_id"], str) or not REQUEST_ID.fullmatch(request["request_id"]):
        raise RequestRejected("schema_identifier_invalid")
    for field in ("subject", "operation", "target", "tool"):
        if not isinstance(request[field], str) or not IDENTIFIER.fullmatch(request[field]):
            raise RequestRejected("schema_identifier_invalid")
    for field in ("authorization_id", "approval_id"):
        if request[field] is not None and (
            not isinstance(request[field], str) or not IDENTIFIER.fullmatch(request[field])
        ):
            raise RequestRejected("schema_identifier_invalid")
    maximum = schema["$defs"]["untrustedText"]["maxLength"]
    for field in ("user_input", "retrieved_context", "tool_output"):
        if not isinstance(request[field], str) or len(request[field]) > maximum:
            raise RequestRejected("schema_untrusted_text_invalid")


def _report(policy: dict, request_id: str, decision: str, reason: str, flags: list[str]) -> dict:
    report = {
        "request_id": request_id,
        "decision": decision,
        "reason": reason,
        "policy_id": policy["policy_id"],
        "flags": flags,
        "tool_invocations": 0,
        "network_calls": 0,
        "child_processes": 0,
        "external_writes": 0,
    }
    if list(report) != policy["report_fields"]:
        raise AssertionError("Relatório diverge da allowlist da policy.")
    return report


def _find_record(records: list[dict], id_field: str, identifier: str) -> dict | None:
    return next((record for record in records if record[id_field] == identifier), None)


def _record_matches_request(record: dict, request: dict) -> bool:
    return all(record[field] == request[field] for field in BOUND_FIELDS)


def evaluate_request(policy: dict, schema: dict, request: dict) -> dict:
    validate_policy(policy)
    request_id = request.get("request_id", "invalid-request") if isinstance(request, dict) else "invalid-request"
    try:
        validate_request_shape(request, schema)
    except RequestRejected as exc:
        return _report(policy, request_id, "deny", exc.code, [])

    flags = []
    override_found = False
    sensitive_found = False
    controls = policy["content_controls"]
    for field in controls["untrusted_fields"]:
        value = request[field]
        if value:
            flags.append(f"untrusted_text:{field}")
        folded = value.casefold()
        if any(fragment.casefold() in folded for fragment in controls["deny_text_fragments"]):
            flags.append(f"policy_override_attempt:{field}")
            override_found = True
        if any(marker.casefold() in folded for marker in controls["sensitive_markers"]):
            flags.append(f"sensitive_marker:{field}")
            sensitive_found = True
    if sensitive_found:
        return _report(policy, request["request_id"], "deny", "sensitive_data_in_untrusted_text", flags)
    if override_found:
        return _report(policy, request["request_id"], "deny", "text_policy_override_attempt", flags)

    subject = policy["subjects"].get(request["subject"])
    if subject is None:
        return _report(policy, request["request_id"], "deny", "subject_unknown", flags)
    if (
        request["operation"] not in policy["allowed_operations"]
        or request["operation"] not in subject["allowed_operations"]
    ):
        return _report(policy, request["request_id"], "deny", "operation_not_allowed", flags)
    if request["tool"] not in policy["allowed_tools"] or request["tool"] not in subject["allowed_tools"]:
        return _report(policy, request["request_id"], "deny", "tool_not_allowed", flags)
    target = policy["targets"].get(request["target"])
    if target is None:
        return _report(policy, request["request_id"], "deny", "target_unknown", flags)
    if target["scope"] not in subject["allowed_scopes"]:
        return _report(policy, request["request_id"], "deny", "target_out_of_scope", flags)

    if request["authorization_id"] is None:
        return _report(policy, request["request_id"], "deny", "authorization_missing", flags)
    authorization = _find_record(
        policy["authorizations"], "authorization_id", request["authorization_id"]
    )
    if authorization is None:
        return _report(policy, request["request_id"], "deny", "authorization_unknown", flags)
    if not _record_matches_request(authorization, request):
        return _report(
            policy, request["request_id"], "deny", "authorization_not_bound_to_request", flags
        )
    evaluation_time = _parse_timestamp(policy["evaluation_time"], "evaluation_time")
    if _parse_timestamp(authorization["expires_at"], "authorization.expires_at") <= evaluation_time:
        return _report(policy, request["request_id"], "deny", "authorization_expired", flags)

    if request["operation"] in policy["approval_required_for"]:
        if request["approval_id"] is None:
            return _report(policy, request["request_id"], "deny", "approval_missing", flags)
        approval = _find_record(policy["approvals"], "approval_id", request["approval_id"])
        if approval is None:
            return _report(policy, request["request_id"], "deny", "approval_unknown", flags)
        if not _record_matches_request(approval, request):
            return _report(
                policy, request["request_id"], "deny", "approval_not_bound_to_request", flags
            )
        if _parse_timestamp(approval["expires_at"], "approval.expires_at") <= evaluation_time:
            return _report(policy, request["request_id"], "deny", "approval_expired", flags)
    return _report(policy, request["request_id"], "allow", "external_policy_satisfied", flags)


def _load_fixtures() -> tuple[dict, dict, list[dict]]:
    unit = _load_json(PLANNED_PATH)
    schema = _load_json(_resolve_fixture(unit["fixture"]["schema"]))
    policy = _load_json(_resolve_fixture(unit["fixture"]["policy"]))
    scenario_set = _load_json(_resolve_fixture(unit["fixture"]["scenarios"]))
    if not isinstance(scenario_set, dict) or set(scenario_set) != {"schema_version", "scenarios"}:
        raise ValueError("Conjunto de cenários fora do contrato.")
    if scenario_set["schema_version"] != "1.0" or not isinstance(scenario_set["scenarios"], list):
        raise ValueError("Versão ou lista de cenários inválida.")
    return schema, policy, scenario_set["scenarios"]


def verify_policy_fixtures() -> dict:
    schema, policy, scenarios = _load_fixtures()
    validate_request_schema(schema)
    validate_policy(policy)
    if len(scenarios) != len(EXPECTED_SCENARIOS):
        raise ValueError("Quantidade de cenários security-06 divergente.")
    if {scenario.get("scenario_id") for scenario in scenarios} != set(EXPECTED_SCENARIOS):
        raise ValueError("IDs de cenários security-06 divergentes.")
    results = {}
    allowed = 0
    denied = 0
    for scenario in scenarios:
        if not isinstance(scenario, dict) or set(scenario) != {"scenario_id", "request", "expected"}:
            raise ValueError("Cenário fora do contrato estrito.")
        if scenario["scenario_id"] != scenario["request"].get("request_id"):
            raise ValueError("scenario_id diverge de request_id.")
        if not isinstance(scenario["expected"], dict) or set(scenario["expected"]) != {
            "decision",
            "reason",
        }:
            raise ValueError("Resultado esperado fora do contrato.")
        before = deepcopy(scenario["request"])
        report = evaluate_request(policy, schema, scenario["request"])
        expected_decision, expected_reason = EXPECTED_SCENARIOS[scenario["scenario_id"]]
        if report["decision"] != expected_decision or report["reason"] != expected_reason:
            raise AssertionError(f"Decisão divergente: {scenario['scenario_id']}")
        if scenario["expected"] != {"decision": expected_decision, "reason": expected_reason}:
            raise ValueError(f"Fixture declara resultado divergente: {scenario['scenario_id']}")
        if scenario["request"] != before:
            raise AssertionError("O avaliador alterou a entrada.")
        if any(report[key] != 0 for key in ("tool_invocations", "network_calls", "child_processes", "external_writes")):
            raise AssertionError("Contrato estático registrou efeito externo.")
        serialized = json.dumps(report, ensure_ascii=False, sort_keys=True)
        forbidden_values = [
            *policy["content_controls"]["deny_text_fragments"],
            *policy["content_controls"]["sensitive_markers"],
        ]
        if any(value.casefold() in serialized.casefold() for value in forbidden_values):
            raise AssertionError("Relatório ecoou conteúdo hostil ou sensível.")
        results[scenario["scenario_id"]] = {
            "decision": report["decision"],
            "reason": report["reason"],
        }
        allowed += report["decision"] == "allow"
        denied += report["decision"] == "deny"
    return {
        "scenarios": results,
        "allowed": allowed,
        "denied": denied,
        "schema_extra_fields_allowed": 0,
        "tool_invocations": 0,
        "network_calls": 0,
        "child_processes": 0,
        "external_writes": 0,
        "input_mutations": 0,
    }


def verify_security_01_05_regressions() -> dict:
    authoring = validate_security_04_05_authoring()
    earlier = verify_security_01_03_regressions()
    supply = verify_supply_fixtures()
    incident = verify_incident_fixtures()
    return {
        "authored_units": [*earlier["authored_units"], *sorted(authoring["units"])],
        "security_01_03_external_actions": earlier["external_actions"],
        "supply_approved": supply["approved"],
        "supply_blocked": supply["blocked"],
        "supply_review": supply["review"],
        "incident_completed": incident["completed"],
        "incident_rejected": incident["rejected"],
        "security_04_05_external_actions": (
            supply["image_downloads"]
            + supply["scanner_invocations"]
            + incident["network_calls"]
            + incident["child_processes"]
            + incident["real_restores"]
            + incident["external_writes"]
        ),
    }


def main() -> None:
    result = {
        "authoring": validate_security_06_authoring(),
        "security-06": verify_policy_fixtures(),
        "security-01-05-regression": verify_security_01_05_regressions(),
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
