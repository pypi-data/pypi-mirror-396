"""
Excel Report Builder for SDK Scenario Data.

This file creates Excel (.xlsx) files that help users understand:
1. What data changed between two systems (Comparison Reports)
2. How complete and accurate the data is (Validation Reports)

FILE STRUCTURE:
- Constants
- Utility Functions
- ScenarioReportStyle
- ComparisonReportGenerator
- ValidationReportGenerator
- ScenarioReportBuilder
"""

import os
import re
import pandas as pd
from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING, Union

if TYPE_CHECKING:
    import xlsxwriter

# =========================================================================
# CONSTANTS
# =========================================================================

EXCEL_SHEET_NAME_MAX_LENGTH = 31
EXCEL_MAX_COLUMN_WIDTH = 50

# Colors used in Excel reports
EXCEL_COLORS = {
    'title_bg': '#E2EFDA',
    'subtitle_text': '#333333',
    'section_header_bg': '#F2F2F2',
    'box_header_bg': '#D9E1F2',
    'change_type_label_bg': '#F9F9F9',
    'example_header_bg': '#FFF2CC',
    'small_text': '#555555',
    'tech_header_bg': '#FCE4D6',
    'header_bg': '#D3D3D3',
    'alt_row_bg': '#D3D3D3',
    'highlight_bg': '#E2EFDA', # Light green highlight for Yes
    'missing_bg': '#FFE6E6',   # Red for missing
    'chart_fill': '#4F81BD',
    'chart_missing_fill': '#E74C3C',
}

# Color bands for conditional formatting (Color, Min, Max, IsExactZero)
BAND_COLORS: List[Tuple[str, float, float, bool]] = [
    ('#5CB85C', 0.0, 0.0, True),
    ('#7BC87A', 0.0, 0.10, False),
    ('#9BD899', 0.10, 0.20, False),
    ('#BDE8BC', 0.20, 0.30, False),
    ('#DFF8DE', 0.30, 0.40, False),
    ('#FFF9E6', 0.40, 0.50, False),
    ('#FFE6CC', 0.50, 0.60, False),
    ('#FFD3B3', 0.60, 0.70, False),
    ('#FFC099', 0.70, 0.80, False),
    ('#FFAD80', 0.80, 0.90, False),
    ('#E74C3C', 0.90, 1.0, False),
]

# Magic Strings
MAGIC_STRINGS = {
    'missing_entirely': 'MISSING ENTIRELY',
    'present': 'PRESENT',
    'change_type': 'change_type',
    'missing_percent': 'Missing %',
    'missing_count': 'Missing Count',
    'required': 'Required',
    'unique': 'Unique',
    'has_value_mappings': 'Has Value Mappings',
    'status': 'Status',
}

# Layout constants
LAYOUT = {
    'title_row_height': 30,
    'subtitle_row_height': 25, # or 80 for long subtitles
    'section_header_height': 25,
    'toc_row_height': 20,
    'standard_row_height': 20,
}


# =========================================================================
# UTILITY FUNCTIONS
# =========================================================================

def _truncate_sheet_name(
    name: str,
    max_length: int = EXCEL_SHEET_NAME_MAX_LENGTH
) -> str:
    """
    Shortens sheet names to fit Excel's 31-character limit.

    Excel throws an error if sheet names exceed 31 characters, so this prevents
    that error by automatically shortening names when needed. Used by all methods
    that create Excel sheets.

    Args:
        name (str): The original sheet name.
        max_length (int): Maximum allowed length (default: 31).

    Returns:
        str: The shortened name if needed, or original if it fits.
    """
    if len(name) <= max_length:
        return name
    return name[:max_length]

def _parse_percentage_value(
    value: Any
) -> Optional[float]:
    """
    Converts percentage strings (e.g., "50.00%") to numbers for Excel formatting.

    Excel needs numeric values (0.50) not strings ("50.00%") for percentage format.
    Used by methods that write percentage columns to Excel.

    Args:
        value (Any): Input value (string with %, number, or None).

    Returns:
        Optional[float]: Numeric value or None if conversion fails.
    """
    if value is None: return None
    if isinstance(value, (int, float)): return float(value)
    try:
        cleaned = str(value).replace("%", "").strip()
        return float(cleaned)
    except (TypeError, ValueError): return None

def _format_standard_worksheet(
    writer: pd.ExcelWriter,
    workbook: 'xlsxwriter.Workbook',
    df: pd.DataFrame,
    sheet_name: str,
    style: 'ScenarioReportStyle'
) -> None:
    """
    Creates a simple data table sheet with headers and auto-sized columns.

    Used for comparison data sheets like the main comparison sheet and optional
    source/target sheets. Creates a new sheet in the Excel file with gray headers
    and white data rows, with columns auto-sized to fit content.

    Args:
        writer (pd.ExcelWriter): The pandas ExcelWriter object.
        workbook (xlsxwriter.Workbook): The Excel workbook object.
        df (pd.DataFrame): The data to write.
        sheet_name (str): Name for the Excel sheet.
        style (ScenarioReportStyle): Style object containing header and data formats.
    """
    sheet_name = _truncate_sheet_name(sheet_name)
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    worksheet = writer.sheets[sheet_name]

    header_format = style.header_format
    data_format = style.data_format

    for i, col in enumerate(df.columns):
        col_data = df[col].astype(str)
        max_data_len = col_data.str.len().max() if len(col_data) > 0 else 0
        if pd.isna(max_data_len): max_data_len = 0
        column_len = max(max_data_len, len(str(col)))
        worksheet.set_column(i, i, min(column_len + 2, EXCEL_MAX_COLUMN_WIDTH), data_format)

    header_row = 0
    for col_num in range(len(df.columns)):
        worksheet.write(header_row, col_num, df.columns[col_num], header_format)


# =========================================================================
# STYLE CLASS
# =========================================================================

