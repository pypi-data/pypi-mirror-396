# Stanley Pipeline

**Stanley** is a research pipeline for detecting, modeling, and analyzing **eclipsing binaries** and potential **circumbinary planets (CBPs)** in space-based photometric data. It was originally developed for the **Kepler** CBP sample and has since been extended to large-scale searches in **TESS** light curves. In circumbinary systems, planetary transits do **not** occur at regular intervals and transit durations vary significantly due to the orbital motion of both stars around the barycenter. As a result, conventional single-star transit search algorithms perform poorly. **Stanley** implements methods specifically optimized for the **variable-timing and variable-duration** transit signatures unique to circumbinary planets.

## Core Capabilities
### Detrending
- Iterative cosine (COFIAM-like) filtering
- TESS-specific quadratic baseline removal
- Variable-duration biweight filters
- Outlier / flare / kink removal
- Optional ellipsoidal and reflection trend modeling

### Binary Modeling & Validation
- Robust eclipse identification
- Multi-stage BLS period and harmonic validation
- Extraction of binary parameters (P, e, omega, eclipse depths and widths)

### Secondary Eclipse Vetting
- Geometric feasibility tests
- Inclination / eccentricity constraints

### Transit Timing Variation Search
- N-body forward modeling via **REBOUND**
- Variable-duration transit stacking matched to dynamically predicted timing signatures

### Scalable Execution
- Fully HPC-compatible (SLURM)
- Each module (detrending, search, analysis) may run independently or as a unified pipeline
- Interpolative potential for less computational load

## Scientific Context
Stanley was first validated on the **Kepler** circumbinary-planet sample, where it successfully recovered all known CBPs including **Kepler-47 b/c/d**, searched for additional planets using variable-duration stacked transit detection, and demonstrated sensitivity to planets smaller than roughly three Earth radii in about half the systems. The current version extends the pipeline to **TESS**, enabling large-scale searches of low-mass eclipsing binaries and supporting **demographic studies** of small circumbinary planets.

## Repository Structure and Data Requirements

This repository contains only the core **source code** (`stanley_cbp/`). All static catalogs needed at runtime are packaged inside:

    stanley_cbp/Databases/

For standard local or Jupyter-based usage, users do not need to download any external data or set any environment variables.

Instead, when running the pipeline (typically from the `Tutorials/` folder), Stanley automatically creates and manages a local runtime workspace containing:

- LightCurves/
- PlanetSearchOutput/
- UserGeneratedData/

This workspace is created relative to the working directory and requires no manual configuration.

## Runtime workspace (HPC / cluster use)
For large-scale or cluster-based runs, users may optionally define a runtime workspace via an environment variable:

`export STANLEY_RUN_ROOT="/path/to/your/STANLEY/Runs"`

When `STANLEY_RUN_ROOT` is set, all runtime products (light curves, diagnostics, and search outputs) are written under this directory instead of the local working directory. This is recommended for HPC environments where scratch space, quotas, or shared filesystems are involved.

If `STANLEY_RUN_ROOT` is not set, STANLEY falls back to the default local behavior described above.

## Installation
Install from PyPI: pip install stanley_cbp

Or install from a locally built wheel: pip install dist/stanley_cbp-0.1.X-py3-none-any.whl

## Environment setup (recommended)

For reproducible installations, this repository provides two Conda environment files:

`environment.yml` — for local machines and Jupyter-based workflows

`clusterEnvironment.yml` — for HPC or cluster environments

Users can create and activate an environment using either file, for example:

`conda env create -f environment.yml`
`conda activate stanley_env`

or, for cluster usage:

`conda env create -f clusterEnvironment.yml`
`conda activate stanley_env`

Once the environment is active, install STANLEY using one of the methods above.

## Using Stanley in Python

Example workflow:

**Import:**  
from stanley_cbp import runDetrendingModule, Stanley_FindPlanets, runAnalysisModule

**Detrending example:**  
`result_det = runDetrendingModule(SystemName="TIC260128333", DetrendingName="DemoDetrend", UseSavedData=0)`

**Search example:**  
`Stanley_FindPlanets(SearchName="DemoSearch", SystemName="TIC260128333", DetrendingName="DemoDetrend", totalSectors=1, currentSector=1)`

**Analysis example:**  
`analysis_out = runAnalysisModule(searchName="DemoSearch", systemName="TIC260128333", totalSectors=1)`

## Tutorials

A `Tutorials/` directory is provided with example Jupyter notebooks.  
These notebooks assume:

- a local **stanley_cbp** installation,  
- that the directory where the notebook is run will automatically function as the runtime workspace,  
- and that Stanley will generate all required folders (`LightCurves/`, `PlanetSearchOutput/`, `UserGeneratedData/`) as needed.

The tutorials demonstrate detrending, running the CBP search, interpreting outputs, and generating diagnostic figures.

## Licensing

This package is released under the **MIT License**.
