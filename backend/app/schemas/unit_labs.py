"""Strict, read-only contracts for the authored non-legacy lab runner."""
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field


Identity = Annotated[str, Field(pattern=r'^[a-z][a-z0-9-]{0,79}$')]
ReviewIdentity = Annotated[str, Field(pattern=r'^[a-z][a-z0-9_-]{0,79}$')]
Answer = Annotated[str, Field(min_length=1, max_length=200)]


class LabSchema(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class UnitLabOption(LabSchema):
    value: Answer
    label: Annotated[str, Field(min_length=1, max_length=300)]


class UnitLabQuestion(LabSchema):
    id: Identity
    prompt: Annotated[str, Field(min_length=1, max_length=800)]
    options: Annotated[list[UnitLabOption], Field(min_length=2, max_length=12)]


class UnitLab(LabSchema):
    unit_id: Identity
    title: Annotated[str, Field(min_length=1, max_length=300)]
    intro: Annotated[str, Field(min_length=1, max_length=1200)]
    limitations: Annotated[str, Field(min_length=1, max_length=1200)]
    questions: Annotated[list[UnitLabQuestion], Field(min_length=1, max_length=20)]


class UnitLabRun(LabSchema):
    """Closed choices only; prose, paths and executable content are intentionally absent."""
    answers: Annotated[dict[Identity, Answer], Field(min_length=1, max_length=20)]


class UnitLabResult(LabSchema):
    unit_id: Identity
    correct: bool
    reviewed_fields: Annotated[list[ReviewIdentity], Field(max_length=20)]
    feedback: Annotated[str, Field(min_length=1, max_length=1000)]
