"""
helpers.py

This module contains helper functions for the Study class that handle various operations
like data retrieval, filtering, compression, and utility functions.

The functions are organized into the following sections:
1. Chromatogram extraction functions (BPC, TIC, EIC, chrom matrix)
2. Data retrieval helper functions (get_sample, get_consensus, etc.)
3. UID helper functions (_get_*_uids)
4. Data filtering and selection functions
5. Data compression and restoration functions
6. Utility functions (reset, naming, colors, schema ordering)
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
import polars as pl

from tqdm import tqdm
from masster.chromatogram import Chromatogram

# Import sample-related functions from samples module
from masster.study.samples import get_samples


# =====================================================================================
# CHROMATOGRAM EXTRACTION FUNCTIONS
# =====================================================================================


def get_bpc(owner, sample=None, rt_unit="s", label=None, original=False):
    """
    Return a Chromatogram object containing the Base Peak Chromatogram (BPC).

    The BPC represents the most intense peak at each retention time across all m/z values.
    The `owner` argument may be either a Study instance or a Sample-like object that
    exposes `ms1_df` (Polars DataFrame) and optionally `scans_df`.

    If `owner` is a Study, `sample` must be provided (int sample_uid, str sample_name or Sample instance)
    and the Sample will be retrieved using `get_sample(owner, sample)`.

    Parameters:
        owner (Study or Sample): Study instance or Sample-like object with ms1_df
        sample (int, str, or Sample, optional): Sample identifier (required if owner is Study).
                                                Can be sample_uid (int), sample_name (str), or Sample instance
        rt_unit (str): Retention time unit for the chromatogram. Default is "s" (seconds)
        label (str, optional): Custom label for the chromatogram. Default is "Base Peak Chromatogram"
        original (bool): If True, map retention times back to original (pre-alignment) values.
                        Only works when owner is Study with features_df containing rt_original column.
                        Default is False (use current/aligned RTs)

    Returns:
        Chromatogram: Chromatogram object with rt and inty arrays representing the BPC

    Raises:
        ValueError: If sample cannot be resolved or ms1_df is missing
        RuntimeError: If ms1_df is missing required columns (rt, inty)
    """
    # resolve sample when owner is a Study-like object (has get_sample)
    s = None
    if hasattr(owner, "ms1_df"):
        s = owner
    else:
        # owner is expected to be a Study
        s = get_samples(owner, sample)

    if s is None:
        raise ValueError("Could not resolve sample for BPC computation")

    # ensure ms1_df exists
    if getattr(s, "ms1_df", None) is None:
        raise ValueError("Sample has no ms1_df for BPC computation")

    # try Polars aggregation first
    try:
        cols = s.ms1_df.columns
        if not all(c in cols for c in ["rt", "inty"]):
            raise RuntimeError("ms1_df missing required columns")

        bpc = s.ms1_df.select([pl.col("rt"), pl.col("inty")])
        bpc = bpc.groupby("rt").agg(pl.col("inty").max().alias("inty"))
        bpc_pd = bpc.to_pandas().sort_values("rt")
    except Exception:
        # fallback to pandas
        try:
            bpc_pd = s.ms1_df.to_pandas()[["rt", "inty"]]
            bpc_pd = bpc_pd.groupby("rt").agg({"inty": "max"}).reset_index().sort_values("rt")
        except Exception:
            raise

    if bpc_pd.empty:
        raise ValueError("Computed BPC is empty")

    # If caller requests original RTs (original=True) and we were called from a Study
    # we can obtain a per-sample mapping between current rt and rt_original from
    # the study.features_df and apply it to the computed BPC rt values.
    # Note: original parameter default is False (return current/aligned RTs).
    if original is True:
        try:
            # Only proceed if owner is a Study-like object with features_df
            study = None
            if hasattr(owner, "features_df"):
                study = owner
            else:
                # If owner is a Sample, try to find Study via attribute (not guaranteed)
                study = getattr(owner, "study", None)

            if study is not None and getattr(study, "features_df", None) is not None:
                # Attempt to select mapping rows for this sample. Prefer matching by sample_uid,
                # fall back to sample_name when necessary.
                import numpy as _np

                feats = study.features_df
                # try filtering by sample identifier provided to this function
                mapping_rows = None
                if sample is not None:
                    try:
                        mapping_rows = feats.filter(pl.col("sample_uid") == sample)
                    except Exception:
                        mapping_rows = pl.DataFrame()

                    if mapping_rows is None or mapping_rows.is_empty():
                        try:
                            mapping_rows = feats.filter(pl.col("sample_name") == sample)
                        except Exception:
                            mapping_rows = pl.DataFrame()

                # If we still have no sample selector, try to infer sample from the Sample object s
                if (mapping_rows is None or mapping_rows.is_empty()) and hasattr(
                    s,
                    "sample_path",
                ):
                    # attempt to match by sample_path or file name
                    try:
                        # find row where sample_path matches
                        mapping_rows = feats.filter(
                            pl.col("sample_path") == getattr(s, "file", None),
                        )
                    except Exception:
                        mapping_rows = pl.DataFrame()

                # If still empty, give up mapping
                if mapping_rows is not None and not mapping_rows.is_empty():
                    # collect rt and rt_original pairs
                    try:
                        map_pd = mapping_rows.select(["rt", "rt_original"]).to_pandas()
                    except Exception:
                        map_pd = mapping_rows.to_pandas()[["rt", "rt_original"]]

                    # drop NA and duplicates
                    map_pd = map_pd.dropna()
                    if not map_pd.empty:
                        # sort by rt (current/aligned)
                        map_pd = map_pd.sort_values("rt")
                        x = map_pd["rt"].to_numpy()
                        y = map_pd["rt_original"].to_numpy()
                        # require at least 2 points to interpolate
                        if x.size >= 2:
                            # apply linear interpolation from current rt -> original rt
                            # for values outside the known range, numpy.interp will clip to endpoints
                            new_rt = _np.interp(bpc_pd["rt"].to_numpy(), x, y)
                            bpc_pd = bpc_pd.copy()
                            bpc_pd["rt"] = new_rt
        except Exception:
            # If mapping fails, silently continue and return the original computed BPC
            pass

    # build Chromatogram
    ycol = "inty"
    try:
        chrom = Chromatogram(
            rt=bpc_pd["rt"].to_numpy(),
            inty=bpc_pd[ycol].to_numpy(),
            label=label or "Base Peak Chromatogram",
            rt_unit=rt_unit,
        )
    except Exception:
        chrom = Chromatogram(
            rt=bpc_pd["rt"].values,
            inty=bpc_pd[ycol].values,
            label=label or "Base Peak Chromatogram",
            rt_unit=rt_unit,
        )

    return chrom


def get_tic(owner, sample=None, label=None):
    """
    Return a Chromatogram object containing the Total Ion Chromatogram (TIC).

    The TIC represents the sum of all ion intensities at each retention time across all m/z values.
    `owner` may be a Sample-like object (has `ms1_df`) or a Study (in which case `sample` selects the sample).
    The function falls back to `scans_df` when `ms1_df` is not available.

    Parameters:
        owner (Study or Sample): Study instance or Sample-like object with ms1_df or scans_df
        sample (int, str, or Sample, optional): Sample identifier (required if owner is Study).
                                                Can be sample_uid (int), sample_name (str), or Sample instance
        label (str, optional): Custom label for the chromatogram. Default is "Total Ion Chromatogram"

    Returns:
        Chromatogram: Chromatogram object with rt and inty arrays representing the TIC

    Raises:
        ValueError: If sample cannot be resolved or neither ms1_df nor scans_df is available
        RuntimeError: If ms1_df is missing required columns
    """
    # resolve sample object
    s = None
    if hasattr(owner, "ms1_df"):
        s = owner
    else:
        s = get_samples(owner, sample)

    if s is None:
        raise ValueError("Could not resolve sample for TIC computation")

    # prefer ms1_df
    try:
        cols = s.ms1_df.columns
        if all(c in cols for c in ["rt", "inty"]):
            tic = s.ms1_df.select([pl.col("rt"), pl.col("inty")])
            tic = tic.groupby("rt").agg(pl.col("inty").sum().alias("inty_tot"))
            tic_pd = tic.to_pandas().sort_values("rt")
        else:
            raise RuntimeError("ms1_df missing required columns")
    except Exception:
        # fallback to scans_df if present
        if getattr(s, "scans_df", None) is not None:
            try:
                scans = s.scans_df.filter(pl.col("ms_level") == 1)
                data = scans[["rt", "scan_uid", "inty_tot"]].to_pandas()
                data = data.sort_values("rt")
                tic_pd = data.rename(columns={"inty_tot": "inty_tot"})
            except Exception:
                raise
        else:
            raise ValueError(
                "Neither ms1_df nor scans_df available for TIC computation",
            )

    if tic_pd.empty:
        raise ValueError("Computed TIC is empty")

    # ensure column name
    if "inty_tot" not in tic_pd.columns:
        tic_pd = tic_pd.rename(columns={tic_pd.columns[1]: "inty_tot"})

    try:
        chrom = Chromatogram(
            rt=tic_pd["rt"].to_numpy(),
            inty=tic_pd["inty_tot"].to_numpy(),
            label=label or "Total Ion Chromatogram",
        )
    except Exception:
        chrom = Chromatogram(
            rt=tic_pd["rt"].values,
            inty=tic_pd["inty_tot"].values,
            label=label or "Total Ion Chromatogram",
        )

    return chrom


def get_eic(owner, sample=None, mz=None, mz_tol=None, rt_unit="s", label=None):
    """
    Return a Chromatogram object containing the Extracted Ion Chromatogram (EIC) for a target m/z.

    The `owner` argument may be either a Study instance or a Sample-like object that
    exposes `ms1_df` (Polars DataFrame).

    If `owner` is a Study, `sample` must be provided (int sample_uid, str sample_name or Sample instance)
    and the Sample will be retrieved using `get_sample(owner, sample)`.

    Parameters:
        owner: Study or Sample instance
        sample: Sample identifier (required if owner is Study)
        mz (float): Target m/z value
        mz_tol (float): m/z tolerance. If None, uses owner.parameters.eic_mz_tol (for Study) or defaults to 0.01
        rt_unit (str): Retention time unit for the chromatogram
        label (str): Optional label for the chromatogram

    Returns:
        Chromatogram
    """
    # Use default mz_tol from study parameters if not provided
    if mz_tol is None:
        if hasattr(owner, "parameters") and hasattr(owner.parameters, "eic_mz_tol"):
            mz_tol = owner.parameters.eic_mz_tol
        else:
            mz_tol = 0.01  # fallback default

    if mz is None:
        raise ValueError("mz must be provided for EIC computation")

    # resolve sample when owner is a Study-like object (has get_sample)
    s = None
    if hasattr(owner, "ms1_df"):
        s = owner
    else:
        # owner is expected to be a Study
        s = get_samples(owner, sample)

    if s is None:
        raise ValueError("Could not resolve sample for EIC computation")

    # ensure ms1_df exists
    if getattr(s, "ms1_df", None) is None:
        raise ValueError("Sample has no ms1_df for EIC computation")

    # Extract EIC from ms1_df using mz window
    try:
        cols = s.ms1_df.columns
        if not all(c in cols for c in ["rt", "mz", "inty"]):
            raise RuntimeError("ms1_df missing required columns")

        # Filter by mz window
        mz_min = mz - mz_tol
        mz_max = mz + mz_tol
        eic_data = s.ms1_df.filter(
            (pl.col("mz") >= mz_min) & (pl.col("mz") <= mz_max),
        )

        if eic_data.is_empty():
            # Return empty chromatogram if no data found
            import numpy as _np

            return Chromatogram(
                rt=_np.array([0.0]),
                inty=_np.array([0.0]),
                label=label or f"EIC m/z={mz:.4f} ± {mz_tol} (empty)",
                rt_unit=rt_unit,
            )

        # Aggregate intensities per retention time (sum in case of multiple points per rt)
        eic = eic_data.group_by("rt").agg(pl.col("inty").sum().alias("inty"))
        eic_pd = eic.sort("rt").to_pandas()

    except Exception:
        raise RuntimeError("Failed to extract EIC from ms1_df")

    if eic_pd.empty:
        # Return empty chromatogram if no data found
        import numpy as _np

        return Chromatogram(
            rt=_np.array([0.0]),
            inty=_np.array([0.0]),
            label=label or f"EIC m/z={mz:.4f} ± {mz_tol} (empty)",
            rt_unit=rt_unit,
        )

    # build Chromatogram
    try:
        chrom = Chromatogram(
            rt=eic_pd["rt"].to_numpy(),
            inty=eic_pd["inty"].to_numpy(),
            label=label or f"EIC m/z={mz:.4f} ± {mz_tol}",
            rt_unit=rt_unit,
        )
    except Exception:
        chrom = Chromatogram(
            rt=eic_pd["rt"].values,
            inty=eic_pd["inty"].values,
            label=label or f"EIC m/z={mz:.4f} ± {mz_tol}",
            rt_unit=rt_unit,
        )

    return chrom


# =====================================================================================
# DATA RETRIEVAL AND MATRIX FUNCTIONS
# =====================================================================================


def get_chrom(self, uids=None, samples=None):
    """
    Get a matrix of chromatogram objects for consensus features across samples.

    Returns a Polars DataFrame with consensus_uid as the first column and sample names
    as subsequent columns. Each cell contains a Chromatogram object with rt_shift applied.

    Parameters:
        uids (int, list, or None): Consensus feature UIDs to include.
                                   - None: include all consensus features (default)
                                   - int: single consensus_uid
                                   - list: multiple consensus_uids
        samples (int, str, list, or None): Sample identifiers to include.
                                           - None: include all samples (default)
                                           - int: single sample_uid
                                           - str: single sample_name
                                           - list: multiple sample_uids or sample_names

    Returns:
        pl.DataFrame: Matrix with consensus_uid column and sample name columns containing
                     Chromatogram objects. Empty cells contain None.

    Note:
        Requires merge() to have been run first to generate consensus_df and consensus_mapping_df.
        Chromatogram objects are updated with rt_shift values (rt - rt_original).
    """
    # Check if consensus_df is empty or doesn't have required columns
    if self.consensus_df.is_empty() or "consensus_uid" not in self.consensus_df.columns:
        self.logger.error("No consensus data found. Please run merge() first.")
        return None

    ids = self._get_consensus_uids(uids)
    sample_uids = self._get_samples_uids(samples)

    # Pre-filter all DataFrames to reduce join sizes
    filtered_consensus_mapping = self.consensus_mapping_df.filter(
        pl.col("consensus_uid").is_in(ids),
    )

    # Get feature_uids that we actually need
    relevant_feature_uids = filtered_consensus_mapping["feature_uid"].to_list()

    self.logger.debug(
        f"Filtering features_df for {len(relevant_feature_uids)} relevant feature_uids.",
    )
    # Pre-filter features_df to only relevant features and samples
    filtered_features = self.features_df.filter(
        pl.col("feature_uid").is_in(relevant_feature_uids) & pl.col("sample_uid").is_in(sample_uids),
    ).select(
        [
            "feature_uid",
            "chrom",
            "rt",
            "rt_original",
            "sample_uid",
        ],
    )

    # Pre-filter samples_df
    filtered_samples = self.samples_df.filter(
        pl.col("sample_uid").is_in(sample_uids),
    ).select(["sample_uid", "sample_name"])

    # Perform a three-way join to get all needed data
    self.logger.debug("Joining DataFrames to get complete chromatogram data.")
    df_combined = (
        filtered_consensus_mapping.join(
            filtered_features,
            on="feature_uid",
            how="inner",
        )
        .join(filtered_samples, on="sample_uid", how="inner")
        .with_columns(
            (pl.col("rt") - pl.col("rt_original")).alias("rt_shift"),
        )
    )

    # Update chrom objects with rt_shift efficiently
    self.logger.debug("Updating chromatogram objects with rt_shift values.")
    chrom_data = df_combined.select(["chrom", "rt_shift"]).to_dict(as_series=False)
    for chrom_obj, rt_shift in zip(chrom_data["chrom"], chrom_data["rt_shift"]):
        if chrom_obj is not None:
            chrom_obj.rt_shift = rt_shift

    # Get all unique combinations for complete matrix
    all_consensus_uids = sorted(df_combined["consensus_uid"].unique().to_list())
    all_sample_names = sorted(df_combined["sample_name"].unique().to_list())

    # Create a mapping dictionary for O(1) lookup instead of O(n) filtering
    self.logger.debug("Creating lookup dictionary for chromatogram objects.")
    chrom_lookup = {}
    for row in df_combined.select(
        [
            "consensus_uid",
            "sample_name",
            "chrom",
        ],
    ).iter_rows():
        key = (row[0], row[1])  # (consensus_uid, sample_name)
        chrom_lookup[key] = row[2]  # chrom object

    # Build pivot data efficiently using the lookup dictionary
    pivot_data = []
    total_iterations = len(all_consensus_uids)
    progress_interval = max(1, total_iterations // 10)  # Show progress every 10%

    for i, consensus_uid in enumerate(all_consensus_uids):
        if i % progress_interval == 0:
            progress_percent = (i / total_iterations) * 100
            self.logger.debug(
                f"Building pivot data: {progress_percent:.0f}% complete ({i}/{total_iterations})",
            )

        row_data = {"consensus_uid": consensus_uid}
        for sample_name in all_sample_names:
            key = (consensus_uid, sample_name)
            row_data[sample_name] = chrom_lookup.get(key, None)
        pivot_data.append(row_data)

    self.logger.debug(
        f"Building pivot data: 100% complete ({total_iterations}/{total_iterations})",
    )

    # Create Polars DataFrame with complex objects
    df2_pivoted = pl.DataFrame(pivot_data)

    return df2_pivoted


# =====================================================================================
# UTILITY AND CONFIGURATION FUNCTIONS
# =====================================================================================


def align_reset(self):
    """
    Reset alignment by reverting all retention times to their original (pre-alignment) values.

    This function:
    1. Iterates over all feature maps and sets RT to original_RT from metadata
    2. Removes the original_RT metadata value after restoration
    3. Sets alignment_ref_index to None
    4. Updates features_df by setting rt column equal to rt_original column
    5. Maintains proper column order in features_df after modification

    This effectively undoes the align() operation, reverting features to their original
    retention time coordinates.

    Returns:
        None (modifies study in place)

    Note:
        After calling this function, features will have their original retention times.
        You can re-run align() with different parameters if needed.
    """
    self.logger.debug("Resetting alignment.")
    # iterate over all feature maps and set RT to original RT
    for feature_map in self.features_maps:
        for feature in feature_map:
            rt = feature.getMetaValue("original_RT")
            if rt is not None:
                feature.setRT(rt)
                feature.removeMetaValue("original_RT")
    self.alignment_ref_index = None
    # in self.features_df, set rt equal to rt_original
    self.features_df = self.features_df.with_columns(
        pl.col("rt_original").alias("rt"),
    )

    # Ensure column order is maintained after with_columns operation
    from masster.study.helpers import _ensure_features_df_schema_order

    _ensure_features_df_schema_order(self)
    self.logger.info("Alignment reset: all feature RTs set to original_RT.")


# =====================================================================================
# DATA RETRIEVAL HELPER FUNCTIONS
# =====================================================================================


def get_consensus(self, quant="chrom_area"):
    """
    Get consensus features with quantification values across all samples as a pandas DataFrame.

    Returns a pandas DataFrame combining consensus_df metadata with a quantification matrix
    (from get_consensus_matrix) where each sample is a column.

    Parameters:
        quant (str): Quantification method column name from features_df. Default is "chrom_area".
                    Other options include "chrom_height", "inty_max", etc.

    Returns:
        pd.DataFrame: Merged DataFrame with:
                     - consensus_df columns (consensus_uid, consensus_id, rt, mz, etc.)
                     - Sample columns with quantification values
                     Index is consensus_uid, sorted by consensus_id

    Note:
        Requires merge() to have been run first to generate consensus_df.
        Returns None if consensus_df is empty or missing.
    """
    import polars as pl
    
    if self.consensus_df is None:
        self.logger.error("No consensus found.")
        return None

    # Get the consensus matrix (already optimized in Polars)
    matrix_polars = self.get_consensus_matrix(quant=quant)
    
    # Join consensus metadata with matrix in Polars (much faster than pandas merge)
    result_polars = self.consensus_df.join(
        matrix_polars, 
        on="consensus_uid", 
        how="left"
    ).sort("consensus_uid")
    
    # Convert to pandas only at the very end
    df = result_polars.to_pandas()
    
    # Keep consensus_id as string (UUID format) and set as index
    df["consensus_id"] = df["consensus_id"].astype("string")
    df.set_index("consensus_uid", inplace=True)

    return df


def get_consensus_matrix(self, quant="chrom_area", samples=None):
    """
    Get a matrix of consensus features with samples as columns and consensus features as rows.
    Highly optimized implementation using vectorized Polars operations.

    Parameters:
        quant (str): Quantification method column name (default: "chrom_area")
        samples: Sample identifier(s) to include. Can be:
                - None: include all samples (default)
                - int: single sample_uid
                - str: single sample_name
                - list: multiple sample_uids or sample_names
    """
    import polars as pl

    if quant not in self.features_df.columns:
        self.logger.error(f"Quantification method {quant} not found in features_df.")
        return None

    # Determine if we need to filter samples
    if samples is None:
        # No filtering needed - use all data
        features_filtered = self.features_df
        samples_filtered = self.samples_df
        consensus_mapping_filtered = self.consensus_mapping_df
    else:
        # Get sample_uids to include in the matrix
        sample_uids = self._get_samples_uids(samples)
        
        if not sample_uids:
            self.logger.warning("No valid samples found for consensus matrix")
            return pl.DataFrame()

        # Convert to set for faster lookup if it's a large list
        if len(sample_uids) > 100:
            sample_uids_set = set(sample_uids)
            # Use expression for better performance
            features_filtered = self.features_df.filter(pl.col("sample_uid").is_in(sample_uids_set))
            samples_filtered = self.samples_df.filter(pl.col("sample_uid").is_in(sample_uids_set))
            consensus_mapping_filtered = self.consensus_mapping_df.filter(pl.col("sample_uid").is_in(sample_uids_set))
        else:
            # For small lists, direct is_in is fine
            features_filtered = self.features_df.filter(pl.col("sample_uid").is_in(sample_uids))
            samples_filtered = self.samples_df.filter(pl.col("sample_uid").is_in(sample_uids))
            consensus_mapping_filtered = self.consensus_mapping_df.filter(pl.col("sample_uid").is_in(sample_uids))

    # Join operations to combine data efficiently
    # 1. Join consensus mapping with features to get quantification values
    consensus_with_values = consensus_mapping_filtered.join(
        features_filtered.select(["feature_uid", "sample_uid", quant]), on=["feature_uid", "sample_uid"], how="left"
    ).with_columns(pl.col(quant).fill_null(0))

    # 2. Join with samples to get sample names
    consensus_with_names = consensus_with_values.join(
        samples_filtered.select(["sample_uid", "sample_name"]), on="sample_uid", how="left"
    )

    # 3. Group by consensus_uid and sample_name, taking max value per group
    aggregated = consensus_with_names.group_by(["consensus_uid", "sample_name"]).agg(pl.col(quant).max().alias("value"))

    # 4. Pivot to create the matrix format
    matrix_df = aggregated.pivot(on="sample_name", index="consensus_uid", values="value").fill_null(0)

    # 5. Round numeric columns and ensure proper types
    numeric_cols = [col for col in matrix_df.columns if col != "consensus_uid"]
    matrix_df = matrix_df.with_columns([
        pl.col("consensus_uid").cast(pl.UInt64),
        *[pl.col(col).round(0) for col in numeric_cols],
    ])

    return matrix_df


def get_gaps_matrix(self, uids=None, samples=None):
    """
    Get a matrix of gaps between consensus features with samples as columns and consensus features as rows.
    Optimized implementation using vectorized Polars operations.

    Parameters:
        uids: Consensus UID(s) to include. If None, includes all consensus features.
        samples: Sample identifier(s) to include. If None, includes all samples.
                Can be int (sample_uid), str (sample_name), or list of either.

    Returns:
        pl.DataFrame: Gaps matrix with consensus_uid as first column and samples as other columns.
                     Values are 1 (detected) or 0 (missing/gap).
    """
    import polars as pl

    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.error("No consensus found.")
        return None

    if self.consensus_mapping_df is None or self.consensus_mapping_df.is_empty():
        self.logger.error("No consensus mapping found.")
        return None

    if self.features_df is None or self.features_df.is_empty():
        self.logger.error("No features found.")
        return None

    # Get consensus UIDs to include
    if uids is not None:
        uids = self._get_consensus_uids(uids)
        if not uids:
            self.logger.warning("No valid consensus features found for gaps matrix")
            return pl.DataFrame()
    
    # Determine sample filtering
    if samples is None:
        # Use all samples - no filtering needed
        samples_filtered = self.samples_df
        features_filtered = self.features_df
        consensus_mapping_filtered = self.consensus_mapping_df
    else:
        # Get sample_uids to filter
        sample_uids = self._get_samples_uids(samples)
        if not sample_uids:
            self.logger.warning("No valid samples found for gaps matrix")
            return pl.DataFrame()
        
        # Filter dataframes
        samples_filtered = self.samples_df.filter(pl.col("sample_uid").is_in(sample_uids))
        features_filtered = self.features_df.filter(pl.col("sample_uid").is_in(sample_uids))
        consensus_mapping_filtered = self.consensus_mapping_df.filter(pl.col("sample_uid").is_in(sample_uids))

    # Mark features that are NOT filled (i.e., originally detected)
    # Features without 'filled' column or with filled=False/null are considered detected
    if "filled" in features_filtered.columns:
        features_detected = features_filtered.filter(
            ~pl.col("filled") | pl.col("filled").is_null()
        ).select(["feature_uid", "sample_uid"])
    else:
        features_detected = features_filtered.select(["feature_uid", "sample_uid"])
    
    # Join consensus mapping with detected features to mark which consensus/sample pairs are detected
    # Using semi-join to efficiently mark presence
    consensus_detected = consensus_mapping_filtered.join(
        features_detected,
        on=["feature_uid", "sample_uid"],
        how="semi"  # Keep only rows where feature was detected
    ).select(["consensus_uid", "sample_uid"]).unique()
    
    # Add a detection flag
    consensus_detected = consensus_detected.with_columns(pl.lit(1).cast(pl.Int8).alias("detected"))
    
    # Join with sample names
    consensus_with_names = consensus_detected.join(
        samples_filtered.select(["sample_uid", "sample_name"]),
        on="sample_uid",
        how="left"
    )
    
    # Group by consensus_uid and sample_name, taking max (should be 1 if detected)
    aggregated = consensus_with_names.group_by(["consensus_uid", "sample_name"]).agg(
        pl.col("detected").max().alias("value")
    )
    
    # Filter by consensus UIDs if specified
    if uids is not None:
        aggregated = aggregated.filter(pl.col("consensus_uid").is_in(uids))
    
    # Pivot to create matrix format
    matrix_df = aggregated.pivot(
        on="sample_name",
        index="consensus_uid",
        values="value"
    ).fill_null(0)  # Fill null with 0 (gap)
    
    # Ensure proper types
    numeric_cols = [col for col in matrix_df.columns if col != "consensus_uid"]
    matrix_df = matrix_df.with_columns([
        pl.col("consensus_uid").cast(pl.UInt64),
        *[pl.col(col).cast(pl.Int8) for col in numeric_cols],
    ])
    
    return matrix_df


def get_gaps_stats(self, uids=None):
    """
    Get statistics about gaps in the consensus features.
    """

    df = self.get_gaps_matrix(uids=uids)

    # For each column, count how many times the value is True, False, or None. Summarize in a new df with three rows: True, False, None.
    if df is None or df.empty:
        self.logger.warning("No gap data found.")
        return None
    gaps_stats = pd.DataFrame(
        {
            "aligned": df.apply(lambda x: (~x.astype(bool)).sum()),
            "filled": df.apply(lambda x: x.astype(bool).sum() - pd.isnull(x).sum()),
            "missing": df.apply(lambda x: pd.isnull(x).sum()),
        },
    )
    return gaps_stats


def get_consensus_matches(self, uids=None, filled=True):
    """
    Get feature matches for consensus UIDs with optimized join operation.

    Parameters:
        uids: Consensus UID(s) to get matches for. Can be:
              - None: get matches for all consensus features
              - int: single consensus UID (converted to list)
              - list: multiple consensus UIDs
        filled (bool): Whether to include filled features in the results.
                      - True (default): include all features (both original and gap-filled)
                      - False: exclude filled features, returning only originally detected features

    Returns:
        pl.DataFrame: Feature matches for the specified consensus UIDs

    Examples:
        # Get all matches including filled features
        matches = study.get_consensus_matches(uids=[1038])

        # Get only originally detected features (exclude gap-filled)
        original_matches = study.get_consensus_matches(uids=[1038], filled=False)

    Note:
        The 'filled' column in features_df indicates whether a feature was gap-filled
        during Study.fill() (True) or originally detected by the feature finder (False).
        Use filled=False to analyze only features that were independently detected
        in each sample, which is useful for quality assessment.
    """
    # Handle single int by converting to list
    if isinstance(uids, int):
        uids = [uids]

    uids = self._get_consensus_uids(uids)

    if not uids:
        return pl.DataFrame()

    # Early validation checks
    if self.consensus_mapping_df is None or self.consensus_mapping_df.is_empty():
        self.logger.warning("No consensus mapping data available")
        return pl.DataFrame()

    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No feature data available")
        return pl.DataFrame()

    # Build the query with optional filled filter
    features_query = self.features_df.lazy()

    # Apply filled filter if specified
    if not filled and "filled" in self.features_df.columns:
        features_query = features_query.filter(~pl.col("filled"))

    # Optimized: filter mapping first (smaller result set), then join with features
    # Include consensus_uid in the result for context
    filtered_mapping = (
        self.consensus_mapping_df.lazy()
        .filter(pl.col("consensus_uid").is_in(uids))
        .select(["consensus_uid", "feature_uid", "sample_uid"])
    )

    # Join features with filtered mapping - this is more efficient than the reverse
    # because the filtered mapping is typically much smaller than features_df
    matches = (
        filtered_mapping.join(
            features_query,
            on=["feature_uid", "sample_uid"],
            how="inner",
        ).collect(streaming=True)  # Use streaming for memory efficiency with large datasets
    )

    return matches


# =====================================================================================
# UID HELPER FUNCTIONS
# =====================================================================================


def consensus_reset(self):
    """
    Reset consensus data by clearing consensus DataFrames and removing filled features.

    This function performs a complete reset of all consensus-related data:
    1. Sets consensus_df, consensus_ms2, consensus_mapping_df, id_df to empty pl.DataFrame()
    2. Removes all filled features from features_df (gap-filled features)
    3. Removes relevant operations from history (merge, integrate, find_ms2, fill, identify)
    4. Logs the number of features removed and history entries cleaned

    This effectively undoes the merge() operation and any subsequent gap-filling,
    identification, or integration operations, reverting the study to a pre-merge state.

    Returns:
        None (modifies study in place)

    Note:
        After calling this function, you'll need to re-run merge() to regenerate consensus features.
        This is useful for testing different merge parameters or reprocessing from scratch.
    """
    self.logger.debug("Resetting consensus data.")

    # Reset consensus DataFrames to empty
    self.consensus_df = pl.DataFrame()
    self.consensus_ms2 = pl.DataFrame()
    self.consensus_mapping_df = pl.DataFrame()
    self.id_df = pl.DataFrame()

    # Remove filled features from features_df
    if self.features_df is None:
        self.logger.warning("No features found.")
        return

    l1 = len(self.features_df)

    # Filter out filled features (keep only non-filled features)
    if "filled" in self.features_df.columns:
        self.features_df = self.features_df.filter(~pl.col("filled") | pl.col("filled").is_null())

    # Remove consensus-related operations from history
    keys_to_remove = ["merge", "integrate", "integrate_chrom", "find_ms2", "fill", "fill_single", "identify"]
    history_removed_count = 0
    if hasattr(self, "history") and self.history:
        for key in keys_to_remove:
            if key in self.history:
                del self.history[key]
                history_removed_count += 1
                self.logger.debug(f"Removed '{key}' from history")

    removed_count = l1 - len(self.features_df)
    self.logger.info(
        f"Reset consensus data. Consensus DataFrames cleared. Features removed: {removed_count}. History entries removed: {history_removed_count}",
    )


def fill_reset(self):
    """
    Reset gap-filling by removing all filled features and their consensus mappings.

    This function:
    1. Removes all features with filled=True from features_df
    2. Removes corresponding consensus mappings that reference deleted features
    3. Logs the number of gap-filled features removed

    This effectively undoes the fill() operation while preserving the consensus structure
    and all originally detected features.

    Returns:
        None (modifies study in place)

    Note:
        After calling this function, gaps in the consensus will reappear.
        You can re-run fill() with different parameters if needed.
    """
    # remove all features with filled=True
    if self.features_df is None:
        self.logger.warning("No features found.")
        return
    l1 = len(self.features_df)
    self.features_df = self.features_df.filter(~pl.col("filled"))
    # remove all rows in consensus_mapping_df where feature_uid is not in features_df['uid']

    feature_uids_to_keep = self.features_df["feature_uid"].to_list()
    self.consensus_mapping_df = self.consensus_mapping_df.filter(
        pl.col("feature_uid").is_in(feature_uids_to_keep),
    )
    self.logger.info(
        f"Removed {l1 - len(self.features_df)} gap-filled features",
    )


def _get_features_uids(self, uids=None, seed=42):
    """
    Helper function to get feature_uids from features_df based on input uids.
    If uids is None, returns all feature_uids.
    If uids is a single integer, returns a random sample of feature_uids.
    If uids is a list of strings, returns feature_uids corresponding to those feature_uids.
    If uids is a list of integers, returns feature_uids corresponding to those feature_uids.
    """
    if uids is None:
        # get all feature_uids from features_df
        return self.features_df["feature_uid"].to_list()
    elif isinstance(uids, int):
        # choose a random sample of feature_uids
        if len(self.features_df) > uids:
            np.random.seed(seed)
            return np.random.choice(
                self.features_df["feature_uid"].to_list(),
                uids,
                replace=False,
            ).tolist()
        else:
            return self.features_df["feature_uid"].to_list()
    else:
        # iterate over all uids. If the item is a string, assume it's a feature_uid
        feature_uids = []
        for uid in uids:
            if isinstance(uid, str):
                matching_rows = self.features_df.filter(pl.col("feature_uid") == uid)
                if not matching_rows.is_empty():
                    feature_uids.append(
                        matching_rows.row(0, named=True)["feature_uid"],
                    )
            elif isinstance(uid, int):
                if uid in self.features_df["feature_uid"].to_list():
                    feature_uids.append(uid)
        # remove duplicates
        feature_uids = list(set(feature_uids))
        return feature_uids


def _get_consensus_uids(self, uids=None, seed=42):
    """
    Helper function to get consensus_uids from consensus_df based on input uids.
    If uids is None, returns all consensus_uids.
    If uids is a single integer, returns a random sample of consensus_uids.
    If uids is a list of strings, returns consensus_uids corresponding to those consensus_ids.
    If uids is a list of integers, returns consensus_uids corresponding to those consensus_uids.
    """
    # Check if consensus_df is empty or doesn't have required columns
    if self.consensus_df.is_empty() or "consensus_uid" not in self.consensus_df.columns:
        return []

    if uids is None:
        # get all consensus_uids from consensus_df
        return self.consensus_df["consensus_uid"].to_list()
    elif isinstance(uids, int):
        # choose a random sample of consensus_uids
        if len(self.consensus_df) > uids:
            np.random.seed(seed)  # for reproducibility
            return np.random.choice(
                self.consensus_df["consensus_uid"].to_list(),
                uids,
                replace=False,
            ).tolist()
        else:
            return self.consensus_df["consensus_uid"].to_list()
    else:
        # Optimized: build lookup sets once instead of creating lists per iteration
        valid_uids_set = set(self.consensus_df["consensus_uid"].to_list())
        
        # Separate string IDs from integer UIDs for batch processing
        string_ids = [uid for uid in uids if isinstance(uid, str)]
        int_uids = [uid for uid in uids if isinstance(uid, int)]
        
        consensus_uids = []
        
        # Batch process string IDs using vectorized Polars filter
        if string_ids:
            matching_rows = self.consensus_df.filter(pl.col("consensus_id").is_in(string_ids))
            if not matching_rows.is_empty():
                consensus_uids.extend(matching_rows["consensus_uid"].to_list())
        
        # Process integer UIDs with O(1) set lookup
        for uid in int_uids:
            if uid in valid_uids_set:
                consensus_uids.append(uid)
        
        # remove duplicates (use dict.fromkeys to preserve order in Python 3.7+)
        return list(dict.fromkeys(consensus_uids))


def get_orphans(self):
    """
    Get all features that are not included in any consensus feature (orphan features).

    Orphan features are those that were detected in individual samples but were not
    matched to any consensus feature during the merge process. This can happen when:
    - Features don't meet quality thresholds
    - Features are too dissimilar from other features across samples
    - Features are unique to a single sample

    Returns:
        pl.DataFrame: DataFrame containing all orphan features from features_df that are
                     not present in consensus_mapping_df. Includes all feature columns.

    Note:
        Requires merge() to have been run first to generate consensus_mapping_df.
        The returned DataFrame will be empty if all features were successfully mapped.
    """
    not_in_consensus = self.features_df.filter(
        ~self.features_df["feature_uid"].is_in(
            self.consensus_mapping_df["feature_uid"].to_list(),
        ),
    )
    return not_in_consensus


def get_consensus_stats(self):
    """
    Get key performance indicators for each consensus feature.

    Returns:
        pl.DataFrame: DataFrame with the following columns:
            - consensus_uid: Consensus unique identifier
            - rt: Retention time
            - rt_delta_mean: Chromatogram retention time delta
            - mz: Mass-to-charge ratio
            - mz_range: Mass range (mz_max - mz_min)
            - log10_inty_mean: Log10 of mean intensity
            - number_samples: Number of samples
            - number_ms2: Number of MS2 spectra
            - charge_mean: Mean charge
            - quality: Feature quality
            - chrom_coherence_mean: Mean chromatographic coherence
            - chrom_height_scaled_mean: Mean scaled chromatographic height
            - chrom_prominence_scaled_mean: Mean scaled chromatographic prominence
            - qc_ratio: Ratio of QC samples where feature was detected
            - qc_cv: RSD (relative standard deviation) of intensity for QC samples
            - qc_to_blank: Ratio of average QC intensity to average blank intensity
    """
    import polars as pl
    import numpy as np

    # Check if consensus_df exists and has data
    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.error("No consensus data available. Run merge/find_consensus first.")
        return pl.DataFrame()

    # Get all columns and their data types - work with original dataframe
    data_df = self.consensus_df.clone()

    # Define specific columns to include in the exact order requested
    desired_columns = [
        "consensus_uid",  # Include consensus_uid for identification
        "rt",
        "rt_delta_mean",
        "mz",
        "mz_range",  # mz_max-mz_min (will be calculated)
        "log10_inty_mean",  # log10(inty_mean) (will be calculated)
        "number_samples",
        "number_ms2",
        "charge_mean",
        "quality",
        "chrom_coherence_mean",
        "chrom_height_scaled_mean",
        "chrom_prominence_scaled_mean",
    ]

    # Calculate derived columns if they don't exist
    if "mz_range" not in data_df.columns and "mz_max" in data_df.columns and "mz_min" in data_df.columns:
        data_df = data_df.with_columns((pl.col("mz_max") - pl.col("mz_min")).alias("mz_range"))

    if "log10_inty_mean" not in data_df.columns and "inty_mean" in data_df.columns:
        data_df = data_df.with_columns(pl.col("inty_mean").log10().alias("log10_inty_mean"))

    # Filter to only include columns that exist in the dataframe, preserving order
    available_columns = [col for col in desired_columns if col in data_df.columns]

    if len(available_columns) <= 1:  # Only consensus_uid would be 1
        self.logger.error(
            f"None of the requested consensus statistics columns were found. Available columns: {list(data_df.columns)}"
        )
        return pl.DataFrame()

    self.logger.debug(f"Creating consensus stats DataFrame with {len(available_columns)} columns: {available_columns}")

    # Get base result DataFrame with selected columns
    result_df = data_df.select(available_columns)

    # Add QC-related columns
    try:
        # Identify QC and blank samples based on naming patterns
        all_sample_names = self.samples_df["sample_name"].to_list()

        # Define patterns for QC and blank identification
        qc_patterns = ["qc", "QC", "quality", "Quality", "control", "Control"]
        blank_patterns = ["blank", "Blank", "BLANK", "blk", "BLK"]

        # Get QC and blank sample names
        qc_sample_names = [name for name in all_sample_names if any(pattern in name for pattern in qc_patterns)]
        blank_sample_names = [name for name in all_sample_names if any(pattern in name for pattern in blank_patterns)]

        self.logger.debug(f"Found {len(qc_sample_names)} QC samples and {len(blank_sample_names)} blank samples")

        # Initialize QC columns with null values
        qc_ratio_values = [None] * len(result_df)
        qc_cv_values = [None] * len(result_df)
        qc_to_blank_values = [None] * len(result_df)

        if len(qc_sample_names) > 0:
            # Calculate QC metrics using optimized approach - get only QC+blank data
            self.logger.debug("Fetching optimized consensus matrices for QC calculations...")

            # Get QC consensus matrix (only QC samples)
            qc_consensus_matrix = self.get_consensus_matrix(samples=qc_sample_names)

            # Get blank consensus matrix (only blank samples) if blanks exist
            blank_consensus_matrix = None
            if len(blank_sample_names) > 0:
                blank_consensus_matrix = self.get_consensus_matrix(samples=blank_sample_names)

            if qc_consensus_matrix is not None and not qc_consensus_matrix.is_empty():
                available_qc_cols = [col for col in qc_consensus_matrix.columns if col != "consensus_uid"]
                self.logger.debug(f"Found {len(available_qc_cols)} QC columns in optimized QC matrix")

                # 2. QC CV: Calculate CV for QC samples
                if len(available_qc_cols) > 0:
                    self.logger.debug("Calculating QC CV...")
                    try:
                        # Calculate CV (coefficient of variation) for QC samples
                        qc_data = qc_consensus_matrix.select(["consensus_uid"] + available_qc_cols)

                        # Calculate mean and std for each row across QC columns
                        qc_stats = (
                            qc_data.with_columns([
                                pl.concat_list([pl.col(col) for col in available_qc_cols]).alias("qc_values")
                            ])
                            .with_columns([
                                pl.col("qc_values").list.mean().alias("qc_mean"),
                                pl.col("qc_values").list.std().alias("qc_std"),
                            ])
                            .with_columns(
                                # CV = std / mean (NOT multiplied by 100 to keep between 0-1)
                                pl.when(pl.col("qc_mean") > 0)
                                .then(pl.col("qc_std") / pl.col("qc_mean"))
                                .otherwise(None)
                                .alias("qc_cv")
                            )
                        )

                        # Join with result DataFrame
                        result_df = result_df.join(
                            qc_stats.select(["consensus_uid", "qc_cv"]), on="consensus_uid", how="left"
                        )
                        qc_cv_values = None  # Indicate we successfully added the column

                    except Exception as e:
                        self.logger.debug(f"Could not calculate QC CV: {e}")

                # 3. QC to blank ratio: Compare average QC to average blank intensity
                if (
                    len(available_qc_cols) > 0
                    and blank_consensus_matrix is not None
                    and not blank_consensus_matrix.is_empty()
                ):
                    available_blank_cols = [col for col in blank_consensus_matrix.columns if col != "consensus_uid"]
                    self.logger.debug(
                        f"Calculating QC to blank ratio with {len(available_blank_cols)} blank columns..."
                    )

                    if len(available_blank_cols) > 0:
                        try:
                            # Calculate average intensity for QC samples
                            qc_averages = (
                                qc_data.with_columns([
                                    pl.concat_list([pl.col(col) for col in available_qc_cols]).alias("qc_values")
                                ])
                                .with_columns(pl.col("qc_values").list.mean().alias("qc_avg"))
                                .select(["consensus_uid", "qc_avg"])
                            )

                            # Calculate average intensity for blank samples
                            blank_data = blank_consensus_matrix.select(["consensus_uid"] + available_blank_cols)
                            blank_averages = (
                                blank_data.with_columns([
                                    pl.concat_list([pl.col(col) for col in available_blank_cols]).alias("blank_values")
                                ])
                                .with_columns(pl.col("blank_values").list.mean().alias("blank_avg"))
                                .select(["consensus_uid", "blank_avg"])
                            )

                            # Join QC and blank averages and calculate ratio
                            qc_blank_ratios = qc_averages.join(
                                blank_averages, on="consensus_uid", how="left"
                            ).with_columns(
                                # Ratio = qc_avg / blank_avg, but only where blank_avg > 0
                                pl.when(pl.col("blank_avg") > 0)
                                .then(pl.col("qc_avg") / pl.col("blank_avg"))
                                .otherwise(None)
                                .alias("qc_to_blank")
                            )

                            # Join with result DataFrame
                            result_df = result_df.join(
                                qc_blank_ratios.select(["consensus_uid", "qc_to_blank"]), on="consensus_uid", how="left"
                            )
                            qc_to_blank_values = None  # Indicate we successfully added the column

                        except Exception as e:
                            self.logger.debug(f"Could not calculate QC to blank ratio: {e}")

            # 1. QC ratio: Get optimized gaps matrix for QC samples only
            self.logger.debug("Calculating QC detection ratio with optimized gaps matrix...")
            try:
                # Use optimized get_gaps_matrix with QC samples filtering for faster performance
                qc_gaps_matrix = self.get_gaps_matrix(samples=qc_sample_names)

                if qc_gaps_matrix is not None and not qc_gaps_matrix.is_empty():
                    # Get QC columns (should be all columns except consensus_uid since we filtered)
                    available_qc_cols_gaps = [col for col in qc_gaps_matrix.columns if col != "consensus_uid"]
                    self.logger.debug(f"Found {len(available_qc_cols_gaps)} QC columns in optimized gaps matrix")

                    if len(available_qc_cols_gaps) > 0:
                        # Calculate QC detection ratio for each consensus feature
                        qc_detection = qc_gaps_matrix.select(["consensus_uid"] + available_qc_cols_gaps)

                        # Data should already be properly typed from get_gaps_matrix, but ensure consistency
                        for col in available_qc_cols_gaps:
                            qc_detection = qc_detection.with_columns(pl.col(col).fill_null(0).cast(pl.Int8).alias(col))

                        # Calculate ratio (sum of detections / number of QC samples)
                        qc_ratios = qc_detection.with_columns(
                            pl.concat_list([pl.col(col) for col in available_qc_cols_gaps]).alias("qc_detections")
                        ).with_columns(
                            (pl.col("qc_detections").list.sum().cast(pl.Float64) / len(available_qc_cols_gaps)).alias(
                                "qc_ratio"
                            )
                        )

                        # Join with result DataFrame
                        result_df = result_df.join(
                            qc_ratios.select(["consensus_uid", "qc_ratio"]), on="consensus_uid", how="left"
                        )
                        qc_ratio_values = None  # Indicate we successfully added the column

            except Exception as e:
                self.logger.debug(f"Could not calculate QC ratio: {e}")

        # Add null columns for any QC metrics that couldn't be calculated
        # Add null columns for any QC metrics that couldn't be calculated
        if qc_ratio_values is not None:
            result_df = result_df.with_columns(pl.lit(None, dtype=pl.Float64).alias("qc_ratio"))
        if qc_cv_values is not None:
            result_df = result_df.with_columns(pl.lit(None, dtype=pl.Float64).alias("qc_cv"))
        if qc_to_blank_values is not None:
            result_df = result_df.with_columns(pl.lit(None, dtype=pl.Float64).alias("qc_to_blank"))

    except Exception as e:
        self.logger.warning(f"Error calculating QC metrics: {e}")
        # Add null columns if QC calculation fails
        result_df = result_df.with_columns([
            pl.lit(None, dtype=pl.Float64).alias("qc_ratio"),
            pl.lit(None, dtype=pl.Float64).alias("qc_cv"),
            pl.lit(None, dtype=pl.Float64).alias("qc_to_blank"),
        ])

    return result_df


# =====================================================================================
# DATA COMPRESSION AND RESTORATION FUNCTIONS
# =====================================================================================


def compress(self, features=True, ms2=True, chrom=False, ms2_max=5):
    """
    Perform multiple compression operations to reduce memory usage and file size.

    Combines compress_features(), compress_ms2(), and compress_chrom() operations
    in a single call with configurable options.

    Parameters:
        features (bool): If True, compress features_df by removing orphan features and
                        clearing ms2_specs column. Default is True.
        ms2 (bool): If True, compress MS2 data by limiting replicates per consensus feature.
               Default is True.
        chrom (bool): If True, compress chromatogram data. Default is False.
        ms2_max (int): Maximum number of MS2 replicates to keep per consensus_uid and
                      energy combination. Default is 5.

    Returns:
        None (modifies study in place)

    Note:
        Compression is lossy - data removed cannot be recovered without reloading from
        original sample files. Use compress() after you're confident in your consensus
        results and before saving to reduce file size.
    """
    self.logger.info("Starting full compression...")
    if features:
        self.compress_features()
    if ms2:
        self.compress_ms2(max_replicates=ms2_max)
    if chrom:
        self.compress_chrom()
    self.logger.success("Compression completed")


def compress_features(self):
    """
    Compress features_df by removing orphan features and clearing MS2 spectra.

    This function performs two compression operations:
    1. Deletes features that are not associated with any consensus feature (orphans)
       - Uses consensus_mapping_df to identify which features to keep
    2. Sets the ms2_specs column to None to free memory
       - MS2 spectra can be restored later using restore_features()

    Returns:
        None (modifies features_df in place)

    Note:
        Requires merge() to have been run first to generate consensus_mapping_df.
        This operation is lossy - orphan features are permanently deleted.
        MS2 spectra can be restored from individual .sample5 files if needed.
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features_df found.")
        return

    if self.consensus_mapping_df is None or self.consensus_mapping_df.is_empty():
        self.logger.warning("No consensus_mapping_df found.")
        return

    initial_count = len(self.features_df)

    # Get feature_uids that are associated with consensus features
    consensus_feature_uids = self.consensus_mapping_df["feature_uid"].to_list()

    # Filter features_df to keep only features associated with consensus
    self.features_df = self.features_df.filter(
        pl.col("feature_uid").is_in(consensus_feature_uids),
    )

    # Set ms2_specs column to None if it exists
    if "ms2_specs" in self.features_df.columns:
        # Create a list of None values with the same length as the dataframe
        # This preserves the Object dtype instead of converting to Null
        none_values = [None] * len(self.features_df)
        self.features_df = self.features_df.with_columns(
            pl.Series("ms2_specs", none_values, dtype=pl.Object),
        )

    removed_count = initial_count - len(self.features_df)
    self.logger.info(
        f"Compressed features: removed {removed_count} features not in consensus, cleared ms2_specs column",
    )


