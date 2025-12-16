"""
Wizard module for automated processing of mass spectrometry studies.

This module provides the Wizard class for fully automated processing of MS data
from raw files to final study results, including batch conversion, assembly,
alignment, merging, plotting, and export.

Key Features:
- Automated discovery and batch conversion of raw data files
- Intelligent resume capability for interrupted processes
- Parallel processing optimization for large datasets
- Adaptive study format based on study size
- Comprehensive logging and progress tracking
- Optimized memory management for large studies

Classes:
- Wizard: Main class for automated study processing
- wizard_def: Default parameters configuration class

Example Usage:
```python
from masster import Wizard, wizard_def

# Create wizard with default parameters
wizard = Wizard(
    source="./raw_data",
    folder="./processed_study",
    polarity="positive",
    num_cores=6
)

```
"""

from __future__ import annotations

import os
import sys
import multiprocessing
from pathlib import Path
from typing import Optional, Any, Dict, List
from dataclasses import dataclass, field

from masster.study.defaults.study_def import study_defaults
from masster._version import __version__ as version
from masster.logger import MassterLogger


@dataclass
class wizard_def:
    """
    Default parameters for the Wizard automated processing system.

    This class provides comprehensive configuration for all stages of automated
    mass spectrometry data processing from raw files to final results.

    Attributes:
        # Core Configuration
        source (str): Path to directory containing raw data files
        folder (str): Output directory for processed study
        polarity (Optional[str]): Ion polarity mode ("positive", "negative", or None for auto-detection)
        num_cores (int): Number of CPU cores to use for parallel processing

        # File Discovery
        file_extensions (List[str]): File extensions to search for
        search_subfolders (bool): Whether to search subdirectories
        skip_patterns (List[str]): Filename patterns to skip
        wiff_sample_selection (str): For WIFF files with multiple samples - 'first', 'last', or 'all' (default: 'last')

        # Processing Parameters
        adducts (List[str]): Adduct specifications for given polarity
        batch_size (int): Number of files to process per batch
        memory_limit_gb (float): Memory limit for processing (GB)

        # Resume & Recovery
        resume_enabled (bool): Enable automatic resume capability
        force_reprocess (bool): Force reprocessing of existing files
        backup_enabled (bool): Create backups of intermediate results

        # Output & Export
        generate_plots (bool): Generate visualization plots
        export_formats (List[str]): Output formats to generate
        compress_output (bool): Compress final study file

        # Logging
        log_level (str): Logging detail level
        log_to_file (bool): Save logs to file
        progress_interval (int): Progress update interval (seconds)
    """

    # === Core Configuration ===
    source: str = ""
    folder: str = ""
    polarity: Optional[str] = None
    num_cores: int = 4

    # === File Discovery ===
    file_extensions: List[str] = field(default_factory=lambda: [".wiff", ".raw", ".mzML"])
    search_subfolders: bool = True
    skip_patterns: List[str] = field(default_factory=lambda: ["condition", "test"])
    wiff_sample_selection: str = "last"  # For WIFF files with multiple samples: 'first', 'last', or 'all'

    # === Processing Parameters ===
    adducts: List[str] = field(default_factory=list)  # Will be set based on polarity
    batch_size: int = 8
    memory_limit_gb: float = 16.0
    max_file_size_gb: float = 4.0

    # === Resume & Recovery ===
    resume_enabled: bool = True
    force_reprocess: bool = False
    backup_enabled: bool = True
    checkpoint_interval: int = 10  # Save progress every N files

    # === Study Assembly ===
    min_samples_for_merge: int | None = None  # Will be set based on study size
    rt_tolerance: float = 2.5
    mz_max_diff: float = 0.01
    alignment_algorithm: str = "kd"
    merge_method: str = "qt"

    # === Feature Detection ===
    chrom_fwhm: float | None = None
    noise: float | None = None
    chrom_peak_snr: float = 5.0
    tol_ppm: float = 10.0
    detector_type: str = "unknown"  # Detected detector type ("orbitrap", "quadrupole", "unknown")

    # === Output & Export ===
    generate_plots: bool = True
    generate_interactive: bool = True
    export_formats: List[str] = field(default_factory=lambda: ["csv", "mgf", "xlsx"])
    compress_output: bool = True
    adaptive_compression: bool = True  # Adapt based on study size

    # === Logging ===
    log_level: str = "INFO"
    log_to_file: bool = True
    progress_interval: int = 30  # seconds
    verbose_progress: bool = True

    # === Advanced Options ===
    use_process_pool: bool = True  # vs ThreadPoolExecutor
    optimize_memory: bool = True
    cleanup_temp_files: bool = True
    validate_outputs: bool = True

    _param_metadata: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "source": {
                "dtype": str,
                "description": "Path to directory containing raw data files",
                "required": True,
            },
            "folder": {
                "dtype": str,
                "description": "Output directory for processed study",
                "required": True,
            },
            "polarity": {
                "dtype": str,
                "description": "Ion polarity mode",
                "default": "positive",
                "allowed_values": ["positive", "negative", "pos", "neg"],
            },
            "num_cores": {
                "dtype": int,
                "description": "Number of CPU cores to use",
                "default": 4,
                "min_value": 1,
                "max_value": multiprocessing.cpu_count(),
            },
            "batch_size": {
                "dtype": int,
                "description": "Number of files to process per batch",
                "default": 8,
                "min_value": 1,
                "max_value": 32,
            },
            "memory_limit_gb": {
                "dtype": float,
                "description": "Memory limit for processing (GB)",
                "default": 16.0,
                "min_value": 1.0,
                "max_value": 128.0,
            },
        },
        repr=False,
    )

    def __post_init__(self):
        """Set polarity-specific defaults after initialization."""
        # Set default adducts based on polarity if not provided
        if not self.adducts:
            if self.polarity and self.polarity.lower() in ["positive", "pos"]:
                self.adducts = ["+H:1:0.8", "+Na:1:0.1", "+NH4:1:0.1"]
            elif self.polarity and self.polarity.lower() in ["negative", "neg"]:
                self.adducts = ["-H:-1:1.0", "+CH2O2:0:0.5"]
            else:
                # Default to positive if polarity is None or unknown
                self.adducts = ["+H:1:0.8", "+Na:1:0.1", "+NH4:1:0.1"]

        # Validate num_cores
        max_cores = multiprocessing.cpu_count()
        if self.num_cores <= 0:
            self.num_cores = max_cores
        elif self.num_cores > max_cores:
            self.num_cores = max_cores

        # Ensure paths are absolute
        if self.source:
            self.source = os.path.abspath(self.source)
        if self.folder:
            self.folder = os.path.abspath(self.folder)


