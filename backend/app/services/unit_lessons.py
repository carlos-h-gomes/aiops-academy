"""Read-only use case for the three published cross-track lessons."""
from app.models.curriculum import load_unit_lesson


def detail(unit_id: str):
    return load_unit_lesson(unit_id)