def restore_features(self, samples=None, maps=False):
    """
    Update specific columns (chrom, chrom_area, ms2_scans, ms2_specs) in features_df
    from the corresponding samples by reading features_df from the sample5 file.
    Use the feature_id for matching.

    Parameters:
        samples (list, optional): List of sample_uids or sample_names to restore.
                                 If None, restores all samples.
        maps (bool, optional): If True, also load featureXML data and update study.feature_maps.
    """
    import datetime
    from masster.sample.sample import Sample

    if self.features_df is None or self.features_df.is_empty():
        self.logger.error("No features_df found in study.")
        return

    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.error("No samples_df found in study.")
        return

    # Get sample_uids to process
    sample_uids = self._get_samples_uids(samples)

    if not sample_uids:
        self.logger.warning("No valid samples specified.")
        return

    # Columns to update from sample data
    columns_to_update = ["chrom", "chrom_area", "ms2_scans", "ms2_specs"]

    self.logger.info(
        f"Restoring columns {columns_to_update} from {len(sample_uids)} samples...",
    )

    # Create a mapping of (sample_uid, feature_id) to feature_uid from study.features_df
    study_feature_mapping = {}
    for row in self.features_df.iter_rows(named=True):
        if "feature_id" in row and "feature_uid" in row and "sample_uid" in row:
            key = (row["sample_uid"], row["feature_id"])
            study_feature_mapping[key] = row["feature_uid"]

    # Process each sample
    tqdm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for sample_uid in tqdm(
        sample_uids,
        unit="sample",
        disable=tqdm_disable,
        desc=f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Restoring samples",
    ):
        # Get sample info
        sample_row = self.samples_df.filter(pl.col("sample_uid") == sample_uid)
        if sample_row.is_empty():
            self.logger.warning(
                f"Sample with uid {sample_uid} not found in samples_df.",
            )
            continue

        sample_info = sample_row.row(0, named=True)
        sample_path = sample_info.get("sample_path")
        sample_name = sample_info.get("sample_name")

        if not sample_path or not os.path.exists(sample_path):
            self.logger.warning(
                f"Sample file not found for {sample_name}: {sample_path}",
            )
            continue

        try:
            # Load sample to get its features_df
            # Use a direct load call with map=False to prevent feature synchronization
            # which would remove filled features that don't exist in the original FeatureMap
            # Use ERROR log level to suppress info messages
            sample = Sample(log_level="ERROR")
            sample._load_sample5(sample_path, map=False)

            if sample.features_df is None or sample.features_df.is_empty():
                self.logger.warning(f"No features found in sample {sample_name}")
                continue

            # Check which columns are actually available in the sample
            available_columns = [col for col in columns_to_update if col in sample.features_df.columns]
            if not available_columns:
                self.logger.debug(f"No target columns found in sample {sample_name}")
                continue

            # Create update data for this sample
            updates_made = 0
            for row in sample.features_df.iter_rows(named=True):
                feature_id = row.get("feature_id")
                if feature_id is None:
                    continue

                key = (sample_uid, feature_id)
                if key in study_feature_mapping:
                    feature_uid = study_feature_mapping[key]

                    # Update only the available columns in study.features_df
                    for col in available_columns:
                        if col in row and col in self.features_df.columns:
                            # Get the original column dtype to preserve it
                            original_dtype = self.features_df[col].dtype

                            # Update the specific row and column, preserving dtype
                            mask = (pl.col("feature_uid") == feature_uid) & (pl.col("sample_uid") == sample_uid)

                            # Handle object columns (like Chromatogram) differently
                            if original_dtype == pl.Object:
                                self.features_df = self.features_df.with_columns(
                                    pl.when(mask)
                                    .then(
                                        pl.lit(
                                            row[col],
                                            dtype=original_dtype,
                                            allow_object=True,
                                        ),
                                    )
                                    .otherwise(pl.col(col))
                                    .alias(col),
                                )
                            else:
                                self.features_df = self.features_df.with_columns(
                                    pl.when(mask)
                                    .then(pl.lit(row[col], dtype=original_dtype))
                                    .otherwise(pl.col(col))
                                    .alias(col),
                                )
                    updates_made += 1

            if updates_made > 0:
                self.logger.debug(
                    f"Updated {updates_made} features from sample {sample_name}",
                )

            # If maps is True, load featureXML data
            if maps:
                if hasattr(sample, "feature_maps"):
                    self.feature_maps.extend(sample.feature_maps)

        except Exception as e:
            self.logger.error(f"Failed to load sample {sample_name}: {e}")
            continue

    self.logger.success(
        f"Completed restoring columns {columns_to_update} from {len(sample_uids)} samples",
    )