class Wizard:
    """
    Automated wizard for end-to-end mass spectrometry data processing.

    The Wizard class provides intelligent automation for processing raw MS data through
    the complete pipeline: file discovery, batch conversion, feature detection, study
    assembly, alignment, consensus generation, gap filling, and export.

    Key Features:
        - Automated file discovery and format detection
        - Intelligent parameter optimization based on data characteristics
        - Parallel processing with optimal resource management
        - Resume capability for interrupted workflows
        - Adaptive study format based on dataset size
        - Comprehensive progress tracking and logging
        - Automated script generation for reproducibility

    Core Methods:
        - create_scripts(): Generate standalone processing scripts and notebooks
        - test_only(): Validate parameters with single file processing
        - test_and_run(): Test parameters, then execute full batch if successful
        - run(): Execute complete batch processing pipeline

    Main Attributes:
        params (wizard_def): Configuration parameters
        source_path (Path): Directory containing raw data files
        folder_path (Path): Output directory for processed study
        logger (MassterLogger): Progress and status logging

    Workflow Stages:
        1. File Discovery: Locate and validate raw data files
        2. Batch Conversion: Convert vendor formats to open formats (if needed)
        3. Sample Processing: Feature detection and MS2 extraction
        4. Study Assembly: Combine samples into study format
        5. Alignment: Cross-sample feature alignment
        6. Consensus: Merge aligned features
        7. Gap Filling: Fill missing values across samples
        8. Integration: Quantify features
        9. Export: Generate output files in multiple formats

    Example:
        >>> from masster import Wizard
        >>> w = Wizard(source="raw_data", folder="output", polarity="positive")
        >>> w.create_scripts()  # Generate analysis scripts
        >>> w.test_only()       # Validate with one file
        >>> w.run()            # Process all files

    Advanced Example:
        >>> w = Wizard(
        ...     source="raw_data",
        ...     folder="output",
        ...     polarity="positive",
        ...     num_cores=8,
        ...     adducts=["+H:1:0.8", "+Na:1:0.2"],
        ...     batch_size=10,
        ...     generate_plots=True
        ... )
        >>> w.test_and_run()  # Test then auto-run if successful

    See Also:
        Sample: For individual sample processing
        Study: For multi-sample analysis
        wizard_def: For parameter configuration
    """

    def __init__(
        self,
        source: str = "",
        folder: str = "",
        polarity: Optional[str] = None,
        adducts: Optional[List[str]] = None,
        num_cores: int = 6,
        **kwargs,
    ):
        """
        Initialize the Wizard with analysis parameters.

        Parameters:
            source: Directory containing raw data files
            folder: Output directory for processed study
            polarity: Ion polarity mode ("positive", "negative", or None for auto-detection)
            adducts: List of adduct specifications (auto-set if None)
            num_cores: Number of CPU cores (0 = auto-detect 75% of available)
            **kwargs: Additional parameters (see wizard_def for full list)
        """

        # Auto-detect optimal number of cores if not specified
        if num_cores <= 0:
            num_cores = max(1, int(multiprocessing.cpu_count() * 0.75))

        # Create parameters instance
        if "params" in kwargs and isinstance(kwargs["params"], wizard_def):
            self.params = kwargs.pop("params")
        else:
            # Create default parameters
            self.params = wizard_def(source=source, folder=folder, polarity=polarity, num_cores=num_cores)

            # Set adducts if provided
            if adducts is not None:
                self.params.adducts = adducts

            # Update with any additional parameters
            for key, value in kwargs.items():
                if hasattr(self.params, key):
                    setattr(self.params, key, value)

        # Validate required parameters
        if not self.params.source:
            raise ValueError("source is required")
        if not self.params.folder:
            raise ValueError("folder is required")

        # Create and validate paths
        self.source_path = Path(self.params.source)
        self.folder_path = Path(self.params.folder)
        self.folder_path.mkdir(parents=True, exist_ok=True)

        # Set default polarity if not specified
        if self.params.polarity is None:
            self.params.polarity = "positive"
            # Update adducts based on default polarity
            self.params.__post_init__()

        # Setup logger
        self.logger = MassterLogger(
            instance_type="wizard",
            level="INFO",
            label="wizard"
        )

    @property
    def polarity(self) -> Optional[str]:
        """Get the ion polarity mode."""
        return self.params.polarity

    @property
    def adducts(self) -> List[str]:
        """Get the adduct specifications."""
        return self.params.adducts

    def create_scripts(self) -> Dict[str, Any]:
        """
        Generate analysis scripts based on source file analysis.

        This method:
        1. Analyzes the source files to extract metadata
        2. Creates 1_processing.py with sample processing logic
        3. Creates 2_notebook.py marimo notebook for study exploration
        4. Returns instructions for next steps

        Returns:
            Dictionary containing:
            - status: "success" or "error"
            - message: Status message
            - instructions: List of next steps
            - files_created: List of created file paths
            - source_info: Metadata about source files
        """
        try:
            # Step 1: Analyze source files to extract metadata
            source_info = self._analyze_source_files()

            # Report extracted information from first file
            self.logger.info(f"Found {source_info.get('number_of_files', 0)} {', '.join(source_info.get('file_types', []))} files")
            
            if source_info.get('first_file'):
                self.logger.info(f"Detected polarity: {source_info.get('polarity', 'unknown')}")
                self.logger.info(f"Detected detector: {source_info.get('detector_type', 'unknown')}")
                if source_info.get('baseline', 0) > 0:
                    self.logger.info(f"Baseline intensity: {source_info.get('baseline', 0):.1f}")
                if source_info.get('length_minutes', 0) > 0:
                    self.logger.info(f"Run length: {source_info.get('length_minutes', 0):.1f} min")
                if source_info.get('ms1_scans_per_second', 0) > 0:
                    self.logger.info(f"MS1 scan rate: {source_info.get('ms1_scans_per_second', 0):.2f} scans/s")

            # Update wizard parameters based on detected metadata
            if source_info.get("polarity") and source_info["polarity"] != "positive":
                self.params.polarity = source_info["polarity"]

            files_created = []

            # Step 2: Create 1_processing.py
            workflow_script_path = self.folder_path / "1_processing.py"
            self.logger.info(f"Creating workflow script: {workflow_script_path.name}")
            workflow_content = self._generate_workflow_script_content(source_info)
            
            # Apply test mode modifications
            workflow_content = self._add_test_mode_support(workflow_content)

            with open(workflow_script_path, "w", encoding="utf-8") as f:
                f.write(workflow_content)
            files_created.append(str(workflow_script_path))

            # Step 3: Create 2_notebook.py marimo notebook
            notebook_path = self.folder_path / "2_notebook.py"
            self.logger.info(f"Creating interactive notebook: {notebook_path.name}")
            notebook_content = self._generate_interactive_notebook_content(source_info)

            with open(notebook_path, "w", encoding="utf-8") as f:
                f.write(notebook_content)
            files_created.append(str(notebook_path))

            # Step 4: Generate instructions
            instructions = self._generate_instructions(source_info, files_created)

            self.logger.success(f"Created {len(files_created)} script files")

            return {
                "status": "success",
                "message": f"Successfully created {len(files_created)} script files",
                "instructions": instructions,
                "files_created": files_created,
                "source_info": source_info,
            }

        except Exception as e:
            import traceback
            tb = traceback.extract_tb(e.__traceback__)
            if tb:
                line_number = tb[-1].lineno
                function_name = tb[-1].name
                error_location = f" (at line {line_number} in {function_name})"
            else:
                error_location = ""
            
            self.logger.error(f"Failed to create scripts: {e}{error_location}")
            
            return {
                "status": "error",
                "message": f"Failed to create scripts: {e}{error_location}",
                "instructions": [],
                "files_created": [],
                "source_info": {},
            }

    def _analyze_source_files(self) -> Dict[str, Any]:
        """Analyze source files to extract metadata."""
        result = {
            "number_of_files": 0,
            "file_types": [],
            "detector_type": "tof",
            "polarity": None,
            "baseline": None,
            "length_minutes": 0.0,
            "ms1_scans_per_second": 0.0,            
            "first_file": None,

        }

        try:
            # Find raw data files
            extensions = [".wiff", ".raw", ".mzML"]
            raw_files = []

            for ext in extensions:
                pattern = f"**/*{ext}"
                files = list(self.source_path.rglob(pattern))
                if files:
                    raw_files.extend(files)
                    if ext not in result["file_types"]:
                        result["file_types"].append(ext)

            result["number_of_files"] = len(raw_files)

            if raw_files:
                result["first_file"] = str(raw_files[0])
                # load first file to infer polarity and length
                self.logger.info(f"Analyzing first file: {raw_files[0].name}")
                from masster import Sample
                sample = Sample(filename=result["first_file"], logging_level='WARNING')
                result['polarity'] = sample.polarity
                # take max from polars ms1_df['rt']
                if sample.ms1_df is not None:
                    if not sample.ms1_df.is_empty() and 'rt' in sample.ms1_df.columns:
                        max_rt = sample.ms1_df['rt'].max()
                        if max_rt is not None and isinstance(max_rt, (int, float)) and max_rt > 0:
                            result["length_minutes"] = float(max_rt) / 60.0
                            result["ms1_scans_per_second"] = len(sample.ms1_df) / float(max_rt) / 60.0
                        
                        baseline = sample.ms1_df['inty'].quantile(0.001)
                        if baseline is not None and isinstance(baseline, (int, float)):
                            result["baseline"] = float(baseline)
                            if baseline > 5e3:
                                result["detector_type"] = "orbitrap"
                            else:
                                result["detector_type"] = "tof"
                    
        except Exception as e:
            self.logger.warning(f"Could not analyze source files: {e}")

        return result

    def _generate_workflow_script_content(self, source_info: Dict[str, Any]) -> str:
        """Generate the content for 1_masster_workflow.py script."""

        # Get default adducts for both polarities from study_defaults
        pos_defaults = study_defaults(polarity="positive")
        neg_defaults = study_defaults(polarity="negative")
        adducts_pos = pos_defaults.adducts
        adducts_neg = neg_defaults.adducts

        # Logic 
        noise = self.params.noise
        if noise is None:
            if source_info.get("detector_type") == "orbitrap":
                noise = max(self.params.noise or 50.0, 5e4)
            elif source_info.get("detector_type") == "tof":
                default_noise = self.params.noise or 50.0
                baseline = source_info.get("baseline", default_noise / 2.0)
                noise = baseline * 2

        chrom_fwhm = self.params.chrom_fwhm
        if chrom_fwhm is None:
            if source_info.get("length_minutes", 0) > 0:
                if source_info["length_minutes"] < 10:
                    chrom_fwhm = 0.5
                else:
                    chrom_fwhm = 2.0

        min_samples_for_merge = self.params.min_samples_for_merge
        if min_samples_for_merge is None:
            min_samples_for_merge = max(3, int(source_info.get("number_of_files", 1) * 0.03))

        # Generate script content     
        script_lines = [
           "#!/usr/bin/env python3",
           '"""',
           "Automated Mass Spectrometry Data Analysis Pipeline",
            f"Generated by masster wizard {version}",          
            '"""',
            "",
            "import os",
            "import sys",
            "import time",
            "from pathlib import Path",
            "from loguru import logger",
            "from masster import Study",
            "from masster import __version__",
            "",
            "# Configure loguru",
            "logger.remove()  # Remove default handler",
            'logger.add(sys.stdout, format="<level>{time:YYYY-MM-DD HH:mm:ss.SSS}</level> | <level>{level: <8}</level> | <level>{message}</level>", level="INFO")',
            "",
            "# Test mode configuration",
            'TEST = os.environ.get("MASSTER_TEST", "0") == "1"',
            'STOP_AFTER_TEST = os.environ.get("MASSTER_STOP_AFTER_TEST", "0") == "1"  # Only run test, don\'t continue to full batch',
            "",
            "# Analysis parameters",
            "PARAMS = {",
            "    # === Core Configuration ===",
            f'    "source": {str(self.source_path)!r},  # Directory containing raw data files',
            f'    "folder": {str(self.folder_path)!r},  # Output directory for processed study',
            f'    "polarity": {self.params.polarity!r},  # Ion polarity mode ("positive" or "negative")',
            f'    "num_cores": {self.params.num_cores},  # Number of CPU cores for parallel processing',
            "",
            "    # === Test Mode ===",
            '    "test": TEST,  # Process only first file for testing',
            '    "stop_after_test": STOP_AFTER_TEST,  # Stop after test, don\'t run full batch',
            "",
            "    # === File Discovery ===",
            f'    "file_extensions": {self.params.file_extensions!r},  # File extensions to search for',
            f'    "search_subfolders": {self.params.search_subfolders},  # Whether to search subdirectories recursively',
            f'    "skip_patterns": {self.params.skip_patterns!r},  # Filename patterns to skip',
            f'    "wiff_sample_selection": {self.params.wiff_sample_selection!r},  # For WIFF files with multiple samples: "first", "last", or "all"',
            "",
            "    # === Processing Parameters ===",
            f'    "adducts_pos": {adducts_pos!r},  # Adduct specifications for positive polarity',
            f'    "adducts_neg": {adducts_neg!r},  # Adduct specifications for negative polarity',
            f'    "noise": {noise},  # Noise threshold for feature detection',
            f'    "chrom_fwhm": {chrom_fwhm},  # Chromatographic peak full width at half maximum (seconds)',
            f'    "chrom_peak_snr": {self.params.chrom_peak_snr},  # Minimum signal-to-noise ratio for chromatographic peaks',
            "",
            "    # === Alignment & Merging ===",
            f'    "rt_tol": {self.params.rt_tolerance},  # Retention time tolerance for alignment (seconds)',
            f'    "mz_tol": {self.params.mz_max_diff},  # Mass-to-charge ratio tolerance for alignment (Da)',
            f'    "alignment_method": {self.params.alignment_algorithm!r},  # Algorithm for sample alignment',
            f'    "min_samples_per_feature": {min_samples_for_merge},  # Minimum samples required per consensus feature',
            f'    "merge_method": {self.params.merge_method!r},  # Method for merging consensus features',
            "",
            "    # === Sample Processing (used in add_samples_from_folder) ===",
            f'    "batch_size": {self.params.batch_size},  # Number of files to process per batch',
            f'    "memory_limit_gb": {self.params.memory_limit_gb},  # Memory limit for processing (GB)',
            "",
            "    # === Script Options ===",
            f'    "resume_enabled": {self.params.resume_enabled},  # Enable automatic resume capability',
            f'    "force_reprocess": {self.params.force_reprocess},  # Force reprocessing of existing files',
            f'    "cleanup_temp_files": {self.params.cleanup_temp_files},  # Clean up temporary files after processing',
            '    "skip_missing": False,  # If True, skip raw file conversion if .sample5 does not exist',
            "}",
            "",
            "",
            "def discover_raw_files(source_folder, file_extensions, search_subfolders=True):",
            '    """Discover raw data files in the source folder."""',
            "    source_path = Path(source_folder)",
            "    raw_files = []",
            "    ",
            "    for ext in file_extensions:",
            "        if search_subfolders:",
            '            pattern = f"**/*{ext}"',
            "            files = list(source_path.rglob(pattern))",
            "        else:",
            '            pattern = f"*{ext}"',
            "            files = list(source_path.glob(pattern))",
            "        raw_files.extend(files)",
            "    ",
            "    return raw_files",
            "",
            "",
            "def process_single_file(args):",
            '    """Process a single raw file to sample5 format - module level for multiprocessing."""',
            "    raw_file, output_folder = args",
            "    from masster import Sample",
            "    ",
            "    try:",
            "        sample_name = raw_file.stem",
            "        sample5_paths = []",
            "        ",
            "        # Check if it's a WIFF file and count samples",
            "        if raw_file.suffix.lower() in ['.wiff', '.wiff2']:",
            "            from masster.sample.sciex import count_samples",
            "            num_samples = count_samples(str(raw_file))",
            "            ",
            "            if num_samples > 1:",
            "                # Determine which samples to process based on wiff_sample_selection",
            '                selection = PARAMS["wiff_sample_selection"].lower()',
            "                if selection == 'all':",
            "                    sample_indices = list(range(num_samples))",
            "                elif selection == 'first':",
            "                    sample_indices = [0]",
            "                elif selection == 'last':",
            "                    sample_indices = [num_samples - 1]",
            "                else:",
            '                    logger.warning(f"Invalid wiff_sample_selection: {selection}. Defaulting to \'last\'")',
            "                    sample_indices = [num_samples - 1]",
            "                ",
            "                # Check if skip_missing is True - verify expected sample5 files exist",
            '                if PARAMS["skip_missing"]:',
            "                    output_path = Path(output_folder)",
            "                    if selection == 'all':",
            '                        existing_samples = list(output_path.glob(f"{sample_name}__s*.sample5"))',
            "                        if not existing_samples:",
            '                            logger.info(f"Skipping {raw_file.name} (no sample5 files found and skip_missing=True)")',
            "                            return []",
            "                    else:",
            "                        # For 'first' or 'last', check if the specific sample5 file exists",
            '                        expected_sample5 = output_path / f"{sample_name}__s{sample_indices[0]}.sample5"',
            "                        if not expected_sample5.exists():",
            '                            logger.info(f"Skipping {raw_file.name} (sample5 file for sample {sample_indices[0]} missing and skip_missing=True)")',
            "                            return None",
            "                ",
            '                logger.info(f"WIFF file {raw_file.name} contains {num_samples} samples - processing {selection}: {sample_indices}")',
            "                ",
            "                # Process selected samples in the WIFF file",
            "                for sample_idx in sample_indices:",
            '                    sample5_path = Path(output_folder) / f"{sample_name}__s{sample_idx}.sample5"',
            "                    ",
            "                    # Skip if sample5 already exists",
            '                    if sample5_path.exists() and not PARAMS["force_reprocess"]:',
            '                        logger.debug(f"  Skipping sample {sample_idx} (already exists)")',
            "                        sample5_paths.append(str(sample5_path))",
            "                        continue",
            "                    ",
            "                    # If we reach here with skip_missing=True, at least one sample5 exists,",
            "                    # so we should process missing ones",
            '                    if not sample5_path.exists() and PARAMS["skip_missing"]:',
            '                        logger.debug(f"  Skipping sample {sample_idx} (sample5 file missing)")',
            "                        continue",
            "                    ",
            '                    logger.info(f"  Converting sample {sample_idx}...")',
            "                    ",
            "                    # Load and process with specific sample_id",
            '                    sample = Sample(log_label=f"{sample_name}__s{sample_idx}")',
            "                    sample.load(filename=str(raw_file), sample_idx=sample_idx)",
            "                    ",
            "                    sample.find_features(",
            '                        noise=PARAMS["noise"],',
            '                        chrom_fwhm=PARAMS["chrom_fwhm"],',
            '                        chrom_peak_snr=PARAMS["chrom_peak_snr"]',
            "                    )",
            "                    sample.find_ms2()",
            "                    sample.find_iso()",
            "                    sample.save(str(sample5_path))",
            "                    sample5_paths.append(str(sample5_path))",
            "                ",
            "                return sample5_paths  # Return list of paths",
            "        ",
            "        # Standard single-file processing (non-WIFF or single-sample WIFF)",
            '        sample5_path = Path(output_folder) / f"{sample_name}.sample5"',
            "        ",
            "        # Skip if sample5 doesn't exist and skip_missing is True",
            '        if not sample5_path.exists() and PARAMS["skip_missing"]:',
            '            logger.info(f"Skipping {raw_file.name} (sample5 file missing and skip_missing=True)")',
            "            return None",
            "        ",
            "        # Skip if sample5 already exists",
            '        if sample5_path.exists() and not PARAMS["force_reprocess"]:',
            '            logger.debug(f"Skipping {raw_file.name} (already exists)")',
            "            return str(sample5_path)",
            "        ",
            '        logger.info(f"Converting {raw_file.name}...")',
            "        ",
            "        # Load and process raw file with full pipeline",
            "        sample = Sample(log_label=sample_name)",
            "        sample.load(filename=str(raw_file))",
            "        sample.find_features(",
            '            noise=PARAMS["noise"],',
            '            chrom_fwhm=PARAMS["chrom_fwhm"],',
            '            chrom_peak_snr=PARAMS["chrom_peak_snr"]',
            "        )",
            "        sample.find_ms2()",
            "        sample.find_adducts()",
            "        # sample.find_iso()",
            "        # sample.export_mgf()",
            '        # sample.plot_2d(filename=f"{sample5_path.replace(".sample5", ".html")}")',
            "        sample.save(str(sample5_path))",
            "        ",
            '        # logger.success(f"Completed {raw_file.name} -> {sample5_path.name}")',
            "        return str(sample5_path)",
            "        ",
            "    except Exception as e:",
            '        logger.error(f"ERROR processing {raw_file.name}: {e}")',
            "        return None",
            "",
            "",
            "def convert_raw_to_sample5(raw_files, output_folder, polarity, num_cores):",
            '    """Convert raw data files to sample5 format."""',
            "    import concurrent.futures",
            "    import os",
            "    ",
            "    # Create output directory",
            "    os.makedirs(output_folder, exist_ok=True)",
            "    ",
            "    # Prepare arguments for multiprocessing",
            "    file_args = [(raw_file, output_folder) for raw_file in raw_files]",
            "    ",
            "    # Process files in parallel",
            "    sample5_files = []",
            "    with concurrent.futures.ProcessPoolExecutor(max_workers=num_cores) as executor:",
            "        futures = [executor.submit(process_single_file, args) for args in file_args]",
            "        ",
            "        for future in concurrent.futures.as_completed(futures):",
            "            result = future.result()",
            "            if result:",
            "                # Handle both single file (str) and multiple files (list) returns",
            "                if isinstance(result, list):",
            "                    sample5_files.extend(result)",
            "                else:",
            "                    sample5_files.append(result)",
            "    ",
            "    return sample5_files",
            "",
            "",
            "def main():",
            '    """Main analysis pipeline."""',
            "    try:",
            '        logger.info("=" * 70)',
            f'        logger.info("masster {version} - Automated MS Data Analysis")',
            "        if TEST:",
            '            logger.info("TEST MODE: Processing single file only")',
            '        logger.info("=" * 70)',
            "        logger.info(f\"Source: {PARAMS['source']}\")",
            "        logger.info(f\"Output: {PARAMS['folder']}\")",
            "        logger.info(f\"Polarity: {PARAMS['polarity']}\")",
            "        logger.info(f\"CPU Cores: {PARAMS['num_cores']}\")",
            "        if TEST:",
            "            logger.info(f\"Mode: {'Test Only' if STOP_AFTER_TEST else 'Test + Full Batch'}\")",
            '        logger.info("=" * 70)',
            "        ",
            "        start_time = time.time()",
            "        ",
            "        # Step 1: Discover raw data files",
            '        logger.info("")',
            '        logger.info("Step 1/7: Discovering raw data files...")',
            "        raw_files = discover_raw_files(",
            "            PARAMS['source'],",
            "            PARAMS['file_extensions'],",
            "            PARAMS['search_subfolders']",
            "        )",
            "        ",
            "        if not raw_files:",
            '            logger.error("No raw data files found!")',
            "            return False",
            "        ",
            '        logger.info(f"Found {len(raw_files)} raw data files")',
            "        for f in raw_files[:5]:  # Show first 5 files",
            '            logger.info(f"  {f.name}")',
            "        if len(raw_files) > 5:",
            '            logger.info(f"  ... and {len(raw_files) - 5} more")',
            "        ",
            "        # Step 2: Process raw files",
            '        logger.info("")',
            '        logger.info("Step 2/7: Processing raw files...")',
            "        sample5_files = convert_raw_to_sample5(",
            "            raw_files,",
            "            PARAMS['folder'],",
            "            PARAMS['polarity'],",
            "            PARAMS['num_cores']",
            "        )",
            "        ",
            "        if not sample5_files:",
            '            logger.error("No sample5 files were created!")',
            "            return False",
            "        ",
            '        logger.success(f"Successfully processed {len(sample5_files)} files to sample5")',
            "        ",
            "        # Step 3: Create and configure study",
            '        logger.info("")',
            '        logger.info("Step 3/7: Initializing study...")',
            "        # Select adducts based on polarity",
            "        adducts = PARAMS['adducts_pos'] if PARAMS['polarity'] in ['positive', 'pos', '+'] else PARAMS['adducts_neg']",
            "        study = Study(folder=PARAMS['folder'], polarity=PARAMS['polarity'], adducts=adducts)",
            "        ",
            "        # Step 4: Add sample5 files to study",
            '        logger.info("")',
            '        logger.info("Step 4/7: Adding samples to study...")',
            "        study.add(str(Path(PARAMS['folder']) / \"*.sample5\"))",
            "        study.features_filter(study.features_select(chrom_coherence=0.2, chrom_prominence_scaled=2.0))",
            "        ",
            "        # Step 5: Core processing",
            '        logger.info("")',
            '        logger.info("Step 5/7: Processing...")',
            "        study.align(",
            "            algorithm=PARAMS['alignment_method'],",
            "            rt_tol=PARAMS['rt_tol']",
            "        )",
            "        ",
            "        # Check that more than 1 file has been loaded",
            "        if len(study.samples_df) <= 1:",
            '            logger.warning("Study merging requires more than 1 sample file")',
            '            logger.warning(f"Only {len(study.samples)} sample(s) loaded - terminating execution")',
            "            return False",
            "        ",
            "        study.merge(",
            '            method="qt",',
            "            min_samples=PARAMS['min_samples_per_feature'],",
            "            threads=PARAMS['num_cores'],",
            "            rt_tol=PARAMS['rt_tol']",
            "        )",
            "        # Fill missing EICs and integrate by consensus",
            "        study.fill()",
            "        study.integrate()",
            "        # Remove poorly integratable consensus features", 
            "        study.consensus_filter(study.consensus_select(sanity=0.2,coherence=0.2))",
            "        ",
            "        # Step 6/7: Saving results",
            '        logger.info("")',
            '        logger.info("Step 6/7: Saving results...")',
            "        study.save(filename=\"data_after_processing.study5\", add_timestamp=False)",
            "        study.export_history(filename=\"history_after_processing.json\")",
            "        study.export_excel()",
            "        study.export_mgf()",
            "        study.export_mztab()",
            "        study.export_csv() # for tima",
            "        ",
            "        # Step 7: Plots",
            '        logger.info("")',
            '        logger.info("Step 7/7: Exporting plots...")',
            '        study.plot_consensus_2d(filename="consensus.html", cmap="viridis_r")',
            '        #study.plot_consensus_2d(filename="consensus.png", cmap="viridis_r")',
            '        study.plot_alignment(filename="alignment.html")',
            '        study.plot_alignment(filename="alignment.png")',
            '        study.plot_samples_pca(filename="pca.html")',
            '        study.plot_samples_pca(filename="pca.png")',
            '        study.plot_bpc(filename="bpc.html")',
            '        study.plot_bpc(filename="bpc.png")',
            '        study.plot_rt_correction(filename="rt_correction.html")',
            '        study.plot_rt_correction(filename="rt_correction.png")',
            '        study.plot_heatmap(filename="heatmap.html")',
            '        study.plot_heatmap(filename="heatmap.png")',
            "        ",
            "        # Print summary",
            "        study.info()",
            "        total_time = time.time() - start_time",
            '        logger.info("")',
            '        logger.info("=" * 70)',
            '        logger.success("ANALYSIS COMPLETE")',
            '        logger.info("=" * 70)',
            '        logger.info(f"Total processing time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")',
            '        logger.info(f"Raw files processed: {len(raw_files)}")',
            '        logger.info(f"Sample5 files created: {len(sample5_files)}")',
            '        if hasattr(study, "consensus_df"):',
            '            logger.info(f"Consensus features generated: {len(study.consensus_df)}")',
            '        logger.info("=" * 70)',
            '        logger.info("")',
            '        logger.info("Next step: Interactive analysis")',
            '        notebook_path = Path(PARAMS["folder"]) / "2_notebook.py"',
            '        if notebook_path.exists():',
            '            logger.info(f"Run: uv run marimo edit {notebook_path}")',
            '        logger.info("")',
            "        ",
            "        return True",
            "        ",
            "    except KeyboardInterrupt:",
            '        logger.warning("Analysis interrupted by user")',
            "        return False",
            "    except Exception as e:",
            '        logger.error(f"Analysis failed with error: {e}")',
            "        import traceback",
            "        traceback.print_exc()",
            "        return False",
            "",
            "",
            'if __name__ == "__main__":',
            "    success = main()",
            "    sys.exit(0 if success else 1)",
        ]

        return "\n".join(script_lines)

    def _generate_interactive_notebook_content(self, source_info: Dict[str, Any]) -> str:
        """Generate the content for 2_notebook.py marimo notebook."""

        notebook_lines = [
            "import marimo",
            "",
            '__generated_with = "0.18.0"',
            'app = marimo.App(width="full")',
            "",
            "",
            "@app.cell(hide_code=True)",
            "def _():",
            "    import marimo as mo",
            "    return (mo,)",
            "",
            "",
            "@app.cell(hide_code=True)",
            "def _(mo):",
            '    mo.md(r"""',
            "    # Interactive Analysis",
            "    This notebook provides an interactive exploration of your processed study. Make sure you have run `python 1_processing.py` first.",
            "    ## Load preprocessed study",
            '    """)',
            "    return",
            "",
            "",
            "@app.cell",
            "def _():",
            f"    data_directory = {str(self.folder_path)!r}",
            "    return (data_directory,)",
            "",
            "",
            "@app.cell",
            "def _(data_directory):",
            "    import masster",
            "    s = masster.Study(folder=data_directory)",
            "    s.load(filename='data_after_processing.study5')",
            "    s.info()",
            "    return (s,)",
            "",
            "",
            "@app.cell(hide_code=True)",
            "def _(mo):",
            '    mo.md(r"""',
            "    ## Sample description",
            '    """)',
            "    return",
            "",
            "",
            "@app.cell(hide_code=True)",
            "def _(s):",
            "    ## Placeholder for importing additional metadata. The input can be a CSV file, a XLSX file, or a DataFrame. The first column mus include either sample_name(s) or UUID7 sample_id(s)",
            "    # s.metadata_import('data.csv') ",
            "",
            "    ## Reset colour of samples. Pick colormaps from https://cmap-docs.readthedocs.io/en/latest/catalog/",
            '    # s.sample_color(by=None, palette="Turbo256")',
            "",
            "    # Visualise sample table. Metadata appears to the right",
            "    s.samples_df",
            "    return",
            "",
            "",
            "@app.cell(hide_code=True)",
            "def _(mo):",
            '    mo.md(r"""',
            "    ## Consensus features",
            "    This is the list of aggregated features that were identified across all samples. Exemplary plots are provided below.",
            '    """)',
            "    return",
            "",
            "",
            "@app.cell",
            "def _(s):",
            "    s.consensus_df",
            "    return",
            "",
            "",
            "@app.cell",
            "def _(s):",
            "    # note that (almost) any column of consensud_df can be used",
            "    s.plot_consensus_2d(colorby='number_samples',cmap='viridis_r', width=900, height=600, sizeby='inty_mean') ",
            "    return",
            "",
            "",
            "@app.cell",
            "def _(s):",
            "    s.plot_consensus_stats()",
            "    return",
            "",
            "",
            "@app.cell(disabled=True)",
            "def _(s):",
            "    s.plot_features_stats()",
            "    return",
            "",
            "",
            "@app.cell(hide_code=True)",
            "def _(mo):",
            '    mo.md(r"""',
            "    ## Feature identification",
            "    We integrate functions for MS1-based matching, with and without RT information. For MS2-based annotation, the consensus data is exported, analyzed by external tools (LipidOracle for lipids, tima for anything else), and then re-imported by masster. Here we provide placeholders for the different workflows. You'll have to adapt and run tehm manually.",
            "    ### Annotation based on MS1 matching",
            '    """)',
            "    return",
            "",
            "",
            "@app.cell",
            "def _(s):",
            "    ## Step 1. Load the library (including name, formula, SMILE, InchiKey, RT if available, and DB identifiers)",
            '    # Built-in libraries include "hsapiens", "scerevisiae", "ecoli"',
            '    s.lib_reset()',
            '    s.lib_load("hsapiens")',
            "    ## Step 2. Identify",
            "    s.identify()",
            "    return",
            "",
            "",
            "@app.cell(hide_code=True)",
            "def _(mo):",
            '    mo.md(r"""',
            "    ### Annotate polar compounds with tima",
            '    """)',
            "    return",
            "",
            "",
            "@app.cell(disabled=True)",
            "def _(s):",
            "    ## Step 1. Export data to CSV and MGF: Both steps are done by the default `1_processing.py`. If you didn't change the processing settings, this step is redundant.",
            "    s.export_csv()",
            "    s.export_mgf()",
            "    ## Step 2. Run tima using the exported files.",
            "    return",
            "",
            "@app.cell(disabled=True)",
            "def _(s):",
            "    ## Step 3. Copy the tima output file to a known location, e.g. ../tima_output",
            "    ## Step 4. Import tima results",
            "    s.lib_reset()",
            "    s.import_tima('data/tima_output/')",
            "    ## Step 5. Keep only compounds with CHNOPS as elements",
            "    s.lib_filter('chnops')",
            "    ## Step 6. Keep only relevant adducts",
            "    s.lib_filter(s.lib_select(adduct=['[M-H]-','[M+H]+','[M+Na]+','[M+NH4]+']))",
            "    ### Step 7. Add stars to identifications based on presence in BIGG model",
            "    s.lib_compare('hsapiens',action='add_stars')",
            "    ### Step 8. Update consensus after filtering",
            "    s.id_update()",
            "    return",
            "",
            "",
            "@app.cell(hide_code=True)",
            "def _(mo):",
            '    mo.md(r"""',
            "    ### Annotate lipids with LipidOracle",
            '    """)',
            "    return",
            "",
            "",
            "@app.cell(disabled=True)",
            "def _(s):",
            "    ## Step 1. Export data to MGF",
            "    s.export_mgf()",
            "    ## Step 2. Run LipidOracle using the exported file.",
            "    return",
            "",
            "@app.cell(disabled=True)",
            "def _(s):",
            "    ## Step 3. Copy the tima output file to a known location, e.g. ../oracle_output",
            "    ## Step 4. Import tima results",
            "    s.lib_reset()",
            "    s.import_oracle('data/oracle_output/')",
            "    return",
            "",
            "",
            "@app.cell(hide_code=True)",
            "def _(mo):",
            '    mo.md(r"""',
            "    ### Visualise identification results",
            '    """)',
            "    return",
            "",
            "",
            "@app.cell",
            "def _(s):",
            "    # Show all matches",
            "    s.get_id()",
            "    return",
            "",
            "",
            "@app.cell",
            "def _(s):",
            "    # list all consensus features with identification. Scroll to the right to see details.",
            "    s.consensus_select(identified=True)",
            "    return",
            "",
            "",
            "@app.cell(hide_code=True)",
            "def _(mo):",
            '    mo.md(r"""',
            "    ## Save after identification",
            '    """)',
            "    return",
            "",
            "",
            "@app.cell(disabled=True)",
            "def _(S):",
            "    s.save()",
            "    return",
            "",
            "",
            "@app.cell(hide_code=True)",
            "def _(mo):",
            '    mo.md(r"""',
            "    ## Export results",
            '    """)',
            "    return",
            "",
            "",
            "@app.cell",
            "def _():",
            "    ## Export to mzTab-M. This includes the annotation and MS2 spectra hidden as comments.",
            "    # s.export_mztab()",
            "    ## Export to Excel workbook",
            "    # s.export_excel()",
            "    ## Export to parquet",
            "    # s.export_parquet()",
            "    return",
            "",
            "",
            "@app.cell(hide_code=True)",
            "def _(mo):",
            '    mo.md(r"""',
            "    ## Plots",
            '    Samples, features, and data can be visualised directly with a bunch of different methods. All come with extensive parameters that allow you to adapt the visualisation to your needs. Use `filename="\\*.html"` to save the plot as an interactive HTML file, or `"\\*.png"` to save a static image.',
            '    """)',
            "    return",
            "",
            "",
            "@app.cell",
            "def _():",
            "    ## plot data as heatmap",
            "    # s.plot_heatmap()",
            "    ## PCA",
            "    # s.plot_samples_pca()",
            "    ## UMAP",
            "    # s.plot_samples_umap()",
            "",
            "    ## TIC",
            "    # s.plot_tic()",
            "    ## BPC",
            "    # s.plot_bpc()",
            "    ## Plot precursos chromatograms of a consensus feature",
            "    # s.plot_chrom(uids=[10])",
            "    ## plot EIC for a given mz",
            "    # s.plot_eic(mz=524.36, mz_tol=0.01)",
            "    ## aaaand much more",
            "    return",
            "",
            "",
            'if __name__ == "__main__":',
            "    app.run()",
        ]

        return "\n".join(notebook_lines)

    def _generate_instructions(self, source_info: Dict[str, Any], files_created: List[str]) -> List[str]:
        """Generate usage instructions for the created scripts."""
        instructions = [
            f"Source analysis: {source_info.get('number_of_files', 0)} files found",
            f"Polarity detected: {source_info.get('polarity', 'unknown')}",
            "Files created:",
        ]
        for file_path in files_created:
            instructions.append(f"  {str(Path(file_path).resolve())}")
        
        # Find the workflow script name from created files
        workflow_script_name = "1_processing.py"
        for file_path in files_created:
            if Path(file_path).name == "1_processing.py":
                workflow_script_name = Path(file_path).name
                break

        instructions.extend([
            "",
            "Next steps:",
            f"1. REVIEW PARAMETERS in {workflow_script_name}:",
            f"   In particular, verify the NOISE, CHROM_FWHM, and MIN_SAMPLES_FOR_MERGE",
            "",
            "2. TEST SINGLE FILE (RECOMMENDED):",
            f"   wizard.test_only()  # Validate parameters with first file only",
            "",
            "3. EXECUTE FULL BATCH:",
            f"   wizard.run()        # Process all files",
            f"   # OR: wizard.test_and_run()  # Test first, then run all",
            f"   # OR: uv run python {workflow_script_name}",
            "",
            "4. INTERACTIVE ANALYSIS:",
            f"   uv run marimo edit \"{Path('2_notebook.py').name}\"",
            "",
        ])

        return instructions

    def _add_test_mode_support(self, workflow_content: str) -> str:
        """Add test mode functionality to the generated workflow script."""
        lines = workflow_content.split("\n")

        # Insert test mode code after print statements in main function
        for i, line in enumerate(lines):
            # Test mode already handled in main() logger.info section
            if 'logger.info("masster' in line and 'Automated MS Data Analysis")' in line:
                # Already handled in the generation, skip
                break

        # Add file limitation logic after file listing
        for i, line in enumerate(lines):
            if 'logger.info(f"  ... and {len(raw_files) - 5} more")' in line:
                lines.insert(i + 1, '        ')
                lines.insert(i + 2, '        # Limit to first file in test mode')
                lines.insert(i + 3, '        if TEST:')
                lines.insert(i + 4, '            raw_files = raw_files[:1]')
                lines.insert(i + 5, '            logger.info("")')
                lines.insert(i + 6, '            logger.info(f"TEST MODE: Processing only first file: {raw_files[0].name}")')
                break

        # Modify num_cores for test mode
        for i, line in enumerate(lines):
            if "PARAMS['num_cores']" in line and "convert_raw_to_sample5(" in lines[i - 2 : i + 3]:
                lines[i] = line.replace(
                    "PARAMS['num_cores']", "PARAMS['num_cores'] if not TEST else 1  # Use single core for test"
                )
                break

        # Add test-only exit logic after successful processing
        for i, line in enumerate(lines):
            if 'logger.success(f"Successfully processed {len(sample5_files)} files to sample5")' in line:
                lines.insert(i + 1, '        ')
                lines.insert(i + 2, '        # Stop here if stop-after-test mode')
                lines.insert(i + 3, '        if STOP_AFTER_TEST:')
                lines.insert(i + 4, '            logger.info("")')
                lines.insert(i + 5, '            logger.info("STOP AFTER TEST mode: Stopping after successful single file processing")')
                lines.insert(i + 6, '            logger.info(f"Test file created: {sample5_files[0]}")')
                lines.insert(i + 7, '            logger.info("")')
                lines.insert(i + 8, '            logger.info("To run full batch, use: wizard.run()")')
                lines.insert(i + 9, "            total_time = time.time() - start_time")
                lines.insert(i + 10, '            logger.info(f"Test processing time: {total_time:.1f} seconds")')
                lines.insert(i + 11, "            return True")
                break

        return "\n".join(lines)

    def test_and_run(self) -> Dict[str, Any]:
        """
        Test the sample processing workflow with a single file, then run full batch.

        This method first runs the 1_processing.py script in test-only mode to process
        the first raw file for validation, then automatically continues with the
        full batch if the test succeeds. The script must already exist - call
        create_scripts() first if needed.

        Returns:
            Dictionary containing:
            - status: "success" or "error"
            - message: Status message
            - instructions: List of next steps
        """
        # Step 1: Run test-only mode first
        self.logger.info("Testing with single file...")
        test_result = self._execute_workflow(test=True, run=False)
        
        if test_result["status"] != "success":
            return {
                "status": "error",
                "message": f"Test failed: {test_result['message']}",
                "instructions": [
                    "Single file test failed",
                    "Review parameters in 1_processing.py",
                    "Fix issues and try again",
                ],
            }
        
        self.logger.success("Test successful!")
        self.logger.info("Processing all files...")
        
        # Step 2: Run full batch mode
        full_result = self._execute_workflow(test=False, run=True)
        
        return full_result

    def test_only(self) -> Dict[str, Any]:
        """
        Test the sample processing workflow with a single file only.

        This method runs the 1_processing.py script in test-only mode to process
        only the first raw file and then stops (does not continue to full study processing).
        The script must already exist - call create_scripts() first if needed.

        Returns:
            Dictionary containing:
            - status: "success" or "error"
            - message: Status message
            - instructions: List of next steps
            - test_file: Path to the processed test file (if successful)
        """
        return self._execute_workflow(test=True, run=False)

    def test(self) -> Dict[str, Any]:
        """
        Test the sample processing workflow with a single file only.

        This method runs the 1_processing.py script in test-only mode to process
        only the first raw file and then stops (does not continue to full study processing).
        The script must already exist - call create_scripts() first if needed.

        Returns:
            Dictionary containing:
            - status: "success" or "error"
            - message: Status message
            - instructions: List of next steps
            - test_file: Path to the processed test file (if successful)
        """
        return self._execute_workflow(test=True, run=False)


    def run(self) -> Dict[str, Any]:
        """
        Run the sample processing workflow.

        This method runs the 1_processing.py script to process raw files.
        The script must already exist - call create_scripts() first if needed.

        Returns:
            Dictionary containing:
            - status: "success" or "error"
            - message: Status message
            - instructions: List of next steps
        """
        return self._execute_workflow(test=False, run=True)

    def _execute_workflow(self, test: bool = False, run: bool = True) -> Dict[str, Any]:
        """
        Execute the workflow script in either test or full mode.

        Args:
            test: If True, run in test mode (single file), otherwise full batch
            run: If False, stop after test (only used with test=True), if True continue with full processing
        """
        try:
            workflow_script_path = self.folder_path / "1_processing.py"

            # Check if workflow script exists
            if not workflow_script_path.exists():
                self.logger.info("Workflow script not found - creating scripts...")
                create_result = self.create_scripts()
                
                if create_result["status"] == "error":
                    return {
                        "status": "error",
                        "message": f"Failed to create workflow script: {create_result['message']}",
                        "instructions": [
                            "Could not create 1_processing.py",
                            "Please check source path and permissions",
                        ],
                    }
                
                self.logger.success("Scripts created successfully")

            # Setup execution mode
            if test and not run:
                mode_label = "test-only"
            elif test:
                mode_label = "test"
            else:
                mode_label = "full batch"

            env = None
            if test:
                import os

                env = os.environ.copy()
                env["MASSTER_TEST"] = "1"
                if not run:
                    env["MASSTER_STOP_AFTER_TEST"] = "1"

            # Execute the workflow script
            self.logger.info(f"Executing {mode_label} workflow: {workflow_script_path.name}")

            import subprocess

            result = subprocess.run([sys.executable, str(workflow_script_path)], cwd=str(self.folder_path), env=env)

            success = result.returncode == 0

            if success:
                if test and not run:
                    self.logger.success("Test completed - single file validated")
                    self.logger.info("Next: wizard.run() to process all files")
                elif test:
                    self.logger.success("Test completed")
                    self.logger.info("Next: wizard.run() to process all files")
                else:
                    self.logger.success("Processing complete")
                    notebook_path = self.folder_path / "2_notebook.py"
                    self.logger.info(f"Next: uv run marimo edit {str(notebook_path)}")

                next_step = "Next: wizard.run()" if test else f"Next: uv run marimo edit {self.folder_path / '2_notebook.py'}"

                return {
                    "status": "success",
                    "message": f"{mode_label.capitalize()} processing completed successfully",
                    "instructions": [
                        f"{mode_label.capitalize()} processing completed",
                        next_step
                    ]
                }
            else:
                self.logger.error(f"Workflow failed with return code {result.returncode}")
                return {
                    "status": "error",
                    "message": f"Workflow execution failed with return code {result.returncode}",
                    "instructions": [
                        "Check the error messages above",
                        "Review parameters in 1_processing.py",
                        f"Try running manually: python {workflow_script_path.name}",
                    ],
                }

        except Exception as e:
            self.logger.error(f"Failed to execute workflow: {e}")
            return {
                "status": "error",
                "message": f"Failed to execute workflow: {e}",
                "instructions": [
                    "Execution failed",
                    "Check that source files exist and are accessible",
                    "Verify folder permissions",
                ],
            }

