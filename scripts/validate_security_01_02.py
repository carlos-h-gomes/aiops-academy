"""Validate private security-01/security-02 authoring and synthetic fixtures."""
from __future__ import annotations

from copy import deepcopy
from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
PLANNED_ROOT = ROOT / "backend/content/planned-units"
CATALOG_PATH = ROOT / "backend/content/curriculum.json"
COURSE_PATH = ROOT / "backend/content/course.json"
MAX_JSON_BYTES = 200_000
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
UNIT_CONTRACTS = {
    "security-01": {
        "order": 1,
        "prerequisites": ["infra-03"],
        "fixture_fields": {"policy", "scenarios"},
        "required_terms": (
            "autenticação",
            "autorização",
            "sujeito",
            "ação",
            "recurso",
            "menor privilégio",
        ),
    },
    "security-02": {
        "order": 2,
        "prerequisites": ["security-01"],
        "fixture_fields": {"policy", "source", "valid_output", "invalid_outputs"},
        "required_terms": (
            "segredo",
            "configuração",
            "dado de estudo",
            "evidência",
            "retenção",
            "redaction",
            "recuperação",
        ),
    },
}
EXPECTED_ACCESS_SCENARIOS = {
    "allow-explicit": {"decision": "allow", "reason": "explicit_permission"},
    "deny-missing-authorization": {
        "decision": "deny",
        "reason": "missing_explicit_permission",
    },
    "deny-cross-scope": {"decision": "deny", "reason": "cross_scope"},
    "deny-escalation": {"decision": "deny", "reason": "escalation_attempt"},
}
EXPECTED_EVIDENCE_REJECTIONS = {
    "secret_leak": "secret_leak",
    "study_data_leak": "study_data_leak",
    "missing_redaction": "missing_redaction",
    "unapproved_field": "unapproved_field",
}


