"""Bounded metadata loading. No progress access or writes."""
import json
from functools import lru_cache
from .catalog import COURSE, LAB_MAP, ROOT
from app.schemas.curriculum import Curriculum, UnitLesson, validate_content_links


PUBLISHED_UNIT_FILES = {
    'data-01': ROOT / 'content/planned-units/data-01.json',
    'data-02': ROOT / 'content/planned-units/data-02.json',
    'data-03': ROOT / 'content/planned-units/data-03.json',
    'data-04': ROOT / 'content/planned-units/data-04.json',
    'data-05': ROOT / 'content/planned-units/data-05.json',
    'data-06': ROOT / 'content/planned-units/data-06.json',
    'security-01': ROOT / 'content/planned-units/security-01.json',
    'security-02': ROOT / 'content/planned-units/security-02.json',
    'security-03': ROOT / 'content/planned-units/security-03.json',
    'security-04': ROOT / 'content/planned-units/security-04.json',
    'security-05': ROOT / 'content/planned-units/security-05.json',
    'security-06': ROOT / 'content/planned-units/security-06.json',
    'agents-01': ROOT / 'content/planned-units/agents-01.json',
    'agents-02': ROOT / 'content/planned-units/agents-02.json',
    'agents-03': ROOT / 'content/planned-units/agents-03.json',
    'agents-04': ROOT / 'content/planned-units/agents-04.json',
    'agents-05': ROOT / 'content/planned-units/agents-05.json',
    'agents-06': ROOT / 'content/planned-units/agents-06.json',
    'agents-07': ROOT / 'content/planned-units/agents-07.json',
    'agents-08': ROOT / 'content/planned-units/agents-08.json',
}


def read_metadata(path, limit):
    with path.open('rb') as file:
        raw = file.read(limit + 1)
    if len(raw) > limit:
        raise ValueError('Metadata file exceeds its size limit.')
    return json.loads(raw)


@lru_cache(maxsize=1)
def load_curriculum():
    try:
        value = Curriculum.model_validate(read_metadata(ROOT / 'content/curriculum.json', 1_000_000))
        manuals = read_metadata(ROOT / 'content/manuals.json', 2_000_000)
        return validate_content_links(value, COURSE, manuals, LAB_MAP)
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise RuntimeError('Curriculum metadata unavailable or inconsistent.') from error


def load_unit_lesson(unit_id: str):
    """Return a fixed public lesson body without reading or writing learner state."""
    try:
        path = PUBLISHED_UNIT_FILES[unit_id]
        unit = next(item for item in load_curriculum().units if item.id == unit_id)
        if unit.status != 'available' or unit.lesson_day is not None:
            raise ValueError('Unit is not a published non-legacy lesson.')
        authored = read_metadata(path, 100_000)
        if authored.get('id') != unit.id or authored.get('status') != 'available':
            raise ValueError('Published lesson source is inconsistent.')
        return UnitLesson.model_validate({
            'id': unit.id, 'title': unit.title, 'summary': unit.summary, 'body': authored['body'],
            'content_version': unit.content_version, 'duration_minutes': unit.duration_minutes,
            'practice': unit.practice, 'sources': unit.sources,
        })
    except (KeyError, OSError, ValueError, TypeError) as error:
        raise RuntimeError('Lesson content unavailable.') from error
