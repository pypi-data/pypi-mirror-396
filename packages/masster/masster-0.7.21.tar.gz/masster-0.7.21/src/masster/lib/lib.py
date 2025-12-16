"""
lib.py

This module provides the Lib class for mass spectrometry compound library 
management and feature annotation.

The Lib class supports annotation of sample.features_df and study.consensus_df 
based on MS1 (rt, m/z, possibly isotopes) and MS2 data.

Key Features:
- **Lib Class**: Main class for managing compound libraries and annotations
- **Compound Libraries**: Load and manage compound databases with metadata
- **Adduct Calculations**: Handle various ionization adducts and charge states
- **Mass Calculations**: Precise mass calculations with adduct corrections
- **Target Matching**: Match detected features against compound libraries
- **Polarity Handling**: Support for positive and negative ionization modes
- **CSV Import**: Import compound data from CSV files with automatic adduct generation

Dependencies:
- `pyopenms`: For mass spectrometry algorithms and data structures
- `polars`: For efficient data manipulation and analysis
- `numpy`: For numerical computations and array operations
- `uuid`: For generating unique identifiers

Supported Adducts:
- Positive mode: [M+H]+, [M+Na]+, [M+K]+, [M+NH4]+, [M-H2O+H]+
- Negative mode: [M-H]-, [M+CH3COO]-, [M+HCOO]-, [M+Cl]-

Example Usage:
```python
from masster.lib import Lib

# Create library instance
lib = Lib()

# Import compounds from CSV
lib.import_csv("compounds.csv", polarity="positive")

# Access library data
print(f"Loaded {len(lib.lib_df)} compounds")
print(lib.lib_df.head())

# Annotate sample features
annotations = lib.annotate_features(sample.features_df)
```
"""

import os
import json
from typing import Optional, Union, List, Dict, Any, TYPE_CHECKING

import polars as pl
import pyopenms as oms

# Import logger
from masster.logger import MassterLogger

if TYPE_CHECKING:
    import pandas as pd


def _calculate_formula_mass_shift(formula: str) -> float:
    """
    Calculate mass shift from formula string like "+H", "-H2O", "+Na-H", etc.

    Parameters
    ----------
    formula : str
        Formula string (e.g., "+H", "-H2O", "+Na-H")

    Returns
    -------
    float
        Mass shift in Daltons
    """
    # Standard atomic masses
    atomic_masses = {
        "H": 1.007825,
        "C": 12.0,
        "N": 14.003074,
        "O": 15.994915,
        "Na": 22.989769,
        "K": 38.963707,
        "Li": 7.016003,
        "Ca": 39.962591,
        "Mg": 23.985042,
        "Fe": 55.934938,
        "Cl": 34.968853,
        "Br": 78.918336,
        "I": 126.904473,
        "P": 30.973762,
        "S": 31.972071,
    }

    total_mass = 0.0

    # Parse formula by splitting on + and - while preserving the operators
    parts = []
    current_part = ""
    current_sign = 1

    for char in formula:
        if char == "+":
            if current_part:
                parts.append((current_sign, current_part))
            current_part = ""
            current_sign = 1
        elif char == "-":
            if current_part:
                parts.append((current_sign, current_part))
            current_part = ""
            current_sign = -1
        else:
            current_part += char

    if current_part:
        parts.append((current_sign, current_part))

    # Process each part
    for sign, part in parts:
        if not part:
            continue

        # Parse element and count (e.g., "H2O" -> H:2, O:1)
        elements = _parse_element_counts(part)

        for element, count in elements.items():
            if element in atomic_masses:
                total_mass += sign * atomic_masses[element] * count

    return total_mass


def _parse_element_counts(formula_part: str) -> Dict[str, int]:
    """Parse element counts from a formula part like 'H2O' -> {'H': 2, 'O': 1}"""
    elements = {}
    i = 0

    while i < len(formula_part):
        # Get element (uppercase letter, possibly followed by lowercase)
        element = formula_part[i]
        i += 1

        while i < len(formula_part) and formula_part[i].islower():
            element += formula_part[i]
            i += 1

        # Get count (digits following element)
        count_str = ""
        while i < len(formula_part) and formula_part[i].isdigit():
            count_str += formula_part[i]
            i += 1

        count = int(count_str) if count_str else 1
        elements[element] = elements.get(element, 0) + count

    return elements


def _format_adduct_name(components: List[Dict]) -> str:
    """Format adduct name from components like [M+H]1+ or [M+2H]2+"""
    if not components:
        return "[M]"

    # Count occurrences of each formula
    from collections import Counter

    formula_counts = Counter(comp["formula"] for comp in components)
    total_charge = sum(comp["charge"] for comp in components)

    # Build formula part with proper multipliers
    formula_parts = []
    for formula, count in sorted(
        formula_counts.items(),
    ):  # Sort for consistent ordering
        if count == 1:
            formula_parts.append(formula)
        else:
            # For multiple occurrences, use count prefix (e.g., 2H, 3Na)
            # Handle special case where formula might already start with + or -
            if formula.startswith(("+", "-")):
                sign = formula[0]
                base_formula = formula[1:]
                formula_parts.append(f"{sign}{count}{base_formula}")
            else:
                formula_parts.append(f"{count}{formula}")

    # Combine formula parts
    formula = "".join(formula_parts)

    # Format charge
    if total_charge == 0:
        charge_str = ""
    elif abs(total_charge) == 1:
        charge_str = "+" if total_charge > 0 else "-"
    else:
        charge_str = (
            f"{abs(total_charge)}+" if total_charge > 0 else f"{abs(total_charge)}-"
        )

    return f"[M{formula}]{charge_str}"


