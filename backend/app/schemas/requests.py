"""Bounded v1 inputs. Additional attributes are rejected."""
from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class Input(BaseModel):
    model_config = ConfigDict(extra='forbid')

class Note(Input):
    text: str = Field(max_length=12000)

class Quiz(Input):
    answers: list[int] = Field(min_length=2,max_length=60)

class Settings(Input):
    start_date: date
    daily_hours: Literal[0.5,0.75,1,1.5,2,3,5] = 1

    @field_validator('daily_hours', mode='before')
    @classmethod
    def numeric_hours(cls, value):
        if type(value) not in (int, float):
            raise ValueError('Disponibilidade deve ser um número permitido.')
        return value

class LabRun(Input):
    source: str = Field(default='',max_length=12000)
    session_id: str = Field(min_length=32,max_length=32,pattern=r'^[a-f0-9]+$')
    action: str = Field(default='',max_length=40)
    check: bool = False

class Rating(Input):
    rating: Literal['again','hard','good','easy']

class Restore(Input):
    version: Literal[1]
    settings: Settings
    notes: dict[str,str] = Field(max_length=30)
    completed: list[int] = Field(max_length=30)
    quizzes: dict[str,float] = Field(max_length=30)
    labs: dict[str,bool] = Field(max_length=20)
    reviews: dict[str,dict] = Field(max_length=30)
    confirm: Literal[True]