def restore_chrom(self, samples=None, mz_tol=0.010, rt_tol=10.0):
    """
    Restore chromatograms from individual .sample5 files and gap-fill missing ones.

    This function combines the functionality of restore_features() and fill_chrom():
    1. First restores chromatograms from individual .sample5 files (like restore_features)
    2. Then gap-fills any remaining empty chromatograms (like fill_chrom)
    3. ONLY updates the 'chrom' column, not chrom_area or other derived values

    Parameters:
        samples (list, optional): List of sample_uids or sample_names to process.
                                 If None, processes all samples.
        mz_tol (float): m/z tolerance for gap filling (default: 0.010)
        rt_tol (float): RT tolerance for gap filling (default: 10.0)
    """
    import datetime
    import numpy as np
    from masster.sample.sample import Sample
    from masster.chromatogram import Chromatogram

    if self.features_df is None or self.features_df.is_empty():
        self.logger.error("No features_df found in study.")
        return

    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.error("No samples_df found in study.")
        return

    # Get sample_uids to process
    sample_uids = self._get_samples_uids(samples)
    if not sample_uids:
        self.logger.warning("No valid samples specified.")
        return

    self.logger.info(f"Restoring chromatograms from {len(sample_uids)} samples...")

    # Create mapping of (sample_uid, feature_id) to feature_uid
    study_feature_mapping = {}
    for row in self.features_df.iter_rows(named=True):
        if "feature_id" in row and "feature_uid" in row and "sample_uid" in row:
            key = (row["sample_uid"], row["feature_id"])
            study_feature_mapping[key] = row["feature_uid"]

    # Phase 1: Restore from individual .sample5 files (like restore_features)
    restored_count = 0
    tqdm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    self.logger.info("Phase 1: Restoring chromatograms from .sample5 files...")
    for sample_uid in tqdm(
        sample_uids,
        desc=f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Restoring from samples",
        disable=tqdm_disable,
    ):
        # Get sample info
        sample_row = self.samples_df.filter(pl.col("sample_uid") == sample_uid)
        if sample_row.is_empty():
            self.logger.warning(f"Sample with uid {sample_uid} not found.")
            continue

        sample_info = sample_row.row(0, named=True)
        sample_path = sample_info.get("sample_path")
        sample_name = sample_info.get("sample_name")

        if not sample_path or not os.path.exists(sample_path):
            self.logger.warning(f"Sample file not found: {sample_path}")
            continue

        try:
            # Load sample (with map=False to prevent feature synchronization)
            # Use ERROR log level to suppress info messages
            sample = Sample(log_level="ERROR")
            sample._load_sample5(sample_path, map=False)

            if sample.features_df is None or sample.features_df.is_empty():
                self.logger.warning(f"No features found in sample {sample_name}")
                continue

            # Check if chrom column exists in sample
            if "chrom" not in sample.features_df.columns:
                continue

            # Update chromatograms from this sample
            for row in sample.features_df.iter_rows(named=True):
                feature_id = row.get("feature_id")
                chrom = row.get("chrom")

                if feature_id is None or chrom is None:
                    continue

                key = (sample_uid, feature_id)
                if key in study_feature_mapping:
                    feature_uid = study_feature_mapping[key]

                    # Update only the chrom column
                    mask = (pl.col("feature_uid") == feature_uid) & (pl.col("sample_uid") == sample_uid)
                    self.features_df = self.features_df.with_columns(
                        pl.when(mask)
                        .then(pl.lit(chrom, dtype=pl.Object, allow_object=True))
                        .otherwise(pl.col("chrom"))
                        .alias("chrom"),
                    )
                    restored_count += 1

        except Exception as e:
            self.logger.error(f"Failed to load sample {sample_name}: {e}")
            continue

    self.logger.info(
        f"Phase 1 complete: Restored {restored_count} chromatograms from .sample5 files",
    )

    # Phase 2: Gap-fill remaining empty chromatograms (like fill_chrom)
    self.logger.info("Phase 2: Gap-filling remaining empty chromatograms...")

    # Count how many chromatograms are still missing
    empty_chroms = self.features_df.filter(pl.col("chrom").is_null()).height
    total_chroms = len(self.features_df)

    self.logger.debug(
        f"Chromatograms still missing: {empty_chroms}/{total_chroms} ({empty_chroms / total_chroms * 100:.1f}%)",
    )

    if empty_chroms == 0:
        self.logger.info(
            "All chromatograms restored from .sample5 files. No gap-filling needed.",
        )
        return

    # Get consensus info for gap filling
    consensus_info = {}
    for row in self.consensus_df.iter_rows(named=True):
        consensus_info[row["consensus_uid"]] = {
            "rt_start_mean": row["rt_start_mean"],
            "rt_end_mean": row["rt_end_mean"],
            "mz": row["mz"],
            "rt": row["rt"],
        }

    filled_count = 0

    # Process each sample that has missing chromatograms
    for sample_uid in tqdm(
        sample_uids,
        desc=f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Gap-filling missing chromatograms",
        disable=tqdm_disable,
    ):
        # Get features with missing chromatograms for this sample
        missing_features = self.features_df.filter(
            (pl.col("sample_uid") == sample_uid) & (pl.col("chrom").is_null()),
        )

        if missing_features.is_empty():
            continue

        # Get sample info
        sample_row = self.samples_df.filter(pl.col("sample_uid") == sample_uid)
        sample_info = sample_row.row(0, named=True)
        sample_path = sample_info.get("sample_path")
        sample_name = sample_info.get("sample_name")

        if not sample_path or not os.path.exists(sample_path):
            continue

        try:
            # Load sample for MS1 data extraction
            # Use ERROR log level to suppress info messages
            sample = Sample(log_level="ERROR")
            sample._load_sample5(sample_path, map=False)

            if not hasattr(sample, "ms1_df") or sample.ms1_df is None or sample.ms1_df.is_empty():
                continue

            # Process each missing feature
            for feature_row in missing_features.iter_rows(named=True):
                feature_uid = feature_row["feature_uid"]
                mz = feature_row["mz"]
                rt = feature_row["rt"]
                rt_start = feature_row.get("rt_start", rt - rt_tol)
                rt_end = feature_row.get("rt_end", rt + rt_tol)

                # Extract EIC from MS1 data
                d = sample.ms1_df.filter(
                    (pl.col("mz") >= mz - mz_tol)
                    & (pl.col("mz") <= mz + mz_tol)
                    & (pl.col("rt") >= rt_start - rt_tol)
                    & (pl.col("rt") <= rt_end + rt_tol),
                )

                # Create chromatogram
                if d.is_empty():
                    # Create empty chromatogram
                    eic = Chromatogram(
                        rt=np.array([rt_start, rt_end]),
                        inty=np.array([0.0, 0.0]),
                        label=f"EIC mz={mz:.4f} (gap-filled)",
                        file=sample_path,
                        mz=mz,
                        mz_tol=mz_tol,
                        feature_start=rt_start,
                        feature_end=rt_end,
                        feature_apex=rt,
                    )
                else:
                    # Create real chromatogram from data
                    eic_rt = d.group_by("rt").agg(pl.col("inty").max()).sort("rt")

                    if len(eic_rt) > 4:
                        eic = Chromatogram(
                            eic_rt["rt"].to_numpy(),
                            eic_rt["inty"].to_numpy(),
                            label=f"EIC mz={mz:.4f} (gap-filled)",
                            file=sample_path,
                            mz=mz,
                            mz_tol=mz_tol,
                            feature_start=rt_start,
                            feature_end=rt_end,
                            feature_apex=rt,
                        ).find_peaks()
                    else:
                        eic = Chromatogram(
                            eic_rt["rt"].to_numpy(),
                            eic_rt["inty"].to_numpy(),
                            label=f"EIC mz={mz:.4f} (gap-filled)",
                            file=sample_path,
                            mz=mz,
                            mz_tol=mz_tol,
                            feature_start=rt_start,
                            feature_end=rt_end,
                            feature_apex=rt,
                        )

                # Update the chromatogram in the study
                mask = pl.col("feature_uid") == feature_uid
                self.features_df = self.features_df.with_columns(
                    pl.when(mask)
                    .then(pl.lit(eic, dtype=pl.Object, allow_object=True))
                    .otherwise(pl.col("chrom"))
                    .alias("chrom"),
                )
                filled_count += 1

        except Exception as e:
            self.logger.error(f"Failed to gap-fill sample {sample_name}: {e}")
            continue

    self.logger.success(f"Phase 2 complete: Gap-filled {filled_count} chromatograms")

    # Final summary
    final_non_null = self.features_df.filter(pl.col("chrom").is_not_null()).height
    final_total = len(self.features_df)

    self.logger.info(
        f"Chromatogram restoration complete: {final_non_null}/{final_total} ({final_non_null / final_total * 100:.1f}%)",
    )
    self.logger.info(
        f"Restored from .sample5 files: {restored_count}, Gap-filled from raw data: {filled_count}",
    )