class Lib:
    """
    A class for managing compound libraries and feature annotation in mass spectrometry data.
    
    The Lib class provides functionality to:
    - Load compound libraries from CSV files
    - Generate adduct variants for compounds
    - Annotate MS1 features based on mass and retention time
    - Support both positive and negative ionization modes
    - Manage compound metadata (SMILES, InChI, formulas, etc.)
    
    Attributes:
        lib_df (pl.DataFrame): Polars DataFrame containing the library data with columns:
            - lib_uid: Unique identifier for each library entry
            - name: Compound name
            - smiles: SMILES notation
            - inchi: InChI identifier
            - inchikey: InChI key
            - formula: Molecular formula
            - adduct: Adduct type
            - m: Mass with adduct
            - z: Charge state
            - mz: Mass-to-charge ratio
            - rt: Retention time (if available)
    
    Example:
        >>> lib = Lib()
        >>> lib.import_csv("compounds.csv", polarity="positive")
        >>> print(f"Loaded {len(lib.lib_df)} library entries")
    """
    
    # Default adduct definitions using OpenMS format
    DEFAULT_ADDUCTS = {
        "positive": [
            "+H:1:0.65",
            "+Na:1:0.15",
            "+K:1:0.05",
            "+NH4:1:0.15",
            "-H2O:0:0.15",
        ],
        "negative": [
            "-H:-1:0.9",
            "+Cl:-1:0.1",
            "+CH2O2:0:0.15",
            "-H2O:0:0.15",
        ]
    }
    
    def __init__(self):
        """Initialize an empty Lib instance."""
        self.lib_df = None
        self.logger = MassterLogger("lib", level="INFO")
        self._initialize_empty_dataframe()
    
    def _initialize_empty_dataframe(self):
        """Initialize an empty DataFrame with the required schema."""
        self.lib_df = pl.DataFrame({
            "lib_uid": pl.Series([], dtype=pl.Int64),
            "cmpd_uid": pl.Series([], dtype=pl.Int64),
            "lib_source": pl.Series([], dtype=pl.Utf8),
            "name": pl.Series([], dtype=pl.Utf8),
            "shortname": pl.Series([], dtype=pl.Utf8),
            "class": pl.Series([], dtype=pl.Utf8),
            "smiles": pl.Series([], dtype=pl.Utf8),
            "inchi": pl.Series([], dtype=pl.Utf8),
            "inchikey": pl.Series([], dtype=pl.Utf8),
            "formula": pl.Series([], dtype=pl.Utf8),
            "iso": pl.Series([], dtype=pl.Int64),
            "adduct": pl.Series([], dtype=pl.Utf8),
            "probability": pl.Series([], dtype=pl.Float64),
            "stars": pl.Series([], dtype=pl.Int64),
            "m": pl.Series([], dtype=pl.Float64),
            "z": pl.Series([], dtype=pl.Int8),
            "mz": pl.Series([], dtype=pl.Float64),
            "rt": pl.Series([], dtype=pl.Float64),
            "quant_group": pl.Series([], dtype=pl.Int64),
            "db": pl.Series([], dtype=pl.Utf8),
            "db_id": pl.Series([], dtype=pl.Utf8),
        })
    
    def _get_adducts(self, 
                    adducts_list: Optional[List[str]] = None, 
                    polarity: Optional[str] = None,
                    min_probability: float = 0.03,
                    **kwargs) -> pl.DataFrame:
        """
        Generate comprehensive adduct specifications for the library.
        
        This method creates a DataFrame of adduct combinations following the same
        syntax as Study() and Sample() classes.
        
        Args:
            adducts_list: List of adduct specifications in OpenMS format (e.g., "+H:1:0.65")
            polarity: "positive", "negative", or None for both
            min_probability: Minimum probability threshold to filter adducts
            **kwargs: Additional parameters for adduct generation
            
        Returns:
            DataFrame with columns:
            - name: Formatted adduct name like "[M+H]1+"
            - charge: Total charge of the adduct
            - mass_shift: Total mass shift in Da
            - probability: Combined probability score
            - complexity: Number of adduct components
        """
        # Get adduct specifications
        if adducts_list is None:
            if polarity is None:
                # Use positive by default
                adducts_list = self.DEFAULT_ADDUCTS["positive"]
            elif polarity.lower() in ["positive", "pos"]:
                adducts_list = self.DEFAULT_ADDUCTS["positive"]
            elif polarity.lower() in ["negative", "neg"]:
                adducts_list = self.DEFAULT_ADDUCTS["negative"]
            else:
                raise ValueError(f"Unknown polarity: {polarity}")
        
        # Parameters
        charge_min = kwargs.get("charge_min", -2)
        charge_max = kwargs.get("charge_max", 2)
        max_combinations = kwargs.get("max_combinations", 2)
        
        # Parse base adduct specifications
        base_specs = []
        
        for adduct_str in adducts_list:
            if not isinstance(adduct_str, str) or ":" not in adduct_str:
                continue
                
            try:
                parts = adduct_str.split(":")
                if len(parts) != 3:
                    continue
                    
                formula_part = parts[0]
                charge = int(parts[1])
                probability = float(parts[2])
                
                # Calculate mass shift from formula
                mass_shift = _calculate_formula_mass_shift(formula_part)
                
                base_specs.append({
                    "formula": formula_part,
                    "charge": charge,
                    "mass_shift": mass_shift,
                    "probability": probability,
                    "raw_string": adduct_str,
                })
                
            except (ValueError, IndexError):
                continue
        
        if not base_specs:
            # Return empty DataFrame with correct schema
            return pl.DataFrame({
                "name": [],
                "charge": [],
                "mass_shift": [],
                "probability": [],
                "complexity": [],
            })
        
        # Generate all valid combinations
        combinations_list = []
        
        # Separate specs by charge type
        positive_specs = [spec for spec in base_specs if spec["charge"] > 0]
        negative_specs = [spec for spec in base_specs if spec["charge"] < 0]
        neutral_specs = [spec for spec in base_specs if spec["charge"] == 0]
        
        # 1. Single adducts
        for spec in base_specs:
            if charge_min <= spec["charge"] <= charge_max:
                formatted_name = _format_adduct_name([spec])
                combinations_list.append({
                    "components": [spec],
                    "formatted_name": formatted_name,
                    "total_mass_shift": spec["mass_shift"],
                    "total_charge": spec["charge"],
                    "combined_probability": spec["probability"],
                    "complexity": 1,
                })
        
        # 2. Generate multiply charged versions (2H+, 3H+, etc.)
        if max_combinations >= 2:
            for spec in positive_specs + negative_specs:
                base_charge = spec["charge"]
                for multiplier in range(2, min(max_combinations + 1, 4)):
                    total_charge = base_charge * multiplier
                    if charge_min <= total_charge <= charge_max:
                        components = [spec] * multiplier
                        formatted_name = _format_adduct_name(components)
                        
                        combinations_list.append({
                            "components": components,
                            "formatted_name": formatted_name,
                            "total_mass_shift": spec["mass_shift"] * multiplier,
                            "total_charge": total_charge,
                            "combined_probability": spec["probability"] ** multiplier,
                            "complexity": multiplier,
                        })
        
        # 3. Mixed combinations (positive + neutral)
        if max_combinations >= 2:
            for pos_spec in positive_specs:
                for neut_spec in neutral_specs:
                    total_charge = pos_spec["charge"] + neut_spec["charge"]
                    if charge_min <= total_charge <= charge_max:
                        components = [pos_spec, neut_spec]
                        formatted_name = _format_adduct_name(components)
                        combinations_list.append({
                            "components": components,
                            "formatted_name": formatted_name,
                            "total_mass_shift": pos_spec["mass_shift"] + neut_spec["mass_shift"],
                            "total_charge": total_charge,
                            "combined_probability": pos_spec["probability"] * neut_spec["probability"],
                            "complexity": 2,
                        })
        
        # Convert to polars DataFrame
        if combinations_list:
            combinations_list.sort(
                key=lambda x: (-x["combined_probability"], x["complexity"])
            )
            
            adducts_df = pl.DataFrame([
                {
                    "name": combo["formatted_name"],
                    "charge": combo["total_charge"],
                    "mass_shift": combo["total_mass_shift"],
                    "probability": combo["combined_probability"],
                    "complexity": combo["complexity"],
                }
                for combo in combinations_list
            ])
        else:
            # Return empty DataFrame with correct schema
            adducts_df = pl.DataFrame({
                "name": [],
                "charge": [],
                "mass_shift": [],
                "probability": [],
                "complexity": [],
            })
        
        # Filter by minimum probability
        if min_probability > 0.0 and len(adducts_df) > 0:
            adducts_df = adducts_df.filter(pl.col("probability") >= min_probability)
        
        return adducts_df
    
    def _neutralize_charged_formula(self, formula: str) -> Optional[str]:
        """
        Neutralize charged formulas by adjusting hydrogen count.
        
        Handles formulas ending with charge indicators:
        - +, 2+, 3+: Remove H, 2H, 3H respectively
        - -, 2-, 3-: Add H, 2H, 3H respectively
        
        Args:
            formula: Molecular formula string (e.g., "C6H12O6+", "C5H14NO+", "C4H5O4-")
            
        Returns:
            Neutralized formula string, or None if formula is invalid/empty
        """
        if not formula or not isinstance(formula, str):
            return None
            
        formula = formula.strip()
        if not formula:
            return None
        
        # Check for charge indicator at the end
        charge = 0
        original_formula = formula
        
        # Check for positive charges (+, 2+, 3+, etc.)
        if formula.endswith('+'):
            # Handle multi-charge like "2+", "3+"
            if len(formula) >= 2 and formula[-2].isdigit():
                charge = int(formula[-2])
                formula = formula[:-2]
            else:
                charge = 1
                formula = formula[:-1]
        
        # Check for negative charges (-, 2-, 3-, etc.)
        elif formula.endswith('-'):
            # Handle multi-charge like "2-", "3-"
            if len(formula) >= 2 and formula[-2].isdigit():
                charge = -int(formula[-2])
                formula = formula[:-2]
            else:
                charge = -1
                formula = formula[:-1]
        
        # If no charge found, return original formula
        if charge == 0:
            return original_formula
        
        # Neutralize by adjusting hydrogen count
        # Positive charge: remove H atoms (formula had extra H)
        # Negative charge: add H atoms (formula was missing H)
        
        try:
            # Use OpenMS to parse the formula and get element counts
            empirical_formula = oms.EmpiricalFormula(formula)
            
            # Convert to string and parse to get hydrogen count
            formula_str = str(empirical_formula)
            
            # Simple regex-based approach to adjust H count
            import re
            
            # Find hydrogen in the formula (H followed by optional number)
            h_match = re.search(r'H(\d*)', formula_str)
            
            if h_match:
                h_count_str = h_match.group(1)
                current_h = int(h_count_str) if h_count_str else 1
            else:
                # No hydrogen in formula
                current_h = 0
            
            # Calculate new hydrogen count
            # For positive charge (+), we remove H
            # For negative charge (-), we add H
            new_h = current_h - charge
            
            if new_h < 0:
                self.logger.trace(f"Cannot neutralize formula '{original_formula}': would result in negative hydrogen count")
                return None
            
            # Reconstruct formula with new hydrogen count
            if h_match:
                if new_h == 0:
                    # Remove H entirely
                    neutralized = re.sub(r'H\d*', '', formula_str)
                elif new_h == 1:
                    # H without number
                    neutralized = re.sub(r'H\d*', 'H', formula_str)
                else:
                    # H with number
                    neutralized = re.sub(r'H\d*', f'H{new_h}', formula_str)
            else:
                # Need to add hydrogen
                if new_h > 0:
                    # Add H at the beginning (or after C if present)
                    if formula_str.startswith('C'):
                        # Find where C ends
                        c_match = re.match(r'C(\d*)', formula_str)
                        if c_match:
                            after_c = len(c_match.group(0))
                            h_str = 'H' if new_h == 1 else f'H{new_h}'
                            neutralized = formula_str[:after_c] + h_str + formula_str[after_c:]
                        else:
                            neutralized = f'H{new_h}' + formula_str
                    else:
                        h_str = 'H' if new_h == 1 else f'H{new_h}'
                        neutralized = h_str + formula_str
                else:
                    neutralized = formula_str
            
            # Clean up any empty elements
            neutralized = neutralized.strip()
            
            return neutralized
            
        except Exception as e:
            self.logger.trace(f"Error neutralizing formula '{original_formula}': {e}")
            return None
    
    def _calculate_accurate_mass(self, formula: str) -> Optional[float]:
        """
        Calculate the accurate mass for a molecular formula using PyOpenMS.
        
        Args:
            formula: Molecular formula string
            
        Returns:
            Accurate mass as float, or None if calculation fails
        """
        # Skip obviously invalid formulas
        if not formula or not isinstance(formula, str):
            return None
        
        # Clean up whitespace
        formula = formula.strip()
        
        # Skip formulas that are obviously invalid
        invalid_patterns = [
            # Contains parentheses with multipliers like (C12H19NO19S3)nH2O
            lambda f: '(' in f and ')' in f and any(c.isalpha() and not c.isupper() for c in f.split(')')[1:]),
            # Contains words instead of chemical symbols
            lambda f: any(word in f.lower() for word in ['and', 'or', 'not', 'with', 'without']),
            # Contains lowercase letters at the start (element symbols should be uppercase)
            lambda f: f and f[0].islower(),
            # Contains unusual characters that shouldn't be in formulas
            lambda f: any(char in f for char in ['@', '#', '$', '%', '^', '&', '*', '=', '+', '?', '/', '\\', '|']),
            # Empty or very short non-standard formulas
            lambda f: len(f) < 2 and not f.isupper(),
        ]
        
        for pattern_check in invalid_patterns:
            try:
                if pattern_check(formula):
                    self.logger.trace(f"Skipping obviously invalid formula: '{formula}'")
                    return None
            except Exception:
                # If pattern checking fails, continue to PyOpenMS parsing
                pass
        
        try:
            empirical_formula = oms.EmpiricalFormula(formula)
            return empirical_formula.getMonoWeight()
        except Exception as e:
            self.logger.trace(f"Error calculating accurate mass for formula '{formula}': {e}")
            return None
    
    def _generate_adduct_variants(self, 
                                compound_data: Dict[str, Any], 
                                adducts: Optional[List[str]] = None,
                                polarity: Optional[str] = None,
                                lib_id_counter: Optional[int] = None,
                                min_probability: float = 0.03) -> tuple[List[Dict[str, Any]], int]:
        """
        Generate adduct variants for a given compound using the new adduct system.
        
        Args:
            compound_data: Dictionary containing compound information
            adducts: List of specific adducts to generate. If None, uses defaults for polarity
            polarity: Ionization polarity ("positive", "negative", or None for positive)
            lib_id_counter: Counter for generating unique lib_uid values
            min_probability: Minimum probability threshold for adduct filtering
            
        Returns:
            Tuple of (list of dictionaries representing adduct variants, updated counter)
        """
        variants = []
        counter = lib_id_counter or 1
        
        # Calculate base accurate mass
        accurate_mass = self._calculate_accurate_mass(compound_data["formula"])
        if accurate_mass is None:
            return variants, counter
        
        # Get adduct specifications using _get_adducts
        adducts_df = self._get_adducts(
            adducts_list=adducts,
            polarity=polarity,
            min_probability=min_probability
        )
        
        if len(adducts_df) == 0:
            return variants, counter
        
        # Generate variants for each adduct
        for adduct_row in adducts_df.iter_rows(named=True):
            adduct_name = adduct_row["name"]
            charge = adduct_row["charge"]
            mass_shift = adduct_row["mass_shift"]
            probability = adduct_row["probability"]
            
            # Calculate adducted mass and m/z
            adducted_mass = accurate_mass + mass_shift
            mz = abs(adducted_mass / charge) if charge != 0 else adducted_mass
            
            # Create variant entry
            variant = {
                "lib_uid": counter,
                "cmpd_uid": compound_data.get("cmpd_uid", None),
                "lib_source": compound_data.get("lib_source", None),
                "name": compound_data.get("name", ""),
                "shortname": compound_data.get("shortname", ""),
                "class": compound_data.get("class", ""),
                "smiles": compound_data.get("smiles", ""),
                "inchi": compound_data.get("inchi", ""),
                "inchikey": compound_data.get("inchikey", ""),
                "formula": compound_data["formula"],
                "iso": 0,  # Default to zero
                "adduct": adduct_name,
                "probability": probability,
                "stars": compound_data.get("stars", 0),
                "m": adducted_mass,
                "z": charge,
                "mz": mz,
                "rt": compound_data.get("rt", None),
                "quant_group": counter,  # Use same as lib_uid for default
                "db_id": compound_data.get("db_id", None),
                "db": compound_data.get("db", None),
            }
            variants.append(variant)
            counter += 1
        
        return variants, counter
    
    def import_csv(self, 
                  csvfile: str, 
                  polarity: Optional[str] = None,
                  adducts: Optional[List[str]] = None,
                  min_probability: float = 0.03) -> None:
        """
        Import compound library from a CSV file.
        
        This method reads a CSV file and generates adduct variants for each compound.
        Missing columns will be filled with appropriate default values.
        
        Args:
            csvfile: Path to the CSV file
            polarity: Ionization polarity ("positive", "negative", or None for positive)
            adducts: Specific adducts to generate. If None, generates defaults for the polarity
            min_probability: Minimum probability threshold for adduct filtering
            
        Expected CSV columns (case-insensitive):
            - Required: Formula (or formula)
            - Optional: Name/name/Compound/compound, SMILES/smiles, InChI/inchi, 
                      InChIKey/inchikey, RT/rt, RT2/rt2
        
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If required columns are missing
        """
        if not os.path.exists(csvfile):
            raise FileNotFoundError(f"CSV file not found: {csvfile}")
        
        # Read CSV file with robust error handling
        try:
            df = pl.read_csv(csvfile, truncate_ragged_lines=True, ignore_errors=True)
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}") from e
        
        # Find column mappings (case-insensitive)
        column_mapping = self._map_csv_columns(df.columns)
        
        # Validate required columns
        if "formula" not in column_mapping:
            raise ValueError("Required column 'Formula' (or 'formula') not found in CSV file")
        
        # Process each compound
        all_variants = []
        cmpd_id_counter = 1
        lib_id_counter = 1
        total_compounds = 0
        skipped_compounds = 0
        
        for row in df.iter_rows(named=True):
            total_compounds += 1
            
            # Get formula and skip if empty/None
            formula = row[column_mapping["formula"]]
            if not formula or not isinstance(formula, str) or not formula.strip():
                skipped_compounds += 1
                continue
            
            # Neutralize charged formulas
            formula = formula.strip()
            neutralized_formula = self._neutralize_charged_formula(formula)
            if neutralized_formula is None:
                # Skip if neutralization failed
                skipped_compounds += 1
                continue
            
            # Extract compound data
            # assign a compound-level uid so all adducts share the same cmpd_uid
            compound_level_uid = cmpd_id_counter
            cmpd_id_counter += 1

            compound_data = {
                "name": row.get(column_mapping.get("name", ""), ""),
                "shortname": row.get(column_mapping.get("shortname", ""), ""),
                "class": row.get(column_mapping.get("class", ""), ""),                
                "smiles": row.get(column_mapping.get("smiles", ""), ""),
                "inchi": row.get(column_mapping.get("inchi", ""), ""),
                "inchikey": row.get(column_mapping.get("inchikey", ""), ""),
                "formula": neutralized_formula,
                "rt": self._safe_float_conversion(row.get(column_mapping.get("rt", ""), None)),
                "db_id": row.get(column_mapping.get("db_id", ""), None),
                "db": row.get(column_mapping.get("db", ""), None),
                "stars": self._safe_int_conversion(row.get(column_mapping.get("stars", ""), 0)),
                "cmpd_uid": compound_level_uid,
            }
            
            # Generate adduct variants
            variants, lib_id_counter = self._generate_adduct_variants(
                compound_data, adducts=adducts, polarity=polarity, 
                lib_id_counter=lib_id_counter, min_probability=min_probability
            )
            all_variants.extend(variants)
            
            # Track if compound was skipped due to invalid formula
            if len(variants) == 0:
                skipped_compounds += 1
            
            # Handle RT2 column if present
            if "rt2" in column_mapping and len(variants) > 0:  # Only if main variants were created
                rt2_value = self._safe_float_conversion(row.get(column_mapping["rt2"], None))
                if rt2_value is not None:
                    # Create additional variants with RT2
                    compound_data_rt2 = compound_data.copy()
                    compound_data_rt2["rt"] = rt2_value
                    compound_data_rt2["name"] = compound_data["name"] + " II"
                    
                    variants_rt2, lib_id_counter = self._generate_adduct_variants(
                        compound_data_rt2, adducts=adducts, polarity=polarity, 
                        lib_id_counter=lib_id_counter, min_probability=min_probability
                    )
                    all_variants.extend(variants_rt2)
        
        # Convert to DataFrame and store
        if all_variants:
            new_lib_df = pl.DataFrame(all_variants)
            
            # Combine with existing data if any
            if self.lib_df is not None and len(self.lib_df) > 0:
                self.lib_df = pl.concat([self.lib_df, new_lib_df])
            else:
                self.lib_df = new_lib_df
                
            #successful_compounds = total_compounds - skipped_compounds
            self.logger.info(f"Imported {len(all_variants)} library entries from {csvfile}")
            #print(f"Processed {total_compounds} compounds: {successful_compounds} successful, {skipped_compounds} skipped due to invalid formulas")
        else:
            self.logger.warning(f"No valid compounds found in {csvfile}")
            if skipped_compounds > 0:
                self.logger.warning(f"All {total_compounds} compounds were skipped due to invalid formulas")
    
    def import_json(self, 
                   jsonfile: str, 
                   polarity: Optional[str] = None,
                   adducts: Optional[List[str]] = None,
                   min_probability: float = 0.03) -> None:
        """
        Import compound library from a JSON file created by csv_to_json.py.
        
        This method reads a JSON file with the structure created by csv_to_json.py
        and generates adduct variants for each compound.
        
        Args:
            jsonfile: Path to the JSON file
            polarity: Ionization polarity ("positive", "negative", or None for positive)
            adducts: Specific adducts to generate. If None, generates defaults for the polarity
            min_probability: Minimum probability threshold for adduct filtering
            
        Expected JSON structure:
            {
                "version": "1.0",
                "creation_date": "2025-10-07T09:17:06.142290",
                "description": "Converted from CSV file...",
                "source_file": "filename.csv",
                "record_count": 123,
                "data": [
                    {
                        "name": "compound name",
                        "smiles": "SMILES string",
                        "inchikey": "InChI key",
                        "formula": "molecular formula",
                        "db_id": "database ID",
                        "db": "database name"
                    },
                    ...
                ]
            }
            
        Raises:
            FileNotFoundError: If JSON file doesn't exist
            ValueError: If JSON structure is invalid or required data is missing
        """
        if not os.path.exists(jsonfile):
            raise FileNotFoundError(f"JSON file not found: {jsonfile}")
        
        # Read and parse JSON file
        try:
            with open(jsonfile, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {e}") from e
        except Exception as e:
            raise ValueError(f"Error reading JSON file: {e}") from e
        
        # Validate JSON structure
        if not isinstance(json_data, dict):
            raise ValueError("JSON file must contain a dictionary at root level")
        
        if "data" not in json_data:
            raise ValueError("JSON file must contain a 'data' field with compound records")
        
        data = json_data["data"]
        if not isinstance(data, list):
            raise ValueError("'data' field must be a list of compound records")
        
        # Extract metadata for reporting
        version = json_data.get("version", "unknown")
        source_file = json_data.get("source_file", "unknown")
        record_count = json_data.get("record_count", len(data))
        
        self.logger.info(f"Loading embedded library: {source_file}, version {version}, records: {record_count}")
        
        # Process each compound
        all_variants = []
        cmpd_id_counter = 1
        lib_id_counter = 1
        total_compounds = 0
        skipped_compounds = 0
        
        for compound_record in data:
            total_compounds += 1
            
            # Validate required fields
            if not isinstance(compound_record, dict):
                skipped_compounds += 1
                continue
            
            # Get formula and skip if empty/None
            formula = compound_record.get("formula", compound_record.get("Formula", ""))
            if not formula or not isinstance(formula, str) or not formula.strip():
                skipped_compounds += 1
                continue
            
            # Neutralize charged formulas
            formula = formula.strip()
            neutralized_formula = self._neutralize_charged_formula(formula)
            if neutralized_formula is None:
                # Skip if neutralization failed
                skipped_compounds += 1
                continue
            
            # Extract compound data, handling both CSV column names and JSON field names
            compound_level_uid = cmpd_id_counter
            cmpd_id_counter += 1
            
            compound_data = {
                "name": compound_record.get("name", compound_record.get("Name", "")),
                "shortname": compound_record.get("shortname", ""),
                "class": compound_record.get("class", ""),
                "smiles": compound_record.get("smiles", compound_record.get("SMILES", "")),
                "inchi": compound_record.get("inchi", compound_record.get("InChI", "")),
                "inchikey": compound_record.get("inchikey", compound_record.get("InChIKey", "")),
                "formula": neutralized_formula,
                "rt": self._safe_float_conversion(compound_record.get("rt", compound_record.get("RT", None))),
                "db_id": compound_record.get("db_id", compound_record.get("database_id", None)),
                "db": compound_record.get("db", compound_record.get("database", None)),
                "stars": self._safe_int_conversion(compound_record.get("stars", 0)),
                "cmpd_uid": compound_level_uid,
            }
            
            # Generate adduct variants
            variants, lib_id_counter = self._generate_adduct_variants(
                compound_data, adducts=adducts, polarity=polarity, 
                lib_id_counter=lib_id_counter, min_probability=min_probability
            )
            all_variants.extend(variants)
            
            # Track if compound was skipped due to invalid formula
            if len(variants) == 0:
                skipped_compounds += 1
        
        # Convert to DataFrame and store
        if all_variants:
            new_lib_df = pl.DataFrame(all_variants)
            
            # Combine with existing data if any
            if self.lib_df is not None and len(self.lib_df) > 0:
                self.lib_df = pl.concat([self.lib_df, new_lib_df])
            else:
                self.lib_df = new_lib_df
                
            self.logger.info(f"Imported {len(all_variants)} library entries from {jsonfile}")
        else:
            self.logger.warning(f"No valid compounds found in {jsonfile}")
            if skipped_compounds > 0:
                self.logger.warning(f"All {total_compounds} compounds were skipped due to invalid formulas")
    
    def _map_csv_columns(self, columns: List[str]) -> Dict[str, str]:
        """
        Map CSV column names to standardized internal names (case-insensitive).
        
        Args:
            columns: List of column names from CSV
            
        Returns:
            Dictionary mapping internal names to actual column names
        """
        mapping = {}
        columns_lower = [col.lower() for col in columns]
        
        # Name mapping
        for name_variant in ["name", "compound"]:
            if name_variant in columns_lower:
                mapping["name"] = columns[columns_lower.index(name_variant)]
                break
        
        # Formula mapping
        for formula_variant in ["formula"]:
            if formula_variant in columns_lower:
                mapping["formula"] = columns[columns_lower.index(formula_variant)]
                break
        
        # SMILES mapping
        for smiles_variant in ["smiles"]:
            if smiles_variant in columns_lower:
                mapping["smiles"] = columns[columns_lower.index(smiles_variant)]
                break
        
        # InChI mapping
        for inchi_variant in ["inchi"]:
            if inchi_variant in columns_lower:
                mapping["inchi"] = columns[columns_lower.index(inchi_variant)]
                break
        
        # InChIKey mapping
        for inchikey_variant in ["inchikey", "inchi_key"]:
            if inchikey_variant in columns_lower:
                mapping["inchikey"] = columns[columns_lower.index(inchikey_variant)]
                break
        
        # RT mapping
        for rt_variant in ["rt", "retention_time", "retentiontime"]:
            if rt_variant in columns_lower:
                mapping["rt"] = columns[columns_lower.index(rt_variant)]
                break
        
        # RT2 mapping
        for rt2_variant in ["rt2", "retention_time2", "retentiontime2"]:
            if rt2_variant in columns_lower:
                mapping["rt2"] = columns[columns_lower.index(rt2_variant)]
                break
        
        # Database ID mapping
        for db_id_variant in ["db_id", "database_id", "dbid"]:
            if db_id_variant in columns_lower:
                mapping["db_id"] = columns[columns_lower.index(db_id_variant)]
                break
        
        # Database mapping
        for db_variant in ["db", "database"]:
            if db_variant in columns_lower:
                mapping["db"] = columns[columns_lower.index(db_variant)]
                break
        
        # Stars mapping
        for stars_variant in ["stars", "star", "confidence"]:
            if stars_variant in columns_lower:
                mapping["stars"] = columns[columns_lower.index(stars_variant)]
                break
        
        return mapping
    
    def _safe_float_conversion(self, value: Any) -> Optional[float]:
        """
        Safely convert a value to float, returning None if conversion fails.
        
        Args:
            value: Value to convert
            
        Returns:
            Float value or None
        """
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int_conversion(self, value: Any) -> Optional[int]:
        """
        Safely convert a value to int, returning None if conversion fails.
        
        Args:
            value: Value to convert
            
        Returns:
            Int value or None
        """
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def annotate_features(self, 
                         features_df: Union[pl.DataFrame, "pd.DataFrame"],
                         mz_tolerance: float = 0.01,
                         rt_tolerance: Optional[float] = None) -> pl.DataFrame:
        """
        Annotate features based on library matches using m/z and retention time.
        
        Args:
            features_df: DataFrame containing features with 'mz' and optionally 'rt' columns
            mz_tolerance: Mass tolerance in Da for matching
            rt_tolerance: Retention time tolerance in minutes for matching (if None, RT not used)
            
        Returns:
            DataFrame with annotation results
        """
        if self.lib_df is None or len(self.lib_df) == 0:
            raise ValueError("Library is empty. Import compounds first.")
        
        # Convert pandas DataFrame to Polars if needed
        if hasattr(features_df, 'to_pandas'):  # It's already a Polars DataFrame
            features_pl = features_df
        elif hasattr(features_df, 'values'):  # It's likely a pandas DataFrame
            try:
                import pandas as pd
                if isinstance(features_df, pd.DataFrame):
                    features_pl = pl.from_pandas(features_df)
                else:
                    features_pl = features_df
            except ImportError:
                features_pl = features_df
        else:
            features_pl = features_df
        
        annotations = []
        
        for feature_row in features_pl.iter_rows(named=True):
            feature_mz = feature_row.get("mz")
            feature_rt = feature_row.get("rt")
            
            if feature_mz is None:
                continue
            
            # Find matching library entries
            mz_matches = self.lib_df.filter(
                (pl.col("mz") >= feature_mz - mz_tolerance) &
                (pl.col("mz") <= feature_mz + mz_tolerance)
            )
            
            # Apply RT filter if both RT tolerance and feature RT are available
            if rt_tolerance is not None and feature_rt is not None:
                # Filter library entries that have RT values
                rt_matches = mz_matches.filter(
                    pl.col("rt").is_not_null() &
                    (pl.col("rt") >= feature_rt - rt_tolerance) &
                    (pl.col("rt") <= feature_rt + rt_tolerance)
                )
                if len(rt_matches) > 0:
                    matches = rt_matches
                else:
                    matches = mz_matches  # Fall back to m/z-only matches
            else:
                matches = mz_matches
            
            # Create annotation entries
            for match_row in matches.iter_rows(named=True):
                annotation = {
                    "feature_mz": feature_mz,
                    "feature_rt": feature_rt,
                    "lib_uid": match_row["lib_uid"],
                    "cmpd_uid": match_row.get("cmpd_uid"),
                    "lib_source": match_row.get("lib_source"),
                    "name": match_row["name"],
                    "shortname": match_row["shortname"],
                    "class": match_row["class"],
                    "formula": match_row["formula"],
                    "iso": match_row.get("iso", 0),
                    "adduct": match_row["adduct"],
                    "smiles": match_row["smiles"],
                    "inchi": match_row["inchi"],
                    "inchikey": match_row["inchikey"],
                    "lib_mz": match_row["mz"],
                    "lib_rt": match_row["rt"],
                    "quant_group": match_row.get("quant_group"),
                    "stars": match_row.get("stars"),
                    "delta_mz": abs(feature_mz - match_row["mz"]),
                    "delta_rt": abs(feature_rt - match_row["rt"]) if feature_rt is not None and match_row["rt"] is not None else None,
                }
                annotations.append(annotation)
        
        return pl.DataFrame(annotations) if annotations else pl.DataFrame()
    
    def get_adducts_for_polarity(self, polarity: str) -> List[str]:
        """
        Get list of supported adducts for a given polarity.
        
        Args:
            polarity: "positive" or "negative"
            
        Returns:
            List of adduct names
        """
        adducts_df = self._get_adducts(polarity=polarity, min_probability=0.0)
        return adducts_df.select("name").to_series().to_list()
    
    def compare(
        self,
        file: Optional[str] = None,
        action: str = "intersect",
        on: str = "inchikey14",
        keep_none: bool = False,
    ) -> Optional[pl.DataFrame]:
        """
        Compare current library with another library and perform actions based on matching compounds.
        
        This method loads a reference library and compares it with the current library based on a 
        specified comparison field (formula, inchikey, inchikey14, or name). It then performs 
        various actions on rows based on whether they match the reference library.
        
        Args:
            file: Path to reference library file (CSV or JSON). If None, no comparison is performed.
            action: Action to perform based on comparison results:
                - 'reset_stars' or 'reset_star': Set stars=0 for rows NOT in reference library
                - 'add_stars' or 'add_star': Increment stars by 1 for rows in reference library
                - 'delete': Remove rows that ARE in reference library
                - 'filter' or 'delete_others': Remove rows that are NOT in reference library
                - 'intersect': Return DataFrame of lib_df rows that ARE in reference library
                - 'difference': Return DataFrame of lib_df rows that are NOT in reference library
                - 'missing': Return DataFrame of reference library rows not matched in lib_df
            on: Field to compare on. Valid values: 'formula', 'inchikey', 'inchikey14', 'name'
            keep_none: If True, treat None/null values as valid matches (keep them regardless)
        
        Returns:
            None for modification actions (modifies self.lib_df in place)
            pl.DataFrame for query actions ('intersect', 'difference', 'missing')
        
        Raises:
            ValueError: If invalid 'on' or 'action' value provided
            FileNotFoundError: If file doesn't exist
        
        Example:
            >>> lib = Lib()
            >>> lib.import_csv("my_compounds.csv")
            >>> # Reset stars for compounds not in reference library
            >>> lib.compare(file="reference_lib.csv", action="reset_stars", on="inchikey14")
            >>> # Filter to keep only compounds in reference library
            >>> lib.compare(file="reference_lib.csv", action="filter", on="name")
            >>> # Get compounds that are in both libraries
            >>> common = lib.compare(file="reference_lib.csv", action="intersect", on="inchikey14")
            >>> # Get compounds missing from reference
            >>> missing = lib.compare(file="reference_lib.csv", action="missing", on="formula")
        """
        # Validate inputs
        valid_on_values = ['formula', 'inchikey', 'inchikey14', 'name']
        if on not in valid_on_values:
            raise ValueError(f"Invalid 'on' value: {on}. Must be one of {valid_on_values}")
        
        valid_actions = ['reset_stars', 'reset_star', 'add_stars', 'add_star', 'delete', 'filter', 'delete_others', 'intersect', 'difference', 'missing']
        if action not in valid_actions:
            raise ValueError(f"Invalid action: {action}. Must be one of {valid_actions}")
        
        # Check if current library is empty
        if self.lib_df is None or self.lib_df.is_empty():
            self.logger.warning("Current library is empty. No comparison performed.")
            return
        
        # If no file provided, nothing to compare
        if file is None:
            self.logger.warning("No reference file provided. No comparison performed.")
            return
        
        # Check if file exists
        if not os.path.exists(file):
            raise FileNotFoundError(f"Reference library file not found: {file}")
        
        # Load reference library
        new_lib = Lib()
        if file.lower().endswith('.json'):
            new_lib.import_json(file)
        elif file.lower().endswith('.csv'):
            new_lib.import_csv(file)
        else:
            # Try CSV by default
            new_lib.import_csv(file)
        
        if new_lib.lib_df is None or new_lib.lib_df.is_empty():
            self.logger.warning(f"Reference library from {file} is empty. No comparison performed.")
            return
        
        # Extract comparison values from reference library
        if on == 'inchikey14':
            # Use first 14 characters of inchikey
            if 'inchikey' not in new_lib.lib_df.columns:
                raise ValueError("Reference library does not have 'inchikey' column for inchikey14 comparison")
            valid_values = (
                new_lib.lib_df
                .select(pl.col('inchikey').str.slice(0, 14).alias('inchikey14'))
                .unique()
                .drop_nulls()
                .to_series()
                .to_list()
            )
        else:
            # Use the column directly
            if on not in new_lib.lib_df.columns:
                raise ValueError(f"Reference library does not have '{on}' column")
            valid_values = (
                new_lib.lib_df
                .select(on)
                .unique()
                .drop_nulls()
                .to_series()
                .to_list()
            )
        
        # Check if comparison column exists in current library
        if on == 'inchikey14':
            if 'inchikey' not in self.lib_df.columns:
                raise ValueError("Current library does not have 'inchikey' column for inchikey14 comparison")
            # Create temporary column for comparison
            comparison_col = pl.col('inchikey').str.slice(0, 14)
        else:
            if on not in self.lib_df.columns:
                raise ValueError(f"Current library does not have '{on}' column")
            comparison_col = pl.col(on)
        
        # Create mask for rows that match reference library
        is_valid = comparison_col.is_in(valid_values)
        
        # Handle None values if keep_none is True
        if keep_none:
            is_none = comparison_col.is_null()
            is_valid = is_valid | is_none
        
        # Apply action based on the mask
        if action in ['reset_stars', 'reset_star']:
            # Set stars=0 for rows NOT in reference library
            self.lib_df = self.lib_df.with_columns(
                pl.when(~is_valid)
                .then(pl.lit(0))
                .otherwise(pl.col('stars'))
                .alias('stars')
            )
        
        elif action in ['add_stars', 'add_star']:
            # Increment stars by 1 for rows in reference library
            self.lib_df = self.lib_df.with_columns(
                pl.when(is_valid)
                .then(pl.col('stars') + 1)
                .otherwise(pl.col('stars'))
                .alias('stars')
            )
        
        elif action == 'delete':
            # Remove rows that ARE in reference library
            self.lib_df = self.lib_df.filter(~is_valid)
        
        elif action in ['filter', 'delete_others']:
            # Remove rows that are NOT in reference library
            self.lib_df = self.lib_df.filter(is_valid)
        
        elif action == 'intersect':
            # Return rows of lib_df that ARE in reference library
            return self.lib_df.filter(is_valid)
        
        elif action == 'difference':
            # Return rows of lib_df that are NOT in reference library
            return self.lib_df.filter(~is_valid)
        
        elif action == 'missing':
            # Return rows of reference library that are NOT matched in lib_df
            # Get the comparison values from current lib_df
            if on == 'inchikey14':
                current_values = (
                    self.lib_df
                    .select(pl.col('inchikey').str.slice(0, 14).alias('inchikey14'))
                    .unique()
                    .drop_nulls()
                    .to_series()
                    .to_list()
                )
                # Filter new_lib for rows not in current library
                missing_df = new_lib.lib_df.filter(
                    ~pl.col('inchikey').str.slice(0, 14).is_in(current_values)
                )
                # Deduplicate by inchikey14 (keep first occurrence)
                missing_df = missing_df.unique(subset=['inchikey'], keep='first', maintain_order=True)
            else:
                current_values = (
                    self.lib_df
                    .select(on)
                    .unique()
                    .drop_nulls()
                    .to_series()
                    .to_list()
                )
                # Filter new_lib for rows not in current library
                missing_df = new_lib.lib_df.filter(~pl.col(on).is_in(current_values))
                # Deduplicate by the comparison column (keep first occurrence)
                missing_df = missing_df.unique(subset=[on], keep='first', maintain_order=True)
            
            return missing_df
        
        return None
    
    def lib_select(
        self,
        uid=None,
        cmpd_uid=None,
        lib_source=None,
        name=None,
        shortname=None,
        class_=None,
        formula=None,
        inchikey=None,
        inchikey14=None,
        adduct=None,
        iso=None,
        mz=None,
        rt=None,
        probability=None,
        stars=None,
        z=None,
        quant_group=None,
        db=None,
    ) -> pl.DataFrame:
        """
        Select library entries based on specified criteria and return the filtered DataFrame.
        
        This method filters lib_df based on various criteria for compound properties,
        returning a Polars DataFrame with matching entries.
        
        Args:
            uid: lib_uid filter (list of UIDs, tuple for range, or None for all)
            cmpd_uid: compound UID filter (list, tuple for range, or single value)
            lib_source: library source filter (str for exact match, list for multiple sources)
            name: compound name filter using regex (str for pattern, list for multiple patterns with OR)
            shortname: short name filter using regex (str for pattern, list for multiple patterns)
            class_: compound class filter using regex (str for pattern, list for multiple patterns)
            formula: molecular formula filter (str for exact match, list for multiple formulas)
            inchikey: InChIKey filter (str for exact match, list for multiple keys)
            inchikey14: InChIKey first 14 chars filter (str for exact match, list for multiple)
            adduct: adduct filter (str for exact match, list for multiple adducts)
            iso: isotope number filter (tuple for range, single value for exact match)
            mz: m/z range filter (tuple for range, single value for minimum)
            rt: retention time range filter (tuple for range, single value for minimum)
            probability: adduct probability filter (tuple for range, single value for minimum)
            stars: stars rating filter (tuple for range, single value for exact match)
            z: charge filter (int for exact match, list for multiple charges)
            quant_group: quantification group filter (int for exact match, list for multiple groups)
            db: database filter (str for exact match, list for multiple databases)
        
        Returns:
            pl.DataFrame: Filtered library DataFrame
        
        Examples:
            >>> lib = Lib()
            >>> lib.import_csv("compounds.csv")
            >>> # Select by m/z range
            >>> selected = lib.lib_select(mz=(100, 500))
            >>> # Select by name pattern
            >>> selected = lib.lib_select(name="glucose")
            >>> # Select by multiple criteria
            >>> selected = lib.lib_select(adduct="[M+H]+", stars=(3, 5))
        """
        if self.lib_df is None or self.lib_df.is_empty():
            self.logger.warning("Library is empty.")
            return pl.DataFrame()
        
        lib = self.lib_df.clone()
        
        # Filter by lib_uid
        if uid is not None:
            if isinstance(uid, tuple) and len(uid) == 2:
                min_uid, max_uid = uid
                lib = lib.filter((pl.col("lib_uid") >= min_uid) & (pl.col("lib_uid") <= max_uid))
            elif isinstance(uid, list):
                lib = lib.filter(pl.col("lib_uid").is_in(uid))
            else:
                lib = lib.filter(pl.col("lib_uid") == uid)
        
        # Filter by cmpd_uid
        if cmpd_uid is not None:
            if isinstance(cmpd_uid, tuple) and len(cmpd_uid) == 2:
                min_uid, max_uid = cmpd_uid
                lib = lib.filter((pl.col("cmpd_uid") >= min_uid) & (pl.col("cmpd_uid") <= max_uid))
            elif isinstance(cmpd_uid, list):
                lib = lib.filter(pl.col("cmpd_uid").is_in(cmpd_uid))
            else:
                lib = lib.filter(pl.col("cmpd_uid") == cmpd_uid)
        
        # Filter by lib_source
        if lib_source is not None:
            if isinstance(lib_source, list):
                lib = lib.filter(pl.col("lib_source").is_in(lib_source))
            else:
                lib = lib.filter(pl.col("lib_source") == lib_source)
        
        # Filter by name (regex)
        if name is not None:
            if isinstance(name, list):
                # Combine multiple patterns with OR
                pattern = "|".join(name)
                lib = lib.filter(pl.col("name").str.contains(pattern, literal=False))
            else:
                lib = lib.filter(pl.col("name").str.contains(name, literal=False))
        
        # Filter by shortname (regex)
        if shortname is not None:
            if isinstance(shortname, list):
                pattern = "|".join(shortname)
                lib = lib.filter(pl.col("shortname").str.contains(pattern, literal=False))
            else:
                lib = lib.filter(pl.col("shortname").str.contains(shortname, literal=False))
        
        # Filter by class (regex)
        if class_ is not None:
            if isinstance(class_, list):
                pattern = "|".join(class_)
                lib = lib.filter(pl.col("class").str.contains(pattern, literal=False))
            else:
                lib = lib.filter(pl.col("class").str.contains(class_, literal=False))
        
        # Filter by formula
        if formula is not None:
            if isinstance(formula, list):
                lib = lib.filter(pl.col("formula").is_in(formula))
            else:
                lib = lib.filter(pl.col("formula") == formula)
        
        # Filter by inchikey
        if inchikey is not None:
            if isinstance(inchikey, list):
                lib = lib.filter(pl.col("inchikey").is_in(inchikey))
            else:
                lib = lib.filter(pl.col("inchikey") == inchikey)
        
        # Filter by inchikey14 (first 14 characters)
        if inchikey14 is not None:
            if isinstance(inchikey14, list):
                lib = lib.filter(pl.col("inchikey").str.slice(0, 14).is_in(inchikey14))
            else:
                lib = lib.filter(pl.col("inchikey").str.slice(0, 14) == inchikey14)
        
        # Filter by adduct
        if adduct is not None:
            # Normalize adduct names: add "1" charge if omitted
            # e.g., "[M-H]-" -> "[M-H]1-", "[M+H]+" -> "[M+H]1+"
            def normalize_adduct(adduct_str):
                """Add charge number '1' if omitted from adduct name."""
                if not isinstance(adduct_str, str):
                    return adduct_str
                # Check if adduct ends with + or - without a digit before it
                import re
                # Pattern: ends with ']' followed by '+' or '-' (no digit before the charge)
                if re.search(r'\][+\-]$', adduct_str):
                    # Add '1' before the final charge sign
                    charge = adduct_str[-1]
                    return adduct_str[:-1] + '1' + charge
                return adduct_str
            
            if isinstance(adduct, list):
                # Normalize both the search terms and the lib_df adducts for comparison
                normalized_search = [normalize_adduct(a) for a in adduct]
                lib = lib.with_columns(
                    pl.col("adduct").map_elements(normalize_adduct, return_dtype=pl.Utf8).alias("adduct_normalized")
                ).filter(
                    pl.col("adduct_normalized").is_in(normalized_search)
                ).drop("adduct_normalized")
            else:
                # Normalize both the search term and the lib_df adducts for comparison
                normalized_search = normalize_adduct(adduct)
                lib = lib.with_columns(
                    pl.col("adduct").map_elements(normalize_adduct, return_dtype=pl.Utf8).alias("adduct_normalized")
                ).filter(
                    pl.col("adduct_normalized") == normalized_search
                ).drop("adduct_normalized")
        
        # Filter by iso
        if iso is not None:
            if isinstance(iso, tuple) and len(iso) == 2:
                min_iso, max_iso = iso
                lib = lib.filter((pl.col("iso") >= min_iso) & (pl.col("iso") <= max_iso))
            else:
                lib = lib.filter(pl.col("iso") == iso)
        
        # Filter by mz
        if mz is not None:
            if isinstance(mz, tuple) and len(mz) == 2:
                min_mz, max_mz = mz
                lib = lib.filter((pl.col("mz") >= min_mz) & (pl.col("mz") <= max_mz))
            else:
                lib = lib.filter(pl.col("mz") >= mz)
        
        # Filter by rt
        if rt is not None:
            if isinstance(rt, tuple) and len(rt) == 2:
                min_rt, max_rt = rt
                lib = lib.filter((pl.col("rt") >= min_rt) & (pl.col("rt") <= max_rt))
            else:
                lib = lib.filter(pl.col("rt") >= rt)
        
        # Filter by probability
        if probability is not None:
            if isinstance(probability, tuple) and len(probability) == 2:
                min_prob, max_prob = probability
                lib = lib.filter((pl.col("probability") >= min_prob) & (pl.col("probability") <= max_prob))
            else:
                lib = lib.filter(pl.col("probability") >= probability)
        
        # Filter by stars
        if stars is not None:
            if isinstance(stars, tuple) and len(stars) == 2:
                min_stars, max_stars = stars
                lib = lib.filter((pl.col("stars") >= min_stars) & (pl.col("stars") <= max_stars))
            else:
                lib = lib.filter(pl.col("stars") == stars)
        
        # Filter by charge
        if z is not None:
            if isinstance(z, list):
                lib = lib.filter(pl.col("z").is_in(z))
            else:
                lib = lib.filter(pl.col("z") == z)
        
        # Filter by quant_group
        if quant_group is not None:
            if isinstance(quant_group, list):
                lib = lib.filter(pl.col("quant_group").is_in(quant_group))
            else:
                lib = lib.filter(pl.col("quant_group") == quant_group)
        
        # Filter by db
        if db is not None:
            if isinstance(db, list):
                lib = lib.filter(pl.col("db").is_in(db))
            else:
                lib = lib.filter(pl.col("db") == db)
        
        return lib
    
    def lib_filter(self, entries):
        """
        Keep only the specified library entries and delete all others (modifies lib_df in place).
        
        This method filters lib_df to keep only specified entries, removing all others.
        Similar to features_filter() but for library entries.
        
        Args:
            entries: Can be one of the following:
                - list: List of lib_uid values to keep
                - pl.DataFrame or pd.DataFrame: DataFrame with 'lib_uid' column - extracts unique values to keep
                - str: Special action:
                    * 'delete_identified': Delete all library entries that appear in id_df
                    * 'delete_orphans': Delete all library entries that do NOT appear in id_df
        
        Returns:
            None (modifies self.lib_df in place)
        
        Raises:
            ValueError: If entries type is invalid or required data is missing
        
        Examples:
            >>> lib = Lib()
            >>> lib.import_csv("compounds.csv")
            >>> # Keep only specific UIDs
            >>> lib.lib_filter([0, 1, 2, 10, 15])
            >>> # Keep only entries from a filtered DataFrame
            >>> selected = lib.lib_select(stars=(4, 5))
            >>> lib.lib_filter(selected)
        """
        if self.lib_df is None or self.lib_df.is_empty():
            self.logger.warning("Library is empty.")
            return
        
        if entries is None:
            self.logger.warning("No entries specified to keep.")
            return
        
        original_count = len(self.lib_df)
        
        # Handle string actions
        if isinstance(entries, str):
            # For string actions, we need id_df
            # Since Lib class doesn't have id_df, we can't support these actions here
            # These will be implemented in Sample and Study wrappers
            raise ValueError(
                f"String action '{entries}' not supported in Lib class. "
                "Use Sample.lib_filter() or Study.lib_filter() instead."
            )
        
        # Handle DataFrame input
        elif hasattr(entries, 'columns'):
            # Check if it's a polars or pandas DataFrame
            if 'lib_uid' in entries.columns:
                # Extract unique lib_uid values
                if hasattr(entries, 'select'):  # Polars
                    lib_uids_to_keep = entries.select('lib_uid').unique().to_series().to_list()
                else:  # Pandas
                    lib_uids_to_keep = entries['lib_uid'].unique().tolist()
            else:
                raise ValueError("DataFrame must contain 'lib_uid' column")
        
        # Handle list input
        elif isinstance(entries, (list, tuple)):
            lib_uids_to_keep = list(entries)
        
        else:
            raise ValueError(
                "entries must be a list of lib_uid values, a DataFrame with 'lib_uid' column, "
                "or a string action ('delete_identified' or 'delete_orphans')"
            )
        
        if not lib_uids_to_keep:
            self.logger.warning("No valid lib_uid values provided to keep.")
            return
        
        # Filter lib_df to keep only specified entries
        self.lib_df = self.lib_df.filter(pl.col("lib_uid").is_in(lib_uids_to_keep))
        
        kept_count = len(self.lib_df)
        deleted_count = original_count - kept_count
        
        # Note: We don't log here since Lib doesn't have a logger by default
        # Logging will be done in Sample/Study wrappers
    
    def __len__(self) -> int:
        """Return number of library entries."""
        return len(self.lib_df) if self.lib_df is not None else 0
    
    def _reload(self):
        """
        Reloads all masster modules to pick up any changes to their source code,
        and updates the instance's class reference to the newly reloaded class version.
        This ensures that the instance uses the latest implementation without restarting the interpreter.
        """
        import importlib
        import sys

        # Get the base module name (masster)
        base_modname = self.__class__.__module__.split(".")[0]
        current_module = self.__class__.__module__

        # Dynamically find all lib submodules
        lib_modules = []
        lib_module_prefix = f"{base_modname}.lib."

        # Get all currently loaded modules that are part of the lib package
        for module_name in sys.modules:
            if module_name.startswith(lib_module_prefix) and module_name != current_module:
                lib_modules.append(module_name)

        # Add core masster modules
        core_modules = [
            f"{base_modname}._version",
            f"{base_modname}.chromatogram",
            f"{base_modname}.spectrum",
            f"{base_modname}.logger",
        ]

        '''# Add study submodules (for cross-dependencies)
        study_modules = []
        study_module_prefix = f"{base_modname}.study."
        for module_name in sys.modules:
            if module_name.startswith(study_module_prefix) and module_name != current_module:
                study_modules.append(module_name)'''

        '''# Add sample submodules (for cross-dependencies)
        sample_modules = []
        sample_module_prefix = f"{base_modname}.sample."
        for module_name in sys.modules:
            if module_name.startswith(sample_module_prefix) and module_name != current_module:
                sample_modules.append(module_name)'''

        all_modules_to_reload = core_modules + lib_modules # sample_modules + study_modules + 

        # Reload all discovered modules
        for full_module_name in all_modules_to_reload:
            try:
                if full_module_name in sys.modules:
                    mod = sys.modules[full_module_name]
                    importlib.reload(mod)
                    # Note: Lib class doesn't have a logger by default, so we just print or use warnings
                    #print(f"Reloaded module: {full_module_name}")
            except Exception as e:
                print(f"Warning: Failed to reload module {full_module_name}: {e}")

        # Finally, reload the current module (lib.py)
        try:
            mod = __import__(current_module, fromlist=[current_module.split(".")[0]])
            importlib.reload(mod)

            # Get the updated class reference from the reloaded module
            new = getattr(mod, self.__class__.__name__)
            # Update the class reference of the instance
            self.__class__ = new

            print("Lib module reload completed")
        except Exception as e:
            print(f"Error: Failed to reload current module {current_module}: {e}")
    
    def __str__(self) -> str:
        """String representation of the library."""
        if self.lib_df is None or len(self.lib_df) == 0:
            return "Empty Lib instance"
        
        unique_compounds = self.lib_df.select("name").unique().height
        unique_adducts = self.lib_df.select("adduct").unique().height
        
        return f"Lib instance with {len(self)} entries ({unique_compounds} unique compounds, {unique_adducts} adduct types)"