class EvidenceRejected(ValueError):
    """A safe, typed rejection that never contains the rejected value."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _reject_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"Chave JSON duplicada: {key}")
        value[key] = item
    return value


def _load_json(path: Path, maximum: int = MAX_JSON_BYTES):
    if not path.is_file():
        raise ValueError(f"Arquivo local ausente: {path.relative_to(ROOT)}")
    if path.stat().st_size > maximum:
        raise ValueError(f"Arquivo excede {maximum} bytes: {path.relative_to(ROOT)}")
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_reject_duplicate_keys,
    )


def _strict_nonempty_text(value, field: str):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Campo textual inválido: {field}")


def _safe_source(source: dict):
    if not isinstance(source, dict) or set(source) != {"title", "url", "reviewed_on"}:
        raise ValueError("Fonte deve conter title, url e reviewed_on.")
    _strict_nonempty_text(source["title"], "sources.title")
    _strict_nonempty_text(source["url"], "sources.url")
    parsed = urlsplit(source["url"])
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or any(character.isspace() for character in source["url"])
    ):
        raise ValueError("Fonte deve usar HTTPS sem credenciais ou espaços.")
    if date.fromisoformat(source["reviewed_on"]).isoformat() != source["reviewed_on"]:
        raise ValueError("reviewed_on deve ser uma data ISO válida.")


def _resolve_json_fixture(value: str, unit_id: str) -> Path:
    _strict_nonempty_text(value, "fixture path")
    expected_root = (ROOT / f"backend/content/fixtures/{unit_id}").resolve()
    candidate = (ROOT / value).resolve()
    if not candidate.is_relative_to(expected_root) or candidate.suffix.lower() != ".json":
        raise ValueError(f"Caminho de fixture fora do diretório de {unit_id}: {value}")
    if not candidate.is_file():
        raise ValueError(f"Fixture local ausente: {value}")
    return candidate


def _validate_body(unit_id: str, body: str):
    _strict_nonempty_text(body, "body")
    positions = []
    for heading in HEADINGS:
        if body.count(heading) != 1:
            raise ValueError(f"Seção obrigatória ausente ou repetida em {unit_id}: {heading}")
        positions.append(body.index(heading))
    if positions != sorted(positions):
        raise ValueError(f"As seções editoriais estão fora da ordem em {unit_id}.")

    exercise = body[body.index("## Exercício") : body.index("## Pistas")]
    numbered_steps = re.findall(r"(?m)^(\d+)\. ", exercise)
    if (
        numbered_steps != [str(number) for number in range(1, len(numbered_steps) + 1)]
        or len(numbered_steps) < 3
    ):
        raise ValueError(f"O exercício de {unit_id} precisa de passos numerados em sequência.")

    hints = body[body.index("## Pistas") : body.index("## Solução comentada")]
    hint_numbers = re.findall(r"\*\*Pista (\d+) —", hints)
    if (
        not 1 <= len(hint_numbers) <= 2
        or hint_numbers != [str(number) for number in range(1, len(hint_numbers) + 1)]
    ):
        raise ValueError(f"{unit_id} deve conter uma ou duas pistas graduais.")

    folded = body.casefold()
    missing = [term for term in UNIT_CONTRACTS[unit_id]["required_terms"] if term.casefold() not in folded]
    if missing:
        raise ValueError(f"{unit_id} não cobre termos obrigatórios: {missing}")


def _validate_fixture_manifest(unit: dict):
    unit_id = unit["id"]
    fixture = unit["fixture"]
    if not isinstance(fixture, dict) or set(fixture) != UNIT_CONTRACTS[unit_id]["fixture_fields"]:
        raise ValueError(f"Manifesto de fixture incompleto em {unit_id}.")
    if unit_id == "security-01":
        for value in fixture.values():
            _resolve_json_fixture(value, unit_id)
        return

    for key in ("policy", "source", "valid_output"):
        _resolve_json_fixture(fixture[key], unit_id)
    invalid = fixture["invalid_outputs"]
    if not isinstance(invalid, dict) or set(invalid) != set(EXPECTED_EVIDENCE_REJECTIONS):
        raise ValueError("security-02 deve declarar todas as saídas inválidas esperadas.")
    for value in invalid.values():
        _resolve_json_fixture(value, unit_id)


def validate_authored_units() -> dict:
    catalog = _load_json(CATALOG_PATH, 1_000_000)
    course = _load_json(COURSE_PATH, 2_000_000)
    results = {}
    expected_translations = [
        {"locale": "pt-BR", "authoring_status": "authored"},
        {"locale": "en", "authoring_status": "planned"},
        {"locale": "es", "authoring_status": "planned"},
    ]
    planned_catalog_translations = [
        {"locale": locale, "status": "planned", "content_version": None}
        for locale in ("pt-BR", "en", "es")
    ]

    for unit_id, contract in UNIT_CONTRACTS.items():
        unit = _load_json(PLANNED_ROOT / f"{unit_id}.json")
        if not isinstance(unit, dict) or set(unit) != AUTHORING_FIELDS:
            raise ValueError(f"{unit_id} não segue o contrato estrito de autoria.")
        if unit["schema_version"] != "1.0" or unit["id"] != unit_id:
            raise ValueError(f"Schema ou identidade inválidos em {unit_id}.")
        if unit["track_id"] != "security" or type(unit["order"]) is not int or unit["order"] != contract["order"]:
            raise ValueError(f"Trilha ou ordem inválida em {unit_id}.")
        if unit["status"] != "available" or unit["duration_minutes"] != {"essential": 75, "complete": 120}:
            raise ValueError(f"{unit_id} não segue o contrato da aula guiada disponível.")
        if unit["prerequisites"] != contract["prerequisites"]:
            raise ValueError(f"Pré-requisito estável divergente em {unit_id}.")
        for field in ("title", "summary"):
            _strict_nonempty_text(unit[field], f"{unit_id}.{field}")
        if not isinstance(unit["competencies"], list) or not unit["competencies"]:
            raise ValueError(f"{unit_id} precisa de competências observáveis.")
        for competency in unit["competencies"]:
            _strict_nonempty_text(competency, f"{unit_id}.competencies")
        if unit["translations"] != expected_translations:
            raise ValueError(f"Somente PT-BR pode estar authored em {unit_id}.")
        _validate_body(unit_id, unit["body"])
        _validate_fixture_manifest(unit)

        sources = unit["sources"]
        if not isinstance(sources, list) or not 1 <= len(sources) <= 30:
            raise ValueError(f"{unit_id} precisa de uma a 30 fontes primárias.")
        for source in sources:
            _safe_source(source)

        matches = [candidate for candidate in catalog["units"] if candidate["id"] == unit_id]
        if len(matches) != 1:
            raise ValueError(f"O catálogo deve preservar exatamente uma identidade {unit_id}.")
        published = matches[0]
        stable_fields = (
            "id",
            "track_id",
            "order",
            "title",
            "summary",
            "status",
            "prerequisites",
            "competencies",
        )
        for field in stable_fields:
            if published[field] != unit[field]:
                raise ValueError(f"A autoria de {unit_id} diverge do catálogo em {field}.")
        version = "2026.09.20.1" if unit_id == "security-01" else "2026.09.21.1"
        if published["status"] != "available" or published["content_version"] != version or published["practice"]["kind"] != "guided_fixture" or len(published["sources"]) != len(sources):
            raise ValueError(f"{unit_id} não expõe a prática guiada esperada.")
        results[unit_id] = {
            "catalog_status": published["status"],
            "authored_locale": "pt-BR",
            "planned_locales": ["en", "es"],
            "dated_primary_sources": len(sources),
        }

    available = [candidate for candidate in catalog["units"] if candidate["status"] == "available"]
    falsely_available = [
        candidate["id"]
        for candidate in catalog["units"]
        if candidate["practice"] is None and candidate["status"] == "available"
    ]
    security_units = [candidate for candidate in catalog["units"] if candidate["track_id"] == "security"]
    if len(available) != 50 or falsely_available:
        raise ValueError("O recorte alterou disponibilidade ou prática do catálogo.")
    if len(security_units) != 6 or [candidate["status"] for candidate in security_units] != ["available"] * 6:
        raise ValueError("A trilha de Segurança deve expor as seis aulas disponíveis com prática guiada.")
    if [lesson["day"] for lesson in course["lessons"]] != list(range(1, 31)):
        raise ValueError("As 30 aulas existentes foram renumeradas ou alteradas em quantidade.")
    return {
        "units": results,
        "available_units": len(available),
        "planned_security_units": len(security_units),
        "legacy_lessons": len(course["lessons"]),
    }


def _load_security_01_fixture() -> tuple[dict, dict]:
    fixture = _load_json(PLANNED_ROOT / "security-01.json")["fixture"]
    return (
        _load_json(_resolve_json_fixture(fixture["policy"], "security-01")),
        _load_json(_resolve_json_fixture(fixture["scenarios"], "security-01")),
    )


def validate_access_policy(policy: dict):
    if not isinstance(policy, dict) or set(policy) != {
        "schema_version",
        "allowed_actions",
        "subjects",
        "resources",
        "grants",
    }:
        raise ValueError("Política de security-01 fora do contrato estrito.")
    if policy["schema_version"] != "1.0" or policy["allowed_actions"] != ["ler", "alterar"]:
        raise ValueError("Versão ou allowlist de ações inválida em security-01.")

    def indexed(items, label):
        if not isinstance(items, list) or not items:
            raise ValueError(f"Lista vazia ou inválida: {label}")
        result = {}
        for item in items:
            if not isinstance(item, dict) or set(item) != {"id", "scope"}:
                raise ValueError(f"Registro inválido em {label}.")
            _strict_nonempty_text(item["id"], f"{label}.id")
            _strict_nonempty_text(item["scope"], f"{label}.scope")
            if item["id"] in result:
                raise ValueError(f"Identidade duplicada em {label}.")
            result[item["id"]] = item
        return result

    subjects = indexed(policy["subjects"], "subjects")
    resources = indexed(policy["resources"], "resources")
    if not isinstance(policy["grants"], list):
        raise ValueError("Concessões precisam ser uma lista.")
    grants = set()
    for grant in policy["grants"]:
        if not isinstance(grant, dict) or set(grant) != {"subject", "action", "resource"}:
            raise ValueError("Concessão fora do contrato estrito.")
        triple = (grant["subject"], grant["action"], grant["resource"])
        if any(not isinstance(value, str) or not value for value in triple):
            raise ValueError("Concessão contém valor inválido.")
        if triple in grants:
            raise ValueError("Concessão duplicada.")
        if grant["subject"] not in subjects or grant["resource"] not in resources:
            raise ValueError("Concessão referencia sujeito ou recurso ausente.")
        if grant["action"] not in policy["allowed_actions"]:
            raise ValueError("Concessão tenta incluir ação fora da allowlist.")
        if subjects[grant["subject"]]["scope"] != resources[grant["resource"]]["scope"]:
            raise ValueError("Concessão cruza escopos.")
        grants.add(triple)
    return subjects, resources, grants


def evaluate_access(policy: dict, subject: str, action: str, resource: str) -> dict[str, str]:
    subjects, resources, grants = validate_access_policy(policy)
    for value, field in ((subject, "subject"), (action, "action"), (resource, "resource")):
        _strict_nonempty_text(value, field)
    if subject not in subjects:
        return {"decision": "deny", "reason": "unknown_subject"}
    if resource not in resources:
        return {"decision": "deny", "reason": "unknown_resource"}
    if action not in policy["allowed_actions"]:
        return {"decision": "deny", "reason": "escalation_attempt"}
    if subjects[subject]["scope"] != resources[resource]["scope"]:
        return {"decision": "deny", "reason": "cross_scope"}
    if (subject, action, resource) not in grants:
        return {"decision": "deny", "reason": "missing_explicit_permission"}
    return {"decision": "allow", "reason": "explicit_permission"}


def verify_access_scenarios() -> dict:
    policy, scenario_fixture = _load_security_01_fixture()
    validate_access_policy(policy)
    if not isinstance(scenario_fixture, dict) or set(scenario_fixture) != {"schema_version", "scenarios"}:
        raise ValueError("Cenários de security-01 fora do contrato estrito.")
    if scenario_fixture["schema_version"] != "1.0" or len(scenario_fixture["scenarios"]) != 4:
        raise ValueError("security-01 precisa de exatamente quatro cenários.")
    results = {}
    for scenario in scenario_fixture["scenarios"]:
        if not isinstance(scenario, dict) or set(scenario) != {
            "id",
            "subject",
            "action",
            "resource",
            "expected",
        }:
            raise ValueError("Cenário de acesso fora do contrato estrito.")
        scenario_id = scenario["id"]
        if scenario_id in results or scenario_id not in EXPECTED_ACCESS_SCENARIOS:
            raise ValueError("ID de cenário ausente, duplicado ou inesperado.")
        if scenario["expected"] != EXPECTED_ACCESS_SCENARIOS[scenario_id]:
            raise ValueError(f"Expectativa divergente no cenário {scenario_id}.")
        result = evaluate_access(policy, scenario["subject"], scenario["action"], scenario["resource"])
        if result != scenario["expected"]:
            raise AssertionError(f"Decisão divergente no cenário {scenario_id}: {result}")
        results[scenario_id] = result
    if set(results) != set(EXPECTED_ACCESS_SCENARIOS):
        raise ValueError("A matriz não cobre os quatro cenários obrigatórios.")
    for action in ("ler", "alterar"):
        if evaluate_access(policy, "ana-sre", action, "runbook-alpha")["decision"] != "allow":
            raise AssertionError(f"A permissão explícita de {action} não foi aceita.")
    without_read = deepcopy(policy)
    without_read["grants"] = [grant for grant in without_read["grants"] if grant["action"] != "ler"]
    if evaluate_access(without_read, "ana-sre", "ler", "runbook-alpha")["reason"] != "missing_explicit_permission":
        raise AssertionError("A ausência de concessão não resultou em negação por padrão.")
    return {
        "scenario_count": len(results),
        "decisions": {scenario_id: value["decision"] for scenario_id, value in results.items()},
        "explicit_actions": ["ler", "alterar"],
        "external_actions": 0,
    }


def _load_security_02_fixture() -> tuple[dict, dict, dict, dict[str, Path]]:
    fixture = _load_json(PLANNED_ROOT / "security-02.json")["fixture"]
    return (
        _load_json(_resolve_json_fixture(fixture["policy"], "security-02")),
        _load_json(_resolve_json_fixture(fixture["source"], "security-02")),
        _load_json(_resolve_json_fixture(fixture["valid_output"], "security-02")),
        {
            key: _resolve_json_fixture(value, "security-02")
            for key, value in fixture["invalid_outputs"].items()
        },
    )


def validate_handling_policy(policy: dict, source: dict):
    policy_fields = {
        "schema_version",
        "redaction_token",
        "allowed_output_fields",
        "required_redactions",
        "classifications",
    }
    if not isinstance(policy, dict) or set(policy) != policy_fields or policy["schema_version"] != "1.0":
        raise ValueError("Política de security-02 fora do contrato estrito.")
    expected_source_fields = {
        "event_id",
        "decision",
        "rule_id",
        "summary",
        "runtime_mode",
        "secret_marker",
        "study_record",
    }
    if not isinstance(source, dict) or set(source) != expected_source_fields:
        raise ValueError("Registro de origem fora do contrato estrito.")
    for key, value in source.items():
        _strict_nonempty_text(value, f"source.{key}")
    if not source["secret_marker"].startswith("SEGREDO-DEMO-INERTE-NAO-USAR-"):
        raise ValueError("O marcador deve declarar explicitamente que é inerte.")
    if not source["study_record"].startswith("ESTUDO-SINTETICO-") or "@example.invalid" not in source["study_record"]:
        raise ValueError("O dado de estudo deve ser sintético e usar domínio reservado .invalid.")
    if policy["redaction_token"] != "[REDIGIDO]":
        raise ValueError("Token de redaction inesperado.")
    if policy["allowed_output_fields"] != [
        "event_id",
        "decision",
        "rule_id",
        "summary",
        "redactions",
    ]:
        raise ValueError("Allowlist de evidência inesperada.")
    if policy["required_redactions"] != ["secret_marker", "study_record"]:
        raise ValueError("Campos protegidos inesperados.")

    classifications = policy["classifications"]
    if not isinstance(classifications, dict) or set(classifications) != expected_source_fields:
        raise ValueError("Toda entrada deve ter classificação explícita.")
    expected_categories = {
        "event_id": "evidence",
        "decision": "evidence",
        "rule_id": "evidence",
        "summary": "evidence",
        "runtime_mode": "configuration",
        "secret_marker": "secret_like",
        "study_record": "study_data",
    }
    for field, classification in classifications.items():
        if not isinstance(classification, dict) or set(classification) != {
            "category",
            "persist",
            "retention_days",
        }:
            raise ValueError(f"Classificação inválida: {field}")
        if classification["category"] != expected_categories[field]:
            raise ValueError(f"Categoria divergente: {field}")
        if type(classification["persist"]) is not bool or type(classification["retention_days"]) is not int:
            raise ValueError(f"Persistência/retenção inválida: {field}")
        should_persist = field in {"event_id", "decision", "rule_id", "summary"}
        expected_retention = 30 if should_persist else 0
        if classification["persist"] != should_persist or classification["retention_days"] != expected_retention:
            raise ValueError(f"Persistência/retenção diverge da minimização: {field}")


def validate_redacted_evidence(policy: dict, source: dict, candidate: dict) -> str:
    validate_handling_policy(policy, source)
    if not isinstance(candidate, dict):
        raise EvidenceRejected("invalid_shape")
    allowed = set(policy["allowed_output_fields"])
    if set(candidate) != allowed:
        raise EvidenceRejected("unapproved_field")
    serialized = json.dumps(candidate, ensure_ascii=False, sort_keys=True)
    if source["secret_marker"] in serialized:
        raise EvidenceRejected("secret_leak")
    if source["study_record"] in serialized:
        raise EvidenceRejected("study_data_leak")
    redactions = candidate.get("redactions")
    required = set(policy["required_redactions"])
    if not isinstance(redactions, dict) or set(redactions) != required:
        raise EvidenceRejected("missing_redaction")
    if any(value != policy["redaction_token"] for value in redactions.values()):
        raise EvidenceRejected("invalid_redaction")
    for field in ("event_id", "decision", "rule_id", "summary"):
        if candidate[field] != source[field]:
            raise EvidenceRejected("evidence_mismatch")
    return "accepted"


def verify_evidence_fixture() -> dict:
    policy, source, valid_output, invalid_paths = _load_security_02_fixture()
    accepted = validate_redacted_evidence(policy, source, valid_output)
    rejected = {}
    for fixture_id, expected_code in EXPECTED_EVIDENCE_REJECTIONS.items():
        try:
            validate_redacted_evidence(policy, source, _load_json(invalid_paths[fixture_id]))
        except EvidenceRejected as error:
            if error.code != expected_code:
                raise AssertionError(f"{fixture_id} falhou com código inesperado: {error.code}") from error
            rejected[fixture_id] = error.code
        else:
            raise AssertionError(f"A saída inválida {fixture_id} foi aceita.")
    return {
        "valid_output": accepted,
        "rejected_outputs": rejected,
        "allowed_fields": len(policy["allowed_output_fields"]),
        "required_redactions": len(policy["required_redactions"]),
        "raw_values_emitted": 0,
        "external_actions": 0,
    }


def main():
    result = {
        "authoring": validate_authored_units(),
        "security-01": verify_access_scenarios(),
        "security-02": verify_evidence_fixture(),
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
