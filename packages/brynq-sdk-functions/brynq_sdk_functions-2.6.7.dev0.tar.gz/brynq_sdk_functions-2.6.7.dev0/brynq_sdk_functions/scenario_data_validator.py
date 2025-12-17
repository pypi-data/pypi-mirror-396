import os
from typing import Dict, Any, List, Optional

import pandas as pd

from .scenario_report_builder import ScenarioReportBuilder


class ScenarioDataValidator:
    """
    Generic scenario-based data validator.

    This validator:
    - Loads **all** parquet files from source and target directories (optionally filtered by a filename substring).
    - Concatenates them into separate DataFrames for source and target systems.
    - For each scenario on the parent (BrynQ TaskScheduler), checks source fields against source data
      and target fields against target data separately.
    - Produces per‑scenario presence statistics that can be rendered into a report.
    """

    def __init__(
        self,
        parent,
        source_data_dir: str,
        target_data_dir: str,
        filename_filter: Optional[str] = None,
    ) -> None:
        """
        Initialize the ScenarioDataValidator.

        Args:
            parent: Parent object that exposes `.scenarios` (e.g. BobToNmbrs TaskScheduler).
            source_data_dir: Directory in which source system parquet files are stored.
            target_data_dir: Directory in which target system parquet files are stored.
            filename_filter: Optional substring; when provided, only parquet files
                whose filename contains this substring will be loaded.
        """
        self.parent = parent
        self.source_data_dir = source_data_dir
        self.target_data_dir = target_data_dir
        self.filename_filter = filename_filter
        self.source_files: List[Dict[str, Any]] = []
        self.target_files: List[Dict[str, Any]] = []

    # --- Data loading -----------------------------------------------------

    def _get_parquet_files_info(self, data_dir: str) -> List[Dict[str, Any]]:
        """
        Load all parquet files from a directory (optionally filtered) and return file info.

        Args:
            data_dir: Directory from which to load parquet files.

        Returns:
            List of dictionaries with file info: {'filename': str, 'path': str, 'dataframe': pd.DataFrame, 'columns': List[str]}

        Raises:
            FileNotFoundError: If data_dir does not exist.
        """
        files_info: List[Dict[str, Any]] = []

        if not os.path.isdir(data_dir):
            raise FileNotFoundError(f"Data directory does not exist: {data_dir}")

        for fname in os.listdir(data_dir):
            if not fname.lower().endswith(".parquet"):
                continue
            if self.filename_filter and self.filename_filter not in fname:
                continue

            fpath = os.path.join(data_dir, fname)
            df = pd.read_parquet(fpath)

            files_info.append({
                'filename': fname,
                'path': fpath,
                'dataframe': df,
                'columns': list(df.columns)
            })

        return files_info

    def load_parquet_files(self) -> None:
        """
        Load all parquet files from source and target directories individually.

        Populates self.source_files and self.target_files with file metadata and dataframes.
        """
        self.source_files = self._get_parquet_files_info(self.source_data_dir)
        self.target_files = self._get_parquet_files_info(self.target_data_dir)

    # --- File matching logic ----------------------------------------------

    def _jaccard_similarity(self, set1: set, set2: set) -> float:
        """
        Calculate Jaccard similarity between two sets.

        Jaccard similarity = |A ∩ B| / |A ∪ B|

        Args:
            set1: First set.
            set2: Second set.

        Returns:
            Jaccard similarity score between 0.0 and 1.0.
        """
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    def _dice_coefficient(self, set1: set, set2: set) -> float:
        """
        Calculate Dice-Sørensen coefficient between two sets.

        Dice coefficient = 2|A ∩ B| / (|A| + |B|)
        Emphasizes overlap more than Jaccard, giving higher scores when there's intersection.

        Args:
            set1: First set.
            set2: Second set.

        Returns:
            Dice coefficient between 0.0 and 1.0.
        """
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = len(set1.intersection(set2))
        total = len(set1) + len(set2)

        return (2 * intersection) / total if total > 0 else 0.0

    def _tversky_index(self, set1: set, set2: set, alpha: float = 0.5, beta: float = 0.5) -> float:
        """
        Calculate Tversky index between two sets (asymmetric similarity measure).

        Tversky index = |A ∩ B| / (|A ∩ B| + α|A - B| + β|B - A|)

        When α = β = 0.5, this equals Dice coefficient.
        When α = β = 1.0, this equals Jaccard similarity.

        Args:
            set1: First set (reference set).
            set2: Second set (comparison set).
            alpha: Weight for elements in set1 but not in set2 (default 0.5).
            beta: Weight for elements in set2 but not in set1 (default 0.5).

        Returns:
            Tversky index between 0.0 and 1.0.
        """
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = set1.intersection(set2)
        only_in_set1 = set1 - set2
        only_in_set2 = set2 - set1

        intersection_size = len(intersection)
        denominator = intersection_size + (alpha * len(only_in_set1)) + (beta * len(only_in_set2))

        return intersection_size / denominator if denominator > 0 else 0.0

    def _overlap_coefficient(self, set1: set, set2: set) -> float:
        """
        Calculate overlap coefficient (Szymkiewicz–Simpson coefficient).

        Overlap coefficient = |A ∩ B| / min(|A|, |B|)
        Measures overlap relative to the smaller set. Useful when sets differ significantly in size.

        Args:
            set1: First set.
            set2: Second set.

        Returns:
            Overlap coefficient between 0.0 and 1.0.
        """
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = len(set1.intersection(set2))
        min_size = min(len(set1), len(set2))

        return intersection / min_size if min_size > 0 else 0.0

    def _f1_score(self, set1: set, set2: set) -> float:
        """
        Calculate F1 score between two sets (harmonic mean of precision and recall).

        Precision = |A ∩ B| / |A|
        Recall = |A ∩ B| / |B|
        F1 = 2 * (precision * recall) / (precision + recall)

        Args:
            set1: First set (reference/expected).
            set2: Second set (predicted/actual).

        Returns:
            F1 score between 0.0 and 1.0.
        """
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = len(set1.intersection(set2))

        precision = intersection / len(set1) if len(set1) > 0 else 0.0
        recall = intersection / len(set2) if len(set2) > 0 else 0.0

        if precision + recall == 0:
            return 0.0

        return 2 * (precision * recall) / (precision + recall)

    def _tokenize_filename(self, filename: str) -> set:
        """
        Tokenize filename into a set of meaningful tokens.

        Args:
            filename: Name of the file (e.g., 'bob_people.parquet').

        Returns:
            Set of tokens (e.g., {'bob', 'people'}).
        """
        # Remove extension and split by common separators
        name = filename.lower().replace('.parquet', '').replace('.parq', '')
        # Split by underscore, hyphen, or camelCase
        tokens = set()
        # Split by underscore and hyphen
        for part in name.replace('_', ' ').replace('-', ' ').split():
            tokens.add(part)
        return tokens

    def _calculate_file_match_score(
        self,
        scenario_fields: List,
        file_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate match score for scenario fields against a file using multiple similarity metrics.

        Uses optimized metrics:
        1. Schema Tversky: Tversky index with asymmetric weights (emphasizes schema matching)
        2. Column Dice: Dice coefficient (emphasizes column overlap)
        3. Column F1: F1 score (balances precision and recall for columns)

        Args:
            scenario_fields: List of scenario field objects.
            file_info: File info dictionary with 'filename', 'columns', etc.

        Returns:
            Dictionary with match metrics and matched fields.
        """
        filename = file_info['filename']
        file_columns = set(file_info['columns'])
        filename_tokens = self._tokenize_filename(filename)

        # Extract field schemas and column names
        field_schemas = set()
        field_column_names = set()
        field_mapping = {}  # Map column name to field object

        for field in scenario_fields:
            field_schema = getattr(field, "schema_name", None)
            if field_schema:
                field_schemas.add(field_schema.lower())

            alias = getattr(field, "alias", None)
            name = getattr(field, "name", None)
            col_name = alias if alias else name
            if col_name:
                field_column_names.add(col_name)
                field_mapping[col_name] = field

        # Calculate schema similarity using Tversky index (asymmetric, weights schema more)
        # Lower alpha/beta means we care less about mismatches, emphasizing matches
        schema_tversky = self._tversky_index(
            field_schemas,
            filename_tokens,
            alpha=0.3,  # Low penalty for schemas in fields but not in filename
            beta=0.3    # Low penalty for tokens in filename but not in schemas
        )

        # Calculate column similarity using Dice coefficient (emphasizes overlap)
        column_dice = self._dice_coefficient(field_column_names, file_columns)

        # Also calculate F1 score for columns (balances precision and recall)
        column_f1 = self._f1_score(field_column_names, file_columns)

        # Calculate overlap coefficient for columns (useful when sets differ in size)
        column_overlap = self._overlap_coefficient(field_column_names, file_columns)

        # Find matched fields (schema matches AND column exists)
        matched_fields = []
        for field in scenario_fields:
            field_schema = getattr(field, "schema_name", None)
            alias = getattr(field, "alias", None)
            name = getattr(field, "name", None)
            col_name = alias if alias else name

            # Check if schema matches filename
            schema_matches = False
            if field_schema:
                schema_lower = field_schema.lower()
                schema_matches = schema_lower in filename_tokens or any(
                    schema_lower in token or token in schema_lower
                    for token in filename_tokens
                )

            # Check if column exists in file
            column_exists = col_name and col_name in file_columns

            # Match if schema matches AND column exists
            if schema_matches and column_exists:
                matched_fields.append(field)

        # Combined score: weighted average using best metrics
        # Schema Tversky (0.5 weight) + Column Dice (0.3 weight) + Column F1 (0.2 weight)
        # This emphasizes schema matching while using better column metrics
        combined_score = (0.5 * schema_tversky) + (0.3 * column_dice) + (0.2 * column_f1)

        return {
            'matched_fields': matched_fields,
            'schema_tversky': schema_tversky,
            'column_dice': column_dice,
            'column_f1': column_f1,
            'column_overlap': column_overlap,
            'combined_score': combined_score,
            'matched_count': len(matched_fields),
            'total_fields': len(scenario_fields)
        }

    def _find_best_file_for_scenario_fields(
        self,
        scenario_fields: List,
        file_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Find which file(s) have the best match for given scenario fields using optimized similarity metrics.

        Uses multiple metrics for ranking:
        1. Schema Tversky: Tversky index with asymmetric weights (emphasizes schema matching)
        2. Column Dice: Dice coefficient (emphasizes column overlap)
        3. Column F1: F1 score (balances precision and recall)
        4. Column Overlap: Overlap coefficient (useful when sets differ in size)

        Files are ranked by combined score (weighted average of metrics).

        Args:
            scenario_fields: List of scenario field objects.
            file_list: List of file info dictionaries.

        Returns:
            List of file info dictionaries with match information, sorted by combined score (best first).
        """
        file_matches = []

        for file_info in file_list:
            match_result = self._calculate_file_match_score(
                scenario_fields,
                file_info
            )

            # Only include files with at least some match
            if match_result['matched_count'] > 0 or match_result['combined_score'] > 0:
                file_match = file_info.copy()
                file_match['match_result'] = match_result
                file_matches.append(file_match)

        # Sort by combined score (descending), then by individual metrics and matched count
        file_matches.sort(
            key=lambda x: (
                x['match_result']['combined_score'],
                x['match_result']['schema_tversky'],
                x['match_result']['column_dice'],
                x['match_result']['column_f1'],
                x['match_result']['matched_count']
            ),
            reverse=True
        )

        return file_matches

    # --- Statistics helpers ----------------------------------------------

    def _process_field_stats(
        self,
        col,
        df: pd.DataFrame,
        total_rows: int,
        collect_all_values: bool = False,
    ) -> Dict[str, Any]:
        """
        Process statistics for a single field against a DataFrame.

        Args:
            col: Field object from scenario.
            df: DataFrame to check against.
            total_rows: Total number of rows in the DataFrame.
            collect_all_values: If True, collect all values instead of just top 5.

        Returns:
            Dictionary with field statistics.
        """
        # Extract column properties
        system_type = getattr(col, "system_type", None)
        logic = getattr(col, "logic", None)
        unique = getattr(col, "unique", False)
        required = getattr(col, "required", False)
        alias = getattr(col, "alias", None)
        label_en = getattr(col, "label_en", None)
        label_nl = getattr(col, "label_nl", None)
        field_type = getattr(col, "field_type", None)

        # Use alias if available, otherwise try to get the field name
        col_name = alias if alias else getattr(col, "name", str(col))

        if col_name not in df.columns:
            return {
                "status": "MISSING ENTIRELY",
                "missing_percent": "100.00%",
                "system_type": system_type,
                "unique": unique,
                "required": required,
                "logic": logic,
                "field_type": field_type,
                "label_en": label_en,
                "label_nl": label_nl,
            }

        series = df[col_name]
        if pd.api.types.is_string_dtype(series.dtype) or series.dtype == 'object':
            is_missing = series.isnull() | (series.astype(str).str.strip() == "")
        else:
            is_missing = series.isnull()

        missing_count = is_missing.sum()
        missing_percent = (
            (missing_count / total_rows) * 100 if total_rows > 0 else 0
        )

        try:
            unique_count_val: Any = series.nunique()
        except TypeError:
            unique_count_val = "N/A (Unhashable)"

        # Get value counts - all values if collect_all_values is True, otherwise top 5
        if collect_all_values:
            value_counts = series[~is_missing].value_counts()
        else:
            value_counts = series[~is_missing].value_counts().head(5)

        # Convert value counts to a dictionary for clear display
        top_values_display = {}
        for key, value in value_counts.items():
            # Check if the key is unhashable (e.g., list, array) and convert it to string for display.
            if isinstance(key, (list, tuple, pd.Series, pd.Index)) or hasattr(key, '__array__'):
                key_str = str(key)
            else:
                key_str = key
            top_values_display[key_str] = value

        # Calculate descriptive stats (min, max, mean, etc.)
        desc_stats = {}
        if pd.api.types.is_numeric_dtype(series):
            # Use descriptive stats for numeric columns, excluding the count
            desc_stats = series.describe().drop(['count']).to_dict()
        elif pd.api.types.is_datetime64_any_dtype(series):
            # Descriptive stats for datetime columns
            non_missing_series = series[~is_missing]
            if len(non_missing_series) > 0:
                desc_stats = {
                    "min": non_missing_series.min(),
                    "max": non_missing_series.max(),
                    "unique_dates": non_missing_series.nunique(),
                }
        elif pd.api.types.is_string_dtype(series) or series.dtype == 'object':
            # Descriptive stats for string columns (including object dtype)
            non_missing_series = series[~is_missing].astype(str)
            if len(non_missing_series) > 0:
                str_lengths = non_missing_series.str.len()
                desc_stats = {
                    "min_length": int(str_lengths.min()),
                    "max_length": int(str_lengths.max()),
                    "mean_length": float(str_lengths.mean()),
                    "std_length": float(str_lengths.std()) if len(str_lengths) > 1 else 0.0,
                }

        return {
            "dtype": str(series.dtype),
            "missing_count": int(missing_count),
            "missing_percent": f"{missing_percent:.2f}%",
            "unique_count": unique_count_val,
            "top_value_counts": top_values_display,
            "descriptive_stats": desc_stats,
            "system_type": system_type,
            "unique": unique,
            "required": required,
            "logic": logic,
            "field_type": field_type,
            "label_en": label_en,
            "label_nl": label_nl,
        }

    def _get_scenario_stats_per_file(
        self,
        source_files: List[Dict[str, Any]],
        target_files: List[Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate presence statistics for all scenarios, checking each file individually
        and matching scenario fields to the best matching files.

        Args:
            source_files: List of source file info dictionaries.
            target_files: List of target file info dictionaries.

        Returns:
            Dictionary keyed by scenario name, each containing stats for that scenario with file tracking.
        """
        all_scenario_stats: Dict[str, Dict[str, Any]] = {}

        for scenario in self.parent.scenarios:
            scenario_name = scenario.name
            source_cols = scenario.all_source_fields
            target_cols = scenario.all_target_fields

            # Get source and target field lists
            source_fields = scenario.source.field_properties
            target_fields = scenario.target.field_properties

            # Create mapping from field names to field objects for all fields
            source_field_map = {}
            for field in source_fields:
                col_name = getattr(field, "alias", None) or getattr(field, "name", str(field))
                if col_name:
                    source_field_map[col_name] = field

            target_field_map = {}
            for field in target_fields:
                col_name = getattr(field, "alias", None) or getattr(field, "name", str(field))
                if col_name:
                    target_field_map[col_name] = field

            # Get fields with value mappings (if method exists)
            source_fields_with_mappings = set()
            target_fields_with_mappings = set()
            try:
                if hasattr(scenario, 'get_source_fields_with_value_mappings'):
                    source_fields_with_mappings = {
                        getattr(f, "alias", None) or getattr(f, "name", str(f))
                        for f in scenario.get_source_fields_with_value_mappings()
                    }
                if hasattr(scenario, 'get_target_fields_with_value_mappings'):
                    target_fields_with_mappings = {
                        getattr(f, "alias", None) or getattr(f, "name", str(f))
                        for f in scenario.get_target_fields_with_value_mappings()
                    }
            except Exception:
                # If methods don't exist or fail, continue without value mapping fields
                pass

            # Find best matching files for source fields
            source_file_matches = self._find_best_file_for_scenario_fields(source_fields, source_files)

            # Find best matching files for target fields
            target_file_matches = self._find_best_file_for_scenario_fields(target_fields, target_files)

            # Calculate total rows across all matched files
            source_total_rows = sum(len(f['dataframe']) for f in source_file_matches)
            target_total_rows = sum(len(f['dataframe']) for f in target_file_matches)

            # Track which files were used (for stats)
            source_files_used = set(f['filename'] for f in source_file_matches)
            target_files_used = set(f['filename'] for f in target_file_matches)

            stats: Dict[str, Any] = {
                "scenario_name": scenario_name,
                "source_total_rows": source_total_rows,
                "target_total_rows": target_total_rows,
                "columns_checked_source": source_cols,
                "columns_checked_target": target_cols,
                "source_files": sorted(list(source_files_used)),
                "target_files": sorted(list(target_files_used)),
                "source_column_stats": {},
                "target_column_stats": {},
            }

            # Track which fields were matched
            matched_source_field_names = set()
            matched_target_field_names = set()

            # Process source fields against matching files
            for file_match in source_file_matches:
                file_df = file_match['dataframe']
                file_rows = len(file_df)
                matched_fields = file_match['match_result']['matched_fields']
                file_columns = set(file_df.columns)

                for col in matched_fields:
                    col_name = getattr(col, "alias", None) or getattr(col, "name", str(col))
                    matched_source_field_names.add(col_name)
                    # Collect all values if this field has value mappings
                    collect_all = col_name in source_fields_with_mappings
                    field_stats = self._process_field_stats(col, file_df, file_rows, collect_all_values=collect_all)
                    # Mark if field has value mappings
                    field_stats['has_value_mappings'] = collect_all
                    # Add file information to stats
                    field_stats['source_file'] = file_match['filename']
                    field_stats['total_rows_in_file'] = file_rows
                    # Initialize scenarios list (will be updated by merge if field is repeated)
                    field_stats['scenarios'] = scenario_name

                    # If column already exists (from another file), keep the one with more data
                    if col_name not in stats["source_column_stats"]:
                        stats["source_column_stats"][col_name] = field_stats
                    else:
                        # Prefer stats from file with more rows
                        existing_stats = stats["source_column_stats"][col_name]
                        existing_file_rows = existing_stats.get('total_rows_in_file', 0)
                        if file_rows > existing_file_rows:
                            stats["source_column_stats"][col_name] = field_stats

                # Also check for fields from all_source_fields that exist in file but weren't matched by schema
                # This catches fields like employee_id, iban that might not have schema matches
                for field in source_fields:
                    col_name = getattr(field, "alias", None) or getattr(field, "name", str(field))
                    if col_name and col_name in file_columns and col_name not in matched_source_field_names:
                        # Field exists in file but wasn't matched by schema - process it anyway
                        matched_source_field_names.add(col_name)
                        collect_all = col_name in source_fields_with_mappings
                        field_stats = self._process_field_stats(field, file_df, file_rows, collect_all_values=collect_all)
                        field_stats['has_value_mappings'] = collect_all
                        field_stats['source_file'] = file_match['filename']
                        field_stats['total_rows_in_file'] = file_rows
                        field_stats['scenarios'] = scenario_name

                        if col_name not in stats["source_column_stats"]:
                            stats["source_column_stats"][col_name] = field_stats
                        else:
                            existing_stats = stats["source_column_stats"][col_name]
                            existing_file_rows = existing_stats.get('total_rows_in_file', 0)
                            if file_rows > existing_file_rows:
                                stats["source_column_stats"][col_name] = field_stats

            # Search ALL source files for fields from all_source_fields that weren't found yet
            # This ensures fields are found even if their files don't match schema
            for field in source_fields:
                col_name = getattr(field, "alias", None) or getattr(field, "name", str(field))
                if col_name and col_name not in matched_source_field_names:
                    # Search through all source files (not just matched ones)
                    for file_info in source_files:
                        file_df = file_info['dataframe']
                        file_columns = set(file_df.columns)
                        if col_name in file_columns:
                            # Found the field in this file - process it
                            matched_source_field_names.add(col_name)
                            file_rows = len(file_df)
                            source_files_used.add(file_info['filename'])  # Track file usage
                            collect_all = col_name in source_fields_with_mappings
                            field_stats = self._process_field_stats(field, file_df, file_rows, collect_all_values=collect_all)
                            field_stats['has_value_mappings'] = collect_all
                            field_stats['source_file'] = file_info['filename']
                            field_stats['total_rows_in_file'] = file_rows
                            field_stats['scenarios'] = scenario_name

                            if col_name not in stats["source_column_stats"]:
                                stats["source_column_stats"][col_name] = field_stats
                            else:
                                # Prefer stats from file with more rows
                                existing_stats = stats["source_column_stats"][col_name]
                                existing_file_rows = existing_stats.get('total_rows_in_file', 0)
                                if file_rows > existing_file_rows:
                                    stats["source_column_stats"][col_name] = field_stats
                            break  # Found in one file, no need to check others

            # Process unmatched source fields (not found in any file)
            # Check all fields from source_fields iterator
            for col in source_fields:
                col_name = getattr(col, "alias", None) or getattr(col, "name", str(col))
                if col_name and col_name not in matched_source_field_names:
                    # Extract column properties for missing field
                    system_type = getattr(col, "system_type", None)
                    logic = getattr(col, "logic", None)
                    unique = getattr(col, "unique", False)
                    required = getattr(col, "required", False)
                    label_en = getattr(col, "label_en", None)
                    label_nl = getattr(col, "label_nl", None)
                    field_type = getattr(col, "field_type", None)

                    stats["source_column_stats"][col_name] = {
                        "status": "MISSING ENTIRELY",
                        "missing_percent": "100.00%",
                        "system_type": system_type,
                        "unique": unique,
                        "required": required,
                        "logic": logic,
                        "field_type": field_type,
                        "label_en": label_en,
                        "label_nl": label_nl,
                        "source_file": "N/A",
                        "has_value_mappings": col_name in source_fields_with_mappings,
                        "scenarios": scenario_name,
                    }

            # Also check all_source_fields - if a field name is in all_source_fields but not processed, mark as missing
            for field_name in source_cols:
                if field_name not in matched_source_field_names and field_name not in stats["source_column_stats"]:
                    # Field is in all_source_fields but we don't have a field object for it
                    # Try to find it in source_field_map, or create a basic missing entry
                    if field_name in source_field_map:
                        col = source_field_map[field_name]
                        system_type = getattr(col, "system_type", None)
                        logic = getattr(col, "logic", None)
                        unique = getattr(col, "unique", False)
                        required = getattr(col, "required", False)
                        label_en = getattr(col, "label_en", None)
                        label_nl = getattr(col, "label_nl", None)
                        field_type = getattr(col, "field_type", None)
                    else:
                        # Field name exists but no field object - use defaults
                        system_type = None
                        logic = None
                        unique = False
                        required = False
                        label_en = None
                        label_nl = None
                        field_type = None

                    stats["source_column_stats"][field_name] = {
                        "status": "MISSING ENTIRELY",
                        "missing_percent": "100.00%",
                        "system_type": system_type,
                        "unique": unique,
                        "required": required,
                        "logic": logic,
                        "field_type": field_type,
                        "label_en": label_en,
                        "label_nl": label_nl,
                        "source_file": "N/A",
                        "has_value_mappings": field_name in source_fields_with_mappings,
                        "scenarios": scenario_name,
                    }

            # Process target fields against matching files
            for file_match in target_file_matches:
                file_df = file_match['dataframe']
                file_rows = len(file_df)
                matched_fields = file_match['match_result']['matched_fields']
                file_columns = set(file_df.columns)

                for col in matched_fields:
                    col_name = getattr(col, "alias", None) or getattr(col, "name", str(col))
                    matched_target_field_names.add(col_name)
                    # Collect all values if this field has value mappings
                    collect_all = col_name in target_fields_with_mappings
                    field_stats = self._process_field_stats(col, file_df, file_rows, collect_all_values=collect_all)
                    # Mark if field has value mappings
                    field_stats['has_value_mappings'] = collect_all
                    # Add file information to stats
                    field_stats['source_file'] = file_match['filename']
                    field_stats['total_rows_in_file'] = file_rows
                    # Initialize scenarios list (will be updated by merge if field is repeated)
                    field_stats['scenarios'] = scenario_name

                    # If column already exists (from another file), keep the one with more data
                    if col_name not in stats["target_column_stats"]:
                        stats["target_column_stats"][col_name] = field_stats
                    else:
                        # Prefer stats from file with more rows
                        existing_stats = stats["target_column_stats"][col_name]
                        existing_file_rows = existing_stats.get('total_rows_in_file', 0)
                        if file_rows > existing_file_rows:
                            stats["target_column_stats"][col_name] = field_stats

                # Also check for fields from all_target_fields that exist in file but weren't matched by schema
                for field in target_fields:
                    col_name = getattr(field, "alias", None) or getattr(field, "name", str(field))
                    if col_name and col_name in file_columns and col_name not in matched_target_field_names:
                        # Field exists in file but wasn't matched by schema - process it anyway
                        matched_target_field_names.add(col_name)
                        collect_all = col_name in target_fields_with_mappings
                        field_stats = self._process_field_stats(field, file_df, file_rows, collect_all_values=collect_all)
                        field_stats['has_value_mappings'] = collect_all
                        field_stats['source_file'] = file_match['filename']
                        field_stats['total_rows_in_file'] = file_rows
                        field_stats['scenarios'] = scenario_name

                        if col_name not in stats["target_column_stats"]:
                            stats["target_column_stats"][col_name] = field_stats
                        else:
                            existing_stats = stats["target_column_stats"][col_name]
                            existing_file_rows = existing_stats.get('total_rows_in_file', 0)
                            if file_rows > existing_file_rows:
                                stats["target_column_stats"][col_name] = field_stats

            # Search ALL target files for fields from all_target_fields that weren't found yet
            # This ensures fields like employee_id, iban are found even if their files don't match schema
            for field in target_fields:
                col_name = getattr(field, "alias", None) or getattr(field, "name", str(field))
                if col_name and col_name not in matched_target_field_names:
                    # Search through all target files (not just matched ones)
                    for file_info in target_files:
                        file_df = file_info['dataframe']
                        file_columns = set(file_df.columns)
                        if col_name in file_columns:
                            # Found the field in this file - process it
                            matched_target_field_names.add(col_name)
                            file_rows = len(file_df)
                            target_files_used.add(file_info['filename'])  # Track file usage
                            collect_all = col_name in target_fields_with_mappings
                            field_stats = self._process_field_stats(field, file_df, file_rows, collect_all_values=collect_all)
                            field_stats['has_value_mappings'] = collect_all
                            field_stats['source_file'] = file_info['filename']
                            field_stats['total_rows_in_file'] = file_rows
                            field_stats['scenarios'] = scenario_name

                            if col_name not in stats["target_column_stats"]:
                                stats["target_column_stats"][col_name] = field_stats
                            else:
                                # Prefer stats from file with more rows
                                existing_stats = stats["target_column_stats"][col_name]
                                existing_file_rows = existing_stats.get('total_rows_in_file', 0)
                                if file_rows > existing_file_rows:
                                    stats["target_column_stats"][col_name] = field_stats
                            break  # Found in one file, no need to check others

            # Process unmatched target fields (not found in any file)
            # Check all fields from target_fields iterator
            for col in target_fields:
                col_name = getattr(col, "alias", None) or getattr(col, "name", str(col))
                if col_name and col_name not in matched_target_field_names:
                    # Extract column properties for missing field
                    system_type = getattr(col, "system_type", None)
                    logic = getattr(col, "logic", None)
                    unique = getattr(col, "unique", False)
                    required = getattr(col, "required", False)
                    label_en = getattr(col, "label_en", None)
                    label_nl = getattr(col, "label_nl", None)
                    field_type = getattr(col, "field_type", None)

                    stats["target_column_stats"][col_name] = {
                        "status": "MISSING ENTIRELY",
                        "missing_percent": "100.00%",
                        "system_type": system_type,
                        "unique": unique,
                        "required": required,
                        "logic": logic,
                        "field_type": field_type,
                        "label_en": label_en,
                        "label_nl": label_nl,
                        "source_file": "N/A",
                        "has_value_mappings": col_name in target_fields_with_mappings,
                        "scenarios": scenario_name,
                    }

            # Also check all_target_fields - if a field name is in all_target_fields but not processed, mark as missing
            for field_name in target_cols:
                if field_name not in matched_target_field_names and field_name not in stats["target_column_stats"]:
                    # Field is in all_target_fields but we don't have a field object for it
                    # Try to find it in target_field_map, or create a basic missing entry
                    if field_name in target_field_map:
                        col = target_field_map[field_name]
                        system_type = getattr(col, "system_type", None)
                        logic = getattr(col, "logic", None)
                        unique = getattr(col, "unique", False)
                        required = getattr(col, "required", False)
                        label_en = getattr(col, "label_en", None)
                        label_nl = getattr(col, "label_nl", None)
                        field_type = getattr(col, "field_type", None)
                    else:
                        # Field name exists but no field object - use defaults
                        system_type = None
                        logic = None
                        unique = False
                        required = False
                        label_en = None
                        label_nl = None
                        field_type = None

                    stats["target_column_stats"][field_name] = {
                        "status": "MISSING ENTIRELY",
                        "missing_percent": "100.00%",
                        "system_type": system_type,
                        "unique": unique,
                        "required": required,
                        "logic": logic,
                        "field_type": field_type,
                        "label_en": label_en,
                        "label_nl": label_nl,
                        "source_file": "N/A",
                        "has_value_mappings": field_name in target_fields_with_mappings,
                        "scenarios": scenario_name,
                    }

            # Update file lists in stats to include all files where fields were found
            stats["source_files"] = sorted(list(source_files_used))
            stats["target_files"] = sorted(list(target_files_used))

            all_scenario_stats[scenario_name] = stats

        return all_scenario_stats

    def _merge_repeated_field_stats(
        self,
        all_scenario_stats: Dict[str, Dict[str, Any]],
        system_type: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Merge statistics for fields that appear in multiple scenarios.

        For fields that appear across scenarios (e.g., employee_id, iban),
        consolidate their statistics by:
        - Combining value counts from all scenarios
        - Taking the best file info (most rows)
        - Merging descriptive statistics

        Args:
            all_scenario_stats: Dictionary of all scenario statistics.
            system_type: 'source' or 'target'.

        Returns:
            Updated all_scenario_stats with merged statistics for repeated fields.
        """
        # Identify fields that appear in multiple scenarios
        field_to_scenarios: Dict[str, List[str]] = {}

        for scenario_name, stats in all_scenario_stats.items():
            if system_type.lower() == 'source':
                column_stats = stats.get('source_column_stats', {})
            else:
                column_stats = stats.get('target_column_stats', {})

            for col_name in column_stats.keys():
                if col_name not in field_to_scenarios:
                    field_to_scenarios[col_name] = []
                field_to_scenarios[col_name].append(scenario_name)

        # Find fields that appear in multiple scenarios
        repeated_fields = {
            field: scenarios
            for field, scenarios in field_to_scenarios.items()
            if len(scenarios) > 1
        }

        if not repeated_fields:
            return all_scenario_stats

        # For each repeated field, merge statistics across scenarios
        for field_name, scenario_names in repeated_fields.items():
            # Collect all stats for this field across scenarios
            field_stats_list = []
            for scenario_name in scenario_names:
                stats = all_scenario_stats[scenario_name]
                if system_type.lower() == 'source':
                    column_stats = stats.get('source_column_stats', {})
                else:
                    column_stats = stats.get('target_column_stats', {})

                if field_name in column_stats:
                    field_stats_list.append({
                        'scenario': scenario_name,
                        'stats': column_stats[field_name]
                    })

            if not field_stats_list:
                continue

            # Merge statistics: prefer stats with more data, combine value counts
            merged_stats = None
            max_rows = 0

            # Find the stats with the most rows (best data)
            for field_stat_info in field_stats_list:
                stats = field_stat_info['stats']
                rows = stats.get('total_rows_in_file', 0)
                if rows > max_rows:
                    max_rows = rows
                    merged_stats = stats.copy()

            # If no stats with rows, use the first one
            if merged_stats is None:
                merged_stats = field_stats_list[0]['stats'].copy()

            # Merge value counts from all scenarios
            all_value_counts = {}
            for field_stat_info in field_stats_list:
                stats = field_stat_info['stats']
                value_counts = stats.get('top_value_counts', {})
                if isinstance(value_counts, dict):
                    for value, count in value_counts.items():
                        if value in all_value_counts:
                            all_value_counts[value] += count
                        else:
                            all_value_counts[value] = count

            # Update merged stats with combined value counts
            if all_value_counts:
                merged_stats['top_value_counts'] = all_value_counts
                # Update unique count if we have combined value counts
                merged_stats['unique_count'] = len(all_value_counts)

            # Add information about which scenarios this field appears in
            merged_stats['scenarios'] = ', '.join(sorted(scenario_names))

            # Update all scenarios with the merged stats
            for scenario_name in scenario_names:
                stats = all_scenario_stats[scenario_name]
                if system_type.lower() == 'source':
                    stats['source_column_stats'][field_name] = merged_stats.copy()
                else:
                    stats['target_column_stats'][field_name] = merged_stats.copy()

        return all_scenario_stats

    # --- Public API -------------------------------------------------------

    def _format_column_table(self, column_stats: Dict[str, Dict[str, Any]], section_title: str) -> str:
        """
        Format a table for column statistics.

        Args:
            column_stats: Dictionary of column statistics.
            section_title: Title for the section (e.g., "Source System" or "Target System").

        Returns:
            Formatted Markdown table string.
        """
        if not column_stats:
            return f"#### {section_title}\n\nNo columns found.\n\n"

        table = f"#### {section_title}\n\n"
        table += "| Column | System Type | Required | Unique | Dtype | Missing % | Unique Count | Top Value Counts (Sample) |\n"
        table += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"

        for col_name, cstats in column_stats.items():
            if cstats.get("status") == "MISSING ENTIRELY":
                system_type = cstats.get("system_type", "N/A")
                required = "✓" if cstats.get("required", False) else ""
                unique = "✓" if cstats.get("unique", False) else ""
                row = (
                    f"| `{col_name}` | `{system_type}` | {required} | {unique} | "
                    f"N/A | **100.00%** | N/A | **COLUMN NOT FOUND** |\n"
                )
            else:
                # Determine if unique_count is a number (int/float) or a string ('N/A (Unhashable)')
                unique_count_str = str(cstats['unique_count'])

                # Format top value counts for table display
                top_values_str = ", ".join([
                    f"'{k}': {v}" for k, v in cstats.get('top_value_counts', {}).items()
                ]) if cstats.get('top_value_counts') else "N/A"

                # Include descriptive stats if present (for numbers, datetime, strings)
                desc_stats_str = ""
                if cstats.get('descriptive_stats'):
                    desc_stats = cstats['descriptive_stats']

                    # Check if it's datetime stats
                    if 'unique_dates' in desc_stats:
                        min_val = desc_stats.get('min', 'N/A')
                        max_val = desc_stats.get('max', 'N/A')
                        unique_dates = desc_stats.get('unique_dates', 'N/A')
                        # Format datetime values
                        if isinstance(min_val, pd.Timestamp):
                            min_format = min_val.strftime('%Y-%m-%d')
                        else:
                            min_format = str(min_val)
                        if isinstance(max_val, pd.Timestamp):
                            max_format = max_val.strftime('%Y-%m-%d')
                        else:
                            max_format = str(max_val)
                        desc_stats_str = f" | Min: {min_format}, Max: {max_format}, Unique Dates: {unique_dates}"
                    # Check if it's string stats
                    elif 'min_length' in desc_stats:
                        min_len = desc_stats.get('min_length', 'N/A')
                        max_len = desc_stats.get('max_length', 'N/A')
                        mean_len = desc_stats.get('mean_length', 'N/A')
                        mean_format = f"{mean_len:.2f}" if isinstance(mean_len, (int, float)) else str(mean_len)
                        desc_stats_str = f" | Min Length: {min_len}, Max Length: {max_len}, Mean Length: {mean_format}"
                    # Numeric stats (existing logic)
                    else:
                        min_val = desc_stats.get('min', 'N/A')
                        max_val = desc_stats.get('max', 'N/A')
                        # Safely format min/max, ensuring they are treated as numbers if possible
                        min_format = f"{min_val:.2f}" if isinstance(min_val, (int, float)) else str(min_val)
                        max_format = f"{max_val:.2f}" if isinstance(max_val, (int, float)) else str(max_val)
                        desc_stats_str = f" | Min: {min_format}, Max: {max_format}"

                # Combine top values and descriptive stats in the same cell
                value_stats_str = top_values_str + desc_stats_str if desc_stats_str else top_values_str

                # Column properties
                system_type = cstats.get("system_type", "N/A")
                required = "✓" if cstats.get("required", False) else ""
                unique = "✓" if cstats.get("unique", False) else ""

                row = (
                    f"| `{col_name}` | `{system_type}` | {required} | {unique} | "
                    f"`{cstats['dtype']}` | `{cstats['missing_percent']}` | "
                    f"`{unique_count_str}` | {value_stats_str} |\n"
                )
            table += row

        return table + "\n"

    def generate_validation_report(self) -> str:
        """
        Generate a Markdown report with presence stats per scenario, showing source and target
        systems separately. Uses per-file validation approach.
        """
        if not self.source_files and not self.target_files:
            self.load_parquet_files()

        if not self.source_files and not self.target_files:
            return "## Scenario Data Validation Report\n\nNo data loaded (no parquet files found)."

        # Get stats for all scenarios using per-file approach
        all_scenario_stats = self._get_scenario_stats_per_file(self.source_files, self.target_files)

        if not all_scenario_stats:
            return (
                "## Scenario Data Validation Report\n\n"
                "No scenarios found or no overlapping fields found between scenarios and data."
            )

        all_reports: List[str] = []

        for scenario_name, stats in all_scenario_stats.items():
            # Skip scenarios with no column stats
            if not stats.get("source_column_stats") and not stats.get("target_column_stats"):
                continue

            # Format as Markdown
            source_files = stats.get('source_files', [])
            target_files = stats.get('target_files', [])
            report = f"### Scenario '{scenario_name}'\n\n"
            report += f"- **Source System Total Rows:** `{stats['source_total_rows']}`\n"
            report += f"- **Target System Total Rows:** `{stats['target_total_rows']}`\n"
            report += f"- **Source Columns Checked:** `{len(stats.get('columns_checked_source', []))}`\n"
            report += f"- **Target Columns Checked:** `{len(stats.get('columns_checked_target', []))}`\n"
            report += f"- **Source Columns Found in Data:** `{len(stats.get('source_column_stats', {}))}`\n"
            report += f"- **Target Columns Found in Data:** `{len(stats.get('target_column_stats', {}))}`\n"
            report += f"- **Source Files Checked:** `{', '.join(source_files) if source_files else 'No matching files'}`\n"
            report += f"- **Target Files Checked:** `{', '.join(target_files) if target_files else 'No matching files'}`\n\n"

            # Add source system table
            report += self._format_column_table(
                stats.get("source_column_stats", {}),
                "Source System"
            )

            # Add target system table
            report += self._format_column_table(
                stats.get("target_column_stats", {}),
                "Target System"
            )

            all_reports.append(report)

        if not all_reports:
            return (
                "## Scenario Data Validation Report\n\n"
                "No overlapping fields found between scenarios and data."
            )

        return "## Scenario Data Validation Report\n\n" + "\n---\n".join(all_reports) + "\n"

    def write_report_to_file(self, source_suffix: str = None, target_suffix: str = None) -> None:
        """
        Generate Excel validation reports for source and target systems and write them to disk.

        Creates two separate Excel files:
        - source_validation_report.xlsx (or source_validation_report_{source_suffix}.xlsx) in source_data_dir
        - target_validation_report.xlsx (or target_validation_report_{target_suffix}.xlsx) in target_data_dir

        Each file contains an explanation sheet and scenario-specific tabs with column statistics.
        Validation is performed per file, matching scenario fields to the best matching parquet files.

        Args:
            source_suffix: Optional suffix to append to source report filename.
            target_suffix: Optional suffix to append to target report filename.

        Examples:
            >>> validator = ScenarioDataValidator(parent_scheduler, source_dir, target_dir)
            >>> validator.write_report_to_file()
            # Generates "source_validation_report.xlsx" and "target_validation_report.xlsx"

            >>> validator.write_report_to_file(source_suffix="2024-01", target_suffix="2024-01")
            # Generates "source_validation_report_2024-01.xlsx" and "target_validation_report_2024-01.xlsx"
        """
        if not self.source_files and not self.target_files:
            self.load_parquet_files()

        if not self.source_files and not self.target_files:
            return

        # Get stats for all scenarios using per-file approach
        all_scenario_stats = self._get_scenario_stats_per_file(self.source_files, self.target_files)

        if not all_scenario_stats:
            return

        # Merge statistics for fields that appear in multiple scenarios
        all_scenario_stats = self._merge_repeated_field_stats(all_scenario_stats, 'source')
        all_scenario_stats = self._merge_repeated_field_stats(all_scenario_stats, 'target')

        # Write source Excel file
        source_filename = "source_validation_report.xlsx" if not source_suffix else f"source_validation_report_{source_suffix}.xlsx"
        source_output_path = os.path.join(self.source_data_dir, source_filename)
        ScenarioReportBuilder().create_validation_report('Source', all_scenario_stats, source_output_path)

        # Write target Excel file
        target_filename = "target_validation_report.xlsx" if not target_suffix else f"target_validation_report_{target_suffix}.xlsx"
        target_output_path = os.path.join(self.target_data_dir, target_filename)
        ScenarioReportBuilder().create_validation_report('Target', all_scenario_stats, target_output_path)
