from typing import Callable, Optional

import re

from xlsxwriter import Workbook
from xlsxwriter.format import Format
from xlsxwriter.worksheet import Worksheet

from .Field import Field


class Creator:
    def __init__(self,
                 workbook: Workbook,
                 worksheet: Worksheet,
                 fields: list[Field],
                 print_title: bool = True,
                 group_formatter: Callable = None,
                 header_format_def: dict = None,
                 group_summary_format_def: dict = None,
                 total_summary_format_def: dict = None
                 ):
        self.workbook = workbook
        self.worksheet = worksheet
        self.fields: list[Field] = fields
        self.fields_visible = [field for field in self.fields if not field.hidden]
        # Should the titles be printed in the first column
        self.print_title: bool = print_title
        # What should be printed as a group title
        if group_formatter is None:
            group_formatter = self._create_group_title
        self.group_formatter: Callable[[dict], str] = group_formatter
        # Excel-format for header columns
        if header_format_def is None:
            header_format_def: dict = {"bold": True, "center_across": True, 'bg_color': '#eeeeee'}
        self.header_format: Format = self.workbook.add_format(header_format_def)

        # Excel-format for group summary
        if group_summary_format_def is None:
            group_summary_format_def: dict = {"bold": True, 'bg_color': '#eeeeee'}

        # Excel-format for header columns
        if total_summary_format_def is None:
            total_summary_format_def: dict = {"bold": True, 'bg_color': '#cccccc'}

        self.group_by_fields: list[Field] = list(filter(lambda field: field.group_by, self.fields))
        self.group_by: bool = any(self.group_by_fields)

        self.show_group_summary: bool = any(filter(lambda field: field.group_summary is not None, self.fields_visible))
        self.show_total_summary: bool = any(filter(lambda field: field.total_summary is not None, self.fields_visible))

        # Checks
        field_names: list[str] = [field.name for field in self.fields]
        assert len(field_names) == len(set(field_names)), "Duplicate field names"

        # Field -> Index
        field_names_map: dict[str, int] = {field.name: idx_j for idx_j, field in enumerate(self.fields_visible)}

        for idx_j, field in enumerate(self.fields_visible):
            field.idx_code = Field.idx_to_code(idx_j) # To Excel codes: 1 -> A, 2 -> B, ...

            # Create cell format
            base_format = {} if field.excel_format_def is None else field.excel_format_def
            field.excel_format = None if base_format == {} else workbook.add_format(base_format)
            field.excel_format_group_summary = workbook.add_format(group_summary_format_def | base_format)
            field.excel_format_total_summary = workbook.add_format(total_summary_format_def | base_format)

            # Replace ?<column-name>? with excel code
            if field.formular is not None:
                matches = re.findall(r"\?(.*?)\?", field.formular)
                if matches:
                    for match in matches:
                        idx_j = field_names_map[match]
                        assert idx_j is not None, f"No field with name '{match}'"
                        field.formular = field.formular.replace(f"?{match}?", Field.idx_to_code(idx_j))


    def create(self, data: list[dict]):
        idx_i: int = 0

        if self.print_title:
            self._print_title_row()
            idx_i += 1

        # If data should be grouped, sort it by the keys
        data = data if not self.group_by else sorted(data, key=self._create_group_key)
        group_values, group_start, data_indices = None, None, []

        for row in data:
            group_changed = False
            if self.group_by:
                group_key = self._create_group_key(row)
                group_changed = group_values != group_key

                # Group changed
                if group_changed:
                    if group_start is not None and self.show_group_summary:
                        self._print_group_summary(idx_i, data_indices[-1])
                        idx_i += 1  # empty row

                    idx_i += 1 if group_start is not None else 0  # empty row

                    # Print group header
                    self.worksheet.merge_range(idx_i, 0, idx_i, len(self.fields_visible) - 1,
                                               self.group_formatter(row), self.header_format)

                    idx_i += 1
                    group_start = idx_i + 1
                    group_values = group_key

            # Write all fields to cells
            for idx_j, field in enumerate(self.fields_visible):
                field.write(self.worksheet, idx_i, idx_j, row, field.excel_format)

            # Set data indices window
            if data_indices == [] or group_changed: # No last group, or group changed -> Add new data indices window
                data_indices.append({"start": idx_i, "end": idx_i})
            else:
                data_indices[-1]["end"] = idx_i  # Increase current data indices window

            idx_i += 1

        # Add group summary for last group
        if self.show_group_summary and group_start is not None:
            self._print_group_summary(idx_i, data_indices[-1])
            idx_i += 1

        # Att total summary
        if self.show_total_summary:
            idx_i += 1
            self._print_total_summary(idx_i, data_indices)


    def _print_title_row(self):
        for idx_j, field in enumerate([field for field in self.fields if not field.hidden]):
            self.worksheet.write_string(0, idx_j, field.title, self.header_format)


    def _print_group_summary(self, idx_i: int, group_window: dict):
        for idx_j, field in enumerate([field for field in self.fields if not field.hidden]):
            if field.group_summary is not None:
                from_cell: str = f"{field.idx_code}{group_window['start'] + 1}"
                to_cell: str = f"{field.idx_code}{group_window['end'] + 1}"
                content = f"={field.group_summary.value}({from_cell}:{to_cell})"
                self.worksheet.write_formula(idx_i, idx_j, content, field.excel_format_group_summary)
            else:
                self.worksheet.write(idx_i, idx_j, "", field.excel_format_group_summary)


    def _print_total_summary(self, idx_i: int, data_indices: list[dict]):
        for idx_j, field in enumerate([field for field in self.fields_visible]):
            if field.total_summary is not None:
                # Create a list of slices for a column
                slices = [f"{field.idx_code}{di['start'] + 1}:{field.idx_code}{di['end'] + 1}" for di in data_indices]
                content = f"={field.total_summary.value}({','.join(slices)})"
                self.worksheet.write_formula(idx_i, idx_j, content, field.excel_format_total_summary)
            else:
                self.worksheet.write(idx_i, idx_j, "", field.excel_format_total_summary)


    def _create_group_key(self, row):
        return [row[field.name] for field in self.fields if field.group_by]


    def _create_group_title(self, row: dict) -> str:
        return ", ".join([row[field.name] for field in self.group_by_fields])
