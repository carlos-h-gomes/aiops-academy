"""Validate the private data-01 authoring source and its synthetic SQL fixture."""
from __future__ import annotations

from datetime import date
from contextlib import closing
import json
from pathlib import Path
import re
import sqlite3
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
UNIT_PATH = ROOT / "backend/content/planned-units/data-01.json"
CATALOG_PATH = ROOT / "backend/content/curriculum.json"
COURSE_PATH = ROOT / "backend/content/course.json"
MAX_AUTHORING_BYTES = 200_000
FIELDS = {
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
EXPECTED_COUNTS = {
    "servicos": 2,
    "runbooks": 2,
    "incidentes": 2,
    "eventos": 4,
}
EXPECTED_REJECTIONS = {
    "foreign_key": "FOREIGN KEY constraint failed",
    "unique": "UNIQUE constraint failed",
    "check": "CHECK constraint failed",
}


def _load_json(path: Path, maximum: int = MAX_AUTHORING_BYTES):
    size = path.stat().st_size
    if size > maximum:
        raise ValueError(f"Arquivo excede {maximum} bytes: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


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


def _resolve_fixture_path(value: str) -> Path:
    _strict_nonempty_text(value, "fixture path")
    candidate = (ROOT / value).resolve()
    if not candidate.is_relative_to(ROOT.resolve()) or candidate.suffix.lower() != ".sql":
        raise ValueError(f"Caminho de fixture fora do repositório ou sem .sql: {value}")
    if not candidate.is_file():
        raise ValueError(f"Fixture local ausente: {value}")
    return candidate


def _validate_body(body: str):
    _strict_nonempty_text(body, "body")
    positions = []
    for heading in HEADINGS:
        if body.count(heading) != 1:
            raise ValueError(f"Seção obrigatória ausente ou repetida: {heading}")
        positions.append(body.index(heading))
    if positions != sorted(positions):
        raise ValueError("As seções editoriais estão fora da ordem definida.")

    exercise = body[body.index("## Exercício") : body.index("## Pistas")]
    numbered_steps = re.findall(r"(?m)^(\d+)\. ", exercise)
    if numbered_steps != [str(number) for number in range(1, len(numbered_steps) + 1)] or len(numbered_steps) < 3:
        raise ValueError("O exercício precisa de ao menos três passos numerados em sequência.")

    hints = body[body.index("## Pistas") : body.index("## Solução comentada")]
    hint_numbers = re.findall(r"\*\*Pista (\d+) —", hints)
    if not 1 <= len(hint_numbers) <= 2 or hint_numbers != [str(number) for number in range(1, len(hint_numbers) + 1)]:
        raise ValueError("A autoria deve conter uma ou duas pistas graduais numeradas.")

    required_terms = ("PK", "FK", "`NOT NULL`", "`CHECK`", "unicidade")
    if any(term not in body for term in required_terms):
        raise ValueError("A solução não cobre todas as categorias de integridade exigidas.")


def validate_authored_unit() -> dict:
    unit = _load_json(UNIT_PATH)
    if not isinstance(unit, dict) or set(unit) != FIELDS:
        raise ValueError("A unidade planejada não segue o contrato estrito de autoria.")
    if unit["schema_version"] != "1.0" or unit["id"] != "data-01":
        raise ValueError("Schema ou identidade de data-01 inválidos.")
    if unit["track_id"] != "data" or type(unit["order"]) is not int or unit["order"] != 1:
        raise ValueError("Trilha ou ordem de data-01 inválida.")
    if unit["status"] != "available" or unit["duration_minutes"] != {"essential": 90, "complete": 150}:
        raise ValueError("data-01 não segue o contrato da aula guiada disponível.")
    for field in ("title", "summary"):
        _strict_nonempty_text(unit[field], field)
    if unit["prerequisites"] != ["infra-05"]:
        raise ValueError("O pré-requisito estável de data-01 deve ser infra-05.")
    if not isinstance(unit["competencies"], list) or not unit["competencies"]:
        raise ValueError("A autoria precisa de competências observáveis.")
    for competency in unit["competencies"]:
        _strict_nonempty_text(competency, "competencies")

    expected_translations = [
        {"locale": "pt-BR", "authoring_status": "authored"},
        {"locale": "en", "authoring_status": "planned"},
        {"locale": "es", "authoring_status": "planned"},
    ]
    if unit["translations"] != expected_translations:
        raise ValueError("Somente PT-BR pode estar authored; EN e ES devem permanecer planned.")
    _validate_body(unit["body"])

    sources = unit["sources"]
    if not isinstance(sources, list) or not 1 <= len(sources) <= 30:
        raise ValueError("A autoria precisa de uma a 30 fontes primárias.")
    for source in sources:
        _safe_source(source)

    fixture = unit["fixture"]
    if not isinstance(fixture, dict) or set(fixture) != {"schema", "valid", "invalid"}:
        raise ValueError("Referências da fixture estão incompletas.")
    if not isinstance(fixture["invalid"], dict) or set(fixture["invalid"]) != set(EXPECTED_REJECTIONS):
        raise ValueError("A fixture deve declarar FK, unicidade e CHECK inválidos.")
    _resolve_fixture_path(fixture["schema"])
    _resolve_fixture_path(fixture["valid"])
    for value in fixture["invalid"].values():
        _resolve_fixture_path(value)

    catalog = _load_json(CATALOG_PATH, 1_000_000)
    matches = [candidate for candidate in catalog["units"] if candidate["id"] == "data-01"]
    if len(matches) != 1:
        raise ValueError("O catálogo deve preservar exatamente uma identidade data-01.")
    published = matches[0]
    for field in ("id", "track_id", "order", "title", "summary", "status", "prerequisites", "competencies"):
        if published[field] != unit[field]:
            raise ValueError(f"A autoria diverge do catálogo em {field}.")
    if (
        published["status"] != "available"
        or published["content_version"] != "2026.09.20.1"
        or published["lesson_day"] is not None
        or published["duration_minutes"] != {"essential": 90, "complete": 150}
        or published["practice"]["kind"] != "guided_fixture"
        or published["practice"]["lab_id"] != "data-01"
        or len(published["sources"]) != 3
        or published["verified_tool_versions"]
        or published["translations"][0] != {"locale": "pt-BR", "status": "available", "content_version": "2026.09.20.1"}
    ):
        raise ValueError("data-01 não segue o contrato de aula guiada disponível.")

    units_without_practice = [candidate["id"] for candidate in catalog["units"] if candidate["practice"] is None]
    falsely_available = [
        candidate["id"]
        for candidate in catalog["units"]
        if candidate["practice"] is None and candidate["status"] == "available"
    ]
    if falsely_available:
        raise ValueError(f"Unidades sem prática anunciadas como disponíveis: {falsely_available}")
    available = [candidate for candidate in catalog["units"] if candidate["status"] == "available"]
    if len(available) != 50:
        raise ValueError("O recorte deve preservar as 30 aulas legadas e as 20 aulas guiadas disponíveis.")

    course = _load_json(COURSE_PATH, 2_000_000)
    if [lesson["day"] for lesson in course["lessons"]] != list(range(1, 31)):
        raise ValueError("As 30 unidades legadas foram renumeradas ou alteradas em quantidade.")

    return {
        "unit": unit["id"],
        "catalog_status": published["status"],
        "available_units": len(available),
        "units_without_practice": len(units_without_practice),
        "authored_locale": "pt-BR",
        "planned_locales": ["en", "es"],
        "local_links": 2 + len(fixture["invalid"]),
        "dated_primary_sources": len(sources),
    }


def _fixture_paths() -> tuple[Path, Path, dict[str, Path]]:
    fixture = _load_json(UNIT_PATH)["fixture"]
    return (
        _resolve_fixture_path(fixture["schema"]),
        _resolve_fixture_path(fixture["valid"]),
        {key: _resolve_fixture_path(value) for key, value in fixture["invalid"].items()},
    )


def _valid_connection() -> sqlite3.Connection:
    schema_path, valid_path, _ = _fixture_paths()
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    if connection.execute("PRAGMA foreign_keys").fetchone() != (1,):
        connection.close()
        raise RuntimeError("O verificador não conseguiu ativar integridade referencial.")
    connection.executescript(schema_path.read_text(encoding="utf-8"))
    connection.executescript(valid_path.read_text(encoding="utf-8"))
    return connection


def valid_fixture_counts() -> dict[str, int]:
    with closing(_valid_connection()) as connection:
        counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in EXPECTED_COUNTS
        }
        if counts != EXPECTED_COUNTS:
            raise AssertionError(f"Contagens inesperadas na carga válida: {counts}")
        if connection.execute("PRAGMA integrity_check").fetchone() != ("ok",):
            raise AssertionError("A carga válida falhou no integrity_check.")
        return counts


def verify_invalid_case(kind: str) -> str:
    if kind not in EXPECTED_REJECTIONS:
        raise ValueError(f"Caso inválido desconhecido: {kind}")
    _, _, invalid_paths = _fixture_paths()
    with closing(_valid_connection()) as connection:
        before = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in EXPECTED_COUNTS
        }
        try:
            connection.execute(invalid_paths[kind].read_text(encoding="utf-8"))
            connection.commit()
        except sqlite3.IntegrityError as error:
            connection.rollback()
            if EXPECTED_REJECTIONS[kind] not in str(error):
                raise AssertionError(f"{kind} falhou por motivo inesperado: {error}") from error
        else:
            raise AssertionError(f"A fixture inválida {kind} foi aceita.")
        after = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in EXPECTED_COUNTS
        }
        if after != before or connection.execute("PRAGMA integrity_check").fetchone() != ("ok",):
            raise AssertionError(f"A rejeição {kind} alterou a base válida.")
    return "rejected"


def verify_fixture() -> dict:
    return {
        "counts": valid_fixture_counts(),
        "invalid": {kind: verify_invalid_case(kind) for kind in EXPECTED_REJECTIONS},
    }


def main():
    result = {
        "authoring": validate_authored_unit(),
        "fixture": verify_fixture(),
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
