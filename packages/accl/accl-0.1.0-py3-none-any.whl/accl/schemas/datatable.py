from typing import Dict, List
from pydantic import BaseModel, conint, field_validator
from enum import Enum
from accl.schemas.base import Alignment, BasePayload, TemplateType, QuestionMeta

class DataTablePayload(BasePayload):
    template_type: TemplateType = TemplateType.DATA_TABLE

    cols: conint(ge=1)
    rows: conint(ge=1)

    header_first_row: bool = False
    header_first_col: bool = False
    align: Alignment = Alignment.LEFT

    cells: List[List[str]]

    @field_validator("cells")
    def validate_cells(cls, v, info):
        # info.data contains previously parsed fields
        rows = info.data.get("rows")
        cols = info.data.get("cols")

        if rows is not None and len(v) != rows:
            raise ValueError(f"`cells` has {len(v)} rows, expected {rows}")

        for i, row in enumerate(v):
            if cols is not None and len(row) != cols:
                raise ValueError(
                    f"`cells` row {i} has {len(row)} columns, expected {cols}"
                )

        return v

class DataTableQuestionContext(BaseModel):
    """
    What you pass into the LLM *per table*:
    - meta: who/where
    - payload: the table itself
    LLM uses payload to generate question text, options, etc.
    """
    meta: QuestionMeta
    payload: DataTablePayload


if __name__ == "__main__":
    payload= DataTablePayload(
        cols=3,
        rows=2,
        header_first_row=True,
        header_first_col=False,
        align=Alignment.CENTER,
        cells=[
            ["Header 1", "Header 2", "Header 3"],
            ["Data 1", "Data 2", "Data 3"],
        ],
    )
    breakpoint()
    print(payload)


    questions= DataTableQuestionContext(
        meta= QuestionMeta(
            id="q1",
            year="2023",
            subject="Math",
            category="Data Handling",
            question_name="Sample Data Table Question",
            expected_time_secs=60,
        ),
        payload= payload,
    )
    breakpoint()
    print(questions)