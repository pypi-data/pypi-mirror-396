import re

from enum import Enum
from typing import Optional

from xlsxwriter.worksheet import Worksheet, Format


class Field:
    class AggregationType(Enum):
        SUM = "SUM"
        AVG = "AVERAGE"
        MIN = "MIN"
        MAX = "MAX"

    @staticmethod
    def idx_to_code(idx: int):
        lbl: str = ""

        while idx >= 0:
            lbl: str = chr(idx % 26 + ord('A')) + lbl
            idx: int = idx // 26 - 1

        return lbl

    def __init__(self, name: str, title: str, formular: str = None, group_by: bool = False, hidden: bool = False,
                 group_summary: AggregationType  = None, total_summary: AggregationType = None,
                 excel_format_def: dict = None):
        self.name: str = name
        self.title: str = title
        self.formular: str = formular
        self.group_by: bool = group_by
        self.hidden: bool = hidden
        self.group_summary: Field.AggregationType= group_summary
        self.total_summary: Field.AggregationType = total_summary
        self.excel_format_def: dict = excel_format_def
        self.excel_format: Optional[Format] = None
        self.excel_format_group_summary: Optional[Format] = None
        self.excel_format_total_summary: Optional[Format] = None
        self.idx_code: Optional[str] = None

        assert not (self.formular is not None and  self.group_by), "Group by a formular is not allowed"

    def write(self, worksheet: Worksheet, i: int, j: int, row: dict, ef: Format) -> None:
        if self.formular is None:
            worksheet.write(i, j, row[self.name], ef)
        else:
            worksheet.write_formula(i, j, self.parse_formular(i, j), ef)

    def parse_formular(self, i: int, j: int) -> str:
        pattern_i: str = r"<(i(?:\+\d+)?)>"
        pattern_j: str = r"<(j(?:\+\d+)?)>"

        def replacer_i(match):
            expr: str = match.group(1)  # e.g., 'i' or 'i+9'
            return str(eval(expr, {"i": i + 1})) # Evaluate the expression using the current value of i

        def replacer_j(match):
            expr: str = match.group(1)  # e.g., 'j' or 'j+9'
            return str(Field.idx_to_code(eval(expr, {"j": j}))) # Evaluate the expression using the current value of j

        result: str = re.sub(pattern_i, replacer_i, self.formular)
        return re.sub(pattern_j, replacer_j, result)
