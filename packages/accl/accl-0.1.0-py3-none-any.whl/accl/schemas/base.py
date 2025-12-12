from enum import Enum
from typing import List
from pydantic import BaseModel, field_validator, conint


class Alignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class TemplateType(str, Enum):
    DATA_TABLE = "data_table"
    CHART = "chart"
    ANGLE = "angle"
    # Later: CHART = "chart", ANGLES = "angles", ...


class QuestionMeta(BaseModel):
    id: str
    year: str
    subject: str
    category: str
    question_name: str
    expected_time_secs: int


class BasePayload(BaseModel):
    template_type: TemplateType