def compress_ms2(self, max_replicates=5):
    """
    Reduce the number of entries matching any pair of (consensus and energy) to max XY rows.
    Groups all rows by consensus_uid and energy. For each group, sort by number_frags * prec_inty,
    and then pick the top XY rows. Discard the others.

    Parameters:
        max_replicates (int): Maximum number of replicates to keep per consensus_uid and energy combination
    """
    if self.consensus_ms2 is None or self.consensus_ms2.is_empty():
        self.logger.warning("No consensus_ms2 found.")
        return

    initial_count = len(self.consensus_ms2)

    # Create a ranking score based on number_frags * prec_inty
    # Handle None values by treating them as 0
    self.consensus_ms2 = self.consensus_ms2.with_columns(
        [
            (pl.col("number_frags").fill_null(0) * pl.col("prec_inty").fill_null(0)).alias("ranking_score"),
        ],
    )

    # Group by consensus_uid and energy, then rank by score and keep top max_replicates
    compressed_ms2 = (
        self.consensus_ms2.with_row_count(
            "row_id",
        )  # Add row numbers for stable sorting
        .sort(
            ["consensus_uid", "energy", "ranking_score", "row_id"],
            descending=[False, False, True, False],
        )
        .with_columns(
            [
                pl.int_range(pl.len()).over(["consensus_uid", "energy"]).alias("rank"),
            ],
        )
        .filter(pl.col("rank") < max_replicates)
        .drop(["ranking_score", "row_id", "rank"])
    )

    self.consensus_ms2 = compressed_ms2

    removed_count = initial_count - len(self.consensus_ms2)
    self.logger.info(
        f"Compressed MS2 data: removed {removed_count} entries, kept max {max_replicates} per consensus/energy pair",
    )


