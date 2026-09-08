"""Bounded metadata loading. No progress access or writes."""
import json
from functools import lru_cache
from .catalog import COURSE, LAB_MAP, ROOT
from app.schemas.curriculum import Curriculum, validate_content_links


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
