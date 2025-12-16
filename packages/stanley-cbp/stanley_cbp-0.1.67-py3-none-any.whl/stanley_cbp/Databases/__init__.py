"""
Static database files packaged with Stanley.

This directory contains CSV tables used throughout the pipeline, including:
- exoplanet archive samples
- TESS and Kepler cut tables
- false positive catalogs
- Villanova orbital data
- filtering and masking helpers

Files in this directory are accessed via:
    importlib.resources.files("stanley_cbp.Databases")
"""