def create_scripts(
    source: str = "",
    folder: str = "",
    polarity: Optional[str] = None,
    adducts: Optional[List[str]] = None,
    num_cores: int = 0,
    **kwargs,
) -> Dict[str, Any]:
    """
    Create analysis scripts without explicitly instantiating a Wizard.

    This is a convenience function that creates a Wizard instance internally
    and calls its create_scripts() method.

    Parameters:
        source: Directory containing raw data files
        folder: Output directory for processed study
        polarity: Ion polarity mode ("positive", "negative", or None for auto-detection)
        adducts: List of adduct specifications (auto-set if None)
        num_cores: Number of CPU cores (0 = auto-detect)
        **kwargs: Additional parameters

    Returns:
        Dictionary containing:
        - status: "success" or "error"
        - message: Status message
        - instructions: List of next steps
        - files_created: List of created file paths
        - source_info: Metadata about source files

    Example:
        >>> import masster.wizard
        >>> result = masster.wizard.create_scripts(
        ...     source=r'D:\\Data\\raw_files',
        ...     folder=r'D:\\Data\\output',
        ...     polarity='negative'
        ... )
        >>> print("Status:", result["status"])
    """

    try:
        # Auto-detect optimal number of cores if not specified
        if num_cores <= 0:
            num_cores = max(1, int(multiprocessing.cpu_count() * 0.75))

        # Create Wizard instance
        wizard = Wizard(source=source, folder=folder, polarity=polarity, adducts=adducts, num_cores=num_cores, **kwargs)

        # Call the instance method
        return wizard.create_scripts()

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create scripts: {e}",
            "instructions": [],
            "files_created": [],
            "source_info": {},
        }


# Export the main classes and functions
__all__ = ["Wizard", "wizard_def", "create_scripts"]
