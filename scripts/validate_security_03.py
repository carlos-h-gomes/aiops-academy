"""Validate private security-03 authoring and static hardening fixtures."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from validate_security_01_02 import (
    _load_json,
    _safe_source,
    _strict_nonempty_text,
    evaluate_access,
    validate_access_policy,
    validate_authored_units as validate_security_01_02_authoring,
    validate_handling_policy,
    verify_access_scenarios,
    verify_evidence_fixture,
)


ROOT = Path(__file__).resolve().parents[1]
PLANNED_PATH = ROOT / "backend/content/planned-units/security-03.json"
FIXTURE_ROOT = ROOT / "backend/content/fixtures/security-03"
CATALOG_PATH = ROOT / "backend/content/curriculum.json"
COURSE_PATH = ROOT / "backend/content/course.json"
EXPECTED_IMPORTS = {
    "identity_policy": "backend/content/fixtures/security-01/policy.json",
    "handling_policy": "backend/content/fixtures/security-02/handling-policy.json",
    "handling_source": "backend/content/fixtures/security-02/source-record.json",
}
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
INVALID_FIXTURE_CODES = {
    "public_bind": ["public_bind"],
    "host_network": ["host_network"],
    "configurable_egress": ["configurable_egress"],
    "unapproved_destination": ["unapproved_egress_destination"],
    "docker_socket": ["docker_socket"],
    "broad_mount": ["host_bind_mount"],
    "privileged": ["privileged_process"],
    "added_capability": ["added_capability"],
    "missing_process_control": ["missing_process_control:read_only"],
}
EXPECTED_PROCESS_CONTROLS = {
    "privileged": False,
    "cap_drop": ["ALL"],
    "cap_add": [],
    "read_only": True,
    "no_new_privileges": True,
    "init": True,
    "restart": "no",
    "pids_limit": True,
}


def _resolve_security_03_fixture(value: str) -> Path:
    _strict_nonempty_text(value, "fixture path")
    candidate = (ROOT / value).resolve()
    if not candidate.is_relative_to(FIXTURE_ROOT.resolve()) or candidate.suffix.lower() != ".json":
        raise ValueError(f"Caminho fora de security-03: {value}")
    if not candidate.is_file():
        raise ValueError(f"Fixture ausente: {value}")
    return candidate


def _load_fixed_import(value: str, import_name: str) -> dict:
    if value != EXPECTED_IMPORTS[import_name]:
        raise ValueError(f"Import não autorizado: {import_name}")
    candidate = (ROOT / value).resolve()
    expected = (ROOT / EXPECTED_IMPORTS[import_name]).resolve()
    if candidate != expected:
        raise ValueError(f"Import fora do caminho fixo: {import_name}")
    return _load_json(candidate)


def validate_security_03_authoring() -> dict:
    unit = _load_json(PLANNED_PATH)
    if not isinstance(unit, dict) or set(unit) != AUTHORING_FIELDS:
        raise ValueError("security-03 não segue o contrato estrito de autoria.")
    if (
        unit["schema_version"] != "1.0"
        or unit["id"] != "security-03"
        or unit["track_id"] != "security"
        or unit["order"] != 3
        or unit["status"] != "available"
        or unit["duration_minutes"] != {"essential": 90, "complete": 150}
        or unit["prerequisites"] != ["security-02"]
    ):
        raise ValueError("Identidade, ordem, estado ou pré-requisito inválido em security-03.")
    for field in ("title", "summary"):
        _strict_nonempty_text(unit[field], f"security-03.{field}")
    if not isinstance(unit["competencies"], list) or not unit["competencies"]:
        raise ValueError("security-03 precisa de competências observáveis.")
    for competency in unit["competencies"]:
        _strict_nonempty_text(competency, "security-03.competencies")
    if unit["translations"] != [
        {"locale": "pt-BR", "authoring_status": "authored"},
        {"locale": "en", "authoring_status": "planned"},
        {"locale": "es", "authoring_status": "planned"},
    ]:
        raise ValueError("Apenas a fonte privada PT-BR pode estar authored.")

    body = unit["body"]
    _strict_nonempty_text(body, "security-03.body")
    positions = []
    for heading in HEADINGS:
        if body.count(heading) != 1:
            raise ValueError(f"Seção ausente ou repetida: {heading}")
        positions.append(body.index(heading))
    if positions != sorted(positions):
        raise ValueError("Seções editoriais fora da ordem.")
    exercise = body[body.index("## Exercício") : body.index("## Pistas")]
    steps = re.findall(r"(?m)^(\d+)\. ", exercise)
    if len(steps) < 3 or steps != [str(number) for number in range(1, len(steps) + 1)]:
        raise ValueError("O exercício precisa de passos numerados em sequência.")
    hints = body[body.index("## Pistas") : body.index("## Solução comentada")]
    hint_numbers = re.findall(r"\*\*Pista (\d+) —", hints)
    if not 1 <= len(hint_numbers) <= 2 or hint_numbers != [str(i) for i in range(1, len(hint_numbers) + 1)]:
        raise ValueError("security-03 deve conter uma ou duas pistas graduais.")
    required_terms = (
        "0.0.0.0",
        "network_mode",
        "egress",
        "socket Docker",
        "mount",
        "privileged",
        "capability",
        "loopback",
        "rota fixa",
        "segredo",
        "identidade",
    )
    folded = body.casefold()
    missing_terms = [term for term in required_terms if term.casefold() not in folded]
    if missing_terms:
        raise ValueError(f"Autoria não cobre termos obrigatórios: {missing_terms}")

    fixture = unit["fixture"]
    if not isinstance(fixture, dict) or set(fixture) != {"policy", "valid_topology", "invalid_topologies"}:
        raise ValueError("Manifesto de fixtures incompleto em security-03.")
    _resolve_security_03_fixture(fixture["policy"])
    _resolve_security_03_fixture(fixture["valid_topology"])
    invalid = fixture["invalid_topologies"]
    if not isinstance(invalid, dict) or set(invalid) != set(INVALID_FIXTURE_CODES):
        raise ValueError("Casos inválidos incompletos em security-03.")
    for value in invalid.values():
        _resolve_security_03_fixture(value)
    if not isinstance(unit["sources"], list) or len(unit["sources"]) < 3:
        raise ValueError("security-03 precisa de fontes primárias suficientes.")
    for source in unit["sources"]:
        _safe_source(source)

    catalog = _load_json(CATALOG_PATH, 1_000_000)
    course = _load_json(COURSE_PATH, 2_000_000)
    matches = [candidate for candidate in catalog["units"] if candidate["id"] == "security-03"]
    if len(matches) != 1:
        raise ValueError("O catálogo deve conter exatamente uma security-03.")
    published = matches[0]
    for field in ("id", "track_id", "order", "title", "summary", "status", "prerequisites", "competencies"):
        if published[field] != unit[field]:
            raise ValueError(f"A autoria diverge do catálogo em {field}.")
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
        raise ValueError("security-03 não expõe a prática guiada publicada esperada.")
    available = [candidate for candidate in catalog["units"] if candidate["status"] == "available"]
    planned = [candidate for candidate in catalog["units"] if candidate["status"] == "planned"]
    if len(catalog["units"]) != 50 or len(available) != 50 or planned:
        raise ValueError("O recorte deve preservar 30 aulas legadas e 20 aulas guiadas disponíveis.")
    if [lesson["day"] for lesson in course["lessons"]] != list(range(1, 31)):
        raise ValueError("As 30 aulas legadas foram alteradas.")
    return {
        "unit": "security-03",
        "catalog_status": "available",
        "catalog_translations": ["available", "planned", "planned"],
        "available_units": 50,
        "planned_units": 0,
        "legacy_lessons": 30,
        "dated_primary_sources": len(unit["sources"]),
    }


def validate_common_policy(policy: dict) -> dict:
    if not isinstance(policy, dict) or set(policy) != {
        "schema_version",
        "imports",
        "evidence_contract",
        "hardening",
    } or policy["schema_version"] != "1.0":
        raise ValueError("Política comum fora do contrato estrito.")
    imports = policy["imports"]
    if imports != EXPECTED_IMPORTS:
        raise ValueError("A política comum precisa usar apenas imports fixos de security-01/02.")
    identity_policy = _load_fixed_import(imports["identity_policy"], "identity_policy")
    handling_policy = _load_fixed_import(imports["handling_policy"], "handling_policy")
    handling_source = _load_fixed_import(imports["handling_source"], "handling_source")
    validate_access_policy(identity_policy)
    validate_handling_policy(handling_policy, handling_source)

    evidence = policy["evidence_contract"]
    if not isinstance(evidence, dict) or set(evidence) != {
        "allowed_fields",
        "protected_categories",
        "redaction_token",
    }:
        raise ValueError("Contrato de evidência comum inválido.")
    if evidence["allowed_fields"] != ["scenario_id", "decision", "reasons"]:
        raise ValueError("A evidência de hardening deve ser mínima e fechada.")
    if evidence["protected_categories"] != ["secret_like", "study_data"]:
        raise ValueError("Categorias protegidas divergentes de security-02.")
    if evidence["redaction_token"] != handling_policy["redaction_token"]:
        raise ValueError("Token de redaction diverge de security-02.")
    protected_fields = {
        field
        for field, classification in handling_policy["classifications"].items()
        if classification["category"] in evidence["protected_categories"]
    }
    if protected_fields != {"secret_marker", "study_record"}:
        raise ValueError("Campos protegidos importados inesperados.")

    hardening = policy["hardening"]
    expected_hardening_fields = {
        "allowed_network_mode",
        "require_internal_network",
        "require_ip_masquerade_disabled",
        "allowed_publishers",
        "allowed_publish_hosts",
        "allowed_egress_mode",
        "allowed_egress_destinations",
        "forbid_user_configurable_egress",
        "forbidden_docker_socket_paths",
        "forbid_host_bind_mounts",
        "forbidden_process_users",
        "required_process_controls",
    }
    if not isinstance(hardening, dict) or set(hardening) != expected_hardening_fields:
        raise ValueError("Regras de hardening fora do contrato estrito.")
    expected_fixed_values = {
        "allowed_network_mode": "isolated",
        "require_internal_network": True,
        "require_ip_masquerade_disabled": True,
        "allowed_publishers": ["recovery-gateway"],
        "allowed_publish_hosts": ["127.0.0.1"],
        "allowed_egress_mode": "fixed",
        "allowed_egress_destinations": ["audit-sink"],
        "forbid_user_configurable_egress": True,
        "forbidden_docker_socket_paths": ["/var/run/docker.sock", "//./pipe/docker_engine"],
        "forbid_host_bind_mounts": True,
        "forbidden_process_users": ["root", "0", "0:0"],
    }
    for field, expected in expected_fixed_values.items():
        if hardening[field] != expected:
            raise ValueError(f"Regra comum divergente: {field}")
    if hardening["required_process_controls"] != EXPECTED_PROCESS_CONTROLS:
        raise ValueError("Controles mínimos de processo divergentes.")
    return {
        "identity_policy": identity_policy,
        "handling_policy": handling_policy,
        "handling_source": handling_source,
        "protected_fields": protected_fields,
        "hardening": hardening,
        "evidence_fields": evidence["allowed_fields"],
    }


def _validate_string_list(value, field: str, maximum: int = 10):
    if not isinstance(value, list) or len(value) > maximum:
        raise ValueError(f"Lista inválida: {field}")
    for item in value:
        _strict_nonempty_text(item, field)


def validate_topology_shape(topology: dict) -> None:
    if not isinstance(topology, dict) or set(topology) != {
        "schema_version",
        "scenario_id",
        "authorization",
        "service",
    } or topology["schema_version"] != "1.0":
        raise ValueError("Topologia fora do contrato estrito.")
    _strict_nonempty_text(topology["scenario_id"], "scenario_id")
    authorization = topology["authorization"]
    if not isinstance(authorization, dict) or set(authorization) != {"subject", "action", "resource"}:
        raise ValueError("Pedido de autorização fora do contrato estrito.")
    for field, value in authorization.items():
        _strict_nonempty_text(value, f"authorization.{field}")

    service = topology["service"]
    if not isinstance(service, dict) or set(service) != {"id", "network", "process", "mounts", "secrets"}:
        raise ValueError("Serviço fora do contrato estrito.")
    _strict_nonempty_text(service["id"], "service.id")
    network = service["network"]
    if not isinstance(network, dict) or set(network) != {
        "mode",
        "internal",
        "enable_ip_masquerade",
        "publications",
        "egress",
    }:
        raise ValueError("Rede fora do contrato estrito.")
    _strict_nonempty_text(network["mode"], "network.mode")
    if type(network["internal"]) is not bool or type(network["enable_ip_masquerade"]) is not bool:
        raise ValueError("Controles de isolamento precisam ser booleanos.")
    publications = network["publications"]
    if not isinstance(publications, list) or len(publications) > 4:
        raise ValueError("Publishers fora do limite.")
    for publication in publications:
        if not isinstance(publication, dict) or set(publication) != {"publisher", "host_ip"}:
            raise ValueError("Publisher fora do contrato estrito.")
        _strict_nonempty_text(publication["publisher"], "publication.publisher")
        _strict_nonempty_text(publication["host_ip"], "publication.host_ip")
    egress = network["egress"]
    if not isinstance(egress, dict) or set(egress) != {"mode", "destinations", "user_configurable"}:
        raise ValueError("Egress fora do contrato estrito.")
    _strict_nonempty_text(egress["mode"], "egress.mode")
    _validate_string_list(egress["destinations"], "egress.destinations", maximum=4)
    if type(egress["user_configurable"]) is not bool:
        raise ValueError("user_configurable precisa ser booleano.")

    process = service["process"]
    allowed_process_fields = {"user", *EXPECTED_PROCESS_CONTROLS}
    if not isinstance(process, dict) or not set(process).issubset(allowed_process_fields):
        raise ValueError("Processo contém campo não permitido.")
    if "user" in process:
        _strict_nonempty_text(process["user"], "process.user")
    for field in ("privileged", "read_only", "no_new_privileges", "init", "pids_limit"):
        if field in process and type(process[field]) is not bool:
            raise ValueError(f"Controle booleano inválido: {field}")
    for field in ("cap_drop", "cap_add"):
        if field in process:
            _validate_string_list(process[field], f"process.{field}")
    if "restart" in process:
        _strict_nonempty_text(process["restart"], "process.restart")

    mounts = service["mounts"]
    if not isinstance(mounts, list) or len(mounts) > 10:
        raise ValueError("Mounts fora do limite.")
    for mount in mounts:
        if not isinstance(mount, dict) or set(mount) != {"type", "source", "target", "read_only"}:
            raise ValueError("Mount fora do contrato estrito.")
        for field in ("type", "source", "target"):
            _strict_nonempty_text(mount[field], f"mount.{field}")
        if type(mount["read_only"]) is not bool:
            raise ValueError("mount.read_only precisa ser booleano.")
    _validate_string_list(service["secrets"], "service.secrets")


def _append_once(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def evaluate_topology(policy: dict, topology: dict) -> dict:
    common = validate_common_policy(policy)
    validate_topology_shape(topology)
    hardening = common["hardening"]
    service = topology["service"]
    network = service["network"]
    process = service["process"]
    reasons: list[str] = []

    request = topology["authorization"]
    access = evaluate_access(
        common["identity_policy"],
        request["subject"],
        request["action"],
        request["resource"],
    )
    if access["decision"] != "allow":
        _append_once(reasons, "identity_not_authorized")

    if network["mode"] == "host":
        _append_once(reasons, "host_network")
    elif network["mode"] != hardening["allowed_network_mode"]:
        _append_once(reasons, "unsupported_network_mode")
    if hardening["require_internal_network"] and not network["internal"]:
        _append_once(reasons, "network_not_internal")
    if hardening["require_ip_masquerade_disabled"] and network["enable_ip_masquerade"]:
        _append_once(reasons, "ip_masquerade_enabled")
    for publication in network["publications"]:
        if publication["publisher"] not in hardening["allowed_publishers"]:
            _append_once(reasons, "unapproved_publisher")
        if publication["host_ip"] not in hardening["allowed_publish_hosts"]:
            _append_once(reasons, "public_bind")
    egress = network["egress"]
    if egress["mode"] != hardening["allowed_egress_mode"]:
        _append_once(reasons, "unsupported_egress_mode")
    if hardening["forbid_user_configurable_egress"] and egress["user_configurable"]:
        _append_once(reasons, "configurable_egress")
    if egress["destinations"] != hardening["allowed_egress_destinations"]:
        _append_once(reasons, "unapproved_egress_destination")

    if service["secrets"]:
        _append_once(reasons, "secret_distribution")
    forbidden_sockets = {path.casefold() for path in hardening["forbidden_docker_socket_paths"]}
    for mount in service["mounts"]:
        socket_exposed = mount["source"].casefold() in forbidden_sockets or mount["target"].casefold() in forbidden_sockets
        if socket_exposed:
            _append_once(reasons, "docker_socket")
        elif hardening["forbid_host_bind_mounts"] and mount["type"] == "bind":
            _append_once(reasons, "host_bind_mount")

    if "user" not in process:
        _append_once(reasons, "missing_process_identity")
    elif process["user"].casefold() in {user.casefold() for user in hardening["forbidden_process_users"]}:
        _append_once(reasons, "root_process")
    for field, expected in hardening["required_process_controls"].items():
        if field not in process:
            _append_once(reasons, f"missing_process_control:{field}")
        elif process[field] != expected:
            if field == "privileged":
                _append_once(reasons, "privileged_process")
            elif field == "cap_add":
                _append_once(reasons, "added_capability")
            elif field == "cap_drop":
                _append_once(reasons, "capabilities_not_dropped")
            else:
                _append_once(reasons, f"missing_process_control:{field}")

    report = {
        "scenario_id": topology["scenario_id"],
        "decision": "deny" if reasons else "accept",
        "reasons": reasons or ["hardening_policy_satisfied"],
    }
    if list(report) != common["evidence_fields"]:
        raise AssertionError("Relatório diverge da allowlist de evidência.")
    serialized = json.dumps(report, ensure_ascii=False, sort_keys=True)
    for protected_field in common["protected_fields"]:
        if protected_field in serialized or common["handling_source"][protected_field] in serialized:
            raise AssertionError("A evidência contém campo ou valor protegido.")
    return report


def _load_security_03_fixture() -> tuple[dict, dict, dict[str, Path]]:
    fixture = _load_json(PLANNED_PATH)["fixture"]
    return (
        _load_json(_resolve_security_03_fixture(fixture["policy"])),
        _load_json(_resolve_security_03_fixture(fixture["valid_topology"])),
        {
            fixture_id: _resolve_security_03_fixture(path)
            for fixture_id, path in fixture["invalid_topologies"].items()
        },
    )


def verify_common_policy() -> dict:
    policy, _, _ = _load_security_03_fixture()
    common = validate_common_policy(policy)
    authorized = evaluate_access(common["identity_policy"], "ana-sre", "alterar", "runbook-alpha")
    if authorized != {"decision": "allow", "reason": "explicit_permission"}:
        raise AssertionError("A política comum não preservou a autorização explícita de security-01.")
    return {
        "identity_import": "validated",
        "handling_import": "validated",
        "authorization": authorized["decision"],
        "protected_fields": len(common["protected_fields"]),
        "external_actions": 0,
    }


def verify_topology_fixtures() -> dict:
    policy, valid_topology, invalid_paths = _load_security_03_fixture()
    accepted = evaluate_topology(policy, valid_topology)
    if accepted != {
        "scenario_id": "accept-isolated-hardening",
        "decision": "accept",
        "reasons": ["hardening_policy_satisfied"],
    }:
        raise AssertionError(f"Topologia segura não foi aceita: {accepted}")
    rejected = {}
    for fixture_id, expected_reasons in INVALID_FIXTURE_CODES.items():
        report = evaluate_topology(policy, _load_json(invalid_paths[fixture_id]))
        if report["decision"] != "deny" or report["reasons"] != expected_reasons:
            raise AssertionError(f"Rejeição divergente em {fixture_id}: {report}")
        rejected[fixture_id] = report["reasons"]
    return {
        "accepted": 1,
        "rejected": rejected,
        "external_actions": 0,
        "runtime_tools": 0,
        "secret_values_emitted": 0,
    }


def verify_security_01_02_regressions() -> dict:
    authoring = validate_security_01_02_authoring()
    access = verify_access_scenarios()
    evidence = verify_evidence_fixture()
    return {
        "authored_units": sorted(authoring["units"]),
        "access_scenarios": access["scenario_count"],
        "evidence_rejections": len(evidence["rejected_outputs"]),
        "external_actions": access["external_actions"] + evidence["external_actions"],
    }


def main() -> None:
    result = {
        "authoring": validate_security_03_authoring(),
        "common-policy": verify_common_policy(),
        "security-03": verify_topology_fixtures(),
        "security-01-02-regression": verify_security_01_02_regressions(),
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