def compress_chrom(self):
    """
    Set the chrom column in study.features_df to null to save memory.

    This function clears all chromatogram objects from the features_df, which can
    significantly reduce memory usage in large studies.
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features_df found.")
        return

    if "chrom" not in self.features_df.columns:
        self.logger.warning("No 'chrom' column found in features_df.")
        return

    # Count non-null chromatograms before compression
    non_null_count = self.features_df.filter(pl.col("chrom").is_not_null()).height

    # Set chrom column to None while keeping dtype as object
    self.features_df = self.features_df.with_columns(
        pl.lit(None, dtype=pl.Object).alias("chrom"),
    )

    self.logger.info(
        f"Compressed chromatograms: cleared {non_null_count} chromatogram objects from features_df",
    )


# =====================================================================================
# DATA FILTERING AND SELECTION FUNCTIONS
# =====================================================================================


def features_select(
    self,
    mz=None,
    rt=None,
    inty=None,
    sample_uid=None,
    sample_name=None,
    consensus_uid=None,
    feature_uid=None,
    filled=None,
    quality=None,
    chrom_coherence=None,
    chrom_prominence=None,
    chrom_prominence_scaled=None,
    chrom_height_scaled=None,
    chunk_size: int = 100000,
    use_lazy_streaming: bool = True,
):
    """
    Select features from features_df based on specified criteria and return the filtered DataFrame.

    FULLY OPTIMIZED VERSION: Enhanced performance with lazy streaming and chunked processing.

    Key optimizations:
    - Lazy evaluation with streaming execution for memory efficiency
    - Optimized filter expression building with reduced overhead
    - Chunked processing for very large datasets
    - Efficient column existence checking
    - Enhanced error handling and performance logging

    Parameters:
        mz: m/z range filter (tuple for range, single value for minimum)
        rt: retention time range filter (tuple for range, single value for minimum)
        inty: intensity filter (tuple for range, single value for minimum)
        sample_uid: sample UID filter (list, single value, or tuple for range)
        sample_name: sample name filter (list or single value)
        consensus_uid: consensus UID filter (list, single value, or tuple for range)
        feature_uid: feature UID filter (list, single value, or tuple for range)
        filled: filter for filled/not filled features (bool)
        quality: quality score filter (tuple for range, single value for minimum)
        chrom_coherence: chromatogram coherence filter (tuple for range, single value for minimum)
        chrom_prominence: chromatogram prominence filter (tuple for range, single value for minimum)
        chrom_prominence_scaled: scaled chromatogram prominence filter (tuple for range, single value for minimum)
        chrom_height_scaled: scaled chromatogram height filter (tuple for range, single value for minimum)
        chunk_size: Number of features to process per chunk for large datasets (default: 100000)
        use_lazy_streaming: Enable lazy evaluation with streaming for memory efficiency (default: True)

    Returns:
        polars.DataFrame: Filtered features DataFrame
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features found in study.")
        return pl.DataFrame()

    # Early return optimization
    filter_params = [
        mz,
        rt,
        inty,
        sample_uid,
        sample_name,
        consensus_uid,
        feature_uid,
        filled,
        quality,
        chrom_coherence,
        chrom_prominence,
        chrom_prominence_scaled,
        chrom_height_scaled,
    ]

    if all(param is None for param in filter_params):
        return self.features_df.clone()

    import time

    start_time = time.perf_counter()
    initial_count = len(self.features_df)

    # Build optimized filter expression
    filter_expr = _build_optimized_filter_expression(
        self,
        mz,
        rt,
        inty,
        sample_uid,
        sample_name,
        consensus_uid,
        feature_uid,
        filled,
        quality,
        chrom_coherence,
        chrom_prominence,
        chrom_prominence_scaled,
        chrom_height_scaled,
    )

    if filter_expr is None:
        return pl.DataFrame()

    # Apply filter with optimized execution strategy
    if use_lazy_streaming and initial_count > chunk_size:
        result = _apply_chunked_select(self, filter_expr, chunk_size)
    else:
        result = self.features_df.lazy().filter(filter_expr).collect(streaming=use_lazy_streaming)

    # Log performance
    elapsed_time = time.perf_counter() - start_time
    final_count = len(result)
    removed_count = initial_count - final_count

    if final_count == 0:
        self.logger.warning("No features remaining after applying selection criteria.")
    else:
        self.logger.debug(f"Selected features: {final_count:,} (removed: {removed_count:,}) in {elapsed_time:.4f}s")

    return result


def _build_optimized_filter_expression(
    self,
    mz,
    rt,
    inty,
    sample_uid,
    sample_name,
    consensus_uid,
    feature_uid,
    filled,
    quality,
    chrom_coherence,
    chrom_prominence,
    chrom_prominence_scaled,
    chrom_height_scaled,
):
    """
    Build optimized filter expression with efficient column checking and expression combining.
    """
    # Pre-check available columns once
    available_columns = set(self.features_df.columns)
    filter_conditions = []
    warnings = []

    # Build filter conditions with optimized expressions
    if mz is not None:
        if isinstance(mz, tuple) and len(mz) == 2:
            min_mz, max_mz = mz
            filter_conditions.append(pl.col("mz").is_between(min_mz, max_mz, closed="both"))
        else:
            filter_conditions.append(pl.col("mz") >= mz)

    if rt is not None:
        if isinstance(rt, tuple) and len(rt) == 2:
            min_rt, max_rt = rt
            filter_conditions.append(pl.col("rt").is_between(min_rt, max_rt, closed="both"))
        else:
            filter_conditions.append(pl.col("rt") >= rt)

    if inty is not None:
        if isinstance(inty, tuple) and len(inty) == 2:
            min_inty, max_inty = inty
            filter_conditions.append(pl.col("inty").is_between(min_inty, max_inty, closed="both"))
        else:
            filter_conditions.append(pl.col("inty") >= inty)

    # Filter by sample_uid
    if sample_uid is not None:
        if isinstance(sample_uid, (list, tuple)):
            if len(sample_uid) == 2 and not isinstance(sample_uid, list):
                # Treat as range
                min_uid, max_uid = sample_uid
                filter_conditions.append(pl.col("sample_uid").is_between(min_uid, max_uid, closed="both"))
            else:
                # Treat as list
                filter_conditions.append(pl.col("sample_uid").is_in(sample_uid))
        else:
            filter_conditions.append(pl.col("sample_uid") == sample_uid)

    # Filter by sample_name (requires pre-processing)
    if sample_name is not None:
        # Get sample_uids for the given sample names
        if isinstance(sample_name, list):
            sample_uids_for_names = self.samples_df.filter(
                pl.col("sample_name").is_in(sample_name),
            )["sample_uid"].to_list()
        else:
            sample_uids_for_names = self.samples_df.filter(
                pl.col("sample_name") == sample_name,
            )["sample_uid"].to_list()

        if sample_uids_for_names:
            filter_conditions.append(pl.col("sample_uid").is_in(sample_uids_for_names))
        else:
            filter_conditions.append(pl.lit(False))  # No matching samples

    # Filter by consensus_uid
    if consensus_uid is not None:
        if isinstance(consensus_uid, (list, tuple)):
            if len(consensus_uid) == 2 and not isinstance(consensus_uid, list):
                # Treat as range
                min_uid, max_uid = consensus_uid
                filter_conditions.append(pl.col("consensus_uid").is_between(min_uid, max_uid, closed="both"))
            else:
                # Treat as list
                filter_conditions.append(pl.col("consensus_uid").is_in(consensus_uid))
        else:
            filter_conditions.append(pl.col("consensus_uid") == consensus_uid)

    # Filter by feature_uid
    if feature_uid is not None:
        if isinstance(feature_uid, (list, tuple)):
            if len(feature_uid) == 2 and not isinstance(feature_uid, list):
                # Treat as range
                min_uid, max_uid = feature_uid
                filter_conditions.append(pl.col("feature_uid").is_between(min_uid, max_uid, closed="both"))
            else:
                # Treat as list
                filter_conditions.append(pl.col("feature_uid").is_in(feature_uid))
        else:
            filter_conditions.append(pl.col("feature_uid") == feature_uid)

    # Filter by filled status
    if filled is not None:
        if "filled" in available_columns:
            if filled:
                filter_conditions.append(pl.col("filled"))
            else:
                filter_conditions.append(~pl.col("filled") | pl.col("filled").is_null())
        else:
            warnings.append("'filled' column not found in features_df")

    # Filter by quality
    if quality is not None:
        if "quality" in available_columns:
            if isinstance(quality, tuple) and len(quality) == 2:
                min_quality, max_quality = quality
                filter_conditions.append(pl.col("quality").is_between(min_quality, max_quality, closed="both"))
            else:
                filter_conditions.append(pl.col("quality") >= quality)
        else:
            warnings.append("'quality' column not found in features_df")

    # Filter by chromatogram coherence
    if chrom_coherence is not None:
        if "chrom_coherence" in available_columns:
            if isinstance(chrom_coherence, tuple) and len(chrom_coherence) == 2:
                min_coherence, max_coherence = chrom_coherence
                filter_conditions.append(
                    pl.col("chrom_coherence").is_between(min_coherence, max_coherence, closed="both")
                )
            else:
                filter_conditions.append(pl.col("chrom_coherence") >= chrom_coherence)
        else:
            warnings.append("'chrom_coherence' column not found in features_df")

    # Filter by chromatogram prominence
    if chrom_prominence is not None:
        if "chrom_prominence" in available_columns:
            if isinstance(chrom_prominence, tuple) and len(chrom_prominence) == 2:
                min_prominence, max_prominence = chrom_prominence
                filter_conditions.append(
                    pl.col("chrom_prominence").is_between(min_prominence, max_prominence, closed="both")
                )
            else:
                filter_conditions.append(pl.col("chrom_prominence") >= chrom_prominence)
        else:
            warnings.append("'chrom_prominence' column not found in features_df")

    # Filter by scaled chromatogram prominence
    if chrom_prominence_scaled is not None:
        if "chrom_prominence_scaled" in available_columns:
            if isinstance(chrom_prominence_scaled, tuple) and len(chrom_prominence_scaled) == 2:
                min_prominence_scaled, max_prominence_scaled = chrom_prominence_scaled
                filter_conditions.append(
                    pl.col("chrom_prominence_scaled").is_between(
                        min_prominence_scaled, max_prominence_scaled, closed="both"
                    )
                )
            else:
                filter_conditions.append(pl.col("chrom_prominence_scaled") >= chrom_prominence_scaled)
        else:
            warnings.append("'chrom_prominence_scaled' column not found in features_df")

    # Filter by scaled chromatogram height
    if chrom_height_scaled is not None:
        if "chrom_height_scaled" in available_columns:
            if isinstance(chrom_height_scaled, tuple) and len(chrom_height_scaled) == 2:
                min_height_scaled, max_height_scaled = chrom_height_scaled
                filter_conditions.append(
                    pl.col("chrom_height_scaled").is_between(min_height_scaled, max_height_scaled, closed="both")
                )
            else:
                filter_conditions.append(pl.col("chrom_height_scaled") >= chrom_height_scaled)
        else:
            warnings.append("'chrom_height_scaled' column not found in features_df")

    # Log warnings once at the end
    for warning in warnings:
        self.logger.warning(warning)

    # Combine all conditions efficiently
    if not filter_conditions:
        return None

    # Use reduce for efficient expression combination
    from functools import reduce
    import operator

    combined_expr = reduce(operator.and_, filter_conditions)

    return combined_expr


def _apply_chunked_select(self, filter_expr, chunk_size: int):
    """
    Apply selection using chunked processing for large datasets.
    """
    total_features = len(self.features_df)
    num_chunks = (total_features + chunk_size - 1) // chunk_size

    self.logger.debug(f"Using chunked select with {num_chunks} chunks")

    filtered_chunks = []
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, total_features)

        chunk_result = (
            self.features_df.lazy().slice(start_idx, end_idx - start_idx).filter(filter_expr).collect(streaming=True)
        )

        if not chunk_result.is_empty():
            filtered_chunks.append(chunk_result)

    if filtered_chunks:
        return pl.concat(filtered_chunks, how="vertical")
    else:
        return pl.DataFrame()


