# masster
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/masster)](https://badge.fury.io/py/masster)
[![PyPI version](https://badge.fury.io/py/masster.svg)](https://badge.fury.io/py/masster)

**MASSter** is a Python package for the analysis of metabolomics experiments by LC-MS/MS data, with a main focus on the challenging tasks of untargeted and large-scale studies.  

## Background and motivation

MASSter is actively used, maintained, and developed by the Zamboni Lab at ETH Zurich. The project started because many needs were unmet by the "usual" software packages (mzMine, MS-DIAL, Workflow4Metabolomics (W4M), ...), for example performance, scalability, sensitivity, robustness, speed, rapid implementation of new features, and embedding in ETL systems.

All methods include many parameters and may wrap alternative algorithms. These options are primarily relevant for advanced users. We recommend running the processing methods with the defaults or using the Wizard.

## Content

MASSter is designed to deal with DDA data, and hides functionalities for DIA and ZTScan DIA data. The sample-centric feature detection uses OpenMS, which is both accurate and fast, and it was wrapped with additional code to improve isotope and adduct detection. All other functionalities are own implementations: centroiding, RT alignment, adduct and isotopomer detection, merging of multiple samples, gap-filling, quantification, etc. 

MASSter was engineered to maximize result quality, sensitivity, scalability, and speed. Yes, it's Python, which can be slower than other languages, but considerable effort was spent on optimizations, including the systematic use of [Polars](https://pola.rs/), NumPy vectorization, multiprocessing, and chunking. MASSter has been tested on studies with 3,000+ LC–MS/MS samples (≈1 million MS2 spectra) and autonomously completed analyses within a few hours.

## Architecture

MASSter defines classes for Spectra, Chromatograms, Libraries, Samples, and Studies (a Study is a collection of samples, i.e. an LC–MS sequence). Users will typically work with a single `Study` object at a time. `Sample` objects are created when analyzing a batch (and saved for caching), or used for development, troubleshooting, or generating illustrations.

The analysis can be done in scripts (without user intervention, e.g. by the integrated Wizard), or interactively in notebooks, i.e. [marimo](https://marimo.io/) or [jupyter](https://jupyter.org/).

## Prerequisites

You'll need to install Python (3.10-3.13, 3.14 has not been tested yet).

MASSter reads raw (Thermo), wiff (SCIEX), or mzML data. Reading vendor formats relies on .NET libraries, and is only possible in Windows. On Linux or MacOS, you'll be forced to use mzML data.

**It's recommended to use data in either the vendor's raw formats (WIFF and Thermo RAW) or mzML in profile mode.** MASSter includes a sophisticated and sufficiently fast centroiding algorithm that works well across the full dynamic range and will only act on spectra that are relevant. In our tests with data from different vendors, the centroiding performed much better than most vendor implementations (which are primarily proteomics-centric).

If you still want to convert raw data to centroided mzML, please use CentroidR: https://github.com/Adafede/CentroidR/tree/0.0.0.9001

## Installation

```bash
pip install masster
```

## Getting started
**The quickest way to use, or learn how to use MASSter, is to use the Wizard** which we integrated and, ideally, takes care of everything automatically. 

The Wizard only needs to know where to find the MS files and where to store the results.
```python
from masster import Wizard
wiz = Wizard(
    source=r'..\..\folder_with_raw_data',    # where to find the data
    folder=r'..\..folder_to_store_results',  # where to save the results
    ncores=10                                # this is optional
    )
wiz.test_and_run()
```

This will trigger the analysis of raw data, and the creation of a script to process all samples and then assemble the study. The whole processing will be stored as `1_masster_workflow.py` in the output folder. The wizard will test once and, if successful, run the full workflow using parallel processes. Once the processing is over you, navigate to `folder` to see what happened...

If you want to interact with your data, we recommend using [marimo](https://marimo.io/) or [jupyter](https://jupyter.org/) and open the `*.study5` file, for example:

```bash
# use marimo to open the script created by marimo
marimo edit '..\\..\\folder_to_store_results\\2_interactive_analysis.py'
# or, if you use uv to manage an environment with masster
uv run marimo edit '..\\..\\folder_to_store_results\\2_interactive_analysis.py'
```

### Basic Workflow for analyzing LC-MS study with 1-1000+ samples
In MASSter, the main object for data analysis is a `Study`, which consists of a bunch of `Samples`. 
```python
import masster
# Initialize the Study object with the default folder
study = masster.Study(folder=r'D:\...\mylcms')

# Load data from folder with raw data, here: WIFF
study.add(r'D:\...\...\...\*.wiff')

# Perform retention time correction
study.align(rt_tol=2.0)
study.plot_alignment()
study.plot_rt_correction()
study.plot_bpc()

# Find consensus features
study.merge(min_samples=3)   # this will keep only the features that were found in 3 or more samples
study.plot_consensus_2d()

# retrieve information
study.info()

# Retrieve EICs for quantification
study.fill()

# Integrate EICs according to consensus metadata
study.integrate()

# export results
study.export_mgf()
study.export_mztab()
study.export_excel()
study.export_parquet()
study.export_csv()

# Save the study to .study5
study.save()

# Some of the plots...
study.plot_samples_pca()
study.plot_samples_umap()
study.plot_samples_2d()
study.plot_heatmap()

# load human metabolome (without RT), annotate by MS1
study.lib_load('human')
study.identify()
study.get_id()
# plot features with putative identification
study.plot(show_only_features_with_id=True,
           colorby="has_ms2",
           tooltip="id")

# import lipidoracle results (MS2 annotation)
study.import_oracle('lipidoracle-folder')

# import tima results (MS2 annotation)
study.import_tima('tima-folder')

# To know more about the available methods...
dir(study)
```
The information is stored in Polars data frame, in particular:
```python
# information on samples
study.samples_df
# information on consensus features
study.consensus_df
```

### Analysis of a single sample
For troubleshooting, exploration, or just to create a figure on a single file, you might want to open and process a single file:  
```python
from masster import Sample
sample = Sample(filename='...') # full path to a *.raw, *.wiff, *.mzML, or *.sample5 file
# peek into sample
sample.info()

# process
sample.find_features(chrom_fwhm=0.5, noise=50) # for orbitrap data, set noise to 1e5
sample.find_adducts()
sample.find_ms2()

# access data
sample.features_df

# save results
sample.save() # stores to *.sample5, our custom hdf5 format
sample.export_mgf()
sample.export_csv()

# some plots
sample.plot_bpc()
sample.plot_tic()
sample.plot_2d()
sample.plot_features_stats()

# explore methods
dir(sample)
```



## Disclaimer

**MASSter is research software under active development.** While we use it extensively in our lab and strive for quality and reliability, please be aware:

- **No warranties**: The software is provided "as is" without any warranty of any kind, express or implied
- **Backward compatibility**: We do not guarantee backward compatibility between versions. Breaking changes may occur as we improve the software
- **Performance**: While optimized for our workflows, performance may vary depending on your data and system configuration
- **Results**: We do our best to ensure accuracy, but you should validate results independently for your research
- **Support**: This is an academic project with limited resources. At the moment, we do not provide external user support.
- **Production use**: If you plan to use MASSter in production or critical workflows, thorough testing with your data is recommended

## License
GNU Affero General Public License v3

See the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
This project uses several third-party libraries, including pyOpenMS which is licensed under the BSD 3-Clause License. For complete information about third-party dependencies and their licenses, see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Citation
If you use MASSter in your research, please cite this repository.
