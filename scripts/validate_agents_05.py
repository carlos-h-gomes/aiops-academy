"""Validate private agents-05 authoring and the static Development lab."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = ROOT / "labs" / "agents-processes-pilot"
sys.path.insert(0, str(LAB_ROOT / "tests"))

from validate_static import validate as validate_lab  # noqa: E402


CATALOG_PATH = ROOT / "backend/content/curriculum.json"
COURSE_PATH = ROOT / "backend/content/course.json"
UNIT_PATH = ROOT / "backend/content/planned-units/agents-05.json"
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
FIXTURE_MANIFEST = {
    "policy": "labs/agents-processes-pilot/fixtures/development/policy.json",
    "ticket": "labs/agents-processes-pilot/fixtures/development/ticket.json",
    "proposal": "labs/agents-processes-pilot/fixtures/development/proposal.json",
    "repository": "labs/agents-processes-pilot/fixtures/development/repository",
    "controller": "labs/agents-processes-pilot/src/development_triage.py",
    "guide": "labs/agents-processes-pilot/GUIDE.md",
    "session": "labs/agents-processes-pilot/src/learning_session.py",
    "runtime_profile": "labs/agents-processes-pilot/runtime.env",
}
def _load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"json_object_required:{path}")
    return value


def validate_authoring() -> dict:
    unit = _load_json(UNIT_PATH)
    if set(unit) != UNIT_FIELDS:
        raise ValueError("agents_05_authoring_contract_invalid")
    expected_translations = [
        {"locale": "pt-BR", "authoring_status": "authored"},
        {"locale": "en", "authoring_status": "planned"},
        {"locale": "es", "authoring_status": "planned"},
    ]
    if (
        unit["schema_version"] != "1.0"
        or unit["id"] != "agents-05"
        or unit["track_id"] != "agents"
        or unit["order"] != 5
        or unit["title"] != "Desenvolvimento: triagem de bugs"
        or unit["status"] != "available"
        or unit["prerequisites"] != ["agents-04"]
        or unit["duration_minutes"] != {"essential": 90, "complete": 150}
        or unit["translations"] != expected_translations
        or unit["fixture"] != FIXTURE_MANIFEST
    ):
        raise ValueError("agents_05_authoring_identity_invalid")
    if not isinstance(unit["competencies"], list) or len(unit["competencies"]) != 2:
        raise ValueError("agents_05_competencies_invalid")
    positions = []
    for heading in HEADINGS:
        if unit["body"].count(heading) != 1:
            raise ValueError(f"agents_05_heading_invalid:{heading}")
        positions.append(unit["body"].index(heading))
    if positions != sorted(positions):
        raise ValueError("agents_05_heading_order_invalid")
    exercise = unit["body"][positions[3] : positions[4]]
    steps = re.findall(r"(?m)^(\d+)\. ", exercise)
    if steps != [str(index) for index in range(1, 9)]:
        raise ValueError("agents_05_exercise_invalid")
    hints = unit["body"][positions[4] : positions[5]]
    if re.findall(r"\*\*Pista (\d+) —", hints) != ["1", "2"]:
        raise ValueError("agents_05_hints_invalid")
    required_terms = (
        "ticket",
        "hipótese",
        "evidência",
        "allowlist",
        "unified diff",
        "área efêmera",
        "aprovação humana sintética",
        "reset",
        "commit",
        "push",
        "shell livre",
        "segredo",
    )
    missing = [term for term in required_terms if term.casefold() not in unit["body"].casefold()]
    if missing:
        raise ValueError(f"agents_05_terms_missing:{missing}")
    for term in ("GUIDE.md", "runtime.env", "review", "reject", "check-paths", "--reviewed-hash"):
        if term not in unit["body"]:
            raise ValueError(f"agents_05_guided_step_missing:{term}")
    for path in FIXTURE_MANIFEST.values():
        if not (ROOT / path).exists():
            raise ValueError(f"agents_05_fixture_missing:{path}")
    if not isinstance(unit["sources"], list) or len(unit["sources"]) != 4:
        raise ValueError("agents_05_sources_invalid")
    for source in unit["sources"]:
        if set(source) != {"title", "url", "reviewed_on"}:
            raise ValueError("agents_05_source_contract_invalid")
        if not source["url"].startswith("https://") or source["reviewed_on"] != "2026-09-11":
            raise ValueError("agents_05_source_invalid")

    catalog = _load_json(CATALOG_PATH)
    published = [item for item in catalog["units"] if item["id"] == "agents-05"]
    if len(published) != 1:
        raise ValueError("agents_05_catalog_identity_invalid")
    published = published[0]
    for field in ("id", "track_id", "order", "title", "summary", "status", "prerequisites", "competencies"):
        if published[field] != unit[field]:
            raise ValueError(f"agents_05_catalog_mismatch:{field}")
    if (
        published["status"] != "available"
        or published["content_version"] != "2026.09.21.1"
        or published["lesson_day"] is not None
        or published["duration_minutes"] != {"essential": 90, "complete": 150}
        or published["practice"] is None
        or not published["sources"]
        or published["verified_tool_versions"]
        or published["translations"] != [
            {"locale": "pt-BR", "status": "available", "content_version": "2026.09.21.1"},
            {"locale": "en", "status": "planned", "content_version": None},
            {"locale": "es", "status": "planned", "content_version": None},
        ]
    ):
        raise ValueError("agents_05_catalog_availability_changed")
    if len(catalog["units"]) != 50:
        raise ValueError("catalog_size_changed")
    if (
        sum(item["status"] == "available" for item in catalog["units"]) != 50
        or sum(item["status"] == "planned" for item in catalog["units"]) != 0
    ):
        raise ValueError("catalog_counts_changed")
    course = _load_json(COURSE_PATH)
    if [lesson["day"] for lesson in course["lessons"]] != list(range(1, 31)):
        raise ValueError("legacy_lessons_changed")
    return {"exercise_steps": len(steps), "hints": 2, "sources": 4, "status": "available"}


def validate_protected_files() -> dict:
    """Protect stable identities without freezing the generated public catalog."""
    course = _load_json(COURSE_PATH)
    if [lesson.get("day") for lesson in course.get("lessons", [])] != list(range(1, 31)):
        raise AssertionError("legacy_lessons_changed")
    units = []
    for order in range(1, 5):
        unit = _load_json(ROOT / f"backend/content/planned-units/agents-{order:02d}.json")
        if (
            unit.get("id") != f"agents-{order:02d}"
            or unit.get("track_id") != "agents"
            or unit.get("order") != order
            or unit.get("prerequisites") != (["infra-06"] if order == 1 else [f"agents-{order - 1:02d}"])
        ):
            raise AssertionError(f"agents_identity_changed:{order}")
        units.append(unit["id"])
    return {"legacy_lessons": 30, "agent_units": units}


def main() -> None:
    result = {
        "authoring": validate_authoring(),
        "lab": validate_lab(),
        "protected": validate_protected_files(),
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