class ScenarioReportStyle:
    """
    Manages all Excel formatting (colors, fonts, styles) for reports.
    """

    def __init__(
        self,
        workbook: 'xlsxwriter.Workbook'
    ):
        """
        Initialize the ScenarioReportStyle with a workbook.

        Args:
            workbook (xlsxwriter.Workbook):
                The xlsxwriter Workbook object to which formats will be added.
        """
        self.workbook = workbook
        self.common_formats = self._init_common_formats()
        self.comparison_formats = self._init_comparison_formats()

        # Cache commonly used formats
        self.header_format = self.workbook.add_format({
            'bold': True, 'text_wrap': True, 'valign': 'top',
            'fg_color': EXCEL_COLORS['header_bg'], 'border': 1
        })
        self.data_format = self.workbook.add_format({
            'text_wrap': True, 'valign': 'top', 'border': 1
        })
        self.missing_format = self.workbook.add_format({
            'text_wrap': True, 'valign': 'top', 'border': 1,
            'fg_color': EXCEL_COLORS['missing_bg'], 'bold': True
        })

    def _init_common_formats(self) -> Dict[str, Any]:
        """
        Initialize generic formats used across different report types.

        Returns:
            Dict[str, Any]: Dictionary of format objects (e.g., 'title', 'subtitle').
        """
        return {
            'title': self.workbook.add_format({
                'bold': True, 'font_size': 16, 'valign': 'vcenter',
                'fg_color': EXCEL_COLORS['title_bg'], 'border': 1, 'text_wrap': True
            }),
            'subtitle': self.workbook.add_format({
                'font_size': 14, 'font_color': EXCEL_COLORS['subtitle_text'],
                'valign': 'top', 'text_wrap': True
            }),
            'section_header': self.workbook.add_format({
                'bold': True, 'font_size': 14, 'valign': 'top', 'bottom': 2,
                'fg_color': EXCEL_COLORS['section_header_bg'], 'text_wrap': True
            }),
            'toc': self.workbook.add_format({
                'text_wrap': True, 'valign': 'top', 'font_size': 14, 'indent': 1
            }),
            'tech_header': self.workbook.add_format({
                'bold': True, 'fg_color': EXCEL_COLORS['tech_header_bg'],
                'border': 1, 'valign': 'top'
            }),
            'tech_text': self.workbook.add_format({
                'text_wrap': True, 'valign': 'top', 'border': 1, 'font_size': 14
            }),
            'tech_text_small': self.workbook.add_format({
                'text_wrap': True, 'valign': 'top', 'border': 1, 'font_size': 14
            })
        }

    def _init_comparison_formats(self) -> Dict[str, Any]:
        """
        Initialize formats specific to Comparison Reports.

        Returns:
            Dict[str, Any]: Dictionary of format objects, including common formats.
        """
        formats = self.common_formats.copy()
        formats.update({
            'box_header': self.workbook.add_format({
                'bold': True, 'fg_color': EXCEL_COLORS['box_header_bg'],
                'border': 1, 'valign': 'top'
            }),
            'box_text': self.workbook.add_format({
                'text_wrap': True, 'valign': 'top', 'border': 1,
                'font_size': 14, 'indent': 1
            }),
            'change_type_label': self.workbook.add_format({
                'bold': True, 'text_wrap': True, 'valign': 'top', 'font_size': 14,
                'fg_color': EXCEL_COLORS['change_type_label_bg'], 'right': 1
            }),
            'change_type_text': self.workbook.add_format({
                'text_wrap': True, 'valign': 'top', 'font_size': 14, 'indent': 1
            }),
            'example_header': self.workbook.add_format({
                'bold': True, 'fg_color': EXCEL_COLORS['example_header_bg'],
                'border': 1, 'text_wrap': True, 'valign': 'vcenter', 'font_size': 14
            }),
            'example_cell': self.workbook.add_format({
                'border': 1, 'text_wrap': True, 'valign': 'vcenter', 'font_size': 14
            }),
            'small_text': self.workbook.add_format({
                'font_size': 14, 'text_wrap': True, 'valign': 'top',
                'italic': True, 'font_color': EXCEL_COLORS['small_text']
            }),
            'action_number': self.workbook.add_format({
                'bold': True, 'text_wrap': True, 'valign': 'top', 'font_size': 14,
                'right': 1, 'fg_color': EXCEL_COLORS['change_type_label_bg']
            }),
            'action_text': self.workbook.add_format({
                'text_wrap': True, 'valign': 'top', 'font_size': 14, 'indent': 1
            })
        })
        return formats

    def get_audit_cell_format(
        self,
        col_name: str,
        value: Any,
        is_missing: bool,
        bg_color: str
    ) -> 'xlsxwriter.format.Format':
        """
        Determine the appropriate cell format based on column type, value, and status.

        Args:
            col_name (str): Name of the column being formatted.
            value (Any): The value in the cell.
            is_missing (bool): Boolean indicating if the value is considered missing.
            bg_color (str): Background color hex string for the cell.

        Returns:
            xlsxwriter.Format: An xlsxwriter Format object.
        """
        if is_missing:
            return self.missing_format

        base_props = {'text_wrap': True, 'valign': 'top', 'border': 1, 'bg_color': bg_color}

        float_cols = {'Min', 'Max', 'Mean', 'Std Dev', '25th Percentile', '50th Percentile', '75th Percentile', 'Mean Length', 'Std Length'}
        int_cols = {'Missing Count', 'Unique Count', 'Unique Dates', 'Min Length', 'Max Length'}
        bool_cols = {MAGIC_STRINGS['required'], MAGIC_STRINGS['unique'], MAGIC_STRINGS['has_value_mappings']}

        if col_name in float_cols:
            if pd.notna(value) and isinstance(value, (int, float)):
                base_props['num_format'] = '0.00'
                base_props['align'] = 'right'
        elif col_name in int_cols:
            if pd.notna(value) and isinstance(value, (int, float)):
                base_props['num_format'] = '0'
                base_props['align'] = 'right'
        elif col_name == MAGIC_STRINGS['missing_percent']:
            base_props['num_format'] = '0.00%'
            base_props['align'] = 'right'
        elif col_name in bool_cols and value is True:
             base_props['fg_color'] = EXCEL_COLORS['highlight_bg']
        elif col_name == MAGIC_STRINGS['status'] and isinstance(value, str) and value.upper() != MAGIC_STRINGS['present']:
             return self.missing_format

        return self.workbook.add_format(base_props)


# =========================================================================
# REPORT GENERATORS
# =========================================================================

