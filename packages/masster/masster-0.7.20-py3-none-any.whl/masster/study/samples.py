"""
samples.py

This module contains sample-related helper functions for the Study class.

The functions are organized into the following sections:
1. Sample configuration and folder management
2. Sample retrieval and statistics
3. Sample naming and metadata management
4. Sample selection and deletion
5. Sample color palette management
"""

from __future__ import annotations

import os

import numpy as np
import polars as pl

from tqdm import tqdm


# =====================================================================================
# SAMPLE CONFIGURATION AND FOLDER MANAGEMENT
# =====================================================================================


def set_study_folder(self, folder):
    """
    Set the folder path for saving and loading study files.

    Creates the directory if it doesn't exist. This folder is used as the default
    location for:
    - Saving study files (.study5)
    - Exporting data (CSV, Excel, etc.)
    - Storing analysis results and reports

    Parameters:
        folder (str): Absolute or relative path to the study folder

    Returns:
        None (sets self.folder attribute)

    Note:
        The directory will be created automatically if it doesn't exist.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    self.folder = folder


# =====================================================================================
# SAMPLE RETRIEVAL AND STATISTICS
# =====================================================================================


def get_samples(self, sample):
    """
    Return a Sample object corresponding to the provided sample identifier.

    This method retrieves a Sample instance from the study's samples_df and attempts to
    load it from disk if a sample_path is available. Uses an internal cache to avoid
    reloading the same sample multiple times.

    Parameters:
        sample (int, str, or Sample): Sample identifier:
                                     - int: sample_uid (unique identifier)
                                     - str: sample_name
                                     - Sample: Sample instance (returned as-is)

    Returns:
        Sample: Loaded Sample object with data from .sample5 file if available

    Raises:
        KeyError: If sample is not found in samples_df
        ValueError: If sample type is not int, str, or Sample instance

    Note:
        This helper mirrors the original Study.get_sample method but lives in samples module for reuse.
        The method uses a _samples_cache attribute if available on the Study instance.
    """
    from masster.sample.sample import Sample

    if isinstance(sample, Sample):
        return sample

    if isinstance(sample, int):
        rows = self.samples_df.filter(pl.col("sample_uid") == sample)
    elif isinstance(sample, str):
        rows = self.samples_df.filter(pl.col("sample_name") == sample)
    else:
        raise ValueError(
            "sample must be an int (sample_uid), str (sample_name) or a Sample instance",
        )

    if rows.is_empty():
        raise KeyError(f"Sample not found: {sample}")

    row = rows.row(0, named=True)
    sample_uid = int(row["sample_uid"]) if row["sample_uid"] is not None else None

    # Use a cache on the Study instance if available
    cache = getattr(self, "_samples_cache", None)
    if cache is not None and sample_uid in cache:
        return cache[sample_uid]

    sample_path = row.get("sample_path", None)
    s = Sample(log_level="ERROR")
    try:
        if sample_path:
            try:
                s.load(sample_path)
            except Exception:
                s = Sample(file=sample_path)
    except Exception:
        pass

    if cache is not None and sample_uid is not None:
        cache[sample_uid] = s
    return s


def _get_samples_uids(self, samples=None, seed=42):
    """
    Helper function to resolve sample identifiers to sample_uids from samples_df.

    This is an internal utility function used throughout the Study module to normalize
    various sample identifier formats into a consistent list of sample_uids.

    Parameters:
        samples (None, int, str, pl.DataFrame, or list): Sample identifier(s) in various formats:
                                          - None: returns all sample_uids (default)
                                          - int: returns N randomly selected sample_uids
                                          - str: returns sample_uid for matching sample_name
                                          - pl.DataFrame: extracts sample_uid column (e.g., from samples_select())
                                          - list of int: returns matching sample_uids
                                          - list of str: returns sample_uids for matching sample_names
        seed (int): Random seed for reproducible random sampling. Default is 42.

    Returns:
        list: List of sample_uids (integers) matching the input criteria.
             Duplicates are removed.

    Note:
        When samples is an integer N, if the total number of samples is less than N,
        returns all available sample_uids instead.
    """
    if samples is None:
        # get all sample_uids from samples_df
        return self.samples_df["sample_uid"].to_list()
    elif isinstance(samples, pl.DataFrame):
        # Extract sample_uid column from DataFrame (e.g., from samples_select())
        if "sample_uid" in samples.columns:
            return samples["sample_uid"].to_list()
        else:
            self.logger.warning("DataFrame does not contain 'sample_uid' column")
            return []
    elif isinstance(samples, int):
        # choose a random sample of sample_uids
        if len(self.samples_df) > samples:
            np.random.seed(seed)  # for reproducibility
            self.logger.info(f"Randomly selected {samples} samples")
            return np.random.choice(
                self.samples_df["sample_uid"].to_list(),
                samples,
                replace=False,
            ).tolist()
        else:
            return self.samples_df["sample_uid"].to_list()
    else:
        # iterate over all samples. If the item is a string, assume it's a sample_name
        sample_uids = []
        for sample in samples:
            if isinstance(sample, str):
                matching_rows = self.samples_df.filter(pl.col("sample_name") == sample)
                if not matching_rows.is_empty():
                    sample_uids.append(
                        matching_rows.row(0, named=True)["sample_uid"],
                    )
            elif isinstance(sample, int):
                if sample in self.samples_df["sample_uid"].to_list():
                    sample_uids.append(sample)
        # remove duplicates
        sample_uids = list(set(sample_uids))
        return sample_uids


def get_samples_stats(self):
    """
    Get comprehensive statistics for all samples in the study.

    Computes detailed statistics for each sample including feature counts, MS data quality,
    retention time alignment metrics, and consensus linking information.

    Returns:
        pl.DataFrame: DataFrame with one row per sample and the following columns:
            - sample_uid: Sample unique identifier
            - num_features: Total number of features per sample
            - num_ms1: Number of MS1 features per sample
            - num_ms2: Number of MS2 features per sample
            - num_linked_ms1: Number of non-filled features present in consensus_mapping_df
            - num_orphans: Number of non-filled features not present in consensus_mapping_df
            - max_rt_correction: Maximum RT correction applied
            - average_rt_correction: Average RT correction applied
            - num_linked_ms2: Number of linked MS2 spectra from consensus_ms2_df
    """
    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.warning("No samples found in study.")
        return pl.DataFrame()

    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features found in study.")
        return pl.DataFrame()

    # Get base sample information
    sample_uids = self.samples_df["sample_uid"].to_list()
    stats_data = []

    for sample_uid in sample_uids:
        # Filter features for this sample
        sample_features = self.features_df.filter(pl.col("sample_uid") == sample_uid)

        if sample_features.is_empty():
            # Sample has no features
            stats_data.append({
                "sample_uid": sample_uid,
                "num_features": 0,
                "num_ms1": 0,
                "num_ms2": 0,
                "num_linked_ms1": 0,
                "num_orphans": 0,
                "max_rt_correction": None,
                "average_rt_correction": None,
                "num_linked_ms2": 0,
            })
            continue

        # Basic feature counts
        num_features = len(sample_features)

        # Count MS1 and MS2 features
        # Assume features with ms_level=1 or missing ms_level are MS1
        num_ms1 = (
            sample_features.filter(pl.col("ms_level").is_null() | (pl.col("ms_level") == 1)).height
            if "ms_level" in sample_features.columns
            else num_features
        )

        num_ms2 = sample_features.filter(pl.col("ms_level") == 2).height if "ms_level" in sample_features.columns else 0

        # Get non-filled features for this sample
        if "filled" in sample_features.columns:
            non_filled_features = sample_features.filter(~pl.col("filled") | pl.col("filled").is_null())
        else:
            non_filled_features = sample_features

        # Count linked MS1 features (non-filled and present in consensus_mapping_df)
        num_linked_ms1 = 0
        if not self.consensus_mapping_df.is_empty() and not non_filled_features.is_empty():
            linked_feature_uids = self.consensus_mapping_df.filter(pl.col("sample_uid") == sample_uid)[
                "feature_uid"
            ].to_list()

            num_linked_ms1 = non_filled_features.filter(pl.col("feature_uid").is_in(linked_feature_uids)).height

        # Count orphan features (non-filled and NOT present in consensus_mapping_df)
        num_orphans = len(non_filled_features) - num_linked_ms1

        # Calculate RT correction statistics
        max_rt_correction = None
        average_rt_correction = None

        if "rt" in sample_features.columns and "rt_original" in sample_features.columns:
            rt_corrections = sample_features.with_columns(
                (pl.col("rt") - pl.col("rt_original")).alias("rt_correction")
            ).filter(pl.col("rt_correction").is_not_null())["rt_correction"]

            if not rt_corrections.is_empty():
                max_rt_correction = rt_corrections.abs().max()
                average_rt_correction = rt_corrections.abs().mean()

        # Count linked MS2 spectra from consensus_ms2_df
        num_linked_ms2 = 0
        if hasattr(self, "consensus_ms2") and self.consensus_ms2 is not None and not self.consensus_ms2.is_empty():
            if "sample_uid" in self.consensus_ms2.columns:
                num_linked_ms2 = self.consensus_ms2.filter(pl.col("sample_uid") == sample_uid).height

        stats_data.append({
            "sample_uid": sample_uid,
            "num_features": num_features,
            "num_ms1": num_ms1,
            "num_ms2": num_ms2,
            "num_linked_ms1": num_linked_ms1,
            "num_orphans": num_orphans,
            "max_rt_correction": max_rt_correction,
            "average_rt_correction": average_rt_correction,
            "num_linked_ms2": num_linked_ms2,
        })

    # Create DataFrame with proper schema
    return pl.DataFrame(
        stats_data,
        schema={
            "sample_uid": pl.UInt64,
            "num_features": pl.UInt32,
            "num_ms1": pl.UInt32,
            "num_ms2": pl.UInt32,
            "num_linked_ms1": pl.UInt32,
            "num_orphans": pl.UInt32,
            "max_rt_correction": pl.Float64,
            "average_rt_correction": pl.Float64,
            "num_linked_ms2": pl.UInt32,
        },
    )


# =====================================================================================
# SAMPLE NAMING AND METADATA MANAGEMENT
# =====================================================================================


def metadata_reset(self):
    """
    Remove all custom metadata columns from samples_df that are not in the schema.

    This function resets samples_df to only contain the columns defined in the
    study5_schema.json specification. Any custom columns added by the user
    (e.g., custom metadata fields) will be removed.

    The following columns are preserved (as defined in study5_schema.json):
    - sample_uid: Sample unique identifier
    - sample_id: Sample unique identifier (UUID7)
    - sample_source: Path to original vendor data file
    - sample_name: Sample name
    - sample_path: Path to .sample5 file
    - sample_type: Sample type (e.g., "sample", "blank", "qc")
    - sample_group: Sample group for grouping
    - sample_batch: Batch number
    - sample_sequence: Sequence/injection order
    - sample_color: Color for visualization
    - num_features: Number of features
    - num_ms1: Number of MS1 spectra
    - num_ms2: Number of MS2 spectra

    Returns:
        None (modifies samples_df in place)

    Note:
        This operation cannot be undone. Custom metadata columns will be permanently removed.
    """
    import json
    import os

    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.warning("No samples found in study.")
        return

    # Get the schema file path (relative to this file)
    schema_path = os.path.join(
        os.path.dirname(__file__),
        "study5_schema.json",
    )

    if not os.path.exists(schema_path):
        self.logger.error(f"Schema file not found: {schema_path}")
        return

    # Load schema
    try:
        with open(schema_path, "r") as f:
            schema = json.load(f)
    except Exception as e:
        self.logger.error(f"Failed to load schema file: {e}")
        return

    # Get allowed columns from schema
    if "samples_df" not in schema or "columns" not in schema["samples_df"]:
        self.logger.error("samples_df schema not found in schema file")
        return

    allowed_columns = list(schema["samples_df"]["columns"].keys())

    # Get current columns
    current_columns = self.samples_df.columns
    columns_to_keep = [col for col in current_columns if col in allowed_columns]
    columns_to_remove = [col for col in current_columns if col not in allowed_columns]

    if not columns_to_remove:
        self.logger.info("No custom metadata columns found. samples_df already matches schema.")
        return

    # Keep only allowed columns
    self.samples_df = self.samples_df.select(columns_to_keep)

    self.logger.info(
        f"Removed {len(columns_to_remove)} custom metadata columns: {columns_to_remove}",
    )
    self.logger.debug(f"Retained {len(columns_to_keep)} schema columns: {columns_to_keep}")


def metadata_import(self, source, reset=False):
    """
    Import metadata from a DataFrame or file and merge with samples_df.

    This function imports custom metadata columns from various sources (Pandas/Polars DataFrames,
    CSV files, Excel files) and merges them with the existing samples_df. The first column of the
    source is used as the key to match samples by either sample_id or sample_name.

    Parameters:
        source (pl.DataFrame, pd.DataFrame, or str): Metadata source:
                                                     - Polars DataFrame
                                                     - Pandas DataFrame
                                                     - str: Path to CSV file (.csv)
                                                     - str: Path to Excel file (.xlsx, .xls)
        reset (bool): If True, removes pre-existing custom columns that match incoming column names
                     before importing. Schema columns (defined in study5_schema.json) are never removed.
                     Default is False (keeps existing columns, overwrites values at matching rows).

    Returns:
        None (modifies samples_df in place by adding/updating metadata columns)

    Raises:
        ValueError: If source is invalid, first column doesn't match samples, or file cannot be read
        FileNotFoundError: If source file path doesn't exist

    Example:
        # Import from CSV file (update existing values)
        study.metadata_import('sample_metadata.csv')

        # Import from CSV and reset matching custom columns first
        study.metadata_import('sample_metadata.csv', reset=True)

        # Import from DataFrame
        import pandas as pd
        metadata_df = pd.DataFrame({
            'sample_name': ['sample1', 'sample2'],
            'custom_field': ['value1', 'value2']
        })
        study.metadata_import(metadata_df)

    Note:
        - Existing columns will be overwritten at matching rows
        - If reset=True, custom columns matching incoming names are removed first
        - Schema columns are always protected from removal
        - Rows are matched by the first column against sample_id or sample_name
        - Unmatched rows in the source will be ignored with a warning
    """
    import os
    import pandas as pd
    import json

    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.error("No samples found in study.")
        return

    # Convert source to DataFrame if it's a file path
    if isinstance(source, str):
        # If path is relative, make it absolute relative to study folder
        if not os.path.isabs(source):
            if hasattr(self, 'folder') and self.folder:
                # For Study class: use study folder
                source = os.path.abspath(os.path.join(self.folder, source))
                self.logger.debug(f"Resolved relative path to: {source}")
            elif hasattr(self, 'file_source') and self.file_source:
                # For Sample class: use file_source directory
                source = os.path.abspath(os.path.join(os.path.dirname(self.file_source), source))
                self.logger.debug(f"Resolved relative path to: {source}")
            else:
                # Fallback to current working directory
                source = os.path.abspath(source)
                self.logger.debug(f"Resolved relative path to: {source}")
        
        if not os.path.exists(source):
            raise FileNotFoundError(f"File not found: {source}")

        # Read file based on extension
        file_ext = os.path.splitext(source)[1].lower()

        try:
            if file_ext == ".csv":
                metadata_df = pd.read_csv(source)
                self.logger.debug(f"Loaded metadata from CSV: {source}")
            elif file_ext in [".xlsx", ".xls"]:
                metadata_df = pd.read_excel(source)
                self.logger.debug(f"Loaded metadata from Excel: {source}")
            else:
                raise ValueError(
                    f"Unsupported file format: {file_ext}. Supported formats: .csv, .xlsx, .xls",
                )
        except Exception as e:
            raise ValueError(f"Failed to read file {source}: {e}")

    elif isinstance(source, pd.DataFrame):
        metadata_df = source.copy()
        self.logger.debug("Using provided Pandas DataFrame")

    elif isinstance(source, pl.DataFrame):
        # Convert Polars to Pandas for easier handling
        metadata_df = source.to_pandas()
        self.logger.debug("Converted Polars DataFrame to Pandas")

    else:
        raise ValueError(
            "source must be a Polars DataFrame, Pandas DataFrame, or file path (str)",
        )

    # Validate DataFrame has at least 2 columns (key + at least one metadata column)
    if metadata_df.shape[1] < 2:
        raise ValueError(
            "Metadata source must have at least 2 columns (key column + metadata columns)",
        )

    # Get the first column as the key column
    key_column = metadata_df.columns[0]
    self.logger.debug(f"Using first column as key: '{key_column}'")

    # Get key values from metadata
    key_values = metadata_df[key_column].tolist()

    # Determine if we're matching by sample_id or sample_name
    samples_pd = self.samples_df.to_pandas()

    # Try matching with sample_id first
    match_column = None
    if "sample_id" in samples_pd.columns:
        sample_ids = samples_pd["sample_id"].tolist()
        # Check how many values match
        matches_id = sum(1 for val in key_values if val in sample_ids)

        if matches_id > 0:
            match_column = "sample_id"
            self.logger.debug(
                f"Matching by sample_id: {matches_id}/{len(key_values)} keys found",
            )

    # If no matches with sample_id, try sample_name
    if match_column is None:
        sample_names = samples_pd["sample_name"].tolist()
        matches_name = sum(1 for val in key_values if val in sample_names)

        if matches_name > 0:
            match_column = "sample_name"
            self.logger.debug(
                f"Matching by sample_name: {matches_name}/{len(key_values)} keys found",
            )
        else:
            raise ValueError(
                f"First column '{key_column}' values do not match any sample_id or sample_name in samples_df",
            )

    # Rename the key column in metadata to match the target column
    metadata_df = metadata_df.rename(columns={key_column: match_column})

    # Get schema columns that must never be removed
    schema_path = os.path.join(os.path.dirname(__file__), "study5_schema.json")
    protected_columns = set()
    
    if os.path.exists(schema_path):
        try:
            with open(schema_path, "r") as f:
                schema = json.load(f)
                if "samples_df" in schema and "columns" in schema["samples_df"]:
                    protected_columns = set(schema["samples_df"]["columns"].keys())
                    self.logger.debug(f"Protected {len(protected_columns)} schema columns from removal")
        except Exception as e:
            self.logger.warning(f"Could not load schema for column protection: {e}")

    # Identify columns to import (all metadata columns except the match column)
    existing_columns = set(samples_pd.columns)
    metadata_columns = set(metadata_df.columns) - {match_column}
    
    # Separate into new columns and existing columns
    new_columns = metadata_columns - existing_columns
    existing_to_update = metadata_columns & existing_columns

    # Handle reset parameter
    if reset and existing_to_update:
        # Remove existing custom columns that will be replaced (but never schema columns)
        columns_to_reset = existing_to_update - protected_columns
        
        if columns_to_reset:
            self.logger.info(
                f"Resetting {len(columns_to_reset)} existing custom columns: {sorted(columns_to_reset)}",
            )
            # Drop these columns from samples_pd before merging
            samples_pd = samples_pd.drop(columns=list(columns_to_reset))
            # Update the existing_columns set
            existing_columns = set(samples_pd.columns)
            # These are now "new" columns since we removed them
            new_columns = metadata_columns - existing_columns
            existing_to_update = metadata_columns & existing_columns
        
        protected_skipped = (metadata_columns & existing_columns) & protected_columns
        if protected_skipped:
            self.logger.warning(
                f"Cannot reset {len(protected_skipped)} schema-protected columns: {sorted(protected_skipped)}",
            )

    # Report what will happen
    if new_columns:
        self.logger.info(f"Adding {len(new_columns)} new columns: {sorted(new_columns)}")
    
    if existing_to_update:
        self.logger.info(
            f"Updating {len(existing_to_update)} existing columns: {sorted(existing_to_update)}",
        )

    if not new_columns and not existing_to_update:
        self.logger.warning("No columns to import")
        return

    # Select columns to merge from metadata
    columns_to_merge = [match_column] + sorted(metadata_columns)
    metadata_to_merge = metadata_df[columns_to_merge]

    # Check for unmatched rows
    unmatched = metadata_to_merge[~metadata_to_merge[match_column].isin(samples_pd[match_column])]
    if len(unmatched) > 0:
        self.logger.warning(
            f"{len(unmatched)} rows in metadata do not match any samples and will be ignored",
        )

    # Merge with samples_df using left join (keep all samples, add metadata where available)
    # Use suffixes to handle column name conflicts for existing columns
    merged_pd = samples_pd.merge(
        metadata_to_merge,
        on=match_column,
        how="left",
        suffixes=("_old", ""),  # Keep new values without suffix, mark old values with _old
    )

    # For columns that existed and are being updated, drop the old versions
    if existing_to_update:
        old_columns_to_drop = [f"{col}_old" for col in existing_to_update if f"{col}_old" in merged_pd.columns]
        if old_columns_to_drop:
            merged_pd = merged_pd.drop(columns=old_columns_to_drop)
            self.logger.debug(f"Dropped {len(old_columns_to_drop)} old column versions after merge")

    # Reorder columns to match schema order: core columns first, then custom columns
    if os.path.exists(schema_path):
        try:
            with open(schema_path, "r") as f:
                schema = json.load(f)
                if "samples_df" in schema and "columns" in schema["samples_df"]:
                    # Get schema column order
                    schema_columns = list(schema["samples_df"]["columns"].keys())
                    
                    # Separate columns into core (from schema) and custom (not in schema)
                    current_columns = list(merged_pd.columns)
                    core_columns = [col for col in schema_columns if col in current_columns]
                    custom_columns = [col for col in current_columns if col not in schema_columns]
                    
                    # Reorder: core columns in schema order, then custom columns sorted
                    ordered_columns = core_columns + sorted(custom_columns)
                    merged_pd = merged_pd[ordered_columns]
                    
                    self.logger.debug(
                        f"Reordered columns: {len(core_columns)} core columns, {len(custom_columns)} custom columns"
                    )
        except Exception as e:
            self.logger.warning(f"Could not reorder columns according to schema: {e}")

    # Convert back to Polars
    self.samples_df = pl.from_pandas(merged_pd)

    # Log summary
    total_imported = len(new_columns) + len(existing_to_update)
    self.logger.success(
        f"Successfully imported {total_imported} metadata columns into samples_df "
        f"({len(new_columns)} new, {len(existing_to_update)} updated)",
    )


def set_samples_name(self, replace_dict):
    """
    Replace sample names in samples_df using a dictionary mapping.

    This function applies a batch rename operation to sample names, replacing all occurrences
    of keys in the replace_dict with their corresponding values. Validates that resulting
    names are unique before applying changes.

    Parameters:
        replace_dict (dict): Dictionary mapping old names (keys) to new names (values).
                           All keys found in sample names will be replaced with their
                           corresponding values.
                           e.g., {"old_name1": "new_name1", "old_name2": "new_name2"}

    Returns:
        None

    Raises:
        ValueError: If replace_dict is not a dictionary
        ValueError: If resulting sample names are not unique
    """
    if not isinstance(replace_dict, dict):
        raise ValueError("replace_dict must be a dictionary")

    if self.samples_df is None or len(self.samples_df) == 0:
        self.logger.warning("No samples found in study.")
        return

    if not replace_dict:
        self.logger.warning("Empty replace_dict provided, no changes made.")
        return

    # Get current sample names
    current_names = self.samples_df.get_column("sample_name").to_list()

    # Create a copy and apply replacements
    new_names = []
    replaced_count = 0

    for name in current_names:
        if name in replace_dict:
            new_names.append(replace_dict[name])
            replaced_count += 1
            self.logger.debug(
                f"Replacing sample name: '{name}' -> '{replace_dict[name]}'",
            )
        else:
            new_names.append(name)

    # Check that all new names are unique
    if len(set(new_names)) != len(new_names):
        duplicates = []
        seen = set()
        for name in new_names:
            if name in seen:
                duplicates.append(name)
            else:
                seen.add(name)
        raise ValueError(
            f"Resulting sample names are not unique. Duplicates found: {duplicates}",
        )

    # If we get here, all names are unique - apply the changes
    self.samples_df = self.samples_df.with_columns(
        pl.Series("sample_name", new_names).alias("sample_name"),
    )

    self.logger.success(f"Successfully replaced {replaced_count} sample names")


def samples_name_reset(self):
    """
    Reset all sample names to match their file basenames (without extensions).

    Extracts the filename from each sample's sample_path, removes all file extensions
    (handles multi-part extensions like .tar.gz, .sample5.gz), and validates that
    resulting names are unique before applying changes.

    Returns:
        None

    Raises:
        ValueError: If resulting sample names are not unique
        RuntimeError: If any sample_path is None or empty
    """
    import os

    if self.samples_df is None or len(self.samples_df) == 0:
        self.logger.warning("No samples found in study.")
        return

    # Get current sample paths
    sample_paths = self.samples_df.get_column("sample_path").to_list()

    # Extract basenames without extensions
    new_names = []

    for i, path in enumerate(sample_paths):
        if path is None or path == "":
            raise RuntimeError(f"Sample at index {i} has no sample_path set")

        # Get basename and remove extension(s)
        basename = os.path.basename(path)
        # Remove all extensions (handles cases like .tar.gz, .sample5.gz, etc.)
        name_without_ext = basename
        while "." in name_without_ext:
            name_without_ext = os.path.splitext(name_without_ext)[0]

        new_names.append(name_without_ext)
        self.logger.debug(
            f"Resetting sample name from path: '{path}' -> '{name_without_ext}'",
        )

    # Check that all new names are unique
    if len(set(new_names)) != len(new_names):
        duplicates = []
        seen = set()
        for name in new_names:
            if name in seen:
                duplicates.append(name)
            else:
                seen.add(name)
        raise ValueError(
            f"Resulting sample names are not unique. Duplicates found: {duplicates}",
        )

    # If we get here, all names are unique - apply the changes
    self.samples_df = self.samples_df.with_columns(
        pl.Series("sample_name", new_names).alias("sample_name"),
    )

    self.logger.info(
        f"Successfully reset {len(new_names)} sample names from sample paths",
    )


def set_samples_source(self, filename):
    """
    Reassign sample_source (raw data file paths) for all samples in samples_df.

    This function updates the sample_source column which points to the original vendor data files.
    If filename is a directory, it constructs new paths by combining the directory with existing
    basenames. If filename is a file, it uses that path directly. Validates file existence
    before updating.

    Parameters:
        filename (str): New file path or directory path for all samples

    Returns:
        None
    """
    import os

    if self.samples_df is None or len(self.samples_df) == 0:
        self.logger.warning("No samples found in study.")
        return

    updated_count = 0
    failed_count = 0

    # Get all current file_source values
    current_sources = self.samples_df.get_column("sample_source").to_list()
    sample_names = self.samples_df.get_column("sample_name").to_list()

    new_sources = []

    for i, (current_source, sample_name) in enumerate(
        zip(current_sources, sample_names),
    ):
        # Check if filename is just a directory path
        if os.path.isdir(filename):
            if current_source is None or current_source == "":
                self.logger.warning(
                    f"Cannot build path for sample '{sample_name}': no current file_source available",
                )
                new_sources.append(current_source)
                failed_count += 1
                continue

            # Get the basename from current file_source
            current_basename = os.path.basename(current_source)
            # Build new absolute path
            new_file_path = os.path.join(filename, current_basename)
        else:
            # filename is a full path, make it absolute
            new_file_path = os.path.abspath(filename)

        # Check if the new file exists
        if not os.path.exists(new_file_path):
            self.logger.warning(
                f"File does not exist for sample '{sample_name}': {new_file_path}",
            )
            new_sources.append(current_source)
            failed_count += 1
            continue

        # File exists, update source
        new_sources.append(new_file_path)
        updated_count += 1

        # Log individual updates at debug level
        self.logger.debug(
            f"Updated file_source for sample '{sample_name}': {current_source} -> {new_file_path}",
        )

    # Update the samples_df with new file_source values
    self.samples_df = self.samples_df.with_columns(
        pl.Series("file_source", new_sources).alias("file_source"),
    )

    # Log summary
    if updated_count > 0:
        self.logger.info(f"Updated file_source for {updated_count} samples")
    if failed_count > 0:
        self.logger.warning(f"Failed to update file_source for {failed_count} samples")


# =====================================================================================
# SAMPLE SELECTION AND DELETION
# =====================================================================================


def samples_select(
    self,
    sample_uid=None,
    sample_name=None,
    sample_type=None,
    sample_group=None,
    sample_batch=None,
    sample_sequence=None,
    num_features=None,
    num_ms1=None,
    num_ms2=None,
    **kwargs,
):
    """
    Select samples from samples_df based on multiple filter criteria.

    Returns a filtered subset of samples_df that match all specified criteria (AND logic).
    Supports filtering by metadata fields (type, group, batch, sequence) and quality metrics
    (feature counts, MS data). Each filter parameter accepts single values, lists, or ranges.
    
    Additional metadata columns can be filtered using keyword arguments.

    Parameters:
        sample_uid: sample UID filter (list, single value, or tuple for range)
        sample_name: sample name filter (list or single value)
        sample_type: sample type filter (list or single value)
        sample_group: sample group filter (list or single value)
        sample_batch: sample batch filter (list, single value, or tuple for range)
        sample_sequence: sample sequence filter (list, single value, or tuple for range)
        num_features: number of features filter (tuple for range, single value for minimum)
        num_ms1: number of MS1 spectra filter (tuple for range, single value for minimum)
        num_ms2: number of MS2 spectra filter (tuple for range, single value for minimum)
        **kwargs: Additional filters for any metadata column in samples_df.
                 Each kwarg should be column_name=filter_value where filter_value can be:
                 - single value: exact match
                 - list: match any value in the list
                 - tuple of 2 values: range filter (min, max) for numeric columns

    Returns:
        polars.DataFrame: Filtered samples DataFrame
        
    Example:
        # Filter by standard parameters
        study.samples_select(sample_type='sample', num_features=(100, 1000))
        
        # Filter by custom metadata columns
        study.samples_select(treatment_group='control', timepoint=[0, 24, 48])
        
        # Combine standard and custom filters
        study.samples_select(sample_type='sample', treatment_group='control', age=(20, 30))
    """
    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.warning("No samples found in study.")
        return pl.DataFrame()

    # Early return if no filters provided
    filter_params = [
        sample_uid,
        sample_name,
        sample_type,
        sample_group,
        sample_batch,
        sample_sequence,
        num_features,
        num_ms1,
        num_ms2,
    ]
    if all(param is None for param in filter_params):
        return self.samples_df.clone()

    initial_count = len(self.samples_df)

    # Pre-check available columns once for efficiency
    available_columns = set(self.samples_df.columns)

    # Build all filter conditions first, then apply them all at once
    filter_conditions = []
    warnings = []

    # Filter by sample_uid
    if sample_uid is not None:
        if isinstance(sample_uid, (list, tuple)):
            if len(sample_uid) == 2 and not isinstance(sample_uid, list):
                # Treat as range
                min_uid, max_uid = sample_uid
                filter_conditions.append(
                    (pl.col("sample_uid") >= min_uid) & (pl.col("sample_uid") <= max_uid),
                )
            else:
                # Treat as list
                filter_conditions.append(pl.col("sample_uid").is_in(sample_uid))
        else:
            filter_conditions.append(pl.col("sample_uid") == sample_uid)

    # Filter by sample_name
    if sample_name is not None:
        if isinstance(sample_name, list):
            filter_conditions.append(pl.col("sample_name").is_in(sample_name))
        else:
            filter_conditions.append(pl.col("sample_name") == sample_name)

    # Filter by sample_type
    if sample_type is not None:
        if "sample_type" in available_columns:
            if isinstance(sample_type, list):
                filter_conditions.append(pl.col("sample_type").is_in(sample_type))
            else:
                filter_conditions.append(pl.col("sample_type") == sample_type)
        else:
            warnings.append("'sample_type' column not found in samples_df")

    # Filter by sample_group
    if sample_group is not None:
        if "sample_group" in available_columns:
            if isinstance(sample_group, list):
                filter_conditions.append(pl.col("sample_group").is_in(sample_group))
            else:
                filter_conditions.append(pl.col("sample_group") == sample_group)
        else:
            warnings.append("'sample_group' column not found in samples_df")

    # Filter by sample_batch
    if sample_batch is not None:
        if "sample_batch" in available_columns:
            if isinstance(sample_batch, (list, tuple)):
                if len(sample_batch) == 2 and not isinstance(sample_batch, list):
                    # Treat as range
                    min_batch, max_batch = sample_batch
                    filter_conditions.append(
                        (pl.col("sample_batch") >= min_batch) & (pl.col("sample_batch") <= max_batch),
                    )
                else:
                    # Treat as list
                    filter_conditions.append(pl.col("sample_batch").is_in(sample_batch))
            else:
                filter_conditions.append(pl.col("sample_batch") == sample_batch)
        else:
            warnings.append("'sample_batch' column not found in samples_df")

    # Filter by sample_sequence
    if sample_sequence is not None:
        if "sample_sequence" in available_columns:
            if isinstance(sample_sequence, (list, tuple)):
                if len(sample_sequence) == 2 and not isinstance(sample_sequence, list):
                    # Treat as range
                    min_seq, max_seq = sample_sequence
                    filter_conditions.append(
                        (pl.col("sample_sequence") >= min_seq) & (pl.col("sample_sequence") <= max_seq),
                    )
                else:
                    # Treat as list
                    filter_conditions.append(
                        pl.col("sample_sequence").is_in(sample_sequence),
                    )
            else:
                filter_conditions.append(pl.col("sample_sequence") == sample_sequence)
        else:
            warnings.append("'sample_sequence' column not found in samples_df")

    # Filter by num_features
    if num_features is not None:
        if "num_features" in available_columns:
            if isinstance(num_features, tuple) and len(num_features) == 2:
                min_features, max_features = num_features
                filter_conditions.append(
                    (pl.col("num_features") >= min_features) & (pl.col("num_features") <= max_features),
                )
            else:
                filter_conditions.append(pl.col("num_features") >= num_features)
        else:
            warnings.append("'num_features' column not found in samples_df")

    # Filter by num_ms1
    if num_ms1 is not None:
        if "num_ms1" in available_columns:
            if isinstance(num_ms1, tuple) and len(num_ms1) == 2:
                min_ms1, max_ms1 = num_ms1
                filter_conditions.append(
                    (pl.col("num_ms1") >= min_ms1) & (pl.col("num_ms1") <= max_ms1),
                )
            else:
                filter_conditions.append(pl.col("num_ms1") >= num_ms1)
        else:
            warnings.append("'num_ms1' column not found in samples_df")

    # Filter by num_ms2
    if num_ms2 is not None:
        if "num_ms2" in available_columns:
            if isinstance(num_ms2, tuple) and len(num_ms2) == 2:
                min_ms2, max_ms2 = num_ms2
                filter_conditions.append(
                    (pl.col("num_ms2") >= min_ms2) & (pl.col("num_ms2") <= max_ms2),
                )
            else:
                filter_conditions.append(pl.col("num_ms2") >= num_ms2)
        else:
            warnings.append("'num_ms2' column not found in samples_df")

    # Filter by additional metadata columns passed as kwargs
    for column_name, filter_value in kwargs.items():
        if column_name in available_columns:
            if isinstance(filter_value, (list, tuple)):
                if len(filter_value) == 2 and not isinstance(filter_value, list):
                    # Treat as range (for numeric columns)
                    min_val, max_val = filter_value
                    try:
                        filter_conditions.append(
                            (pl.col(column_name) >= min_val) & (pl.col(column_name) <= max_val),
                        )
                    except Exception:
                        # If range comparison fails, treat as list
                        filter_conditions.append(pl.col(column_name).is_in(filter_value))
                else:
                    # Treat as list of values
                    filter_conditions.append(pl.col(column_name).is_in(filter_value))
            else:
                # Single value - exact match
                filter_conditions.append(pl.col(column_name) == filter_value)
        else:
            warnings.append(f"'{column_name}' column not found in samples_df")

    # Log all warnings once at the end for efficiency
    for warning in warnings:
        self.logger.warning(warning)

    # Apply all filters at once using lazy evaluation for optimal performance
    if filter_conditions:
        # Combine all conditions with AND
        combined_filter = filter_conditions[0]
        for condition in filter_conditions[1:]:
            combined_filter = combined_filter & condition

        # Apply the combined filter using lazy evaluation
        samples = self.samples_df.lazy().filter(combined_filter).collect()
    else:
        samples = self.samples_df.clone()

    final_count = len(samples)

    if final_count == 0:
        self.logger.warning("No samples remaining after applying selection criteria.")
    else:
        self.logger.info(f"Samples selected: {final_count} (out of {initial_count})")

    return samples


def samples_delete(self, samples):
    """
    Delete samples and all associated data from the entire study.

    This function performs a comprehensive deletion of samples and all related data across
    all study DataFrames. This is a destructive operation that cannot be undone.

    The following data is removed:
    - samples_df: Removes the sample rows
    - features_df: Removes all features belonging to these samples
    - consensus_mapping_df: Removes mappings for features from these samples
    - consensus_ms2: Removes MS2 spectra for features from these samples
    - feature_maps: Removes the corresponding feature maps

    Parameters:
        samples: Samples to delete. Can be:
                - list of int: List of sample_uids to delete
                - polars.DataFrame: DataFrame obtained from samples_select (will use sample_uid column)
                - int: Single sample_uid to delete

    Returns:
        None (modifies study DataFrames and feature_maps in place)
    """
    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.warning("No samples found in study.")
        return

    # Early return if no samples provided
    if samples is None:
        self.logger.warning("No samples provided for deletion.")
        return

    initial_sample_count = len(self.samples_df)

    # Determine sample_uids to remove
    if isinstance(samples, pl.DataFrame):
        if "sample_uid" not in samples.columns:
            self.logger.error("samples DataFrame must contain 'sample_uid' column")
            return
        sample_uids_to_remove = samples["sample_uid"].to_list()
    elif isinstance(samples, (list, tuple)):
        sample_uids_to_remove = list(samples)  # Convert tuple to list if needed
    elif isinstance(samples, int):
        sample_uids_to_remove = [samples]
    else:
        self.logger.error("samples parameter must be a DataFrame, list, tuple, or int")
        return

    # Early return if no UIDs to remove
    if not sample_uids_to_remove:
        self.logger.warning("No sample UIDs provided for deletion.")
        return

    # Convert to set for faster lookup if list is large
    if len(sample_uids_to_remove) > 100:
        sample_uids_set = set(sample_uids_to_remove)
        # Use the set for filtering if it's significantly smaller
        if len(sample_uids_set) < len(sample_uids_to_remove) * 0.8:
            sample_uids_to_remove = list(sample_uids_set)

    self.logger.info(
        f"Deleting {len(sample_uids_to_remove)} samples and all related data...",
    )

    # Get feature_uids that need to be removed from features_df
    feature_uids_to_remove = []
    initial_features_count = 0
    if self.features_df is not None and not self.features_df.is_empty():
        initial_features_count = len(self.features_df)
        feature_uids_to_remove = self.features_df.filter(
            pl.col("sample_uid").is_in(sample_uids_to_remove),
        )["feature_uid"].to_list()

    # 1. Remove samples from samples_df
    self.samples_df = self.samples_df.filter(
        ~pl.col("sample_uid").is_in(sample_uids_to_remove),
    )

    # 2. Remove corresponding features from features_df
    removed_features_count = 0
    if feature_uids_to_remove and self.features_df is not None and not self.features_df.is_empty():
        self.features_df = self.features_df.filter(
            ~pl.col("sample_uid").is_in(sample_uids_to_remove),
        )
        removed_features_count = initial_features_count - len(self.features_df)

    # 3. Remove from consensus_mapping_df
    removed_mapping_count = 0
    if feature_uids_to_remove and self.consensus_mapping_df is not None and not self.consensus_mapping_df.is_empty():
        initial_mapping_count = len(self.consensus_mapping_df)
        self.consensus_mapping_df = self.consensus_mapping_df.filter(
            ~pl.col("feature_uid").is_in(feature_uids_to_remove),
        )
        removed_mapping_count = initial_mapping_count - len(self.consensus_mapping_df)

    # 4. Remove from consensus_ms2 if it exists
    removed_ms2_count = 0
    if hasattr(self, "consensus_ms2") and self.consensus_ms2 is not None and not self.consensus_ms2.is_empty():
        initial_ms2_count = len(self.consensus_ms2)
        self.consensus_ms2 = self.consensus_ms2.filter(
            ~pl.col("sample_uid").is_in(sample_uids_to_remove),
        )
        removed_ms2_count = initial_ms2_count - len(self.consensus_ms2)

    # Calculate and log results
    removed_sample_count = initial_sample_count - len(self.samples_df)
    final_sample_count = len(self.samples_df)

    # Create comprehensive summary message
    summary_parts = [
        f"Deleted {removed_sample_count} samples",
    ]

    if removed_features_count > 0:
        summary_parts.append(f"{removed_features_count} features")

    if removed_mapping_count > 0:
        summary_parts.append(f"{removed_mapping_count} consensus mappings")

    if removed_ms2_count > 0:
        summary_parts.append(f"{removed_ms2_count} MS2 spectra")

    summary_parts.append(f"Remaining samples: {final_sample_count}")

    self.logger.info(". ".join(summary_parts))


# =====================================================================================
# SAMPLE COLOR PALETTE MANAGEMENT
# =====================================================================================


def set_samples_color(self, by=None, palette="Turbo256"):
    """
    Assign colors to samples for visualization using various strategies and palettes.

    This function sets the sample_color column in samples_df, which is used by plotting
    functions to consistently color samples across different visualizations. Colors can be
    assigned sequentially, by metadata grouping, or from a custom list.

    The default behavior (by=None) samples colors evenly from the specified palette,
    ensuring good color separation across all samples.

    Parameters:
        by (str or list, optional): Property to base colors on. Options:
                                     - 'sample_uid': Use sample_uid values to assign colors
                                     - 'sample_index': Use sample index (position) to assign colors
                                     - 'sample_type': Use sample_type values to assign colors
                                     - 'sample_name': Use sample_name values to assign colors
                                     - Any metadata column name: Use that column's values to assign colors
                                     - list of colors: Use provided list of hex color codes
                                     - None: Use sequential colors from palette (default)
        palette (str): Color palette to use. Options:
                      - 'Turbo256': Turbo colormap (256 colors, perceptually uniform)
                      - 'Viridis256': Viridis colormap (256 colors, perceptually uniform)
                      - 'Plasma256': Plasma colormap (256 colors, perceptually uniform)
                      - 'Inferno256': Inferno colormap (256 colors, perceptually uniform)
                      - 'Magma256': Magma colormap (256 colors, perceptually uniform)
                      - 'Cividis256': Cividis colormap (256 colors, colorblind-friendly)
                      - 'Set1': Qualitative palette (9 distinct colors)
                      - 'Set2': Qualitative palette (8 distinct colors)
                      - 'Set3': Qualitative palette (12 distinct colors)
                      - 'Tab10': Tableau 10 palette (10 distinct colors)
                      - 'Tab20': Tableau 20 palette (20 distinct colors)
                      - 'Dark2': Dark qualitative palette (8 colors)
                      - 'Paired': Paired qualitative palette (12 colors)
                      - 'Spectral': Spectral diverging colormap
                      - 'Rainbow': Rainbow colormap
                      - 'Coolwarm': Cool-warm diverging colormap
                      - 'Seismic': Seismic diverging colormap
                      - Any other colormap name supported by the cmap library

                      For a complete catalog of available colormaps, see:
                      https://cmap-docs.readthedocs.io/en/latest/catalog/

    Returns:
        None (modifies self.samples_df in place)

    Example:
        # Set colors based on sample type
        study.set_sample_color(by='sample_type', palette='Set1')

        # Set colors based on a custom metadata column
        study.set_sample_color(by='treatment_group', palette='Tab10')

        # Set colors using a custom color list
        study.set_sample_color(by=['#FF0000', '#00FF00', '#0000FF'])

        # Reset to default Turbo256 sequential colors
        study.set_sample_color()
    """
    if self.samples_df is None or len(self.samples_df) == 0:
        self.logger.warning("No samples found in study.")
        return

    sample_count = len(self.samples_df)

    # Handle custom color list
    if isinstance(by, list):
        if len(by) < sample_count:
            self.logger.warning(
                f"Provided color list has {len(by)} colors but {sample_count} samples. Repeating colors.",
            )
            # Cycle through the provided colors if there aren't enough
            colors = []
            for i in range(sample_count):
                colors.append(by[i % len(by)])
        else:
            colors = by[:sample_count]
    else:
        # Use the new approach: sample colors evenly from the whole colormap
        if by is None:
            # Sequential colors evenly sampled from the colormap
            try:
                colors = _sample_colors_from_colormap(palette, sample_count)
            except ValueError as e:
                self.logger.error(f"Error sampling colors from colormap: {e}")
                return

        elif by == "sample_uid":
            # Use sample_uid to determine position in evenly sampled colormap
            sample_uids = self.samples_df["sample_uid"].to_list()
            try:
                # Sample colors evenly for the number of samples
                palette_colors = _sample_colors_from_colormap(palette, sample_count)
                colors = []
                for uid in sample_uids:
                    # Use modulo to cycle through evenly sampled colors
                    color_index = uid % len(palette_colors)
                    colors.append(palette_colors[color_index])
            except ValueError as e:
                self.logger.error(f"Error sampling colors from colormap: {e}")
                return

        elif by == "sample_index":
            # Use sample index (position in DataFrame) with evenly sampled colors
            try:
                colors = _sample_colors_from_colormap(palette, sample_count)
            except ValueError as e:
                self.logger.error(f"Error sampling colors from colormap: {e}")
                return

        elif by == "sample_type":
            # Use sample_type to assign colors - same type gets same color
            # Sample colors evenly across colormap for unique types
            sample_types = self.samples_df["sample_type"].to_list()
            unique_types = list({t for t in sample_types if t is not None})

            try:
                # Sample colors evenly for unique types
                type_colors = _sample_colors_from_colormap(palette, len(unique_types))
                type_to_color = {}

                for i, sample_type in enumerate(unique_types):
                    type_to_color[sample_type] = type_colors[i]

                colors = []
                for sample_type in sample_types:
                    if sample_type is None:
                        # Default to first color for None
                        colors.append(type_colors[0] if type_colors else "#000000")
                    else:
                        colors.append(type_to_color[sample_type])
            except ValueError as e:
                self.logger.error(f"Error sampling colors from colormap: {e}")
                return

        elif by == "sample_name":
            # Use sample_name to assign colors - same name gets same color (unlikely but possible)
            # Sample colors evenly across colormap for unique names
            sample_names = self.samples_df["sample_name"].to_list()
            unique_names = list({n for n in sample_names if n is not None})

            try:
                # Sample colors evenly for unique names
                name_colors = _sample_colors_from_colormap(palette, len(unique_names))
                name_to_color = {}

                for i, sample_name in enumerate(unique_names):
                    name_to_color[sample_name] = name_colors[i]

                colors = []
                for sample_name in sample_names:
                    if sample_name is None:
                        # Default to first color for None
                        colors.append(name_colors[0] if name_colors else "#000000")
                    else:
                        colors.append(name_to_color[sample_name])
            except ValueError as e:
                self.logger.error(f"Error sampling colors from colormap: {e}")
                return
        else:
            # Check if 'by' is a column name in samples_df (metadata column)
            if by in self.samples_df.columns:
                self.logger.debug(f"Using metadata column '{by}' for color assignment")
                column_values = self.samples_df[by].to_list()
                unique_values = list({v for v in column_values if v is not None})

                try:
                    # Sample colors evenly for unique values
                    value_colors = _sample_colors_from_colormap(palette, len(unique_values))
                    value_to_color = {}

                    for i, value in enumerate(unique_values):
                        value_to_color[value] = value_colors[i]

                    colors = []
                    for value in column_values:
                        if value is None:
                            # Default to first color for None
                            colors.append(value_colors[0] if value_colors else "#808080")
                        else:
                            colors.append(value_to_color[value])
                except ValueError as e:
                    self.logger.error(f"Error sampling colors from colormap: {e}")
                    return
            else:
                self.logger.error(
                    f"Invalid by value: '{by}'. Must be 'sample_uid', 'sample_index', 'sample_type', "
                    f"'sample_name', a valid column name in samples_df, a list of colors, or None.",
                )
                return

    # Update the sample_color column
    self.samples_df = self.samples_df.with_columns(
        pl.Series("sample_color", colors).alias("sample_color"),
    )

    if isinstance(by, list):
        self.logger.debug(
            f"Set sample colors using provided color list ({len(by)} colors)",
        )
    elif by is None:
        self.logger.debug(f"Set sequential sample colors using {palette} palette")
    else:
        self.logger.debug(f"Set sample colors based on {by} using {palette} palette")


def _sample_colors_from_colormap(palette_name, n_colors):
    """
    Sample N colors evenly distributed across the full colormap range.

    This internal utility function extracts colors from a colormap with even spacing,
    avoiding extreme endpoints (very dark/light colors) by sampling from the 10-90% range.
    Uses the cmap library for access to scientific and qualitative colormaps.

    Parameters:
        palette_name (str): Name of the palette/colormap
        n_colors (int): Number of colors to sample

    Returns:
        list: List of hex color codes sampled evenly from the colormap

    Raises:
        ValueError: If palette_name is not supported
    """
    try:
        from cmap import Colormap
    except ImportError:
        raise ValueError(
            "cmap library is required for color palettes. Install with: pip install cmap",
        )

    # Map common palette names to cmap names (same as _get_color_palette)
    palette_mapping = {
        # Scientific colormaps
        "Turbo256": "turbo",
        "Viridis256": "viridis",
        "Plasma256": "plasma",
        "Inferno256": "inferno",
        "Magma256": "magma",
        "Cividis256": "cividis",
        # Qualitative palettes
        "Set1": "Set1",
        "Set2": "Set2",
        "Set3": "Set3",
        "Tab10": "tab10",
        "Tab20": "tab20",
        "Dark2": "Dark2",
        "Paired": "Paired",
        # Additional useful palettes
        "Spectral": "Spectral",
        "Rainbow": "rainbow",
        "Coolwarm": "coolwarm",
        "Seismic": "seismic",
    }

    # Get the cmap name
    cmap_name = palette_mapping.get(palette_name, palette_name.lower())

    try:
        # Create colormap
        cm = Colormap(cmap_name)

        colors = []

        # Distribute samples evenly across the full colormap range (same approach as set_sample_color(by=None))
        for i in range(n_colors):
            # Evenly distribute samples across colormap (avoiding endpoints to prevent white/black)
            normalized_value = (i + 0.5) / n_colors  # +0.5 to center samples in their bins
            # Map to a subset of colormap to avoid extreme colors (use 10% to 90% range)
            normalized_value = 0.1 + (normalized_value * 0.8)

            color_rgba = cm(normalized_value)

            # Convert RGBA to hex
            if len(color_rgba) >= 3:
                r, g, b = color_rgba[:3]
                # Convert to 0-255 range if needed
                if max(color_rgba[:3]) <= 1.0:
                    r, g, b = int(r * 255), int(g * 255), int(b * 255)
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                colors.append(hex_color)

        return colors

    except Exception as e:
        raise ValueError(
            f"Failed to create colormap '{cmap_name}': {e}. Available palettes: {list(palette_mapping.keys())}",
        )