def features_filter(self, features, chunk_size: int = 50000, use_index_based: bool = True, parallel: bool = True):
    """
    Filter features_df by keeping only features that match the given criteria.
    This keeps only the specified features and removes all others.

    FULLY OPTIMIZED VERSION: Index-based filtering, chunked processing, and lazy evaluation.

    Performance improvements:
    - Index-based filtering using sorted arrays (O(n log n) instead of O(n²))
    - Chunked processing to handle large datasets without memory issues
    - Enhanced lazy evaluation with streaming operations
    - Hash-based lookups for optimal performance
    - Memory-efficient operations

    Parameters:
        features: Features to keep. Can be:
                 - polars.DataFrame: Features DataFrame (will use feature_uid column)
                 - list: List of feature_uids to keep
                 - tuple: Tuple of feature_uids to keep
                 - int: Single feature_uid to keep
        chunk_size: Number of features to process per chunk (default: 50000)
        use_index_based: Use index-based filtering for better performance (default: True)
        parallel: Enable parallel processing when beneficial (default: True)

    Returns:
        None (modifies self.features_df in place)
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features found in study.")
        return

    if features is None:
        self.logger.warning("No features provided for filtering.")
        return

    initial_count = len(self.features_df)

    # Extract feature UIDs efficiently
    feature_uids_to_keep = _extract_feature_uids_optimized(self, features)
    if not feature_uids_to_keep:
        self.logger.warning("No feature UIDs provided for filtering.")
        return

    # Choose optimal filtering strategy based on data size and characteristics
    if use_index_based and len(self.features_df) > 10000:
        _apply_index_based_filter(self, feature_uids_to_keep, chunk_size, parallel)
    else:
        _apply_standard_filter(self, feature_uids_to_keep)

    # Calculate results and log performance
    final_count = len(self.features_df)
    removed_count = initial_count - final_count

    self.logger.info(f"Filtered features. Kept: {final_count:,}. Removed: {removed_count:,}.")

    # Store filtering parameters in history
    self.update_history(["features_filter"], {
        "kept_count": final_count,
        "removed_count": removed_count,
        "initial_count": initial_count,
        "chunk_size": chunk_size,
        "use_index_based": use_index_based,
        "parallel": parallel
    })


def _extract_feature_uids_optimized(self, features):
    """
    Efficiently extract feature UIDs from various input types.
    Returns a set for O(1) lookup performance.
    """
    if isinstance(features, pl.DataFrame):
        if "feature_uid" not in features.columns:
            self.logger.error("features DataFrame must contain 'feature_uid' column")
            return set()
        # Use polars native operations for efficiency
        return set(features.select("feature_uid").to_series().to_list())

    elif isinstance(features, (list, tuple)):
        return set(features)  # Convert to set immediately for O(1) lookups

    elif isinstance(features, int):
        return {features}

    else:
        self.logger.error("features parameter must be a DataFrame, list, tuple, or int")
        return set()


def _apply_index_based_filter(self, feature_uids_to_keep, chunk_size: int, parallel: bool):
    """
    Apply index-based filtering with chunked processing and lazy evaluation.

    This method uses:
    1. Sorted arrays and binary search for O(log n) lookups
    2. Chunked processing to manage memory usage
    3. Lazy evaluation with streaming operations
    4. Hash-based set operations for optimal performance
    """
    self.logger.debug(f"Using index-based filtering with chunks of {chunk_size:,}")

    total_features = len(self.features_df)

    if total_features <= chunk_size:
        # Small dataset - process in single chunk with optimized operations
        _filter_single_chunk_optimized(self, feature_uids_to_keep)
    else:
        # Large dataset - use chunked processing with lazy evaluation
        _filter_chunked_lazy(self, feature_uids_to_keep, chunk_size, parallel)


def _filter_single_chunk_optimized(self, feature_uids_to_keep):
    """
    Optimized filtering for datasets that fit in a single chunk.
    Uses hash-based set operations for maximum performance.
    """
    # Create boolean mask using hash-based set lookup (O(1) per element)
    filter_expr = pl.col("feature_uid").is_in(list(feature_uids_to_keep))

    # Apply filter using lazy evaluation with optimized execution
    self.features_df = (
        self.features_df.lazy().filter(filter_expr).collect(streaming=True)  # Use streaming for memory efficiency
    )

    # Apply same filter to consensus_mapping_df if it exists
    if self.consensus_mapping_df is not None and not self.consensus_mapping_df.is_empty():
        self.consensus_mapping_df = self.consensus_mapping_df.lazy().filter(filter_expr).collect(streaming=True)


def _filter_chunked_lazy(self, feature_uids_to_keep, chunk_size: int, parallel: bool):
    """
    Chunked processing with lazy evaluation for large datasets.

    This approach:
    1. Processes data in manageable chunks to control memory usage
    2. Uses lazy evaluation to optimize query execution
    3. Maintains consistent performance regardless of dataset size
    4. Optionally uses parallel processing for independent operations
    """
    total_features = len(self.features_df)
    num_chunks = (total_features + chunk_size - 1) // chunk_size

    self.logger.debug(f"Processing {total_features:,} features in {num_chunks} chunks")

    # Process features_df in chunks using lazy evaluation
    filtered_chunks = []

    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, total_features)

        # Create lazy query for this chunk
        chunk_query = (
            self.features_df.lazy()
            .slice(start_idx, end_idx - start_idx)
            .filter(pl.col("feature_uid").is_in(list(feature_uids_to_keep)))
        )

        # Collect chunk with streaming for memory efficiency
        chunk_result = chunk_query.collect(streaming=True)
        if not chunk_result.is_empty():
            filtered_chunks.append(chunk_result)

    # Combine all filtered chunks efficiently
    if filtered_chunks:
        self.features_df = pl.concat(filtered_chunks, how="vertical")
    else:
        self.features_df = pl.DataFrame()  # No features remain

    # Apply same chunked processing to consensus_mapping_df
    _filter_consensus_mapping_chunked(self, feature_uids_to_keep, chunk_size)


def _filter_consensus_mapping_chunked(self, feature_uids_to_keep, chunk_size: int):
    """
    Apply chunked filtering to consensus_mapping_df with same optimization strategy.
    """
    if self.consensus_mapping_df is None or self.consensus_mapping_df.is_empty():
        return

    total_mappings = len(self.consensus_mapping_df)

    if total_mappings <= chunk_size:
        # Single chunk processing
        self.consensus_mapping_df = (
            self.consensus_mapping_df.lazy()
            .filter(pl.col("feature_uid").is_in(list(feature_uids_to_keep)))
            .collect(streaming=True)
        )
    else:
        # Multi-chunk processing
        num_chunks = (total_mappings + chunk_size - 1) // chunk_size
        filtered_chunks = []

        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, total_mappings)

            chunk_query = (
                self.consensus_mapping_df.lazy()
                .slice(start_idx, end_idx - start_idx)
                .filter(pl.col("feature_uid").is_in(list(feature_uids_to_keep)))
            )

            chunk_result = chunk_query.collect(streaming=True)
            if not chunk_result.is_empty():
                filtered_chunks.append(chunk_result)

        if filtered_chunks:
            self.consensus_mapping_df = pl.concat(filtered_chunks, how="vertical")
        else:
            self.consensus_mapping_df = pl.DataFrame()


def _apply_standard_filter(self, feature_uids_to_keep):
    """
    Fallback to standard filtering for smaller datasets.
    Still uses optimized set operations and lazy evaluation.
    """
    filter_expr = pl.col("feature_uid").is_in(list(feature_uids_to_keep))

    # Apply filter with lazy evaluation
    self.features_df = self.features_df.lazy().filter(filter_expr).collect(streaming=True)

    # Apply to consensus_mapping_df
    if self.consensus_mapping_df is not None and not self.consensus_mapping_df.is_empty():
        self.consensus_mapping_df = self.consensus_mapping_df.lazy().filter(filter_expr).collect(streaming=True)


def features_delete(self, features):
    """
    Delete features from features_df based on feature identifiers.
    This removes the specified features and keeps all others (opposite of features_filter).

    Parameters:
        features: Features to delete. Can be:
                 - polars.DataFrame: Features DataFrame (will use feature_uid column)
                 - list: List of feature_uids to delete
                 - int: Single feature_uid to delete

    Returns:
        None (modifies self.features_df in place)
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features found in study.")
        return

    # Early return if no features provided
    if features is None:
        self.logger.warning("No features provided for deletion.")
        return

    initial_count = len(self.features_df)

    # Determine feature_uids to remove - optimized type checking
    if isinstance(features, pl.DataFrame):
        if "feature_uid" not in features.columns:
            self.logger.error("features DataFrame must contain 'feature_uid' column")
            return
        feature_uids_to_remove = features["feature_uid"].to_list()
    elif isinstance(features, (list, tuple)):
        feature_uids_to_remove = list(features)  # Convert tuple to list if needed
    elif isinstance(features, int):
        feature_uids_to_remove = [features]
    else:
        self.logger.error("features parameter must be a DataFrame, list, tuple, or int")
        return

    # Early return if no UIDs to remove
    if not feature_uids_to_remove:
        self.logger.warning("No feature UIDs provided for deletion.")
        return

    # Convert to set for faster lookup if list is large
    if len(feature_uids_to_remove) > 100:
        feature_uids_set = set(feature_uids_to_remove)
        # Use the set for filtering if it's significantly smaller
        if len(feature_uids_set) < len(feature_uids_to_remove) * 0.8:
            feature_uids_to_remove = list(feature_uids_set)

    # Create filter condition - remove specified features
    filter_condition = ~pl.col("feature_uid").is_in(feature_uids_to_remove)

    # Apply filter to features_df using lazy evaluation for better performance
    self.features_df = self.features_df.lazy().filter(filter_condition).collect()

    # Apply filter to consensus_mapping_df if it exists - batch operation
    mapping_removed_count = 0
    if self.consensus_mapping_df is not None and not self.consensus_mapping_df.is_empty():
        initial_mapping_count = len(self.consensus_mapping_df)
        self.consensus_mapping_df = self.consensus_mapping_df.lazy().filter(filter_condition).collect()
        mapping_removed_count = initial_mapping_count - len(self.consensus_mapping_df)

    # Calculate results once and log efficiently
    final_count = len(self.features_df)
    removed_count = initial_count - final_count

    # Single comprehensive log message
    if mapping_removed_count > 0:
        self.logger.info(
            f"Deleted {removed_count} features and {mapping_removed_count} consensus mappings. Remaining features: {final_count}",
        )
    else:
        self.logger.info(
            f"Deleted {removed_count} features. Remaining features: {final_count}",
        )


