"""Validate private security-04/05 authoring and synthetic exercises."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re

from validate_security_01_02 import _load_json, _safe_source, _strict_nonempty_text
from validate_security_03 import (
    validate_security_03_authoring,
    verify_common_policy,
    verify_security_01_02_regressions,
    verify_topology_fixtures,
)


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "backend/content/curriculum.json"
COURSE_PATH = ROOT / "backend/content/course.json"
PLANNED_ROOT = ROOT / "backend/content/planned-units"
FIXTURE_ROOT = ROOT / "backend/content/fixtures"
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
    "security-04": {
        "order": 4,
        "prerequisites": ["security-03"],
        "minimum_sources": 4,
        "terms": (
            "latest",
            "digest",
            "proveniência verificável",
            "licença incerta",
            "SBOM",
            "scanner",
            "não garant",
            "não-root",
            "limites",
            "zero pull",
        ),
    },
    "security-05": {
        "order": 5,
        "prerequisites": ["security-04"],
        "minimum_sources": 3,
        "terms": (
            "detectar",
            "preservar evidência",
            "conter",
            "erradicar",
            "recuperar",
            "verificar",
            "prevenir",
            "origem",
            "destino",
            "pós-condições",
            "reset",
            "zero rede",
        ),
    },
}
SUPPLY_EXPECTED = {
    "approve-pinned-fixture": ("approve", ["supply_chain_policy_satisfied"]),
    "block-latest": ("block", ["floating_tag_latest"]),
    "block-missing-digest": ("block", ["missing_image_digest"]),
    "block-unverified-provenance": ("block", ["provenance_not_verifiable"]),
    "block-uncertain-license": ("block", ["uncertain_license"]),
    "review-outdated-package": ("review", ["dependency_update_due"]),
}
INCIDENT_EXPECTED = {
    "recover-authorized-copy": ("complete", []),
    "reject-missing-evidence": ("reject", ["missing_required_evidence"]),
    "reject-excess-evidence": ("reject", ["evidence_not_minimal"]),
    "reject-wrong-order": ("reject", ["invalid_decision_order"]),
    "reject-wrong-destination": ("reject", ["recovery_destination_not_allowed"]),
    "reject-missing-postcondition": (
        "reject",
        ["postcondition_missing:containment_remains_active"],
    ),
}
FINDING_DETAILS = {
    "floating_tag_latest": ("critical", "pin_version_and_digest"),
    "missing_image_digest": ("critical", "record_verified_digest"),
    "invalid_image_digest": ("critical", "record_verified_digest"),
    "provenance_not_verifiable": ("high", "obtain_and_verify_provenance"),
    "provenance_subject_mismatch": ("high", "reconcile_provenance_subject"),
    "uncertain_license": ("high", "hold_until_license_confirmed"),
    "dependency_update_due": ("medium", "update_before_runtime"),
    "sbom_components_missing": ("high", "produce_complete_component_inventory"),
    "supply_chain_policy_satisfied": ("info", "none"),
}


def _resolve_fixture(unit_id: str, value: str) -> Path:
    _strict_nonempty_text(value, "fixture path")
    allowed_root = (FIXTURE_ROOT / unit_id).resolve()
    candidate = (ROOT / value).resolve()
    if not candidate.is_relative_to(allowed_root) or candidate.suffix.lower() != ".json":
        raise ValueError(f"Caminho fora de {unit_id}: {value}")
    if not candidate.is_file():
        raise ValueError(f"Fixture ausente: {value}")
    return candidate


def _validate_authoring(unit_id: str, catalog: dict, course: dict) -> dict:
    contract = UNIT_CONTRACTS[unit_id]
    unit = _load_json(PLANNED_ROOT / f"{unit_id}.json")
    if not isinstance(unit, dict) or set(unit) != AUTHORING_FIELDS:
        raise ValueError(f"{unit_id} não segue o contrato estrito de autoria.")
    if (
        unit["schema_version"] != "1.0"
        or unit["id"] != unit_id
        or unit["track_id"] != "security"
        or unit["order"] != contract["order"]
        or unit["status"] != "available"
        or unit["duration_minutes"] != {"essential": 90, "complete": 150}
        or unit["prerequisites"] != contract["prerequisites"]
    ):
        raise ValueError(f"Identidade, ordem, estado ou pré-requisito inválido em {unit_id}.")
    for field in ("title", "summary"):
        _strict_nonempty_text(unit[field], f"{unit_id}.{field}")
    if not isinstance(unit["competencies"], list) or not unit["competencies"]:
        raise ValueError(f"{unit_id} precisa de competências observáveis.")
    for competency in unit["competencies"]:
        _strict_nonempty_text(competency, f"{unit_id}.competencies")
    if unit["translations"] != [
        {"locale": "pt-BR", "authoring_status": "authored"},
        {"locale": "en", "authoring_status": "planned"},
        {"locale": "es", "authoring_status": "planned"},
    ]:
        raise ValueError("Apenas a fonte privada PT-BR pode estar authored.")

    body = unit["body"]
    _strict_nonempty_text(body, f"{unit_id}.body")
    positions = []
    for heading in HEADINGS:
        if body.count(heading) != 1:
            raise ValueError(f"Seção ausente ou repetida em {unit_id}: {heading}")
        positions.append(body.index(heading))
    if positions != sorted(positions):
        raise ValueError(f"Seções editoriais fora da ordem em {unit_id}.")
    exercise = body[body.index("## Exercício") : body.index("## Pistas")]
    steps = re.findall(r"(?m)^(\d+)\. ", exercise)
    if len(steps) < 3 or steps != [str(i) for i in range(1, len(steps) + 1)]:
        raise ValueError(f"Exercício numerado inválido em {unit_id}.")
    hints = body[body.index("## Pistas") : body.index("## Solução comentada")]
    hint_numbers = re.findall(r"\*\*Pista (\d+) —", hints)
    if not 1 <= len(hint_numbers) <= 2 or hint_numbers != [
        str(i) for i in range(1, len(hint_numbers) + 1)
    ]:
        raise ValueError(f"{unit_id} deve conter uma ou duas pistas graduais.")
    folded = body.casefold()
    missing_terms = [term for term in contract["terms"] if term.casefold() not in folded]
    if missing_terms:
        raise ValueError(f"{unit_id} não cobre termos obrigatórios: {missing_terms}")

    fixture = unit["fixture"]
    if not isinstance(fixture, dict) or set(fixture) != {"policy", "scenarios"}:
        raise ValueError(f"Manifesto de fixtures incompleto em {unit_id}.")
    _resolve_fixture(unit_id, fixture["policy"])
    _resolve_fixture(unit_id, fixture["scenarios"])
    if not isinstance(unit["sources"], list) or len(unit["sources"]) < contract["minimum_sources"]:
        raise ValueError(f"{unit_id} precisa de fontes primárias suficientes.")
    for source in unit["sources"]:
        _safe_source(source)

    matches = [candidate for candidate in catalog["units"] if candidate["id"] == unit_id]
    if len(matches) != 1:
        raise ValueError(f"O catálogo deve conter exatamente uma {unit_id}.")
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
            raise ValueError(f"A autoria {unit_id} diverge do catálogo em {field}.")
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
        raise ValueError(f"{unit_id} não expõe a prática guiada publicada esperada.")
    return {
        "unit": unit_id,
        "catalog_status": published["status"],
        "authored_locale": "pt-BR",
        "planned_locales": ["en", "es"],
        "dated_primary_sources": len(unit["sources"]),
    }


def validate_authored_units() -> dict:
    catalog = _load_json(CATALOG_PATH, 1_000_000)
    course = _load_json(COURSE_PATH, 2_000_000)
    results = {
        unit_id: _validate_authoring(unit_id, catalog, course)
        for unit_id in UNIT_CONTRACTS
    }
    available = [unit for unit in catalog["units"] if unit["status"] == "available"]
    planned = [unit for unit in catalog["units"] if unit["status"] == "planned"]
    if len(catalog["units"]) != 50 or len(available) != 50 or planned:
        raise ValueError("O recorte deve preservar 30 aulas legadas e 20 aulas guiadas disponíveis.")
    if [lesson["day"] for lesson in course["lessons"]] != list(range(1, 31)):
        raise ValueError("As 30 aulas legadas foram alteradas.")
    return {
        "units": results,
        "available_units": len(available),
        "planned_units": len(planned),
        "legacy_lessons": len(course["lessons"]),
    }


def _string_list(value, field: str, *, minimum: int = 0, maximum: int = 20) -> None:
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise ValueError(f"Lista inválida: {field}")
    for item in value:
        _strict_nonempty_text(item, field)


def validate_supply_policy(policy: dict) -> None:
    expected_fields = {
        "schema_version",
        "forbidden_tags",
        "digest_algorithm",
        "require_verified_provenance",
        "allowed_verification_basis",
        "allowed_license_status",
        "required_runtime_controls",
        "evidence_fields",
        "disclaimer",
    }
    if not isinstance(policy, dict) or set(policy) != expected_fields or policy["schema_version"] != "1.0":
        raise ValueError("Política de supply chain fora do contrato estrito.")
    if policy["forbidden_tags"] != ["latest"] or policy["digest_algorithm"] != "sha256":
        raise ValueError("Regra de tag/digest divergente.")
    if policy["require_verified_provenance"] is not True:
        raise ValueError("Proveniência verificável deve ser obrigatória.")
    if policy["allowed_verification_basis"] != ["synthetic-offline-proof"]:
        raise ValueError("Base de verificação deve permanecer sintética e fixa.")
    if policy["allowed_license_status"] != ["confirmed"]:
        raise ValueError("Licença precisa estar confirmada.")
    required_controls = {
        "runs_as_non_root": True,
        "read_only": True,
        "no_new_privileges": True,
        "cap_drop_all": True,
        "resource_limits_declared": True,
    }
    if policy["required_runtime_controls"] != required_controls:
        raise ValueError("Controles mínimos de runtime divergentes.")
    if policy["evidence_fields"] != ["scenario_id", "decision", "findings"]:
        raise ValueError("Relatório de supply chain não é mínimo.")
    disclaimer = policy["disclaimer"]
    _strict_nonempty_text(disclaimer, "disclaimer")
    if "não garantem" not in disclaimer or "scanner" not in disclaimer:
        raise ValueError("A política precisa explicitar o limite de scanner/SBOM.")


def validate_supply_scenario(scenario: dict) -> None:
    if not isinstance(scenario, dict) or set(scenario) != {"scenario_id", "manifest", "sbom"}:
        raise ValueError("Cenário de supply chain fora do contrato estrito.")
    _strict_nonempty_text(scenario["scenario_id"], "scenario_id")
    manifest = scenario["manifest"]
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema_version",
        "image",
        "provenance",
        "runtime_controls",
    } or manifest["schema_version"] != "1.0":
        raise ValueError("Manifesto sintético fora do contrato estrito.")
    image = manifest["image"]
    if not isinstance(image, dict) or set(image) != {"reference", "tag", "digest"}:
        raise ValueError("Referência de imagem fora do contrato estrito.")
    _strict_nonempty_text(image["reference"], "image.reference")
    _strict_nonempty_text(image["tag"], "image.tag")
    if image["digest"] is not None:
        _strict_nonempty_text(image["digest"], "image.digest")

    provenance = manifest["provenance"]
    if not isinstance(provenance, dict) or set(provenance) != {
        "available",
        "verified",
        "subject_digest",
        "source",
        "verification_basis",
    }:
        raise ValueError("Proveniência sintética fora do contrato estrito.")
    if type(provenance["available"]) is not bool or type(provenance["verified"]) is not bool:
        raise ValueError("Flags de proveniência precisam ser booleanas.")
    if provenance["subject_digest"] is not None:
        _strict_nonempty_text(provenance["subject_digest"], "provenance.subject_digest")
    _strict_nonempty_text(provenance["source"], "provenance.source")
    _strict_nonempty_text(provenance["verification_basis"], "provenance.verification_basis")

    controls = manifest["runtime_controls"]
    expected_control_fields = {
        "runs_as_non_root",
        "read_only",
        "no_new_privileges",
        "cap_drop_all",
        "resource_limits_declared",
    }
    if not isinstance(controls, dict) or set(controls) != expected_control_fields:
        raise ValueError("Controles de runtime fora do contrato estrito.")
    if any(type(value) is not bool for value in controls.values()):
        raise ValueError("Controles de runtime precisam ser booleanos.")

    sbom = scenario["sbom"]
    if not isinstance(sbom, dict) or set(sbom) != {
        "schema_version",
        "format",
        "spec_version",
        "document_id",
        "components",
    } or sbom["schema_version"] != "1.0":
        raise ValueError("SBOM sintético fora do contrato estrito.")
    if sbom["format"] != "SPDX-synthetic-subset" or sbom["spec_version"] != "3.0.1":
        raise ValueError("SBOM precisa permanecer identificado como subconjunto sintético.")
    _strict_nonempty_text(sbom["document_id"], "sbom.document_id")
    if not isinstance(sbom["components"], list) or len(sbom["components"]) > 20:
        raise ValueError("Lista de componentes inválida.")
    for component in sbom["components"]:
        if not isinstance(component, dict) or set(component) != {
            "component_id",
            "name",
            "version",
            "license_concluded",
            "license_status",
            "maintenance_status",
        }:
            raise ValueError("Componente SBOM fora do contrato estrito.")
        for field, value in component.items():
            _strict_nonempty_text(value, f"component.{field}")
        if component["maintenance_status"] not in {"current", "update_available"}:
            raise ValueError("Estado de manutenção não permitido.")


def _add_code(codes: list[str], code: str) -> None:
    if code not in codes:
        codes.append(code)


def evaluate_supply_scenario(policy: dict, scenario: dict) -> dict:
    validate_supply_policy(policy)
    validate_supply_scenario(scenario)
    manifest = scenario["manifest"]
    image = manifest["image"]
    provenance = manifest["provenance"]
    codes: list[str] = []
    if image["tag"].casefold() in {tag.casefold() for tag in policy["forbidden_tags"]}:
        _add_code(codes, "floating_tag_latest")
    digest = image["digest"]
    digest_valid = isinstance(digest, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is not None
    if digest is None:
        _add_code(codes, "missing_image_digest")
    elif not digest_valid:
        _add_code(codes, "invalid_image_digest")
    provenance_verifiable = (
        provenance["available"]
        and provenance["verified"]
        and provenance["verification_basis"] in policy["allowed_verification_basis"]
    )
    if policy["require_verified_provenance"] and not provenance_verifiable:
        _add_code(codes, "provenance_not_verifiable")
    elif digest_valid and provenance["subject_digest"] != digest:
        _add_code(codes, "provenance_subject_mismatch")
    for control, expected in policy["required_runtime_controls"].items():
        if manifest["runtime_controls"][control] != expected:
            code = f"runtime_control_missing:{control}"
            _add_code(codes, code)
    components = scenario["sbom"]["components"]
    if not components:
        _add_code(codes, "sbom_components_missing")
    for component in components:
        if (
            component["license_status"] not in policy["allowed_license_status"]
            or component["license_concluded"] in {"NOASSERTION", "NONE"}
        ):
            _add_code(codes, "uncertain_license")
        if component["maintenance_status"] == "update_available":
            _add_code(codes, "dependency_update_due")
    if not codes:
        codes = ["supply_chain_policy_satisfied"]
    findings = []
    for code in codes:
        detail = FINDING_DETAILS.get(code)
        if detail is None and code.startswith("runtime_control_missing:"):
            control = code.split(":", 1)[1]
            detail = ("high", f"enable_runtime_control:{control}")
        if detail is None:
            raise AssertionError(f"Achado sem prioridade e ação: {code}")
        findings.append({"code": code, "priority": detail[0], "action": detail[1]})
    priorities = {finding["priority"] for finding in findings}
    if priorities & {"critical", "high"}:
        decision = "block"
    elif "medium" in priorities:
        decision = "review"
    else:
        decision = "approve"
    report = {"scenario_id": scenario["scenario_id"], "decision": decision, "findings": findings}
    if list(report) != policy["evidence_fields"]:
        raise AssertionError("Relatório de supply chain diverge da allowlist.")
    return report


def _load_unit_fixtures(unit_id: str) -> tuple[dict, list[dict]]:
    fixture = _load_json(PLANNED_ROOT / f"{unit_id}.json")["fixture"]
    policy = _load_json(_resolve_fixture(unit_id, fixture["policy"]))
    scenarios_document = _load_json(_resolve_fixture(unit_id, fixture["scenarios"]))
    if not isinstance(scenarios_document, dict) or set(scenarios_document) != {"schema_version", "scenarios"}:
        raise ValueError(f"Documento de cenários inválido em {unit_id}.")
    if scenarios_document["schema_version"] != "1.0" or not isinstance(scenarios_document["scenarios"], list):
        raise ValueError(f"Versão ou lista de cenários inválida em {unit_id}.")
    return policy, scenarios_document["scenarios"]


def verify_supply_fixtures() -> dict:
    policy, scenarios = _load_unit_fixtures("security-04")
    if {scenario["scenario_id"] for scenario in scenarios} != set(SUPPLY_EXPECTED):
        raise ValueError("Conjunto de cenários security-04 divergente.")
    results = {}
    for scenario in scenarios:
        report = evaluate_supply_scenario(policy, scenario)
        expected_decision, expected_codes = SUPPLY_EXPECTED[scenario["scenario_id"]]
        codes = [finding["code"] for finding in report["findings"]]
        if report["decision"] != expected_decision or codes != expected_codes:
            raise AssertionError(f"Resultado supply chain divergente: {scenario['scenario_id']}")
        results[scenario["scenario_id"]] = {"decision": report["decision"], "codes": codes}
    return {
        "scenarios": results,
        "approved": 1,
        "blocked": 4,
        "review": 1,
        "image_downloads": 0,
        "scanner_invocations": 0,
        "external_actions": 0,
    }


def validate_incident_policy(policy: dict) -> None:
    expected_fields = {
        "schema_version",
        "required_decision_order",
        "allowed_evidence_fields",
        "required_evidence_fields",
        "allowed_containment_actions",
        "allowed_eradication_actions",
        "allowed_recovery_destinations",
        "required_postconditions",
        "report_fields",
    }
    if not isinstance(policy, dict) or set(policy) != expected_fields or policy["schema_version"] != "1.0":
        raise ValueError("Política de incidente fora do contrato estrito.")
    if policy["required_decision_order"] != [
        "detect",
        "preserve_evidence",
        "contain",
        "eradicate",
        "recover",
        "verify",
        "prevent",
    ]:
        raise ValueError("Ordem de decisão divergente.")
    if policy["allowed_evidence_fields"] != ["incident_id", "signal_id", "observed_at", "summary"]:
        raise ValueError("Allowlist de evidência divergente.")
    if policy["required_evidence_fields"] != policy["allowed_evidence_fields"]:
        raise ValueError("Todos os campos permitidos precisam ser obrigatórios nesta fixture.")
    if policy["allowed_containment_actions"] != ["isolate-fixture-workload"]:
        raise ValueError("Ação de contenção deve permanecer sintética e fixa.")
    if policy["allowed_eradication_actions"] != ["remove-fixture-change-from-copy"]:
        raise ValueError("Ação de erradicação deve permanecer sintética e fixa.")
    if policy["allowed_recovery_destinations"] != ["recovery-slot-beta"]:
        raise ValueError("Destino de recuperação deve permanecer sintético e fixo.")
    if policy["required_postconditions"] != [
        "origin_unchanged",
        "destination_matches_known_good",
        "containment_remains_active",
        "prevention_recorded",
    ]:
        raise ValueError("Pós-condições divergentes.")
    if policy["report_fields"] != [
        "scenario_id",
        "decision",
        "reasons",
        "completed_stages",
        "origin_unchanged",
        "postconditions",
    ]:
        raise ValueError("Relatório de incidente não é mínimo.")


def validate_incident_scenario(scenario: dict) -> None:
    expected_fields = {
        "scenario_id",
        "incident",
        "evidence",
        "decision_steps",
        "containment",
        "eradication",
        "recovery",
        "verification",
        "prevention",
    }
    if not isinstance(scenario, dict) or set(scenario) != expected_fields:
        raise ValueError("Cenário de incidente fora do contrato estrito.")
    _strict_nonempty_text(scenario["scenario_id"], "scenario_id")
    incident = scenario["incident"]
    if not isinstance(incident, dict) or set(incident) != {
        "incident_id",
        "source_id",
        "signal_id",
        "source_snapshot",
        "known_good_snapshot",
    }:
        raise ValueError("Incidente fora do contrato estrito.")
    for field in ("incident_id", "source_id", "signal_id"):
        _strict_nonempty_text(incident[field], f"incident.{field}")
    for field in ("source_snapshot", "known_good_snapshot"):
        if not isinstance(incident[field], dict):
            raise ValueError(f"Snapshot inválido: {field}")
    if not isinstance(scenario["evidence"], dict) or len(scenario["evidence"]) > 10:
        raise ValueError("Evidência fora do limite estrutural.")
    _string_list(scenario["decision_steps"], "decision_steps", minimum=1, maximum=10)
    containment = scenario["containment"]
    if not isinstance(containment, dict) or set(containment) != {"action", "target"}:
        raise ValueError("Contenção fora do contrato estrito.")
    _strict_nonempty_text(containment["action"], "containment.action")
    _strict_nonempty_text(containment["target"], "containment.target")
    eradication = scenario["eradication"]
    if not isinstance(eradication, dict) or set(eradication) != {"action"}:
        raise ValueError("Erradicação fora do contrato estrito.")
    _strict_nonempty_text(eradication["action"], "eradication.action")
    recovery = scenario["recovery"]
    if not isinstance(recovery, dict) or set(recovery) != {"destination", "snapshot"}:
        raise ValueError("Recuperação fora do contrato estrito.")
    _strict_nonempty_text(recovery["destination"], "recovery.destination")
    _strict_nonempty_text(recovery["snapshot"], "recovery.snapshot")
    verification = scenario["verification"]
    if not isinstance(verification, dict) or set(verification) != {"postconditions"}:
        raise ValueError("Verificação fora do contrato estrito.")
    _string_list(verification["postconditions"], "verification.postconditions", maximum=10)
    prevention = scenario["prevention"]
    if not isinstance(prevention, dict) or set(prevention) != {"control"}:
        raise ValueError("Prevenção fora do contrato estrito.")
    _strict_nonempty_text(prevention["control"], "prevention.control")


def _canonical_digest(value: dict) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


class SyntheticIncidentSession:
    """In-memory-only state machine over a deep-copied synthetic fixture."""

    def __init__(self, scenario: dict):
        self._origin = deepcopy(scenario["incident"]["source_snapshot"])
        self._origin_reference = deepcopy(self._origin)
        self._origin_digest = _canonical_digest(self._origin)
        self._known_good = deepcopy(scenario["incident"]["known_good_snapshot"])
        self._baseline = {
            "contained": False,
            "eradicated": False,
            "destination": None,
            "recovered_snapshot": None,
            "verified": False,
            "prevention": None,
            "timeline": [],
        }
        self.state = deepcopy(self._baseline)

    @property
    def origin_unchanged(self) -> bool:
        return self._origin == self._origin_reference and _canonical_digest(self._origin) == self._origin_digest

    def run(self, policy: dict, scenario: dict) -> dict:
        self.state["timeline"].extend(["detect", "preserve_evidence"])
        self.state["contained"] = True
        self.state["timeline"].append("contain")
        self.state["eradicated"] = True
        self.state["timeline"].append("eradicate")
        self.state["destination"] = scenario["recovery"]["destination"]
        self.state["recovered_snapshot"] = deepcopy(self._known_good)
        self.state["timeline"].append("recover")
        self.state["verified"] = (
            self.origin_unchanged
            and self.state["recovered_snapshot"] == self._known_good
            and self.state["contained"]
        )
        self.state["timeline"].append("verify")
        self.state["prevention"] = scenario["prevention"]["control"]
        self.state["timeline"].append("prevent")
        postconditions = {
            "origin_unchanged": self.origin_unchanged,
            "destination_matches_known_good": self.state["recovered_snapshot"] == self._known_good,
            "containment_remains_active": self.state["contained"],
            "prevention_recorded": bool(self.state["prevention"]),
        }
        if list(postconditions) != policy["required_postconditions"] or not all(postconditions.values()):
            raise AssertionError("Pós-condições não foram satisfeitas pela sessão sintética.")
        return postconditions

    def reset(self) -> dict:
        self.state = deepcopy(self._baseline)
        return deepcopy(self.state)


def _incident_rejection_report(policy: dict, scenario: dict, reasons: list[str]) -> dict:
    report = {
        "scenario_id": scenario["scenario_id"],
        "decision": "reject",
        "reasons": reasons,
        "completed_stages": [],
        "origin_unchanged": True,
        "postconditions": {name: False for name in policy["required_postconditions"]},
    }
    if list(report) != policy["report_fields"]:
        raise AssertionError("Relatório de rejeição diverge da allowlist.")
    return report


def evaluate_incident_scenario(policy: dict, scenario: dict) -> tuple[dict, SyntheticIncidentSession | None]:
    validate_incident_policy(policy)
    validate_incident_scenario(scenario)
    reasons: list[str] = []
    evidence = scenario["evidence"]
    allowed_evidence = set(policy["allowed_evidence_fields"])
    required_evidence = set(policy["required_evidence_fields"])
    if not required_evidence.issubset(evidence) or any(
        not isinstance(evidence.get(field), str) or not evidence.get(field, "").strip()
        for field in required_evidence
    ):
        _add_code(reasons, "missing_required_evidence")
    if set(evidence) - allowed_evidence:
        _add_code(reasons, "evidence_not_minimal")
    incident = scenario["incident"]
    if required_evidence.issubset(evidence) and (
        evidence["incident_id"] != incident["incident_id"] or evidence["signal_id"] != incident["signal_id"]
    ):
        _add_code(reasons, "evidence_context_mismatch")
    if scenario["decision_steps"] != policy["required_decision_order"]:
        _add_code(reasons, "invalid_decision_order")
    if scenario["containment"]["action"] not in policy["allowed_containment_actions"]:
        _add_code(reasons, "containment_action_not_allowed")
    if scenario["eradication"]["action"] not in policy["allowed_eradication_actions"]:
        _add_code(reasons, "eradication_action_not_allowed")
    recovery = scenario["recovery"]
    if (
        recovery["destination"] not in policy["allowed_recovery_destinations"]
        or recovery["destination"] == incident["source_id"]
    ):
        _add_code(reasons, "recovery_destination_not_allowed")
    if recovery["snapshot"] != "known_good_snapshot":
        _add_code(reasons, "recovery_snapshot_not_allowed")
    declared_postconditions = scenario["verification"]["postconditions"]
    for required in policy["required_postconditions"]:
        if required not in declared_postconditions:
            _add_code(reasons, f"postcondition_missing:{required}")
    if set(declared_postconditions) - set(policy["required_postconditions"]):
        _add_code(reasons, "unexpected_postcondition")
    if reasons:
        return _incident_rejection_report(policy, scenario, reasons), None

    session = SyntheticIncidentSession(scenario)
    postconditions = session.run(policy, scenario)
    report = {
        "scenario_id": scenario["scenario_id"],
        "decision": "complete",
        "reasons": ["incident_exercise_completed"],
        "completed_stages": list(session.state["timeline"]),
        "origin_unchanged": session.origin_unchanged,
        "postconditions": postconditions,
    }
    if list(report) != policy["report_fields"]:
        raise AssertionError("Relatório de incidente diverge da allowlist.")
    return report, session


def verify_incident_fixtures() -> dict:
    policy, scenarios = _load_unit_fixtures("security-05")
    if {scenario["scenario_id"] for scenario in scenarios} != set(INCIDENT_EXPECTED):
        raise ValueError("Conjunto de cenários security-05 divergente.")
    results = {}
    valid_session = None
    for scenario in scenarios:
        report, session = evaluate_incident_scenario(policy, scenario)
        expected_decision, expected_reasons = INCIDENT_EXPECTED[scenario["scenario_id"]]
        if report["decision"] != expected_decision:
            raise AssertionError(f"Decisão de incidente divergente: {scenario['scenario_id']}")
        if expected_reasons and report["reasons"] != expected_reasons:
            raise AssertionError(f"Motivo de incidente divergente: {scenario['scenario_id']}")
        if expected_decision == "complete":
            valid_session = session
        elif report["completed_stages"] or session is not None:
            raise AssertionError("Cenário recusado alterou estado.")
        results[scenario["scenario_id"]] = {
            "decision": report["decision"],
            "reasons": report["reasons"],
        }
    if valid_session is None:
        raise AssertionError("Sessão válida ausente.")
    first_reset = valid_session.reset()
    second_reset = valid_session.reset()
    if first_reset != second_reset or first_reset["timeline"]:
        raise AssertionError("Reset não é repetível.")
    return {
        "scenarios": results,
        "completed": 1,
        "rejected": 5,
        "origin_unchanged": valid_session.origin_unchanged,
        "repeatable_resets": 2,
        "network_calls": 0,
        "child_processes": 0,
        "real_restores": 0,
        "external_writes": 0,
    }


def verify_security_01_03_regressions() -> dict:
    security_03_authoring = validate_security_03_authoring()
    common = verify_common_policy()
    topology = verify_topology_fixtures()
    earlier = verify_security_01_02_regressions()
    return {
        "authored_units": sorted([*earlier["authored_units"], security_03_authoring["unit"]]),
        "access_scenarios": earlier["access_scenarios"],
        "evidence_rejections": earlier["evidence_rejections"],
        "hardening_acceptances": topology["accepted"],
        "hardening_rejections": len(topology["rejected"]),
        "common_policy": common["authorization"],
        "external_actions": earlier["external_actions"] + topology["external_actions"],
    }


def main() -> None:
    result = {
        "authoring": validate_authored_units(),
        "security-04": verify_supply_fixtures(),
        "security-05": verify_incident_fixtures(),
        "security-01-03-regression": verify_security_01_03_regressions(),
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