class ComparisonReportGenerator:
    """
    Handles creation of Comparison Reports.

    EXCEL FILE STRUCTURE:
    =====================
    Sheet 1: "Explanation"
    ├── Title: "Bob → Nmbrs Data Comparison"
    ├── Table of Contents: Lists all sheets in the file
    ├── Quick Start Guide: How to read the comparison
    ├── Change Types: Explains NEW, EDITED, DELETED records
    ├── Example: Shows a sample change
    ├── Action Items: What the user needs to do
    └── Technical Details: Configuration info

    Sheet 2: "Comparison Personal" (main data)
    └── Shows all records with differences (NEW, EDITED, DELETED)

    Sheet 3+: Optional source/target data sheets
    """

    def create_report(
        self,
        df_compare: pd.DataFrame,
        filepath: str,
        sheetname: str,
        source_system: str,
        target_system: str,
        scenario_name: str,
        unique_columns: List[str],
        all_target_fields: List[str],
        cols_to_check: List[str],
        df_source: Optional[pd.DataFrame] = None,
        df_target: Optional[pd.DataFrame] = None
    ) -> None:
        """
        Creates a Comparison Report Excel file showing what changed between two systems.

        The main comparison sheet shows records with a "change_type" column:
        - NEW: Record exists in source but not in target (will be created)
        - EDITED: Record exists in both but values differ (will be updated)
        - DELETED: Record exists in target but not in source (will be removed)

        Args:
            df_compare (pd.DataFrame): The main comparison data - rows with differences. Must have a "change_type" column.
            filepath (str): Where to save the Excel file (e.g., "reports/comparison.xlsx").
            sheetname (str): Name for the main comparison sheet (e.g., "Comparison Personal").
            source_system (str): Name of the source system (e.g., "Bob", "Workday").
            target_system (str): Name of the target system (e.g., "Nmbrs", "Sage").
            scenario_name (str): Name of the scenario being compared (e.g., "Personal", "Salary").
            unique_columns (List[str]): Columns used to match records (e.g., ["employee_id"]).
            all_target_fields (List[str]): All fields that should exist in the target system.
            cols_to_check (List[str]): Fields that were compared for differences.
            df_source (Optional[pd.DataFrame]): Optional original source data (for reference sheet).
            df_target (Optional[pd.DataFrame]): Optional original target data (for reference sheet).
        """
        if df_compare is None or df_compare.empty:
            return # Optionally raise error if empty df is invalid state

        if MAGIC_STRINGS['change_type'] not in df_compare.columns:
            raise ValueError(f"DataFrame must contain '{MAGIC_STRINGS['change_type']}' column")

        try:
            with pd.ExcelWriter(filepath, engine='xlsxwriter', mode="w") as writer:
                workbook = writer.book
                style = ScenarioReportStyle(workbook)

                self._create_explanation_sheet(
                    writer, workbook, source_system, target_system, sheetname,
                    df_source, df_target, scenario_name, unique_columns,
                    all_target_fields, cols_to_check, style
                )

                _format_standard_worksheet(writer, workbook, df_compare, sheetname, style)

                if df_source is not None and not df_source.empty:
                    name = sheetname.replace('comparison ', '').replace(' scenario', '') + f' {source_system} transformed'
                    _format_standard_worksheet(writer, workbook, df_source, name, style)

                if df_target is not None and not df_target.empty:
                    name = sheetname.replace('comparison ', '').replace(' scenario', '') + f' {target_system} transformed'
                    _format_standard_worksheet(writer, workbook, df_target, name, style)

        except Exception as e:
            raise RuntimeError(f"Failed to create comparison report at {filepath}: {str(e)}") from e

    def _create_explanation_sheet(
        self,
        writer: pd.ExcelWriter,
        workbook: 'xlsxwriter.Workbook',
        source_system: str,
        target_system: str,
        sheetname: str,
        df_source: Optional[pd.DataFrame],
        df_target: Optional[pd.DataFrame],
        scenario_name: str,
        unique_columns: List[str],
        all_target_fields: List[str],
        cols_to_check: List[str],
        style: ScenarioReportStyle
    ) -> None:
        """
        Creates the "Explanation" sheet with instructions and overview.

        This is the first sheet users see - it explains how to read the comparison and
        what each section means.
        """
        explanation_sheetname = _truncate_sheet_name("Explanation")
        ws = workbook.add_worksheet(explanation_sheetname)
        writer.sheets[explanation_sheetname] = ws

        ws.set_column('A:A', 70)
        ws.set_column('B:B', 15)
        ws.set_column('C:E', 40)

        formats = style.comparison_formats
        row = 3

        self._write_title(ws, formats, source_system, target_system)
        row = self._write_toc(ws, formats, row, sheetname, source_system, target_system, df_source, df_target) + 1
        row = self._write_quick_start(ws, formats, row, source_system, target_system, unique_columns) + 2
        row = self._write_change_types(ws, formats, row, source_system, target_system) + 2
        row = self._write_example(ws, formats, row, source_system, target_system) + 2
        row = self._write_actions(ws, formats, row, _truncate_sheet_name(sheetname), source_system, target_system) + 2
        self._write_tech_details(ws, formats, row, scenario_name, unique_columns, all_target_fields, cols_to_check)
        ws.freeze_panes(3, 0)

    def _write_title(
        self,
        ws: 'xlsxwriter.Worksheet',
        formats: Dict[str, Any],
        source: str,
        target: str
    ) -> None:
        """Writes the title header at the top of the Explanation sheet."""
        ws.merge_range('A1:E1', f'{source} → {target} Data Comparison', formats['title'])
        ws.set_row(0, LAYOUT['title_row_height'])
        ws.merge_range('A2:E2', f'This workbook shows what has changed between {source} and {target} so you can review and approve updates.', formats['subtitle'])
        ws.set_row(1, LAYOUT['subtitle_row_height'])

    def _write_toc(
        self,
        ws: 'xlsxwriter.Worksheet',
        formats: Dict[str, Any],
        row: int,
        sheetname: str,
        source: str,
        target: str,
        df_source: Optional[pd.DataFrame],
        df_target: Optional[pd.DataFrame]
    ) -> int:
        """
        Writes the Table of Contents listing all sheets in the Excel file.

        Helps users navigate the file and understand what each sheet contains.
        """
        ws.write(row, 0, 'What\'s in this workbook?', formats['section_header'])
        ws.set_row(row, LAYOUT['section_header_height'])
        row += 1

        items = [("1. Explanation (this sheet)", "- How to read and use this comparison")]
        items.append((f"2. {_truncate_sheet_name(sheetname)}", "- Main comparison results with all detected changes"))

        idx = 3
        if df_source is not None and not df_source.empty:
            name = _truncate_sheet_name(sheetname.replace('comparison ', '').replace(' scenario', '') + f' {source} transformed')
            items.append((f"{idx}. {name}", f"- All transformed data from {source}"))
            idx += 1

        if df_target is not None and not df_target.empty:
            name = _truncate_sheet_name(sheetname.replace('comparison ', '').replace(' scenario', '') + f' {target} transformed')
            items.append((f"{idx}. {name}", f"- Current data from {target}"))

        for title, desc in items:
            ws.set_row(row, LAYOUT['toc_row_height'])
            ws.write(row, 0, title, formats['toc'])
            ws.write(row, 1, desc, formats['toc'])
            row += 1
        return row

    def _write_quick_start(
        self,
        ws: 'xlsxwriter.Worksheet',
        formats: Dict[str, Any],
        row: int,
        source: str,
        target: str,
        unique_cols: List[str]
    ) -> int:
        """
        Writes the "Quick Start Guide" explaining how the comparison works.

        Users need to understand how records are matched and what columns mean.
        """
        ws.write(row, 0, 'Quick Start Guide', formats['section_header'])
        ws.set_row(row, LAYOUT['section_header_height'])
        row += 1

        ws.merge_range(row, 0, row, 4, 'How it works', formats['box_header'])
        ws.set_row(row, 22)
        row += 1

        texts = [
            f"Each row = 1 record (matched by: {', '.join(unique_cols)}). Records that only exist in one system are marked as 'new' or 'deleted'.",
            f"Main columns show values from {source} (these are the proposed updates).",
            f"The 'changed_values' column shows the current {target} values that will be replaced."
        ]

        for text in texts:
            ws.set_row(row, 30 if text == texts[0] else 25)
            ws.merge_range(row, 0, row, 4, text, formats['box_text'])
            row += 1
        return row

    def _write_change_types(
        self,
        ws: 'xlsxwriter.Worksheet',
        formats: Dict[str, Any],
        row: int,
        source: str,
        target: str
    ) -> int:
        """
        Explains what NEW, EDITED, and DELETED mean in the comparison.

        Users need to understand the change_type values they'll see in the data.
        """
        ws.write(row, 0, 'Understanding the Change Types', formats['section_header'])
        ws.set_row(row, LAYOUT['section_header_height'])
        row += 1

        types = [
            ("NEW", f"Only exists in {source}. We propose to create this in {target}."),
            ("EDITED / UPDATED", f"Exists in both systems but values differ. {source} value is in the row, {target} value is in 'changed_values'."),
            ("DELETED", f"Only exists in {target}, not in {source} anymore.")
        ]

        for label, desc in types:
            height = 35 if label == "EDITED / UPDATED" else 30
            ws.set_row(row, height)
            ws.write(row, 0, label, formats['change_type_label'])
            ws.merge_range(row, 1, row, 4, desc, formats['change_type_text'])
            row += 1
        return row

    def _write_example(
        self,
        ws: 'xlsxwriter.Worksheet',
        formats: Dict[str, Any],
        row: int,
        source: str,
        target: str
    ) -> int:
        """
        Shows a concrete example of what an "edited" record looks like.

        Helps users understand the data format before reviewing actual records.
        """
        ws.write(row, 0, 'Example', formats['section_header'])
        ws.set_row(row, LAYOUT['section_header_height'])
        row += 1

        ws.set_row(row, 25)
        headers = ['Name', 'Change Type', f'Changed Values (from {target})']
        ws.write(row, 0, headers[0], formats['example_header'])
        ws.write(row, 1, headers[1], formats['example_header'])
        ws.merge_range(row, 2, row, 4, headers[2], formats['example_header'])
        row += 1

        ws.set_row(row, 25)
        ws.write(row, 0, 'Ruben', formats['example_cell'])
        ws.write(row, 1, 'edited', formats['example_cell'])
        ws.merge_range(row, 2, row, 4, "{'name': 'Robin'}", formats['example_cell'])
        row += 1

        ws.set_row(row, 30)
        ws.merge_range(row, 0, row, 4,
                       f"What this means: {target} currently has 'Robin' as the name. {source} has 'Ruben'. The row is marked as 'edited' because these values differ.",
                       formats['small_text'])
        return row + 1

    def _write_actions(
        self,
        ws: 'xlsxwriter.Worksheet',
        formats: Dict[str, Any],
        row: int,
        sheetname: str,
        source: str,
        target: str
    ) -> int:
        """
        Writes numbered action items telling users what to do with the comparison data.

        Guides users through the review process step-by-step.
        """
        ws.write(row, 0, 'What You Need to Do', formats['section_header'])
        ws.set_row(row, LAYOUT['section_header_height'])
        row += 1

        actions = [
            f"Go to the '{sheetname}' sheet and filter by 'change_type' to focus on specific change types.",
            f"For 'edited' records: Compare the {source} value with the 'changed_values' column to verify the update is correct.",
            f"For 'deleted' records: Confirm with HR/payroll policy before removing these from {target}.",
            "For 'new' records: Review to ensure these should be created in the target system."
        ]

        for i, action in enumerate(actions, 1):
            height = 35 if i in [2, 3] else 30
            ws.set_row(row, height)
            ws.write(row, 0, f"{i}.", formats['action_number'])
            ws.merge_range(row, 1, row, 4, action, formats['action_text'])
            row += 1
        return row

    def _write_tech_details(
        self,
        ws: 'xlsxwriter.Worksheet',
        formats: Dict[str, Any],
        row: int,
        name: str,
        unique: List[str],
        fields: List[str],
        checked: List[str]
    ) -> int:
        """
        Writes technical configuration details at the bottom of the Explanation sheet.

        Helps developers and support troubleshoot issues by showing how the comparison was configured.
        """
        ws.write(row, 0, 'Technical / configuration details', formats['section_header'])
        ws.set_row(row, LAYOUT['section_header_height'])
        row += 1

        ws.merge_range(row, 0, row, 4, 'Scenario configuration', formats['tech_header'])
        ws.set_row(row, 22)
        row += 1

        details = [
            (f"Scenario name:", name),
            (f"All target fields ({len(fields)}):", ", ".join(fields)),
            (f"Checked columns ({len(checked)}):", ", ".join(checked)),
            (f"Unique columns (used for matching) ({len(unique)}):", ", ".join(unique))
        ]

        for label, val in details:
            ws.set_row(row, 20)
            ws.write(row, 0, label, formats['tech_text'])
            if label == "Scenario name:":
                 ws.merge_range(row, 1, row, 4, val, formats['tech_text'])
                 row += 1
            else:
                row += 1
                text_len = len(val)
                height = max(25, (text_len // 100 + 1) * 15)
                ws.set_row(row, height)
                ws.merge_range(row, 0, row, 4, val, formats['tech_text_small'])
                row += 1
        return row


class ValidationReportGenerator:
    """
    Handles creation of Validation Reports.

    EXCEL FILE STRUCTURE:
    =====================
    Sheet 1: "Explanation"
    ├── Title: "Source System Data Validation Report"
    ├── Table of Contents: Lists all scenario sheets
    └── Overview Table: Summary of data coverage per scenario

    Sheet 2: "Value Mappings"
    └── Lists all fields that have value mappings (e.g., "Yes" → "1")

    Sheet 3+: One sheet per scenario (e.g., "Personal")
    ├── Summary Data Audit (top section)
    │   ├── Table: Missing values per column
    │   └── Chart: Visual bar chart of missing values
    └── Detailed Audit (bottom section)
        └── Table: Complete statistics for every column
    """

    def create_report(
        self,
        system_type: str,
        all_scenario_stats: Dict[str, Dict[str, Any]],
        output_path: str
    ) -> None:
        """
        Creates a Validation Report Excel file showing data quality and completeness.

        Shows data quality metrics:
        - Missing %: How much data is missing (0% = all present, 100% = all missing)
        - Missing Count: Number of empty/null values
        - Column statistics: Min, Max, Mean, etc. (for numeric columns)
        - Value mappings: What values exist in the data

        Args:
            system_type (str): Either 'Source' or 'Target' - which system's data to validate.
            all_scenario_stats (Dict[str, Dict[str, Any]]): Dictionary containing statistics for each scenario.
                Format: {'Personal': {'source_column_stats': {...}, 'source_total_rows': 100}, ...}
            output_path (str): Where to save the Excel file (e.g., "reports/validation.xlsx").
        """
        if not all_scenario_stats:
            return

        try:
            with pd.ExcelWriter(output_path, engine='xlsxwriter', mode='w') as writer:
                workbook = writer.book
                style = ScenarioReportStyle(workbook)

                self._create_explanation_sheet(workbook, writer, system_type, all_scenario_stats, style)
                self._create_value_mappings_sheet(workbook, writer, system_type, all_scenario_stats, style)

                for scenario_name, stats in all_scenario_stats.items():
                    key = 'source_column_stats' if system_type.lower() == 'source' else 'target_column_stats'
                    column_stats = stats.get(key, {})
                    if not column_stats: continue

                    df = self._column_stats_to_dataframe(column_stats)
                    if df.empty: continue

                    sheet_name = _truncate_sheet_name(scenario_name)
                    ws = workbook.add_worksheet(sheet_name)
                    writer.sheets[sheet_name] = ws

                    total_rows = stats.get(f"{system_type.lower()}_total_rows", 0)
                    self._format_scenario_worksheet(workbook, ws, df, scenario_name, total_rows, style)
        except Exception as e:
            raise RuntimeError(f"Failed to create validation report at {output_path}: {str(e)}") from e

    def _create_explanation_sheet(
        self,
        workbook: 'xlsxwriter.Workbook',
        writer: pd.ExcelWriter,
        system_type: str,
        stats: Dict[str, Any],
        style: ScenarioReportStyle
    ) -> None:
        """
        Creates the "Explanation" sheet with title, TOC, and overview table.

        This is the first sheet users see - it explains what's in the file and shows
        a coverage summary.
        """
        name = _truncate_sheet_name("Explanation")
        ws = workbook.add_worksheet(name)
        writer.sheets[name] = ws

        ws.set_column('A:A', 37)
        ws.set_column('B:B', 50)
        ws.set_column('C:C', 50)
        ws.set_column('D:E', 50)

        formats = style.common_formats

        ws.merge_range('A1:E1', f'{system_type} System Data Validation Report', formats['title'])
        ws.set_row(0, LAYOUT['title_row_height'])

        ws.merge_range('A2:C2',
                       f'This workbook shows data validation statistics for the {system_type.lower()} system. '
                       'Validation is performed per file, matching scenario fields to the best matching parquet files.',
                       formats['subtitle'])
        ws.set_row(1, 80) # Keep 80 for subtitle as in original

        row = 3
        ws.write(row, 0, "What's in this workbook?", formats['section_header'])
        ws.set_row(row, LAYOUT['section_header_height'])
        row += 1

        items = [("1. Explanation (this sheet)", "- How to read and use this validation report")]
        for i, s_name in enumerate(stats.keys(), 2):
            items.append((f"{i}. {_truncate_sheet_name(s_name)}", f"- Column statistics for {s_name} scenario"))

        for title, desc in items:
            ws.set_row(row, 25)
            ws.write(row, 0, title, formats['toc'])
            ws.write(row, 1, desc, formats['toc'])
            row += 1

        row += 1
        self._write_overview_table(ws, workbook, row, stats, system_type, style)
        ws.freeze_panes(3, 0)

    def _write_overview_table(
        self,
        ws: 'xlsxwriter.Worksheet',
        wb: 'xlsxwriter.Workbook',
        row: int,
        stats: Dict[str, Any],
        system_type: str,
        style: ScenarioReportStyle
    ) -> None:
        """
        Writes the "At a glance" coverage table and chart in the Explanation sheet.

        Shows data completeness summary before users dive into detailed scenario sheets.
        """
        ws.set_column('B:B', 53)
        overview = self._build_overview(stats, system_type)
        if not overview: return

        ws.write(row, 0, 'At a glance: coverage per scenario', style.common_formats['section_header'])
        ws.set_row(row, LAYOUT['section_header_height'])
        row += 1

        headers = ['Scenario', 'Columns checked', 'Available', 'Missing', 'Completeness']
        header_fmt = wb.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D9E1F2', 'border': 1, 'align': 'center'})

        for i, h in enumerate(headers):
            ws.write(row, i, h, header_fmt)

        data_start = row + 1
        cell_fmt = wb.add_format({'text_wrap': True, 'valign': 'top', 'border': 1, 'font_size': 12})
        num_fmt = wb.add_format({'text_wrap': True, 'valign': 'top', 'border': 1, 'num_format': '0', 'align': 'right'})
        pct_fmt = wb.add_format({'text_wrap': True, 'valign': 'top', 'border': 1, 'num_format': '0%', 'align': 'right'})

        for i, item in enumerate(overview):
            r = data_start + i
            ws.write(r, 0, item['scenario'], cell_fmt)
            ws.write_number(r, 1, item['expected_columns'], num_fmt)
            ws.write_number(r, 2, item['available_columns'], num_fmt)
            ws.write_number(r, 3, item['missing_columns'], num_fmt)
            ws.write_number(r, 4, item['completeness'], pct_fmt)

        data_end = data_start + len(overview) - 1
        ws.conditional_format(data_start, 4, data_end, 4, {'type': '3_color_scale', 'min_color': '#E74C3C', 'mid_color': '#FFEB84', 'max_color': '#5CB85C'})

        chart = wb.add_chart({'type': 'column'})
        chart.add_series({
            'name': 'Completeness',
            'categories': [ws.name, data_start, 0, data_end, 0],
            'values': [ws.name, data_start, 4, data_end, 4],
            'fill': {'color': EXCEL_COLORS['chart_fill']},
            'data_labels': {'value': True, 'num_format': '0%'}
        })
        chart.set_title({'name': 'Data coverage per scenario'})
        chart.set_y_axis({'num_format': '0%', 'major_gridlines': {'visible': False}})
        chart.set_legend({'position': 'none'})
        ws.insert_chart(data_start, 6, chart)

    def _create_value_mappings_sheet(
        self,
        wb: 'xlsxwriter.Workbook',
        writer: pd.ExcelWriter,
        system_type: str,
        stats: Dict[str, Any],
        style: ScenarioReportStyle
    ) -> None:
        """
        Creates a sheet listing all fields with value mappings and their possible values.

        Users need to see what values exist before creating mappings (e.g., "Yes" → "1").
        """
        name = _truncate_sheet_name("Value Mappings")
        ws = wb.add_worksheet(name)
        writer.sheets[name] = ws

        rows = []
        for s_name, s_stats in stats.items():
            key = 'source_column_stats' if system_type.lower() == 'source' else 'target_column_stats'
            for col, cstats in s_stats.get(key, {}).items():
                if cstats.get('has_value_mappings'):
                    top = cstats.get('top_value_counts', {})
                    val_str = '\n'.join([f"{v} ({c})" for v, c in top.items()]) if top else 'No values found'
                    rows.append({
                        'Scenario': s_name, 'Column': col,
                        'Source File': cstats.get('source_file', 'N/A'),
                        'System Type': cstats.get('system_type', 'N/A'),
                        'Total Unique Values': len(top) if top else 0,
                        'All Values (with counts)': val_str
                    })

        headers = ['Scenario', 'Column', 'Source File', 'System Type', 'Total Unique Values', 'All Values (with counts)']
        for i, h in enumerate(headers):
            ws.write(0, i, h, style.header_format)

        if not rows:
            ws.write(1, 0, 'No fields with value mappings found')
        else:
            df = pd.DataFrame(rows)[headers]
            for r in range(len(df)):
                for c in range(len(headers)):
                    ws.write(r + 1, c, df.iloc[r, c], style.data_format)

        ws.set_column(0, 0, 20)
        ws.set_column(1, 1, 30)
        ws.set_column(5, 5, 60)
        ws.freeze_panes(1, 0)

    def _format_scenario_worksheet(
        self,
        wb: 'xlsxwriter.Workbook',
        ws: 'xlsxwriter.Worksheet',
        df: pd.DataFrame,
        name: str,
        total_rows: int,
        style: ScenarioReportStyle
    ) -> None:
        """
        Creates a scenario sheet with summary table (top) and detailed stats table (bottom).

        One sheet is created per scenario showing all column statistics.
        """
        row = 0
        ws.write(row, 0, 'Summary Data Audit', style.common_formats['title'])
        ws.merge_range(row, 0, row, 4, 'Summary Data Audit', style.common_formats['title'])
        row += 2

        summary = self._prepare_summary(df, total_rows)
        self._write_summary_table(ws, wb, row, summary, style)

        end_row = row + len(summary)
        if summary:
            self._insert_chart(ws, wb, row, end_row, summary, name, total_rows)
            row += max(20, len(summary) + 5)
        else:
            row += 3

        self._write_audit_table(ws, wb, row, df, style)

    def _prepare_summary(
        self,
        df: pd.DataFrame,
        total_rows: int
    ) -> List[Dict[str, Any]]:
        """
        Extracts missing value statistics and sorts by missing count (worst first).

        Used to create the summary table at the top of scenario sheets.
        """
        data = []
        for _, row in df.iterrows():
            miss_count = row.get(MAGIC_STRINGS['missing_count'], 0)
            if pd.notna(miss_count) and isinstance(miss_count, (int, float)) and miss_count >= 0:
                data.append({
                    'label': row.get('Label') or row.get('Column', 'N/A'),
                    'missing_count': int(miss_count),
                    'missing_percent': row.get(MAGIC_STRINGS['missing_percent'], '0.00%'),
                    'total_rows': row.get('Total Rows in File') or total_rows
                })
        return sorted(data, key=lambda x: x['missing_count'], reverse=True)

    def _write_summary_table(
        self,
        ws: 'xlsxwriter.Worksheet',
        wb: 'xlsxwriter.Workbook',
        row: int,
        data: List[Dict[str, Any]],
        style: ScenarioReportStyle
    ) -> None:
        """
        Writes a 4-column table showing missing values per column.

        This is the top section of scenario sheets - a quick overview before the detailed stats.
        """
        headers = ['Label', 'Missing Count', 'Missing %', 'Total Rows']
        for i, h in enumerate(headers):
            ws.write(row, i, h, style.header_format)

        bg_alt = EXCEL_COLORS['alt_row_bg']
        fmts = {
            'n': {'base': wb.add_format({'text_wrap': True, 'valign': 'top', 'border': 1}),
                  'num': wb.add_format({'text_wrap': True, 'valign': 'top', 'border': 1, 'num_format': '0', 'align': 'right'}),
                  'pct': wb.add_format({'text_wrap': True, 'valign': 'top', 'border': 1, 'num_format': '0.00%', 'align': 'right'})},
            'a': {'base': wb.add_format({'text_wrap': True, 'valign': 'top', 'border': 1, 'bg_color': bg_alt}),
                  'num': wb.add_format({'text_wrap': True, 'valign': 'top', 'border': 1, 'num_format': '0', 'align': 'right', 'bg_color': bg_alt}),
                  'pct': wb.add_format({'text_wrap': True, 'valign': 'top', 'border': 1, 'num_format': '0.00%', 'align': 'right', 'bg_color': bg_alt})}
        }

        for i, d in enumerate(data):
            f = fmts['a'] if (i % 2 != 0) else fmts['n']
            r = row + 1 + i
            ws.write(r, 0, d['label'], f['base'])
            ws.write_number(r, 1, d['missing_count'], f['num'])

            pct = _parse_percentage_value(d['missing_percent'])
            if pct is not None: ws.write_number(r, 2, pct / 100, f['pct'])
            else: ws.write(r, 2, d['missing_percent'], f['base'])

            ws.write_number(r, 3, d['total_rows'], f['num']) if d['total_rows'] else ws.write(r, 3, 'N/A', f['base'])

    def _insert_chart(
        self,
        ws: 'xlsxwriter.Worksheet',
        wb: 'xlsxwriter.Workbook',
        start: int,
        end: int,
        data: List[Dict[str, Any]],
        name: str,
        total: int
    ) -> None:
        """
        Inserts a bar chart visualizing missing values next to the summary table.

        Visual representation makes it easier to spot columns with the most missing data.
        """
        chart = wb.add_chart({'type': 'bar'})
        chart.add_series({
            'name': 'Missing Count',
            'categories': [ws.name, start + 1, 0, start + len(data), 0],
            'values': [ws.name, start + 1, 1, start + len(data), 1],
            'fill': {'color': EXCEL_COLORS['chart_missing_fill']},
            'data_labels': {'value': True, 'num_format': '0', 'position': 'outside_end'}
        })
        chart.set_title({'name': f'Missing values per column - {name}'})
        chart.set_x_axis({'major_gridlines': {'visible': True}, 'min': 0, 'max': total if total > 0 else None})
        chart.set_y_axis({'reverse': True})
        chart.set_legend({'position': 'none'})
        chart.set_size({'width': 720, 'height': max(300, len(data) * 20)})
        ws.insert_chart(start + 1, 1, chart)

    def _write_audit_table(
        self,
        ws: 'xlsxwriter.Worksheet',
        wb: 'xlsxwriter.Workbook',
        row: int,
        df: pd.DataFrame,
        style: ScenarioReportStyle
    ) -> None:
        """
        Writes the comprehensive statistics table for every column.

        This is the bottom section of scenario sheets - a complete view of all column statistics.
        """
        ws.write(row, 0, 'Detailed Audit', style.common_formats['title'])
        ws.merge_range(row, 0, row, len(df.columns) - 1, 'Detailed Audit', style.common_formats['title'])
        row += 2

        for i, c in enumerate(df.columns):
            ws.write(row, i, c, style.header_format)
        row += 1

        start_row = row
        for i, (idx, r) in enumerate(df.iterrows()):
            bg = EXCEL_COLORS['alt_row_bg'] if i % 2 != 0 else '#FFFFFF'
            is_miss = r.get(MAGIC_STRINGS['status']) == MAGIC_STRINGS['missing_entirely']

            for j, c in enumerate(df.columns):
                val = r[c]
                fmt = style.get_audit_cell_format(c, val, is_miss, bg)

                disp = "Yes" if isinstance(val, bool) and val and c in [MAGIC_STRINGS['required'], MAGIC_STRINGS['unique'], MAGIC_STRINGS['has_value_mappings']] else ("No" if isinstance(val, bool) and c in [MAGIC_STRINGS['required'], MAGIC_STRINGS['unique'], MAGIC_STRINGS['has_value_mappings']] else val)

                if c == MAGIC_STRINGS['missing_percent']:
                    p = _parse_percentage_value(val)
                    if p is not None:
                        ws.write_number(row, j, p / 100, fmt)
                        continue

                if pd.isna(disp): ws.write(row, j, '', fmt)
                else: ws.write(row, j, disp, fmt)
            row += 1

        # Auto-filter
        ws.autofilter(start_row - 1, 0, row - 1, len(df.columns) - 1)

        # Format columns widths
        for i, col in enumerate(df.columns):
            l = max(df[col].astype(str).str.len().max() if not df.empty else 0, len(str(col)))
            ws.set_column(i, i, min(max(l + 2, 10), 50))

        # Conditional formatting
        if MAGIC_STRINGS['missing_percent'] in df.columns:
            idx = df.columns.get_loc(MAGIC_STRINGS['missing_percent'])
            letter = chr(65 + idx) # simplistic for < 26 cols, better use util if needed
            first = start_row + 1
            for color, min_v, max_v, exact in BAND_COLORS:
                f = wb.add_format({'bg_color': color, 'text_wrap': True, 'valign': 'top', 'border': 1})
                if exact:
                    ws.conditional_format(start_row, idx, row - 1, idx, {'type': 'cell', 'criteria': '==', 'value': 0, 'format': f})
                else:
                    crit = f'=AND({letter}{first}>{min_v},{letter}{first}<={max_v})'
                    ws.conditional_format(start_row, idx, row - 1, idx, {'type': 'formula', 'criteria': crit, 'format': f})

    def _column_stats_to_dataframe(
        self,
        stats: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Converts nested statistics dictionary into a flat DataFrame for Excel.

        Excel tables need flat data (rows/columns), not nested dictionaries.
        """
        if not stats: return pd.DataFrame()
        rows = []
        for col, s in stats.items():
            row = {
                'Column': col,
                'Label': s.get('label_en') or s.get('label_nl') or 'N/A',
                'Scenarios': s.get('scenarios', 'N/A'),
                MAGIC_STRINGS['missing_percent']: s.get('missing_percent', '100.00%'),
                MAGIC_STRINGS['missing_count']: s.get('missing_count', 0) if s.get('status') != MAGIC_STRINGS['missing_entirely'] else None,
                'Source File': s.get('source_file', 'N/A'),
                'System Type': s.get('system_type', 'N/A'),
                MAGIC_STRINGS['required']: s.get('required', False),
                MAGIC_STRINGS['unique']: s.get('unique', False),
                'Dtype': s.get('dtype', 'N/A') if s.get('status') != MAGIC_STRINGS['missing_entirely'] else 'N/A',
                'Unique Count': s.get('unique_count', 'N/A'),
                MAGIC_STRINGS['has_value_mappings']: s.get('has_value_mappings', False),
                'Total Rows in File': s.get('total_rows_in_file', None),
                MAGIC_STRINGS['status']: s.get('status')
            }

            top = s.get('top_value_counts', {})
            row['Top Value Counts'] = ', '.join([f"'{k}': {v}" for k, v in top.items()]) if top else ('N/A' if s.get('status') != MAGIC_STRINGS['missing_entirely'] else 'COLUMN NOT FOUND')

            desc = s.get('descriptive_stats', {})
            if desc:
                if 'unique_dates' in desc:
                     row['Unique Dates'] = desc.get('unique_dates')
                     row['Min Date'] = str(desc.get('min'))
                     row['Max Date'] = str(desc.get('max'))
                elif 'min_length' in desc:
                     row['Min Length'] = desc.get('min_length')
                     row['Max Length'] = desc.get('max_length')
                     row['Mean Length'] = round(desc.get('mean_length', 0), 2) if desc.get('mean_length') else None
                else:
                    m = {'min': 'Min', 'max': 'Max', 'mean': 'Mean', 'std': 'Std Dev', '25%': '25th Percentile', '50%': '50th Percentile', '75%': '75th Percentile'}
                    for k, v in m.items():
                        val = desc.get(k)
                        if val is not None: row[v] = round(val, 2) if isinstance(val, float) else val
            rows.append(row)

        df = pd.DataFrame(rows)
        cols = ['Column', 'Label', 'Scenarios', MAGIC_STRINGS['missing_percent'], MAGIC_STRINGS['missing_count'],
                'Source File', 'System Type', MAGIC_STRINGS['required'], MAGIC_STRINGS['unique'], 'Dtype',
                'Unique Count', MAGIC_STRINGS['has_value_mappings'], 'Top Value Counts', 'Min', 'Max', 'Mean',
                'Std Dev', '25th Percentile', '50th Percentile', '75th Percentile', 'Min Date', 'Max Date',
                'Unique Dates', 'Min Length', 'Max Length', 'Mean Length', 'Std Length', 'Total Rows in File',
                MAGIC_STRINGS['status']]
        for c in cols:
            if c not in df.columns: df[c] = None
        return df[cols]

    def _build_overview(
        self,
        stats: Dict[str, Any],
        system_type: str
    ) -> List[Dict[str, Any]]:
        """
        Calculates high-level coverage statistics per scenario.

        Used for the "At a glance" overview table in the Explanation sheet.
        """
        rows = []
        for s_name, s in stats.items():
            c_stats = s.get(f"{system_type.lower()}_column_stats", {})
            exp = len(s.get(f"columns_checked_{system_type.lower()}", []))
            avail = sum(1 for c in c_stats.values() if c.get("status") != MAGIC_STRINGS['missing_entirely'])
            rows.append({
                "scenario": s_name, "expected_columns": exp, "available_columns": avail,
                "missing_columns": max(exp - avail, 0),
                "completeness": avail / exp if exp > 0 else 0.0
            })
        return rows


# =========================================================================
# FACADE CLASS
# =========================================================================

class ScenarioReportBuilder:
    """
    Creates Excel reports that show data differences and quality statistics.

    WHAT THIS CLASS DOES:
    =====================
    This class creates Excel files (.xlsx) that help people understand:
    1. What data changed between two systems (Comparison Reports)
    2. How complete and accurate the data is (Validation Reports)

    PROJECT CONTEXT:
    ================
    In this SDK project, we move data from one system (like "Bob") to another (like "Nmbrs").
    Before moving data, we need to:
    - Compare what's different (Comparison Reports)
    - Check data quality (Validation Reports)

    This class ONLY creates the Excel files - it doesn't transform or validate data.
    Other classes handle the data work; this class just makes it look nice in Excel.

    EXCEL FILE STRUCTURE:
    =====================

    COMPARISON REPORT (created by create_comparison_report):
    ---------------------------------------------------------
    Excel File: "comparison_scenario_Personal.xlsx"

    Sheet 1: "Explanation"
    ├── Title: "Bob → Nmbrs Data Comparison"
    ├── Table of Contents: Lists all sheets in the file
    ├── Quick Start Guide: How to read the comparison
    ├── Change Types: Explains NEW, EDITED, DELETED records
    ├── Example: Shows a sample change
    ├── Action Items: What the user needs to do
    └── Technical Details: Configuration info

    Sheet 2: "Comparison Personal" (main data)
    └── Shows all records with differences (NEW, EDITED, DELETED)

    Sheet 3: "Personal Bob transformed" (optional)
    └── Shows all source data after transformation

    Sheet 4: "Personal Nmbrs transformed" (optional)
    └── Shows all target data

    VALIDATION REPORT (created by create_validation_report):
    --------------------------------------------------------
    Excel File: "source_validation_report.xlsx" or "target_validation_report.xlsx"

    Sheet 1: "Explanation"
    ├── Title: "Source System Data Validation Report"
    ├── Table of Contents: Lists all scenario sheets
    └── Overview Table: Summary of data coverage per scenario

    Sheet 2: "Value Mappings"
    └── Lists all fields that have value mappings (e.g., "Yes" → "1")

    Sheet 3+: One sheet per scenario (e.g., "Personal")
    ├── Summary Data Audit (top section)
    │   ├── Table: Missing values per column
    │   └── Chart: Visual bar chart of missing values
    └── Detailed Audit (bottom section)
        └── Table: Complete statistics for every column

    CODE ORGANIZATION:
    ==================
    The code is organized to match the Excel structure:

    1. SHARED CONSTANTS & INITIALIZATION
       - Excel limits (sheet name length, column width)
       - Basic setup

    2. PUBLIC INTERFACE
       - create_comparison_report() → Creates Comparison Report Excel file
       - create_validation_report() → Creates Validation Report Excel file

    3. SHARED EXCEL FORMATTING HELPERS
       - _truncate_sheet_name() → Makes sheet names fit Excel's 31-char limit
       - _format_standard_worksheet() → Formats simple data tables

    4. COMPARISON REPORT SPECIFIC LOGIC
       - Creates the "Explanation" sheet for Comparison Reports
       - Each method writes one section (Title, TOC, Quick Start, etc.)

    5. VALIDATION REPORT SPECIFIC LOGIC
       - Creates the "Explanation" sheet for Validation Reports
       - Creates scenario sheets with summary and detailed tables

    Examples:
        >>> builder = ScenarioReportBuilder()
        >>> # Generate a comparison report
        >>> builder.create_comparison_report(
        ...     df_compare=diff_df,
        ...     filepath="comparison_report.xlsx",
        ...     sheetname="Personal Comparison",
        ...     source_system="Bob",
        ...     target_system="Nmbrs",
        ...     scenario_name="Personal",
        ...     unique_columns=["employee_id"],
        ...     all_target_fields=["employee_id", "first_name"],
        ...     cols_to_check=["first_name"]
        ... )
    """

    def __init__(self):
        """Initialize the ScenarioReportBuilder."""
        self.comparison_generator = ComparisonReportGenerator()
        self.validation_generator = ValidationReportGenerator()

    def create_comparison_report(
        self,
        df_compare: pd.DataFrame,
        filepath: str,
        sheetname: str,
        source_system: str,
        target_system: str,
        scenario_name: str,
        unique_columns: List[str],
        all_target_fields: List[str],
        cols_to_check: List[str],
        df_source: Optional[pd.DataFrame] = None,
        df_target: Optional[pd.DataFrame] = None
    ) -> None:
        """
        Creates a Comparison Report Excel file showing what changed between two systems.

        An Excel file with multiple sheets showing data differences. Used BEFORE moving
        data to see what will change. File structure:
        - Sheet 1: "Explanation" (instructions on how to read the comparison)
        - Sheet 2: Main comparison sheet (all differences with change_type column)
        - Sheet 3+: Optional source/target data sheets

        The main comparison sheet shows records with a "change_type" column:
        - NEW: Record exists in source but not in target (will be created)
        - EDITED: Record exists in both but values differ (will be updated)
        - DELETED: Record exists in target but not in source (will be removed)

        Args:
            df_compare (pd.DataFrame): The main comparison data - rows with differences. Must have a "change_type" column.
            filepath (str): Where to save the Excel file (e.g., "reports/comparison.xlsx").
            sheetname (str): Name for the main comparison sheet (e.g., "Comparison Personal").
            source_system (str): Name of the source system (e.g., "Bob", "Workday").
            target_system (str): Name of the target system (e.g., "Nmbrs", "Sage").
            scenario_name (str): Name of the scenario being compared (e.g., "Personal", "Salary").
            unique_columns (List[str]): Columns used to match records (e.g., ["employee_id"]).
            all_target_fields (List[str]): All fields that should exist in the target system.
            cols_to_check (List[str]): Fields that were compared for differences.
            df_source (Optional[pd.DataFrame]): Optional original source data (for reference sheet).
            df_target (Optional[pd.DataFrame]): Optional original target data (for reference sheet).

        Examples:
            >>> builder = ScenarioReportBuilder()
            >>> builder.create_comparison_report(
            ...     df_compare=df_diff,
            ...     filepath="report.xlsx",
            ...     sheetname="Diffs",
            ...     source_system="Source",
            ...     target_system="Target",
            ...     scenario_name="Example",
            ...     unique_columns=["id"],
            ...     all_target_fields=["id", "name"],
            ...     cols_to_check=["name"]
            ... )
        """
        self.comparison_generator.create_report(
            df_compare=df_compare,
            filepath=filepath,
            sheetname=sheetname,
            source_system=source_system,
            target_system=target_system,
            scenario_name=scenario_name,
            unique_columns=unique_columns,
            all_target_fields=all_target_fields,
            cols_to_check=cols_to_check,
            df_source=df_source,
            df_target=df_target
        )

    def create_validation_report(
        self,
        system_type: str,
        all_scenario_stats: Dict[str, Dict[str, Any]],
        output_path: str
    ) -> None:
        """
        Creates a Validation Report Excel file showing data quality and completeness.

        An Excel file showing how complete and accurate the data is. Used to check data
        quality BEFORE moving it. File structure:
        - Sheet 1: "Explanation" (title, TOC, overview table)
        - Sheet 2: "Value Mappings" (lists all mapped values)
        - Sheet 3+: One sheet per scenario with summary table (top) and detailed stats (bottom)

        Shows data quality metrics:
        - Missing %: How much data is missing (0% = all present, 100% = all missing)
        - Missing Count: Number of empty/null values
        - Column statistics: Min, Max, Mean, etc. (for numeric columns)
        - Value mappings: What values exist in the data

        Args:
            system_type (str): Either 'Source' or 'Target' - which system's data to validate.
            all_scenario_stats (Dict[str, Dict[str, Any]]): Dictionary containing statistics for each scenario.
                Format: {'Personal': {'source_column_stats': {...}, 'source_total_rows': 100}, ...}
            output_path (str): Where to save the Excel file (e.g., "reports/validation.xlsx").

        Examples:
            >>> builder = ScenarioReportBuilder()
            >>> stats = {'Personal': {'source_column_stats': {...}, 'source_total_rows': 100}}
            >>> builder.create_validation_report('Source', stats, 'validation_report.xlsx')
        """
        self.validation_generator.create_report(
            system_type=system_type,
            all_scenario_stats=all_scenario_stats,
            output_path=output_path
        )