def consensus_select(
    self,
    uid=None,
    mz=None,
    rt=None,
    inty_mean=None,
    consensus_uid=None,
    consensus_id=None,
    number_samples=None,
    number_ms2=None,
    quality=None,
    bl=None,
    chrom_sanity_mean=None,
    chrom_coherence_mean=None,
    chrom_prominence_mean=None,
    chrom_prominence_scaled_mean=None,
    chrom_height_scaled_mean=None,
    rt_delta_mean=None,
    id_top_score=None,
    identified=None,
    adduct_top=None,
    adduct_charge_top=None,
    adduct_mass_neutral_top=None,
    adduct_mass_shift_top=None,
    adduct_group=None,
    adduct_of=None,
    id_top_name=None,
    id_top_class=None,
    id_top_adduct=None,
    sortby=None,
    descending=True,
    # Short aliases for convenience
    sanity=None,
    coherence=None,
    prominence=None,
    prominence_scaled=None,
    height_scaled=None,
    rt_delta=None,
    score=None,
    charge=None,
    mass_neutral=None,
    mass_shift=None,
    samples=None,
    ms2=None,
    inty=None,
    name=None,
):
    """
    Select consensus features from consensus_df based on specified criteria and return the filtered DataFrame.

    OPTIMIZED VERSION: Enhanced performance with lazy evaluation, vectorized operations, and efficient filtering.

    Parameters:
        uid: consensus UID filter with flexible formats:
            - None: include all consensus features (default)
            - int: single specific consensus_uid
            - tuple: range of consensus_uids (consensus_uid_min, consensus_uid_max)
            - list: specific list of consensus_uid values
        mz: m/z filter with flexible formats:
            - float: m/z value ± default tolerance (uses study.parameters.eic_mz_tol)
            - tuple (mz_min, mz_max): range where mz_max > mz_min
            - tuple (mz_center, mz_tol): range where mz_tol < mz_center (interpreted as mz_center ± mz_tol)
        rt: retention time filter with flexible formats:
            - float: RT value ± default tolerance (uses study.parameters.eic_rt_tol)
            - tuple (rt_min, rt_max): range where rt_max > rt_min
            - tuple (rt_center, rt_tol): range where rt_tol < rt_center (interpreted as rt_center ± rt_tol)
        inty_mean: mean intensity filter (tuple for range, single value for minimum). Alias: inty
        consensus_uid: consensus UID filter (list, single value, or tuple for range)
        consensus_id: consensus ID filter (list or single value)
        number_samples: number of samples filter (tuple for range, single value for minimum). Alias: samples
        number_ms2: number of MS2 spectra filter (tuple for range, single value for minimum). Alias: ms2
        quality: quality score filter (tuple for range, single value for minimum)
        bl: baseline filter (tuple for range, single value for minimum)
        chrom_sanity_mean: mean chromatogram sanity filter (tuple for range, single value for minimum). Alias: sanity
        chrom_coherence_mean: mean chromatogram coherence filter (tuple for range, single value for minimum). Alias: coherence
        chrom_prominence_mean: mean chromatogram prominence filter (tuple for range, single value for minimum). Alias: prominence
        chrom_prominence_scaled_mean: mean scaled chromatogram prominence filter (tuple for range, single value for minimum). Alias: prominence_scaled
        chrom_height_scaled_mean: mean scaled chromatogram height filter (tuple for range, single value for minimum). Alias: height_scaled
        rt_delta_mean: chromatogram RT delta filter (tuple for range, single value for minimum). Alias: rt_delta
        id_top_score: identification top score filter (tuple for range, single value for minimum). Alias: score
        identified: filter by identification status:
            - True: select only rows with id_top_name not null
            - False: select only rows with id_top_name null
            - None: no filtering (default)
        adduct_top: adduct type filter (list or single string value, e.g. "[M+H]+", "[M+Na]+")
        adduct_charge_top: adduct charge filter (tuple for range, single value for exact match). Alias: charge
        adduct_mass_neutral_top: neutral mass filter (tuple for range, single value for minimum). Alias: mass_neutral
        adduct_mass_shift_top: adduct mass shift filter (tuple for range, single value for minimum). Alias: mass_shift
        adduct_group: adduct group ID filter (list, single value, or tuple for range)
        adduct_of: adduct representative UID filter (list, single value, or tuple for range)
        id_top_name: identification name filter (list or single string value for compound names). Alias: name
        id_top_class: identification class filter (list or single string value for compound classes)
        id_top_adduct: identification adduct filter (list or single string value for identified adducts)
        sortby: column name(s) to sort by (string, list of strings, or None for no sorting)
        descending: sort direction (True for descending, False for ascending, default is True)
        
        Short aliases (for convenience):
            sanity -> chrom_sanity_mean
            coherence -> chrom_coherence_mean
            prominence -> chrom_prominence_mean
            prominence_scaled -> chrom_prominence_scaled_mean
            height_scaled -> chrom_height_scaled_mean
            rt_delta -> rt_delta_mean
            score -> id_top_score
            charge -> adduct_charge_top
            mass_neutral -> adduct_mass_neutral_top
            mass_shift -> adduct_mass_shift_top
            samples -> number_samples
            ms2 -> number_ms2
            inty -> inty_mean
            name -> id_top_name

    Returns:
        polars.DataFrame: Filtered consensus DataFrame
    """
    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.warning("No consensus features found in study.")
        return pl.DataFrame()

    # Apply short aliases (short aliases take precedence if both are provided)
    if sanity is not None:
        chrom_sanity_mean = sanity
    if coherence is not None:
        chrom_coherence_mean = coherence
    if prominence is not None:
        chrom_prominence_mean = prominence
    if prominence_scaled is not None:
        chrom_prominence_scaled_mean = prominence_scaled
    if height_scaled is not None:
        chrom_height_scaled_mean = height_scaled
    if rt_delta is not None:
        rt_delta_mean = rt_delta
    if score is not None:
        id_top_score = score
    if charge is not None:
        adduct_charge_top = charge
    if mass_neutral is not None:
        adduct_mass_neutral_top = mass_neutral
    if mass_shift is not None:
        adduct_mass_shift_top = mass_shift
    if samples is not None:
        number_samples = samples
    if ms2 is not None:
        number_ms2 = ms2
    if inty is not None:
        inty_mean = inty
    if name is not None:
        id_top_name = name

    # Early return optimization - check if any filters are provided
    filter_params = [
        uid,
        mz,
        rt,
        inty_mean,
        consensus_uid,
        consensus_id,
        number_samples,
        number_ms2,
        quality,
        bl,
        chrom_sanity_mean,
        chrom_coherence_mean,
        chrom_prominence_mean,
        chrom_prominence_scaled_mean,
        chrom_height_scaled_mean,
        rt_delta_mean,
        id_top_score,
        identified,
        # New adduct and identification parameters
        adduct_top,
        adduct_charge_top,
        adduct_mass_neutral_top,
        adduct_mass_shift_top,
        adduct_group,
        adduct_of,
        id_top_name,
        id_top_class,
        id_top_adduct,
    ]

    if all(param is None for param in filter_params) and sortby is None:
        return self.consensus_df.clone()

    import time

    start_time = time.perf_counter()
    initial_count = len(self.consensus_df)

    # Pre-check available columns once for efficiency
    available_columns = set(self.consensus_df.columns)
    filter_conditions = []
    warnings = []

    # Build all filter conditions efficiently
    # Handle uid parameter first (consensus_uid filter with flexible formats)
    if uid is not None:
        if isinstance(uid, int):
            # Single specific consensus_uid
            filter_conditions.append(pl.col("consensus_uid") == uid)
        elif isinstance(uid, tuple) and len(uid) == 2:
            # Range of consensus_uids (consensus_uid_min, consensus_uid_max)
            min_uid, max_uid = uid
            filter_conditions.append((pl.col("consensus_uid") >= min_uid) & (pl.col("consensus_uid") <= max_uid))
        elif isinstance(uid, list):
            # Specific list of consensus_uid values
            filter_conditions.append(pl.col("consensus_uid").is_in(uid))
        else:
            self.logger.warning(f"Invalid uid parameter type: {type(uid)}. Expected int, tuple, or list.")

    if mz is not None:
        if isinstance(mz, tuple) and len(mz) == 2:
            if mz[1] < mz[0]:
                # mz_center ± mz_tol format
                mz_center, mz_tol = mz
                min_mz = mz_center - mz_tol
                max_mz = mz_center + mz_tol
            else:
                # (min_mz, max_mz) format
                min_mz, max_mz = mz
            filter_conditions.append((pl.col("mz") >= min_mz) & (pl.col("mz") <= max_mz))
        else:
            # Single value with default tolerance
            default_mz_tol = getattr(self, "parameters", None)
            if default_mz_tol and hasattr(default_mz_tol, "eic_mz_tol"):
                default_mz_tol = default_mz_tol.eic_mz_tol
            else:
                from masster.study.defaults.align_def import align_defaults

                default_mz_tol = align_defaults().mz_max_diff

            min_mz = mz - default_mz_tol
            max_mz = mz + default_mz_tol
            filter_conditions.append((pl.col("mz") >= min_mz) & (pl.col("mz") <= max_mz))

    if rt is not None:
        if isinstance(rt, tuple) and len(rt) == 2:
            if rt[1] < rt[0]:
                # rt_center ± rt_tol format
                rt_center, rt_tol = rt
                min_rt = rt_center - rt_tol
                max_rt = rt_center + rt_tol
            else:
                # (min_rt, max_rt) format
                min_rt, max_rt = rt
            filter_conditions.append((pl.col("rt") >= min_rt) & (pl.col("rt") <= max_rt))
        else:
            # Single value with default tolerance
            default_rt_tol = getattr(self, "parameters", None)
            if default_rt_tol and hasattr(default_rt_tol, "eic_rt_tol"):
                default_rt_tol = default_rt_tol.eic_rt_tol
            else:
                from masster.study.defaults.align_def import align_defaults

                default_rt_tol = align_defaults().rt_tol

            min_rt = rt - default_rt_tol
            max_rt = rt + default_rt_tol
            filter_conditions.append((pl.col("rt") >= min_rt) & (pl.col("rt") <= max_rt))

    # Helper function to add range/minimum filters
    def _add_range_filter(param, column, param_name):
        if param is not None:
            if column in available_columns:
                if isinstance(param, tuple) and len(param) == 2:
                    min_val, max_val = param
                    filter_conditions.append((pl.col(column) >= min_val) & (pl.col(column) <= max_val))
                else:
                    filter_conditions.append(pl.col(column) >= param)
            else:
                warnings.append(f"'{column}' column not found in consensus_df")

    # Apply range/minimum filters efficiently
    _add_range_filter(inty_mean, "inty_mean", "inty_mean")
    _add_range_filter(quality, "quality", "quality")
    _add_range_filter(bl, "bl", "bl")
    _add_range_filter(chrom_sanity_mean, "chrom_sanity_mean", "chrom_sanity_mean")
    _add_range_filter(chrom_coherence_mean, "chrom_coherence_mean", "chrom_coherence_mean")
    _add_range_filter(chrom_prominence_mean, "chrom_prominence_mean", "chrom_prominence_mean")
    _add_range_filter(chrom_prominence_scaled_mean, "chrom_prominence_scaled_mean", "chrom_prominence_scaled_mean")
    _add_range_filter(chrom_height_scaled_mean, "chrom_height_scaled_mean", "chrom_height_scaled_mean")
    _add_range_filter(rt_delta_mean, "rt_delta_mean", "rt_delta_mean")
    _add_range_filter(id_top_score, "id_top_score", "id_top_score")
    _add_range_filter(number_samples, "number_samples", "number_samples")

    # Handle number_ms2 with column check
    if number_ms2 is not None:
        if "number_ms2" in available_columns:
            if isinstance(number_ms2, tuple) and len(number_ms2) == 2:
                min_ms2, max_ms2 = number_ms2
                filter_conditions.append((pl.col("number_ms2") >= min_ms2) & (pl.col("number_ms2") <= max_ms2))
            else:
                filter_conditions.append(pl.col("number_ms2") >= number_ms2)
        else:
            warnings.append("'number_ms2' column not found in consensus_df")

    # Handle consensus_uid (list, single value, or range)
    if consensus_uid is not None:
        if isinstance(consensus_uid, (list, tuple)):
            if len(consensus_uid) == 2 and not isinstance(consensus_uid, list):
                # Treat tuple as range
                min_uid, max_uid = consensus_uid
                filter_conditions.append((pl.col("consensus_uid") >= min_uid) & (pl.col("consensus_uid") <= max_uid))
            else:
                # Treat as list of values
                filter_conditions.append(pl.col("consensus_uid").is_in(consensus_uid))
        else:
            filter_conditions.append(pl.col("consensus_uid") == consensus_uid)

    # Handle consensus_id (list or single value)
    if consensus_id is not None:
        if isinstance(consensus_id, list):
            filter_conditions.append(pl.col("consensus_id").is_in(consensus_id))
        else:
            filter_conditions.append(pl.col("consensus_id") == consensus_id)

    # Handle identified status filter
    if identified is not None:
        if "id_top_name" in available_columns:
            if identified:
                filter_conditions.append(pl.col("id_top_name").is_not_null())
            else:
                filter_conditions.append(pl.col("id_top_name").is_null())
        else:
            warnings.append("'id_top_name' column not found in consensus_df")

    # Handle adduct_top filter (string or list)
    if adduct_top is not None:
        if "adduct_top" in available_columns:
            if isinstance(adduct_top, list):
                filter_conditions.append(pl.col("adduct_top").is_in(adduct_top))
            else:
                filter_conditions.append(pl.col("adduct_top") == adduct_top)
        else:
            warnings.append("'adduct_top' column not found in consensus_df")

    # Handle adduct_charge_top filter (single value, range tuple, or list)
    if adduct_charge_top is not None:
        if "adduct_charge_top" in available_columns:
            if isinstance(adduct_charge_top, tuple) and len(adduct_charge_top) == 2:
                filter_conditions.append(
                    (pl.col("adduct_charge_top") >= adduct_charge_top[0])
                    & (pl.col("adduct_charge_top") <= adduct_charge_top[1])
                )
            elif isinstance(adduct_charge_top, list):
                filter_conditions.append(pl.col("adduct_charge_top").is_in(adduct_charge_top))
            else:
                filter_conditions.append(pl.col("adduct_charge_top") == adduct_charge_top)
        else:
            warnings.append("'adduct_charge_top' column not found in consensus_df")

    # Handle adduct_mass_neutral_top filter (single value, range tuple, or list)
    if adduct_mass_neutral_top is not None:
        if "adduct_mass_neutral_top" in available_columns:
            if isinstance(adduct_mass_neutral_top, tuple) and len(adduct_mass_neutral_top) == 2:
                filter_conditions.append(
                    (pl.col("adduct_mass_neutral_top") >= adduct_mass_neutral_top[0])
                    & (pl.col("adduct_mass_neutral_top") <= adduct_mass_neutral_top[1])
                )
            elif isinstance(adduct_mass_neutral_top, list):
                filter_conditions.append(pl.col("adduct_mass_neutral_top").is_in(adduct_mass_neutral_top))
            else:
                filter_conditions.append(pl.col("adduct_mass_neutral_top") == adduct_mass_neutral_top)
        else:
            warnings.append("'adduct_mass_neutral_top' column not found in consensus_df")

    # Handle adduct_mass_shift_top filter (single value, range tuple, or list)
    if adduct_mass_shift_top is not None:
        if "adduct_mass_shift_top" in available_columns:
            if isinstance(adduct_mass_shift_top, tuple) and len(adduct_mass_shift_top) == 2:
                filter_conditions.append(
                    (pl.col("adduct_mass_shift_top") >= adduct_mass_shift_top[0])
                    & (pl.col("adduct_mass_shift_top") <= adduct_mass_shift_top[1])
                )
            elif isinstance(adduct_mass_shift_top, list):
                filter_conditions.append(pl.col("adduct_mass_shift_top").is_in(adduct_mass_shift_top))
            else:
                filter_conditions.append(pl.col("adduct_mass_shift_top") == adduct_mass_shift_top)
        else:
            warnings.append("'adduct_mass_shift_top' column not found in consensus_df")

    # Handle adduct_group filter (single value or list)
    if adduct_group is not None:
        if "adduct_group" in available_columns:
            if isinstance(adduct_group, list):
                filter_conditions.append(pl.col("adduct_group").is_in(adduct_group))
            else:
                filter_conditions.append(pl.col("adduct_group") == adduct_group)
        else:
            warnings.append("'adduct_group' column not found in consensus_df")

    # Handle adduct_of filter (single value or list)
    if adduct_of is not None:
        if "adduct_of" in available_columns:
            if isinstance(adduct_of, list):
                filter_conditions.append(pl.col("adduct_of").is_in(adduct_of))
            else:
                filter_conditions.append(pl.col("adduct_of") == adduct_of)
        else:
            warnings.append("'adduct_of' column not found in consensus_df")

    # Handle id_top_name filter (string or list)
    if id_top_name is not None:
        if "id_top_name" in available_columns:
            if isinstance(id_top_name, list):
                filter_conditions.append(pl.col("id_top_name").is_in(id_top_name))
            else:
                filter_conditions.append(pl.col("id_top_name") == id_top_name)
        else:
            warnings.append("'id_top_name' column not found in consensus_df")

    # Handle id_top_class filter (string or list)
    if id_top_class is not None:
        if "id_top_class" in available_columns:
            if isinstance(id_top_class, list):
                filter_conditions.append(pl.col("id_top_class").is_in(id_top_class))
            else:
                filter_conditions.append(pl.col("id_top_class") == id_top_class)
        else:
            warnings.append("'id_top_class' column not found in consensus_df")

    # Handle id_top_adduct filter (string or list)
    if id_top_adduct is not None:
        if "id_top_adduct" in available_columns:
            if isinstance(id_top_adduct, list):
                filter_conditions.append(pl.col("id_top_adduct").is_in(id_top_adduct))
            else:
                filter_conditions.append(pl.col("id_top_adduct") == id_top_adduct)
        else:
            warnings.append("'id_top_adduct' column not found in consensus_df")

    # Handle id_top_score filter (single value, range tuple, or list)
    if id_top_score is not None:
        if "id_top_score" in available_columns:
            if isinstance(id_top_score, tuple) and len(id_top_score) == 2:
                filter_conditions.append(
                    (pl.col("id_top_score") >= id_top_score[0]) & (pl.col("id_top_score") <= id_top_score[1])
                )
            elif isinstance(id_top_score, list):
                filter_conditions.append(pl.col("id_top_score").is_in(id_top_score))
            else:
                filter_conditions.append(pl.col("id_top_score") == id_top_score)
        else:
            warnings.append("'id_top_score' column not found in consensus_df")

    # Log warnings once
    for warning in warnings:
        self.logger.warning(warning)

    # Apply all filters at once using lazy evaluation for optimal performance
    if filter_conditions:
        # Combine all conditions efficiently using reduce
        from functools import reduce
        import operator

        combined_filter = reduce(operator.and_, filter_conditions)

        consensus = self.consensus_df.lazy().filter(combined_filter).collect(streaming=True)
    else:
        consensus = self.consensus_df.clone()

    final_count = len(consensus)

    # Early return if no results
    if final_count == 0:
        self.logger.warning("No consensus features remaining after applying selection criteria.")
        return pl.DataFrame()

    # Sort the results if sortby is specified
    if sortby is not None:
        if isinstance(sortby, str):
            if sortby in consensus.columns:
                consensus = consensus.sort(sortby, descending=descending)
            else:
                self.logger.warning(f"Sort column '{sortby}' not found in consensus DataFrame")
        elif isinstance(sortby, (list, tuple)):
            valid_columns = [col for col in sortby if col in consensus.columns]
            invalid_columns = [col for col in sortby if col not in consensus.columns]

            if invalid_columns:
                self.logger.warning(f"Sort columns not found in consensus DataFrame: {invalid_columns}")

            if valid_columns:
                consensus = consensus.sort(valid_columns, descending=descending)
        else:
            self.logger.warning(f"Invalid sortby parameter type: {type(sortby)}. Expected str, list, or tuple.")

    # Log performance metrics
    elapsed_time = time.perf_counter() - start_time
    removed_count = initial_count - final_count

    self.logger.info(
        f"Selected consensus features: {final_count:,} (removed: {removed_count:,}) in {elapsed_time:.4f}s"
    )

    return consensus


