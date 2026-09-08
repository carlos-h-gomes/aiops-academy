"""Strict public curriculum metadata; no learner state or executable content."""
from datetime import date
from typing import Annotated, Literal
from urllib.parse import urlsplit
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Identity = Annotated[str, Field(pattern=r'^[a-z][a-z0-9-]{0,79}$')]
Text = Annotated[str, Field(min_length=1, max_length=1000)]


class Metadata(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class Source(Metadata):
    title: Text
    url: Annotated[str, Field(max_length=2000)]

    @field_validator('url')
    @classmethod
    def safe_url(cls, value):
        url = urlsplit(value)
        if url.scheme != 'https' or not url.hostname or url.username or url.password or any(c.isspace() for c in value):
            raise ValueError('Source must use HTTPS without credentials or spaces.')
        return value


class Translation(Metadata):
    locale: Literal['pt-BR', 'en', 'es']
    status: Literal['available', 'planned']
    content_version: str | None


class Duration(Metadata):
    essential: Annotated[int, Field(ge=1, le=1200)]
    complete: Annotated[int, Field(ge=1, le=1200)]

    @model_validator(mode='after')
    def coherent(self):
        if self.complete < self.essential:
            raise ValueError('Complete duration cannot be less than essential duration.')
        return self


class Practice(Metadata):
    kind: Literal['simulation']
    lab_id: Identity
    title: Text
    limitations: Text


class Unit(Metadata):
    id: Identity
    track_id: Identity
    order: Annotated[int, Field(ge=1, le=200)]
    title: Text
    summary: Text
    status: Literal['available', 'planned']
    content_version: str | None
    lesson_day: Annotated[int, Field(ge=1, le=30)] | None
    competencies: Annotated[list[Text], Field(min_length=1, max_length=20)]
    prerequisites: Annotated[list[Identity], Field(max_length=20)]
    duration_minutes: Duration | None
    practice: Practice | None
    sources: Annotated[list[Source], Field(max_length=30)]
    translations: Annotated[list[Translation], Field(min_length=3, max_length=3)]
    # Empty means no real-product version was verified by this metadata increment.
    verified_tool_versions: Annotated[list[Text], Field(max_length=20)]

    @model_validator(mode='after')
    def readiness(self):
        locales = {item.locale: item for item in self.translations}
        if set(locales) != {'pt-BR', 'en', 'es'}:
            raise ValueError('Translations must declare each supported locale once.')
        if len(set(self.prerequisites)) != len(self.prerequisites) or self.id in self.prerequisites:
            raise ValueError('Repeated or self prerequisite.')
        for translation in self.translations:
            if translation.status == 'available':
                if self.status != 'available' or not self.content_version or translation.content_version != self.content_version:
                    raise ValueError('Available translation must match available source revision.')
            elif translation.content_version is not None:
                raise ValueError('Planned translation cannot claim a content revision.')
        if self.status == 'available':
            if self.lesson_day is None or not self.content_version or self.duration_minutes is None or self.practice is None or not self.sources or locales['pt-BR'].status != 'available':
                raise ValueError('Available unit needs source lesson, duration, practice, references and Portuguese content.')
        elif any(x is not None for x in (self.lesson_day, self.content_version, self.duration_minutes, self.practice)) or self.sources or self.verified_tool_versions:
            raise ValueError('Planned unit cannot claim available content, measured practice or references.')
        return self


class Guide(Metadata):
    id: Identity
    title: Text


class Track(Metadata):
    id: Identity
    title: Text
    summary: Text
    outcome: Text
    guides: Annotated[list[Guide], Field(max_length=25)]


class Curriculum(Metadata):
    schema_version: Literal['1.0']
    version: Annotated[str, Field(min_length=1, max_length=40)]
    metadata_reviewed_on: str
    tracks: Annotated[list[Track], Field(min_length=1, max_length=20)]
    units: Annotated[list[Unit], Field(min_length=1, max_length=200)]

    @field_validator('metadata_reviewed_on')
    @classmethod
    def iso_date(cls, value):
        if date.fromisoformat(value).isoformat() != value:
            raise ValueError('Use ISO calendar date.')
        return value

    @model_validator(mode='after')
    def graph(self):
        tracks = {track.id for track in self.tracks}
        units = {unit.id: unit for unit in self.units}
        if len(tracks) != len(self.tracks) or len(units) != len(self.units):
            raise ValueError('Duplicate track or unit identity.')
        orders, days = set(), set()
        for track in self.tracks:
            if len({guide.id for guide in track.guides}) != len(track.guides):
                raise ValueError('Duplicate guide in track.')
            if not any(unit.track_id == track.id for unit in self.units):
                raise ValueError('Track must declare its available or planned units.')
        for unit in self.units:
            if unit.track_id not in tracks or any(ref not in units for ref in unit.prerequisites):
                raise ValueError('Dangling track or prerequisite.')
            key = (unit.track_id, unit.order)
            if key in orders:
                raise ValueError('Duplicate order within a track.')
            orders.add(key)
            if unit.lesson_day is not None:
                if unit.lesson_day in days or unit.id != f'infra-{unit.lesson_day:02d}' or unit.track_id != 'infra':
                    raise ValueError('Legacy lesson identity is immutable and cannot be duplicated.')
                days.add(unit.lesson_day)
            if unit.status == 'available' and any(units[ref].status != 'available' for ref in unit.prerequisites):
                raise ValueError('Available content cannot require a planned unit.')
        visiting, visited = set(), set()
        def visit(identity):
            if identity in visiting:
                raise ValueError('Cyclic prerequisites.')
            if identity in visited:
                return
            visiting.add(identity)
            for ref in units[identity].prerequisites:
                visit(ref)
            visiting.remove(identity)
            visited.add(identity)
        for identity in units:
            visit(identity)
        return self


def validate_content_links(value: Curriculum, course: dict, manuals: list, labs: dict):
    """Check authored references against actual content before exposing or writing it."""
    lessons = {lesson['day']: lesson for lesson in course['lessons']}
    sources = {source['id']: source for source in course['sources']}
    guides = {guide['id']: guide for guide in manuals}
    available = [unit for unit in value.units if unit.status == 'available']
    if {unit.lesson_day for unit in available} != set(lessons):
        raise ValueError('All legacy lessons must remain represented once.')
    for track in value.tracks:
        for guide in track.guides:
            if guide.id not in guides or guide.title != guides[guide.id]['title']:
                raise ValueError('Missing or stale library guide.')
    for unit in available:
        lesson = lessons[unit.lesson_day]
        expected_sources = [Source(title=sources[key]['title'], url=sources[key]['url']) for key in lesson['sources']]
        if unit.title != lesson['title'] or unit.summary != lesson['summary'] or unit.competencies != lesson['objectives'] or unit.content_version != course['version'] or unit.sources != expected_sources:
            raise ValueError('Lesson metadata is stale; regenerate the catalog.')
        lab = labs.get(lesson['lab'])
        if not lab or unit.practice.lab_id != lab['id'] or unit.practice.title != lab['title'] or unit.practice.limitations != lab['limitations']:
            raise ValueError('Missing or stale practice reference.')
        if unit.duration_minutes.essential != 180 or unit.duration_minutes.complete != lesson['minutes']:
            raise ValueError('Lesson duration does not match the legacy course.')
    return value
