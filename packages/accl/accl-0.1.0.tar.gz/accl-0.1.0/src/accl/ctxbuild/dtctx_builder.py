from __future__ import annotations

from typing import Dict, List
import random
from typing import Tuple, Optional
from accl.ctxbuild.base import BaseContextBuilder
from accl.utils.num_gen import generate_random_table
from accl.schemas.base import (
    Alignment,
    QuestionMeta,
    TemplateType,
)
from accl.schemas.datatable import DataTablePayload, DataTableQuestionContext

class DataTableContextBuilder(BaseContextBuilder):
    template_type = TemplateType.DATA_TABLE

    def build(
        self,
        cells: List[List[str]],
        header_first_row: bool = False,
        header_first_col: bool = False,
        align: Alignment = Alignment.LEFT,
    ) -> DataTablePayload:
        """
        Create a DataTablePayload from a 2D list of cells and property flags.

        - `cells` is a 2D array of strings, shape = rows x cols.
        - rows/cols are inferred from `cells`.
        - header flags and alignment are passed through.
        """
        if not cells:
            raise ValueError("`cells` must contain at least one row")

        rows = len(cells)
        cols = len(cells[0])

        payload = DataTablePayload(
            cols=cols,
            rows=rows,
            header_first_row=header_first_row,
            header_first_col=header_first_col,
            align=align,
            cells=cells,
        )
        return payload



def choose_header_config(table_params: dict) -> Tuple[bool, bool, Optional[str]]:
    """
    Decide the header layout for this table instance.

    Returns:
        header_first_row (bool),
        header_first_col (bool),
        chosen_row_prefix (str or None)
    """
    header_modes = table_params.get("header_modes", ["col_only"])
    mode = random.choice(header_modes)

    row_prefixes = table_params.get("row_prefixes", [])
    row_prefix = None

    if mode == "col_only":
        # Always want a header row in these stat/prob tables
        header_first_row = True
        header_first_col = False
        row_prefix = None

    elif mode == "row_and_col":
        header_first_row = True
        header_first_col = True
        row_prefix = random.choice(row_prefixes) if row_prefixes else None

    else:
        # Fallback – behave like col_only
        header_first_row = True
        header_first_col = False
        row_prefix = None

    return header_first_row, header_first_col, row_prefix


def build_datatable_context(
    template_cfg: dict,
    meta_cfg: dict,

) -> Dict[str, List[DataTableQuestionContext]]:
    """
    Generic builder for DATA_TABLE contexts.

    topic_cfg comes from template_config.yaml under topics.<topic_name>.
    meta_cfg comes from question_meta_configs.<meta_key>.
    """


    num_tables: int = template_cfg["num_tables"]
    table_params: dict = template_cfg["table_params"]

    contexts: List[DataTableQuestionContext] = []

    for i in range(num_tables):

        prefixes = table_params.get("category_prefixes", ["Item"])
        category_prefix = random.choice(prefixes)
        header_first_row, header_first_col, row_prefix = choose_header_config(table_params)


        rows = random.randint(*table_params["rows"])
        cols = random.randint(*table_params["cols"])

        cells = generate_random_table(
            rows=rows,
            cols=cols,
            min_count=table_params["min_count"],
            max_count=table_params["max_count"],
            category_prefix=category_prefix,
            header_first_row= header_first_row,
            header_first_col=header_first_col,
            row_prefix=row_prefix, 
        )
        
        cells = [[str(cell) for cell in row] for row in cells]


        rows = len(cells)
        cols = len(cells[0])
        # breakpoint()

        payload = DataTablePayload(
            cols=cols,
            rows=rows,
            header_first_row=header_first_row,
            header_first_col=header_first_col,
            align=Alignment(table_params["align"]),
            cells=cells,
        )

        meta = QuestionMeta(
            id=f'{meta_cfg["id_prefix"]}{i+1}',
            year=meta_cfg["year"],
            subject=meta_cfg["subject"],
            category=meta_cfg["category"],
            question_name=f'{meta_cfg["question_name_prefix"]}{i+1}',
            expected_time_secs=meta_cfg["expected_time_secs"],
        )

        contexts.append(DataTableQuestionContext(meta=meta, payload=payload))

    return {"data_tables": contexts}