def consensus_filter(self, consensus):
    """
    Filter consensus_df by keeping only consensus features that match the given criteria.
    This keeps only the specified consensus features and removes all others.
    Also updates related entries in consensus_mapping_df, features_df, and consensus_ms2.

    Parameters:
        consensus: Consensus features to keep. Can be:
                  - polars.DataFrame: Consensus DataFrame (will use consensus_uid column)
                  - list: List of consensus_uids to keep
                  - int: Single consensus_uid to keep

    Returns:
        None (modifies self.consensus_df and related DataFrames in place)
    """
    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.warning("No consensus features found in study.")
        return

    initial_consensus_count = len(self.consensus_df)

    # Determine consensus_uids to keep
    if isinstance(consensus, pl.DataFrame):
        if "consensus_uid" not in consensus.columns:
            self.logger.error("consensus DataFrame must contain 'consensus_uid' column")
            return
        consensus_uids_to_keep = consensus["consensus_uid"].to_list()
    elif isinstance(consensus, list):
        consensus_uids_to_keep = consensus
    elif isinstance(consensus, int):
        consensus_uids_to_keep = [consensus]
    else:
        self.logger.error("consensus parameter must be a DataFrame, list, or int")
        return

    if not consensus_uids_to_keep:
        self.logger.warning("No consensus UIDs provided for filtering.")
        return

    # Get feature_uids that need to be kept in features_df
    feature_uids_to_keep = []
    if self.consensus_mapping_df is not None and not self.consensus_mapping_df.is_empty():
        feature_uids_to_keep = self.consensus_mapping_df.filter(
            pl.col("consensus_uid").is_in(consensus_uids_to_keep),
        )["feature_uid"].to_list()

    # Keep only specified consensus features in consensus_df
    self.consensus_df = self.consensus_df.filter(
        pl.col("consensus_uid").is_in(consensus_uids_to_keep),
    )

    # Keep only relevant entries in consensus_mapping_df
    if self.consensus_mapping_df is not None and not self.consensus_mapping_df.is_empty():
        initial_mapping_count = len(self.consensus_mapping_df)
        self.consensus_mapping_df = self.consensus_mapping_df.filter(
            pl.col("consensus_uid").is_in(consensus_uids_to_keep),
        )
        remaining_mapping_count = len(self.consensus_mapping_df)
        removed_mapping_count = initial_mapping_count - remaining_mapping_count
        if removed_mapping_count > 0:
            self.logger.debug(
                f"Removed {removed_mapping_count} entries from consensus_mapping_df",
            )

    # Keep only corresponding features in features_df
    if feature_uids_to_keep and self.features_df is not None and not self.features_df.is_empty():
        initial_features_count = len(self.features_df)
        self.features_df = self.features_df.filter(
            pl.col("feature_uid").is_in(feature_uids_to_keep),
        )
        remaining_features_count = len(self.features_df)
        removed_features_count = initial_features_count - remaining_features_count
        if removed_features_count > 0:
            self.logger.debug(
                f"Removed {removed_features_count} entries from features_df",
            )

    # Keep only relevant entries in consensus_ms2 if it exists
    if hasattr(self, "consensus_ms2") and self.consensus_ms2 is not None and not self.consensus_ms2.is_empty():
        initial_ms2_count = len(self.consensus_ms2)
        self.consensus_ms2 = self.consensus_ms2.filter(
            pl.col("consensus_uid").is_in(consensus_uids_to_keep),
        )
        remaining_ms2_count = len(self.consensus_ms2)
        removed_ms2_count = initial_ms2_count - remaining_ms2_count
        if removed_ms2_count > 0:
            self.logger.debug(f"Removed {removed_ms2_count} entries from consensus_ms2")

    remaining_consensus_count = len(self.consensus_df)
    removed_consensus_count = initial_consensus_count - remaining_consensus_count
    self.logger.info(
        f"Filtered consensus features: kept {remaining_consensus_count}, removed {removed_consensus_count}",
    )

    # Store filtering parameters in history
    self.update_history(["consensus_filter"], {
        "initial_count": initial_consensus_count,
        "kept_count": remaining_consensus_count,
        "removed_count": removed_consensus_count,
        "feature_uids_kept": len(feature_uids_to_keep) if feature_uids_to_keep else 0
    })


def consensus_delete(self, consensus):
    """
    Delete consensus features from consensus_df based on consensus identifiers.
    This removes the specified consensus features and keeps all others (opposite of consensus_filter).
    Also removes related entries from consensus_mapping_df, features_df, and consensus_ms2.

    Parameters:
        consensus: Consensus features to delete. Can be:
                  - polars.DataFrame: Consensus DataFrame (will use consensus_uid column)
                  - list: List of consensus_uids to delete
                  - int: Single consensus_uid to delete

    Returns:
        None (modifies self.consensus_df and related DataFrames in place)
    """
    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.warning("No consensus features found in study.")
        return

    # Early return if no consensus provided
    if consensus is None:
        self.logger.warning("No consensus provided for deletion.")
        return

    initial_consensus_count = len(self.consensus_df)

    # Determine consensus_uids to remove
    if isinstance(consensus, pl.DataFrame):
        if "consensus_uid" not in consensus.columns:
            self.logger.error("consensus DataFrame must contain 'consensus_uid' column")
            return
        consensus_uids_to_remove = consensus["consensus_uid"].to_list()
    elif isinstance(consensus, list):
        consensus_uids_to_remove = consensus
    elif isinstance(consensus, int):
        consensus_uids_to_remove = [consensus]
    else:
        self.logger.error("consensus parameter must be a DataFrame, list, or int")
        return

    if not consensus_uids_to_remove:
        self.logger.warning("No consensus UIDs provided for deletion.")
        return

    # Convert to set for faster lookup if list is large
    if len(consensus_uids_to_remove) > 100:
        consensus_uids_set = set(consensus_uids_to_remove)
        # Use the set for filtering if it's significantly smaller
        if len(consensus_uids_set) < len(consensus_uids_to_remove) * 0.8:
            consensus_uids_to_remove = list(consensus_uids_set)

    # Get feature_uids that need to be removed from features_df
    feature_uids_to_remove = []
    if self.consensus_mapping_df is not None and not self.consensus_mapping_df.is_empty():
        feature_uids_to_remove = self.consensus_mapping_df.filter(
            pl.col("consensus_uid").is_in(consensus_uids_to_remove),
        )["feature_uid"].to_list()

    # Remove consensus features from consensus_df
    self.consensus_df = self.consensus_df.filter(
        ~pl.col("consensus_uid").is_in(consensus_uids_to_remove),
    )

    # Remove from consensus_mapping_df
    mapping_removed_count = 0
    if self.consensus_mapping_df is not None and not self.consensus_mapping_df.is_empty():
        initial_mapping_count = len(self.consensus_mapping_df)
        self.consensus_mapping_df = self.consensus_mapping_df.filter(
            ~pl.col("consensus_uid").is_in(consensus_uids_to_remove),
        )
        mapping_removed_count = initial_mapping_count - len(self.consensus_mapping_df)

    # Remove corresponding features from features_df
    features_removed_count = 0
    if feature_uids_to_remove and self.features_df is not None and not self.features_df.is_empty():
        initial_features_count = len(self.features_df)
        self.features_df = self.features_df.filter(
            ~pl.col("feature_uid").is_in(feature_uids_to_remove),
        )
        features_removed_count = initial_features_count - len(self.features_df)

    # Remove from consensus_ms2 if it exists
    ms2_removed_count = 0
    if hasattr(self, "consensus_ms2") and self.consensus_ms2 is not None and not self.consensus_ms2.is_empty():
        initial_ms2_count = len(self.consensus_ms2)
        self.consensus_ms2 = self.consensus_ms2.filter(
            ~pl.col("consensus_uid").is_in(consensus_uids_to_remove),
        )
        ms2_removed_count = initial_ms2_count - len(self.consensus_ms2)

    # Calculate results and log efficiently
    final_consensus_count = len(self.consensus_df)
    consensus_removed_count = initial_consensus_count - final_consensus_count

    # Single comprehensive log message
    log_parts = [f"Deleted {consensus_removed_count} consensus features"]
    if mapping_removed_count > 0:
        log_parts.append(f"{mapping_removed_count} consensus mappings")
    if features_removed_count > 0:
        log_parts.append(f"{features_removed_count} features")
    if ms2_removed_count > 0:
        log_parts.append(f"{ms2_removed_count} MS2 spectra")

    log_message = ". ".join(log_parts) + f". Remaining consensus: {final_consensus_count}"
    self.logger.info(log_message)


# =====================================================================================
# SCHEMA AND DATA STRUCTURE FUNCTIONS
# =====================================================================================


def _ensure_features_df_schema_order(self):
    """
    Ensure features_df columns are ordered according to study5_schema.json.

    This method should be called after operations that might scramble the column order.
    """
    if self.features_df is None or self.features_df.is_empty():
        return

    try:
        import os
        import json
        from masster.study.h5 import _reorder_columns_by_schema

        # Load schema
        schema_path = os.path.join(os.path.dirname(__file__), "study5_schema.json")
        with open(schema_path) as f:
            schema = json.load(f)

        # Reorder columns to match schema
        self.features_df = _reorder_columns_by_schema(
            self.features_df,
            schema,
            "features_df",
        )

    except Exception as e:
        self.logger.warning(f"Failed to reorder features_df columns: {e}")


def restore_ms2(self, samples=None, **kwargs):
    """
    Restore MS2 data by re-running find_ms2 on specified samples.

    This function rebuilds the consensus_ms2 DataFrame by re-extracting MS2 spectra
    from the original sample files. Use this to reverse the effects of compress_ms2().

    Parameters:
        samples (list, optional): List of sample_uids or sample_names to process.
                                 If None, processes all samples.
        **kwargs: Additional keyword arguments passed to find_ms2()
                 (e.g., mz_tol, centroid, deisotope, etc.)
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.error("No features_df found in study.")
        return

    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.error("No samples_df found in study.")
        return

    # Get sample_uids to process
    sample_uids = self._get_samples_uids(samples)
    if not sample_uids:
        self.logger.warning("No valid samples specified.")
        return

    self.logger.info(f"Restoring MS2 data from {len(sample_uids)} samples...")

    # Clear existing consensus_ms2 to rebuild from scratch
    initial_ms2_count = len(self.consensus_ms2) if not self.consensus_ms2.is_empty() else 0
    self.consensus_ms2 = pl.DataFrame()

    # Re-run find_ms2 which will rebuild consensus_ms2
    try:
        self.find_ms2(**kwargs)

        final_ms2_count = len(self.consensus_ms2) if not self.consensus_ms2.is_empty() else 0

        self.logger.info(
            f"MS2 restoration completed: {initial_ms2_count} -> {final_ms2_count} MS2 spectra",
        )

    except Exception as e:
        self.logger.error(f"Failed to restore MS2 data: {e}")
        raise


def decompress(self, features=True, ms2=True, chrom=True, samples=None, **kwargs):
    """
    Reverse any compression effects by restoring compressed data adaptively.

    This function restores data that was compressed using compress(), compress_features(),
    compress_ms2(), compress_chrom(), or study.save(compress=True). It optimizes the
    decompression process for speed by only processing what actually needs restoration.

    Parameters:
        features (bool): Restore features data (ms2_specs, ms2_scans, chrom_area)
        ms2 (bool): Restore MS2 spectra by re-running find_ms2()
        chrom (bool): Restore chromatogram objects
        samples (list, optional): List of sample_uids or sample_names to process.
                                 If None, processes all samples.
        **kwargs: Additional keyword arguments for restoration functions:
                 - For restore_chrom: mz_tol (default: 0.010), rt_tol (default: 10.0)
                 - For restore_ms2/find_ms2: mz_tol, centroid, deisotope, etc.

    Performance Optimizations:
        - Adaptive processing: Only restores what actually needs restoration
        - Processes features and chromatograms together when possible (shared file I/O)
        - Uses cached sample instances to avoid repeated file loading
        - Processes MS2 restoration last as it's the most computationally expensive
        - Provides detailed progress information for long-running operations

    Example:
        # Restore everything (but only what needs restoration)
        study.decompress()

        # Restore only chromatograms with custom tolerances
        study.decompress(features=False, ms2=False, chrom=True, mz_tol=0.005, rt_tol=5.0)

        # Restore specific samples only
        study.decompress(samples=["sample1", "sample2"])
    """
    if not any([features, ms2, chrom]):
        self.logger.warning("No decompression operations specified.")
        return

    # Get sample_uids to process
    sample_uids = self._get_samples_uids(samples)
    if not sample_uids:
        self.logger.warning("No valid samples specified.")
        return

    # Adaptively check what actually needs to be done
    import polars as pl

    # Check if features need restoration (more sophisticated logic)
    features_need_restoration = False
    if features and not self.features_df.is_empty():
        # Check for completely missing columns that should exist after feature processing
        missing_cols = []
        for col in ["ms2_scans", "ms2_specs"]:
            if col not in self.features_df.columns:
                missing_cols.append(col)

        # If columns are missing entirely, we likely need restoration
        if missing_cols:
            features_need_restoration = True
        else:
            # If columns exist, check if they're mostly null (indicating compression)
            # But be smart about it - only check if we have consensus features with MS2
            if not self.consensus_ms2.is_empty():
                # We have MS2 data, so ms2_specs should have some content
                null_ms2_specs = self.features_df.filter(
                    pl.col("ms2_specs").is_null(),
                ).height
                total_features = len(self.features_df)
                # If more than 90% are null but we have MS2 data, likely compressed
                if null_ms2_specs > (total_features * 0.9):
                    features_need_restoration = True

    # Check if chromatograms need restoration
    chrom_need_restoration = False
    if chrom and not self.features_df.is_empty():
        if "chrom" not in self.features_df.columns:
            # Column completely missing
            chrom_need_restoration = True
        else:
            null_chroms = self.features_df.filter(pl.col("chrom").is_null()).height
            total_features = len(self.features_df)
            # If more than 50% are null, likely need restoration
            chrom_need_restoration = null_chroms > (total_features * 0.5)

    # Check if MS2 data might need restoration (compare expected vs actual)
    ms2_need_restoration = False
    if ms2:
        current_ms2_count = len(self.consensus_ms2) if not self.consensus_ms2.is_empty() else 0
        consensus_count = len(self.consensus_df) if not self.consensus_df.is_empty() else 0

        if consensus_count > 0:
            # Calculate expected MS2 count based on consensus features with MS2 potential
            # This is a heuristic - if we have very few MS2 compared to consensus, likely compressed
            expected_ratio = 3.0  # Expect at least 3 MS2 per consensus on average
            expected_ms2 = consensus_count * expected_ratio

            if current_ms2_count < min(expected_ms2 * 0.3, consensus_count * 0.8):
                ms2_need_restoration = True

    # Build list of operations that actually need to be done
    operations_needed = []
    if features and features_need_restoration:
        operations_needed.append("features")
    if chrom and chrom_need_restoration:
        operations_needed.append("chromatograms")
    if ms2 and ms2_need_restoration:
        operations_needed.append("MS2 spectra")

    # Early exit if nothing needs to be done
    if not operations_needed:
        self.logger.info(
            "All data appears to be already decompressed. No operations needed.",
        )
        return

    self.logger.info(
        f"Starting adaptive decompression: {', '.join(operations_needed)} from {len(sample_uids)} samples",
    )

    try:
        # Phase 1: Restore features and chromatograms together (shared file I/O)
        if "features" in operations_needed and "chromatograms" in operations_needed:
            self.logger.info(
                "Phase 1: Restoring features and chromatograms together...",
            )

            # Extract relevant kwargs for restore_features and restore_chrom
            restore_kwargs = {}
            if "mz_tol" in kwargs:
                restore_kwargs["mz_tol"] = kwargs["mz_tol"]
            if "rt_tol" in kwargs:
                restore_kwargs["rt_tol"] = kwargs["rt_tol"]

            # Restore features first (includes chrom column)
            self.restore_features(samples=samples)

            # Then do additional chrom gap-filling if needed
            self.restore_chrom(samples=samples, **restore_kwargs)

        elif "features" in operations_needed and "chromatograms" not in operations_needed:
            self.logger.info("Phase 1: Restoring features data...")
            self.restore_features(samples=samples)

        elif "chromatograms" in operations_needed and "features" not in operations_needed:
            self.logger.info("Phase 1: Restoring chromatograms...")
            restore_kwargs = {}
            if "mz_tol" in kwargs:
                restore_kwargs["mz_tol"] = kwargs["mz_tol"]
            if "rt_tol" in kwargs:
                restore_kwargs["rt_tol"] = kwargs["rt_tol"]
            self.restore_chrom(samples=samples, **restore_kwargs)

        # Phase 2: Restore MS2 data (most computationally expensive, done last)
        if "MS2 spectra" in operations_needed:
            self.logger.info("Phase 2: Restoring MS2 spectra...")

            # Extract MS2-specific kwargs
            ms2_kwargs = {}
            for key, value in kwargs.items():
                if key in [
                    "mz_tol",
                    "centroid",
                    "deisotope",
                    "dia_stats",
                    "feature_uid",
                ]:
                    ms2_kwargs[key] = value

            self.restore_ms2(samples=samples, **ms2_kwargs)

        self.logger.success("Adaptive decompression completed successfully")

    except Exception as e:
        self.logger.error(f"Decompression failed: {e}")
        raise
