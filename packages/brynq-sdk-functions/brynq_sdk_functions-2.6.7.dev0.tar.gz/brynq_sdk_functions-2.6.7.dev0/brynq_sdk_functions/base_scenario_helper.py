import os
import re
import pandas as pd
import numpy as np
from typing import List, Optional, Literal, Union, TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from brynq_sdk_brynq import BrynQ
    from brynq_sdk_brynq.brynq_sdk_brynq.schemas.scenarios import ParsedScenario
    from brynq_sdk_task_scheduler import TaskScheduler


from .functions import Functions
# from .scenario_report_builder import ScenarioReportBuilder in other PR

class BaseScenarioHelper():
    """
    Base helper class for source-to-target ETL integration for a scenario. basic 'do and log' actions can be performed using this baseclass.

    This class provides common functionality for data transformation, cleaning, comparison,
    and logging that is shared across all scenario-specific helper classes. Each scenario
    helper (e.g., Personal, Address, Salary) inherits from this base class to leverage
    standardized data processing methods.

    Key Features:
        - Data cleaning and validation (missing values, duplicates, formatting)
        - Data comparison between source and target systems
        - Excel report generation for change tracking, seeing transformed data.
        - Structured logging with scenario-specific prefixes
        - Date and decimal field normalization

    Logging System:
        All log messages are automatically prefixed with the scenario name (e.g., [Personal])
        to provide context. The logging system uses two levels:
        - DEBUG: Technical details for developers (column names, counts, percentages)
        - INFO: Business-friendly messages for HR/payroll users (human-readable explanations)
        Messages use proper English grammar and formatting for clarity.

    Usage:
        Child classes should set the following attributes in their __init__:
        - scenario_name: Name of the scenario (e.g., "Personal", "Address")
        - scenario: Scenario object from the scenario SDK
        - unique_columns: List of columns used for matching records
        - required_columns: List of columns that must be present

    Example:
        >>> from brynq_sdk_brynq import Brynq
        >>>
        >>> # Initialize Brynq client
        >>> client = Brynq(credentials=your_credentials)
        >>>
        >>> # Create a custom scenario helper
        >>> class Personal(BaseScenarioHelper):
        ...     \"\"\"
        ...     This class is responsible for transforming and comparing person data between Source and Target.
        ...     \"\"\"
        ...
        ...     def __init__(self, parent):
        ...         super().__init__(parent)
        ...         self.scenario_name = 'Personal'
        ...         self.scenario = self.parent.scenarios[self.scenario_name]
        ...         self.unique_columns = [col for col in self.scenario.target.unique_fields
        ...                               if col in self.scenario.all_target_fields]
        ...         self.required_columns = [col for col in self.scenario.target.required_fields
        ...                                  if col in self.scenario.all_target_fields]
    """

    MISSING_VALUES: List[str] = [
        '<NA>', 'nan', 'None', 'NaN', 'null', 'NaT', '_NA_', '', r'\[\]', r'\{ \}'
    ]

    def __init__(self, parent: Union['BrynQ', 'TaskScheduler']) -> None:
        """
        Args:
            parent: Parent class (Initialised Brynq object in the main code)
        """
        self.parent: Union[BrynQ, TaskScheduler] = parent
        self.missing_values: List[str] = self.MISSING_VALUES
        # To be set by child classes
        self.scenario_name: Optional[str] = None
        self.scenario: Optional[ParsedScenario] = None
        self.unique_columns: List[str] = []
        self.required_columns: List[str] = []
        self.system_type: Optional[Literal['source', 'target']] = None
        self._last_cleaned_types: Optional[Dict[str, Any]] = None
        self.cols_to_check: List[str] = []

    def log_with_prefix(self, message: str, loglevel: str = 'INFO') -> None:
        """
        Log a message with scenario name prefix.

        Args:
            message: The log message
            loglevel: Log level (DEBUG, INFO, ERROR)

        Example:
            >>> helper.log_with_prefix('Processing employee data', 'INFO')
            [SCENARIO (source) | INFO] Processing employee data
        """
        if self.scenario_name:
            if self.system_type:
                prefixed_message = f"[{self.scenario_name} ({self.system_type}) | {loglevel}] {message}"
            else:
                prefixed_message = f"[{self.scenario_name} | {loglevel}] {message}"
        else:
            prefixed_message = f"[{loglevel}] {message}"
        self.parent.write_execution_log(prefixed_message, loglevel=loglevel)

    def get_empty_target_dataframe(self, unique_key: bool = True) -> pd.DataFrame:
        """
        Return an empty DataFrame with the correct target field columns for the scenario.

        Returns:
            Empty DataFrame with all target fields as columns

        This method is useful when a transformation results in an empty DataFrame
        but the downstream code expects specific column names.

        Raises:
            ValueError: If scenario is not initialized. Set self.scenario in __init__ before using this method.
        """
        if not self.scenario:
            raise ValueError(
                "Scenario must be initialized before using get_empty_target_dataframe(). "
                "Set self.scenario in your helper class."
            )

        # Create empty DataFrame with target field columns
        target_fields = list(self.scenario.all_target_fields)
        if unique_key and "unique_key" not in target_fields:
            target_fields.append("unique_key")
        return pd.DataFrame(columns=target_fields)

    def _get_column_display_string(self, columns: List[str]) -> str:
        """
        Get human-readable display string for a list of columns.

        Args:
            columns: List of column names

        Returns:
            Formatted string joining column labels or names (e.g. "Name and Age")
        """
        column_labels = []
        for col in columns:
            if self.scenario and col in self.scenario.field_properties:
                label = self.scenario.field_properties[col].label
                column_labels.append(label if label else col)
            else:
                column_labels.append(col)

        if len(column_labels) == 1:
            return column_labels[0]
        elif len(column_labels) == 2:
            return f"{column_labels[0]} and {column_labels[1]}"
        else:
            return f"{', '.join(column_labels[:-1])} and {column_labels[-1]}"

    def drop_missing_and_log(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Remove rows with missing values in essential columns because records without
        required fields (like unique identifiers) can't be properly processed or merged.

        Typically called for unique/required fields that are critical for data integrity.
        Missing values are standardized to pd.NA before dropping so all missing value
        formats are detected consistently.

        Args:
            df: DataFrame to drop missing values from
            columns: List of column names to check for missing values

        Returns:
            DataFrame with rows containing missing values in specified columns removed

        Logging Setup:
        This method generates two types of log messages:

        DEBUG logs (for developers):
        - Detailed technical information with column names and percentages
        - Example: "[Employee (ZENEGY) | DEBUG] Missing values in columns: employee_number: 1 (11.1%) at line: 100"
        - Example: "[Employee (ZENEGY) | DEBUG] Dropped 1 rows out of 9 due to missing values in columns: employee_number at line: 100"

        INFO logs (for HR/business users):
        - Human-friendly messages explaining business impact
        - Uses human-readable labels and proper English formatting (A, B and C)
        - Example: "[Employee (ZENEGY) | INFO] 1 out of 9 records were removed because essential information (Employee Number) was missing. at line: 100"

        Examples
        --------
        >>> df = pd.DataFrame({
        ...     'employee_id': [1, 2, None, 4],
        ...     'employee_number': ['E001', None, 'E003', 'E004'],
        ...     'name': ['Alice', 'Bob', 'Charlie', 'David']
        ... })
        >>> df_cleaned = helper.drop_missing_and_log(df, columns=['employee_number'])
        [Employee (ZENEGY) | DEBUG] Missing values in columns: employee_number: 1 (25.0%)
        [Employee (ZENEGY) | DEBUG] Dropped 1 rows out of 4 due to missing values in columns: employee_number
        [Employee (ZENEGY) | INFO] 1 out of 4 records were removed because essential information (Employee Number) was missing.
        >>> df_cleaned
           employee_id employee_number      name
        0          1.0           E001     Alice
        2          NaN           E003   Charlie
        3          4.0           E004     David
        """
        if df.empty:
            self.log_with_prefix("Empty DataFrame in drop_missing_and_log, returning as-is", loglevel='DEBUG')
            return df
        if not columns:
            raise ValueError("Columns list cannot be empty. Provide at least one column name to check for missing values.")
        if not self.scenario:
            raise ValueError("Scenario must be initialized before using drop_missing_and_log(). Set self.scenario in your helper class.")
        initial_count = len(df)
        df_cleaned = df.copy()

        # Count missing values BEFORE cleaning so we can log what was originally missing.
        missing_report = []
        for col in columns:
            if col in df_cleaned.columns:
                # Use .values to ensure we only count column values, not index
                col_values = df_cleaned[col].values
                isna_count = int(pd.isna(col_values).sum())
                string_missing_count = sum(int((col_values == val).sum()) for val in self.missing_values)
                missing_count = isna_count + string_missing_count
                missing_pct = (missing_count / initial_count * 100) if initial_count > 0 else 0
                if missing_count > 0:
                    missing_report.append(f"{col}: {missing_count} ({missing_pct:.1f}%)")
                df_cleaned[col] = df_cleaned[col].replace(self.missing_values, pd.NA)

        # Drop rows AFTER standardizing to pd.NA
        df_dropped = df_cleaned.dropna(subset=columns, how='any')
        final_count = len(df_dropped)
        dropped_count = initial_count - final_count

        if missing_report:
            self.log_with_prefix(f"Missing values in columns: {', '.join(missing_report)}", loglevel='DEBUG')
        if dropped_count > 0:
            # DEBUG log uses raw column names for developers who need exact field references.
            self.log_with_prefix(f"Dropped {dropped_count} rows out of {initial_count} due to missing values in columns: {', '.join(columns)}", loglevel='DEBUG')
            # INFO log uses human-readable labels because pythonic field names (like "employee_id") aren't meaningful to business users.
            # Fall back to pythonic names if field has no label.
            columns_display = self._get_column_display_string(columns)
            self.log_with_prefix(f"{dropped_count} out of {initial_count} records were removed because essential information ({columns_display}) was missing.", loglevel='INFO')

        return df_dropped

    def drop_duplicates_and_log(
        self,
        df: pd.DataFrame,
        subset: List[str],
        keep: Literal['first', 'last'] = 'first'
    ) -> pd.DataFrame:
        """
        Remove duplicate rows based on specified columns.

        Typically called for unique key columns to ensure each record is distinct.
        Rows are sorted BEFORE deduplication to prioritize rows with actual data over
        empty values, ensuring we keep the most complete record.

        Args:
            df: DataFrame to deduplicate
            subset: List of column names to check for duplicates
            keep: Which duplicate to keep ('first', 'last', or False to drop all)

        Returns:
            DataFrame with duplicates removed

        Logging Setup:
        This method generates two types of log messages:

        DEBUG logs (for developers):
        - Technical details about duplicate detection and removal
        - Uses raw column names for exact field references
        - Example: "[Employee (ZENEGY) | DEBUG] Found 8 duplicate rows (50.0%) based on columns: employee_number at line: 101"
        - Example: "[Employee (ZENEGY) | DEBUG] Removed 8 duplicate rows out of 16 based on columns: employee_number at line: 101"

        INFO logs (for HR/business users):
        - Business-friendly messages explaining data quality actions
        - Uses human-readable labels and proper English formatting (A, B and C)
        - Example: "[Employee (ZENEGY) | INFO] 8 employee records appeared more than once (same Employee Number and Social Security Number). Duplicates were reviewed and removed."

        Examples
        --------
        >>> df = pd.DataFrame({
        ...     'first_name': ['Alice', 'Alice', 'Bob', 'Alice', 'Charlie'],
        ...     'last_name': ['Smith', 'Jones', 'Smith', 'Smith', 'Brown'],
        ...     'department': ['HR', 'IT', 'HR', 'Finance', 'IT']
        ... })
        >>> df_deduplicated = helper.drop_duplicates_and_log(df, subset=['first_name', 'last_name'])
        [Employee (ZENEGY) | DEBUG] Found 1 duplicate rows (20.0%) based on columns: first_name, last_name
        [Employee (ZENEGY) | DEBUG] Removed 1 duplicate rows out of 5 based on columns: first_name, last_name
        [Employee (ZENEGY) | INFO] 1 employee record appeared more than once (same First Name and Last Name). Duplicates were reviewed and removed.
        >>> df_deduplicated
          first_name last_name department
        0      Alice     Smith         HR
        1      Alice     Jones         IT
        2        Bob     Smith         HR
        4    Charlie     Brown         IT
        """
        if df.empty:
            self.log_with_prefix("Empty DataFrame in drop_duplicates_and_log, returning as-is", loglevel='DEBUG')
            return df
        if not subset:
            raise ValueError("Subset list cannot be empty. Provide at least one column name to check for duplicates.")
        if not self.scenario:
            raise ValueError("Scenario must be initialized before using drop_duplicates_and_log(). Set self.scenario in your helper class.")

        # Sort BEFORE deduplication so we keep rows with actual data instead of empty strings.
        # This ensures the most complete record is preserved when duplicates exist.
        sort_col = [
            col for col in self.scenario.all_target_fields
            if (col in df.columns) and (col not in subset)
        ]
        df = df.sort_values(by=sort_col, ascending=False)
        initial_count = len(df)

        # Count duplicates BEFORE removal so we can log what was detected.
        duplicate_count = df.duplicated(subset=subset, keep='first').sum()
        duplicate_pct = (duplicate_count / initial_count * 100) if initial_count > 0 else 0

        if duplicate_count > 0:
            # DEBUG log uses raw column names for developers who need exact field references.
            self.log_with_prefix(f"Found {duplicate_count} duplicate rows ({duplicate_pct:.1f}%) based on columns: {', '.join(subset)}", loglevel='DEBUG')

        # Remove duplicates AFTER sorting so we keep the most complete record.
        df_deduplicated = df.drop_duplicates(subset=subset, keep=keep)

        final_count = len(df_deduplicated)
        removed_count = initial_count - final_count

        if removed_count > 0:
            # DEBUG log uses raw column names for developers who need exact field references.
            self.log_with_prefix(f"Removed {removed_count} duplicate rows out of {initial_count} based on columns: {', '.join(subset)}", loglevel='DEBUG')
            # INFO log uses human-readable labels because pythonic field names aren't meaningful to business users.
            # Fall back to pythonic names if field has no label.
            subset_display = self._get_column_display_string(subset)
            self.log_with_prefix(f"{removed_count} employee record{'s' if removed_count > 1 else ''} appeared more than once (same {subset_display}). Duplicates were reviewed and removed.", loglevel='INFO')
        else:
            # DEBUG log uses raw column names for developers who need exact field references.
            self.log_with_prefix(f"No duplicates found based on columns: {', '.join(subset)}", loglevel='DEBUG')

        # Sort by subset AFTER deduplication so the DataFrame is organized for debugging.
        df_deduplicated = df_deduplicated.sort_values(by=subset).reset_index(drop=True)

        return df_deduplicated

    def clean_dataframe(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Clean DataFrame values to strings and missing values to empty strings.

        Used before comparison operations (like compare_dataframes) because comparison functions
        expect all values as strings and handle empty values as ''.
        Converts all data types to strings, replaces NaN and custom missing values with empty strings,
        then sorts by the specified columns for easier debugging.

        Args:
            df: DataFrame to clean
            columns: List of column names to sort by

        Returns:
            DataFrame with all values as strings, missing values as '', sorted by columns
        """
        if df.empty:
            self.log_with_prefix("Empty DataFrame in clean_dataframe, returning as-is", loglevel='DEBUG')
            return df
        if not columns:
            raise ValueError("Columns list cannot be empty. Provide at least one column name to sort by.")

        # Store original types before conversion
        self._last_cleaned_types = df.dtypes.to_dict()

        df = df.astype(str)
        df = df.fillna('')
        df = df.replace(self.missing_values, '')
        df = df.sort_values(by=columns).reset_index(drop=True)
        return df

    def format_decimal_field(
        self,
        df: pd.DataFrame,
        field_name: str,
        decimal_places: Literal[0, 1, 2],
        decimal_delimiter: str = r'\.'
    ) -> pd.DataFrame:
        """
        Format numeric values as strings with consistent decimal precision.

        Used before df_compare to ensure decimals are consistent between systems.
        Different systems may represent the same numeric value differently (e.g., 1.0 vs 1.00 vs 1),
        which causes false differences in comparisons. This method standardizes all numeric values
        to strings with exact decimal places, preserving empty values as empty strings.

        Args:
            df: DataFrame containing the field
            field_name: Name of the field to format
            decimal_places: Number of decimal places (0, 1, or 2)
            decimal_delimiter: Regular expression pattern for decimal delimiter (default: r'\.' for period)

        Returns:
            Modified DataFrame with formatted field as strings

        Examples
        --------
        >>> df = pd.DataFrame({
        ...     'salary': [50000.0, 1234.567, 1000.0, None, 0.0]
        ... })
        >>> df_formatted = helper.format_decimal_field(df, 'salary', decimal_places=2)
        >>> df_formatted['salary']
        0    50000.00
        1     1234.57
        2     1000.00
        3
        4        0.00
        Name: salary, dtype: object

        Formatting with comma as decimal delimiter:

        >>> df_formatted = helper.format_decimal_field(df, 'salary', decimal_places=2, decimal_delimiter=r',')
        >>> df_formatted['salary']
        0    50000,00
        1     1234,57
        2     1000,00
        3
        4        0,00
        Name: salary, dtype: object
        """
        if df.empty:
            self.log_with_prefix("Empty DataFrame in format_decimal_field, returning as-is", loglevel='DEBUG')
            return df

        df = df.copy()

        if field_name not in df.columns:
            self.log_with_prefix(f"Field '{field_name}' not found in DataFrame, skipping format_decimal_field", loglevel='DEBUG')
            return df

        mask_empty = (df[field_name] == '') | (df[field_name].isna())    # Store empty values to restore later
        numeric_values = pd.to_numeric(df[field_name], errors='coerce')  # Convert to numeric to handle mixed types uniformly
        mask_numeric = numeric_values.notna()
        numeric_values = numeric_values.round(decimal_places)

        def format_numeric_value(val: int | float | str | None | pd._libs.missing.NAType):
            """
            Format a numeric value as a string with specified decimal precision.

            Args:
                val: Numeric value to format (float or NaN)

            Returns:
                Formatted string representation of the value, or empty string for NaN
            """
            if pd.isna(val):
                return ''
            if decimal_places == 0:
                return str(int(val))
            else:
                formatted = f"{float(val):.{decimal_places}f}"
                if decimal_delimiter != r'\.':
                    formatted = re.sub(r'\.', decimal_delimiter.replace('\\', ''), formatted)
                return formatted

        # Convert to object to allow mixed types (formatted strings + empty strings)
        df[field_name] = df[field_name].astype(object)
        df.loc[mask_numeric, field_name] = numeric_values.loc[mask_numeric].apply(format_numeric_value)

        # Use (1e-4) because floating-point precision errors prevent exact equality checks
        is_exactly_one = mask_numeric & (abs(numeric_values - 1.0) < 1e-4)
        is_exactly_zero = mask_numeric & (abs(numeric_values - 0.0) < 1e-4)

        if decimal_places == 0:
            one_str = "1"
            zero_str = "0"
        else:
            decimal_part = '0' * decimal_places
            if decimal_delimiter == r'\.':
                one_str = f"1.{decimal_part}"
                zero_str = f"0.{decimal_part}"
            else:
                delimiter = decimal_delimiter.replace('\\', '')
                one_str = f"1{delimiter}{decimal_part}"
                zero_str = f"0{delimiter}{decimal_part}"

        df.loc[is_exactly_one, field_name] = one_str
        df.loc[is_exactly_zero, field_name] = zero_str

        # Restore empty strings
        df.loc[mask_empty, field_name] = ''

        return df

    def format_date_field(self, df: pd.DataFrame, field_name: str | List[str]) -> pd.DataFrame:
        """
        Normalize date-like columns to ISO format yyyy-mm-dd.

        Used before df_compare to ensure dates are consistent between systems.
        Different systems may represent dates differently (e.g., "01/15/2024" vs "2024-01-15" vs Timestamp),
        which causes false differences in comparisons. This method standardizes all date values to ISO format
        strings, preserving empty values as empty strings.

        Args:
            df: DataFrame containing the date-like columns
            field_name: Name of the column(s) to normalize (single string or list of strings)

        Returns:
            DataFrame with the specified columns formatted as yyyy-mm-dd strings

        Examples
        --------
        >>> df = pd.DataFrame({
        ...     'hire_date': ['2024-01-15', '01/15/2024', '2024-01-15T10:30:00', None, pd.NaT]
        ... })
        >>> df_formatted = helper.format_date_field(df, 'hire_date')
        >>> df_formatted['hire_date']
        0    2024-01-15
        1    2024-01-15
        2    2024-01-15
        3
        4
        Name: hire_date, dtype: object
        """
        if df.empty:
            self.log_with_prefix("Empty DataFrame in format_date_field, returning as-is", loglevel='DEBUG')
            return df

        df = df.copy()

        if not field_name:
            raise ValueError("field_name cannot be empty. Provide at least one column name to format.")

        # Convert single field name to list for uniform processing
        if isinstance(field_name, str):
            field_names = [field_name]
        else:
            field_names = field_name

        for field in field_names:
            if field not in df.columns:
                continue
            # Capture empty values before parsing to preserve them as empty strings for comparison
            is_empty = df[field].isna() | (df[field].astype(str).str.strip() == '')
            # Parse and format to ISO standard because different systems use different date formats
            parsed = pd.to_datetime(df[field], errors='coerce', utc=False, dayfirst=False, infer_datetime_format=True)
            formatted = parsed.dt.strftime('%Y-%m-%d')
            # Restore empty strings because empty values must remain empty, not formatted dates
            formatted = formatted.mask(is_empty, '')
            df[field] = formatted
        return df

    def format_to_integer(self, df: pd.DataFrame, field_name: str | List[str]) -> pd.DataFrame:
        """
        Format numeric fields to integer strings, handling floats, NaN values, and other types.

        Used before df_compare to ensure integers are consistent between systems.
        Different systems may represent the same integer differently (e.g., 123 vs "123" vs 123.0),
        which causes false differences in comparisons. This method standardizes all numeric values
        to integer strings, preserving empty values as empty strings.

        Args:
            df: DataFrame containing the field(s) to format
            field_name: Single field name (str) or list of field names to format

        Returns:
            DataFrame with formatted fields as integer strings

        Examples
        --------
        >>> df = pd.DataFrame({
        ...     'employee_id': [123, '456', 789.0, None, '123.0', 100.5]
        ... })
        >>> df_formatted = helper.format_to_integer(df, 'employee_id')
        >>> df_formatted['employee_id']
        0    123
        1    456
        2    789
        3
        4    123
        5    101
        Name: employee_id, dtype: object
        """
        if df.empty:
            self.log_with_prefix("Empty DataFrame in format_to_integer, returning as-is", loglevel='DEBUG')
            return df

        df = df.copy()

        if not field_name:
            raise ValueError("field_name cannot be empty. Provide at least one column name to format.")

        if isinstance(field_name, str):
            field_names = [field_name]
        else:
            field_names = field_name

        def format_value(val: Union[str, int, float, None]) -> str:
            """
            Convert a value to integer string format.

            Standardizes numeric values (strings, floats, integers) to integer strings for consistent
            comparison. Preserves empty values as empty strings.
            """
            if pd.isna(val):
                return ""

            # Convert strings to numeric first because strings like "123.0" need parsing before integer conversion
            if isinstance(val, str):
                val = val.strip()
                if val == '':
                    return ""
                try:
                    val = float(val)
                except (ValueError, TypeError):
                    return str(val)

            # Convert floats to integers because all floats should become integer strings for comparison
            # Round first to 0 decimals before converting to integer
            if isinstance(val, float):
                return str(int(round(val, 0)))

            # for compare
            if isinstance(val, (int, np.integer)):
                return str(int(val))

            return str(val)

        for field in field_names:
            if field not in df.columns:
                continue
            df[field] = df[field].apply(format_value)

        return df

    def compare_data(
        self,
        df_source: pd.DataFrame,
        df_target: pd.DataFrame,
        report: bool = True,
        id_col: str = 'unique_key'
    ) -> Union[pd.DataFrame, bool]:
        """
        Compare source and target data to find what changed.

        Finds records that are new, edited, or deleted between source and target systems.
        Only compares data columns (not unique keys) to focus on actual changes.

        Args:
            df_source: Source data to compare
            df_target: Target data to compare
            report: If True, saves results to Excel file
            id_col: Column name used to match records (default: 'unique_key')

        Returns:
            DataFrame with change_type column ('new', 'edited', 'deleted') and statistics logged.
        """
        self.log_with_prefix("Comparing source and target data", loglevel='INFO')
        try:
            # Validate inputs
            if df_source.empty and df_target.empty:
                self.log_with_prefix("Both source and target DataFrames empty in compare_data, returning empty", loglevel='DEBUG')
                return pd.DataFrame()
            if not self.scenario:
                raise ValueError("Scenario must be initialized before using compare_data(). Set self.scenario in your helper class.")

            # Section 1: Prepare dataframes and determine columns to compare
            # Copy to avoid modifying originals, and filter to data columns only (not unique keys)
            # unique keys are used for matching, not for detecting changes
            df_actual = df_source.copy()
            df_old = df_target.copy()
            self.cols_to_check = [
                col for col in self.scenario.all_target_fields
                if (
                    col not in self.unique_columns
                    and col not in self.scenario.target_fields_to_ignore_in_compare
                    and col in df_source.columns
                    and col in df_target.columns
                )
            ]

            # Section 2:
            # Without id_col, we can't match records between source and target
            if id_col not in df_actual or id_col not in df_old:
                self.log_with_prefix(
                    f"Neither '{id_col}' found in source nor target data. Skipping comparison.",
                    loglevel='INFO'
                )
                return False

            # Section 3: Run comparison now that data is prepared and validated
            # Results are needed for statistics, sorting, and reporting in subsequent sections
            df_compare = Functions().detect_changes_between_dataframes(
                df_old=df_old,
                df_actual=df_actual,
                check_columns=self.cols_to_check,
                unique_key='unique_key',
                keep_old_values='list',
            )

            # Section 4:
            # help users understand the scope of changes at a glance
            total_records = len(df_compare)
            num_new = (df_compare['change_type'] == 'new').sum()
            num_edited = (df_compare['change_type'] == 'edited').sum()
            num_deleted = (df_compare['change_type'] == 'deleted').sum()

            pct_new = (num_new / total_records * 100) if total_records else 0
            pct_edited = (num_edited / total_records * 100) if total_records else 0
            pct_deleted = (num_deleted / total_records * 100) if total_records else 0

            self.log_with_prefix(
                f"{total_records} records compared, of which {pct_new:.1f}% new, "
                f"{pct_edited:.1f}% updated, {pct_deleted:.1f}% deleted. ",
                loglevel='INFO'
            )

            # Section 5: Log unchanged records for debugging
            # Records in source but not in comparison results are unchanged (no differences found)
            if id_col:
                missing_ids = df_source[~df_source[id_col].isin(df_compare[id_col])][id_col]
                if not missing_ids.empty:
                    self.log_with_prefix(
                        f"{len(missing_ids)} {id_col} values found in source but not in comparison results: {missing_ids.tolist()[:5]} (at most 5 examples); these are unchanged",
                        loglevel='DEBUG'
                    )

            # Section 6: Sort results for readability for ease of debugging
            if 'change_type' in df_compare.columns:
                change_type_order = {'edited': 0, 'new': 1, 'deleted': 2}
                df_compare['__change_type_sort'] = df_compare['change_type'].map(change_type_order)

                if 'changed_fields' in df_compare.columns:
                    num_changes = df_compare['changed_fields'].str.len().fillna(0).astype(int)
                    mask_edited = (df_compare['change_type'] == 'edited')
                    df_compare['__changed_fields_sort'] = np.where(
                        mask_edited,
                        -num_changes,
                        0
                    )
                else:
                    df_compare['__changed_fields_sort'] = 0

                df_compare = (
                    df_compare
                    .sort_values(by=['__change_type_sort', '__changed_fields_sort'])
                    .drop(columns=['__change_type_sort', '__changed_fields_sort'])
                    .reset_index(drop=True)
                )

            # Section 7: enable when branch excel-report-functions is merged with master.
            # Save report at the end so Excel contains final sorted results ready for review
            # if report == True:
            #     source_system = getattr(self.parent, 'source_system_name', 'Source')
            #     target_system = getattr(self.parent, 'target_system_name', 'Target')
            #     filepath = os.path.join(self.parent.comparison_dir, f"comparison_scenario_{self.scenario_name}.xlsx")

            #     ScenarioReportBuilder().create_comparison_report(
            #         df_compare=df_compare,
            #         filepath=filepath,
            #         sheetname=f"Comparison {self.scenario_name}",
            #         source_system=source_system,
            #         target_system=target_system,
            #         scenario_name=self.scenario_name,
            #         unique_columns=self.unique_columns,
            #         all_target_fields=self.scenario.all_target_fields,
            #         cols_to_check=self.cols_to_check,
            #         df_source=df_source,
            #         df_target=df_target
            #     )
            #     self.log_with_prefix(f"Excel comparison report saved to: {filepath}", loglevel='DEBUG')

            return df_compare
        except Exception as e:
            self.parent.error_handling(e)
