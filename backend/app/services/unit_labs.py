"""Read-only application service for fixed authored lab decisions."""
from app.models.unit_labs import grade_unit_lab, load_unit_lab
from app.models.curriculum import load_unit_lesson


def detail(unit_id: str):
    # Reuse the published-lesson allowlist before exposing a lab definition.
    load_unit_lesson(unit_id)
    return load_unit_lab(unit_id)


def run(unit_id: str, answers: dict[str, str]):
    load_unit_lesson(unit_id)
    return grade_unit_lab(unit_id, answers)
