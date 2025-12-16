import numpy as np
from scipy.signal import argrelextrema
import sys, os, io, rebound, csv, math, warnings
from astropy.table import Table
import astropy.units as u
from astropy.time import Time
import pandas as pd

# >>> NEW: headless backend for cluster
import matplotlib
matplotlib.use("Agg")

import lightkurve as lk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages   # >>> NEW
from collections import namedtuple
from astroquery.mast import Catalogs

# PACKAGE / REPO DUAL-MODE INTERNAL IMPORTS
try:
    # package mode: stanley_cbp.Stanley_TransitTiming, stanley_cbp.Stanley_Constants
    from . import Stanley_TransitTiming as SSTT
    from .Stanley_Constants import *
except ImportError:
    # flat repo mode: direct imports
    import Stanley_TransitTiming as SSTT
    from Stanley_Constants import *

import wotan
import itertools
from astropy.timeseries import BoxLeastSquares
from typing import Optional, Literal
import scipy.optimize as so
from scipy.optimize import root_scalar, curve_fit
from scipy.signal import find_peaks
import numbers
from astropy.timeseries import LombScargle
import time as TIME
from multiprocessing import Pool, cpu_count
import batman
from PyAstronomy.modelSuite import forTrans as ft
from ldtk import LDPSetCreator, BoxcarFilter, TabulatedFilter
from ldtk.filters import sdss_i, kepler
from pathlib import Path
from typing import Optional, Dict, List
import re

# >>> NEW: for diagnostics helpers
import json
import textwrap
import os
from importlib import resources


def _resolve_base_dir(base_dir=None) -> Path:
    """
    Resolve the *workspace root* used for user-generated products.

    Priority:
      1) explicit base_dir arg
      2) STANLEY_WORKDIR (new), or STANLEY_CBP_BASE_DIR / STANLEY_BASE_DIR (backwards compat)
      3) current working directory (Jupyter / local scripts)
    """
    if base_dir:
        return Path(base_dir).expanduser().resolve()

    # New preferred env var, plus backwards-compatible ones
    env = (
        os.getenv("STANLEY_WORKDIR")
        or os.getenv("STANLEY_CBP_BASE_DIR")
        or os.getenv("STANLEY_BASE_DIR")
    )
    if env:
        return Path(env).expanduser().resolve()

    # Default: wherever the user is running from
    return Path.cwd().resolve()


def base_dir() -> Path:
    """
    Workspace root where LightCurves, PlanetSearchOutput,
    UserGeneratedData, DiagnosticReports, etc. live.

    - In notebooks: the notebook directory (cwd).
    - On cluster: whatever the SLURM script sets via STANLEY_WORKDIR.
    """
    return _resolve_base_dir(None)


def p_outputs(search_name: str, *parts) -> Path:
    """
    Planet search output directory for a given search_name.
    """
    return base_dir() / "PlanetSearchOutput" / search_name / Path(*parts)


def p_lightcurves(*parts) -> Path:
    """
    Root for LightCurves products under the workspace.
    """
    return base_dir() / "LightCurves" / Path(*parts)


def p_processed(det_name: str, *parts) -> Path:
    """
    Processed light curve products grouped by detrending name.
    """
    return p_lightcurves("Processed", det_name, *parts)


def p_user_data(*parts, debug=False) -> Path:
    """
    Store user-generated files (manual cuts, injections, etc.)
    at <workspace_root>/UserGeneratedData, where workspace_root
    is given by _resolve_base_dir(None).
    """

    # Guaranteed-correct workspace root
    root = Path(_resolve_base_dir(None)).resolve()

    # UserGeneratedData lives directly under that root
    user_dir = root / "UserGeneratedData"
    user_dir.mkdir(parents=True, exist_ok=True)

    # Resolve final path
    full_path = user_dir / Path(*parts) if parts else user_dir

    # Optional debug printing
    if debug:
        print(f"[p_user_data] workspace root: {root}")
        print(f"[p_user_data] user_dir:      {user_dir}")
        print(f"[p_user_data] full_path:     {full_path}")

    return full_path



# Packaged databases
def p_databases(*parts) -> Path:
    """
    Return a path to a file inside the packaged Databases directory.

    Works when:
    - stanley_cbp is installed via pip (Databases shipped inside the wheel)
    - running from a source checkout (fallback to source-tree layout)
    """
    relative = Path(*parts)

    # 1. Try to load packaged data (site-packages / wheel)
    try:
        db_root = resources.files("stanley_cbp.Databases")
        return Path(db_root) / relative
    except Exception:
        pass

    # 2. Fallback: user is running from a source tree with Databases
    #    alongside this module inside the package.
    pkg_root = Path(__file__).resolve().parent  # e.g. stanley_cbp/
    return pkg_root / "Databases" / relative


def _ensure_parent(path: Path):
    """
    Ensure that the parent directory exists.
    Does not create the file itself.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

def GetID(SystemName):
	'''
	Functionality:
		Parse an input system name to determine the mission prefix (KIC/TIC) and the numeric identifier,
		then resolve the numeric ID via the appropriate catalog lookup function.
	Arguments:
		SystemName (str): Input string such as 'KIC8561063', 'TIC 123456789', or just '8561063'.
	Returns:
		tuple: (ID (str), mission (str)) where ID is the resolved numeric identifier as a string and
		       mission is either 'KIC' or 'TIC'.
	'''
	# Split SystemName into TIC & Number or KIC & Number
	
	# Check if the first 3 chars are alphabetic (anticipates 'KIC' or 'TIC')
	first_chars_of_SystemName = SystemName[0:3]
	if first_chars_of_SystemName.isalpha():  # Check for alphabet (a-z or A-Z)
		# Either it's TIC___ or KIC___
		mission = first_chars_of_SystemName
		number = SystemName[3:]  # Shave off TIC or KIC (first 3 characters)
		number = number.replace(" ", "")  # Remove any embedded spaces
	else:
		# If no alphabetic prefix, assume Kepler (KIC) by default
		mission = 'KIC'
		number = SystemName  # No characters at the front to shave off
		
	# Pass the number to the correct resolver
	if mission == 'TIC':
		ID = GetTIC(number)
	elif mission == "KIC":
		ID = GetKIC(number)
	else:
		# Defensive check; should not hit for expected inputs
		raise Exception("Mission not KIC or TIC")

	return ID, mission


# Inputs the number of the KIC and grabs the whole system
def GetKIC(ID):
	'''
	Functionality:
		Validate or resolve a Kepler Input Catalog (KIC) identifier. If the provided ID is not numeric,
		query MAST TIC to find a corresponding KIC within a 5 arcsec radius.
	Arguments:
		ID (str): String that is either a numeric KIC or a target name resolvable by MAST.
	Returns:
		str: A KIC identifier (numeric as a string). Returns a sentinel '99999999999' if unresolved.
	'''
	if ID.isnumeric() == True:
		# Already numeric: assume this is a valid KIC
		KIC = ID
	else:
		print('Need to look up KIC for ' + ID)
		# Use a MAST lookup. This queries the TESS Input Catalog (TIC) but may include KIC cross-matches.
		catalogTIC = Catalogs.query_object(ID, radius=5/60/60, catalog="TIC")  # Search radius is 5 arcsec
		catalogTIC.sort('dstArcSec')  # Sort so that the closest match is first
	
		target_data = catalogTIC[0]  # Choose the top (closest) value
	
		# Try to get the KIC from the returned row
		if (type(target_data['KIC']) == np.ma.core.MaskedConstant):
			# No KIC present => likely not observed by Kepler
			print('Could not find a KIC for ' + ID)
			KIC = '99999999999'  # Sentinel value; downstream will fail cleanly if used
		else:
			KIC = target_data['KIC']
			print('Found KIC = ' + KIC)
			
	return KIC


def GetTIC(ID):
	'''
	Functionality:
		Validate or resolve a TESS Input Catalog (TIC) identifier. If the provided ID is not numeric,
		query MAST TIC to find a corresponding TIC within a 5 arcsec radius.
	Arguments:
		ID (str): String that is either a numeric TIC or a target name resolvable by MAST.
	Returns:
		str: A TIC identifier (numeric as a string). Returns a sentinel '99999999999' if unresolved.
	'''
	if ID.isnumeric() == True:
		# Already numeric: assume this is a valid TIC
		TIC = ID
	else:
		print('Need to look up TIC for ' + ID)
		# Use a MAST lookup of the TIC
		catalogTIC = Catalogs.query_object(ID, radius=5/60/60, catalog="TIC")  # Search radius is 5 arcsec
		catalogTIC.sort('dstArcSec')  # Sort so that the closest match is first
	
		target_data = catalogTIC[0]  # Choose the closest match
	
		# Try to get the TIC from the returned row
		if (type(target_data['TIC']) == np.ma.core.MaskedConstant):
			# No TIC present => cannot proceed with TESS identifiers
			print('Could not find a TIC for ' + ID)
			TIC = '99999999999'  # Sentinel to trigger downstream handling
		else:
			TIC = target_data['TIC']
			print('Found TIC = ' + TIC)
			
	return TIC


def CreateReboundSim(Pbin,ecc,omega,mA,mB,RA,RB,bjd0,startTime):
	'''
	Functionality:
		Create a REBOUND two-body binary-star simulation and advance it so that the simulation time aligns
		with the requested start time relative to a provided reference epoch (bjd0).
	Arguments:
		Pbin (float): Binary period in seconds.
		ecc (float): Orbital eccentricity of the secondary relative to the primary.
		omega (float): Argument of periapse (radians) of the secondary's orbit.
		mA (float): Mass of primary star in kilograms.
		mB (float): Mass of secondary star in kilograms.
		RA (float): Radius of primary star in meters.
		RB (float): Radius of secondary star in meters.
		bjd0 (float): Reference epoch (in seconds; consistent with Pbin units) to align to.
		startTime (float): Target simulation time (seconds) at which to start output/analysis.
	Returns:
		rebound.Simulation: Initialized and time-aligned REBOUND simulation object.
	'''
	# Now create the rebound simulation file; for now, this only has a binary
	sim = rebound.Simulation()
	sim.units = ('s','m','kg')  # Ensure SI units throughout
	
	# Convert mass and period to semi-major axis (if needed elsewhere)
	# a = PeriodToSemiMajorAxis(mass, Pbin)  # Example placeholder, not used here

	# Start the binary with theta = +90 deg, corresponding to a primary eclipse configuration.
	# To align with the data time series (which likely does not start at exactly a primary eclipse),
	# we integrate forward/back from bjd0 so the simulation time equals startTime.
	# Alternatively, one could solve Kepler's equation to set phases directly.

	# Add primary
	sim.add(m=mA, r=RA)
	# Add secondary with orbital elements relative to primary
	sim.add(m=mB, r=RB, P=Pbin, e=ecc, inc=np.radians(0.), omega=omega, Omega=np.radians(0.), theta=np.radians(90.))
	
	# Move to the barycentric center-of-mass frame
	sim.move_to_com()

	# Advance simulation so that bjd0 maps to startTime
	sim.integrate(startTime - bjd0)
	# Set the current simulation time to startTime explicitly
	sim.t = startTime

	return sim


def LoadData(mission,ID,DetrendingName, remove_eclipses = True, use_saved_data = False):
	'''
	Functionality:
		Dispatch data-loading based on mission ('TIC' or 'KIC'), returning light curves and parameters.
	Arguments:
		mission (str): 'TIC' for TESS or 'KIC' for Kepler.
		ID (str): Target identifier string (numeric or name-resolvable).
		DetrendingName (str): Label used for saving processed outputs.
		remove_eclipses (bool, optional): If True, create an eclipse-masked light curve. Default True.
		use_saved_data (bool, optional): If True, load previously saved CSV instead of downloading. Default False.
	Returns:
		Depends on mission loader:
		  For KIC: (sim, timeOrig, fluxOrig, timeCut, fluxCut, orbit_params, stellar_params, sector_times)
	'''
	if mission == "TIC":
		# Route to TIC loader (not shown in this snippet)
		return LoadDataTIC(mission,ID,DetrendingName, remove_eclipses, use_saved_data)
	elif mission == "KIC":
		# Route to KIC loader (defined below)
		return LoadDataKIC(mission,ID,DetrendingName,remove_eclipses,use_saved_data)
	else:
		# Defensive: only KIC/TIC supported
		raise Exception(f"Mission {mission} not supported (not KIC or TIC)")
		


def LoadDataKIC(mission, ID, DetrendingName, remove_eclipses=True, use_saved_data=False):
    '''
    Functionality:
        Load and prepare Kepler (KIC) light curve data and system parameters. Attempts to:
          1) Read orbital parameters from the Villanova EB catalog,
          2) Read stellar parameters from Windemuth (2019),
          3) Download or load the Kepler light curve via lightkurve,
          4) Optionally remove eclipses,
          5) Initialize a REBOUND simulation aligned to the light curve start time,
          6) Save starting binary parameters to disk.
    Arguments:
        mission (str): Mission identifier, expected to be 'KIC' here.
        ID (str): KIC target identifier (numeric string).
        DetrendingName (str): Label for output/processed directory naming.
        remove_eclipses (bool, optional): If True, return eclipse-masked light curve. Default True.
        use_saved_data (bool, optional): If True, read cached CSV from ../LightCurves/Raw/. Default False.
    Returns:
        tuple: (sim, timeOrig, fluxOrig, timeCut, fluxCut, orbit_params, stellar_params, sector_times)
               sim (rebound.Simulation): Initialized binary simulation.
               timeOrig (np.ndarray): Original time array (seconds; shifted and converted).
               fluxOrig (np.ndarray): Normalized flux array.
               timeCut (np.ndarray): Time array with eclipses removed (if requested).
               fluxCut (np.ndarray): Flux array with eclipses removed (if requested).
               orbit_params (dict): Derived/loaded orbital parameters.
               stellar_params (dict): Derived/loaded stellar parameters incl. median_flux_err.
               sector_times: None for Kepler (placeholder to align with TESS interface).
    '''
    # In this function we load in light curve based on its target name.
    # We will return two versions of the light curve: one being the original and the other with the eclipses cut.
    # This function will also return some key characteristics of the binary, such as its period.

    # mission is TIC or KIC
    # ID is the TIC or KIC ID number

    # There are two types of data needed: orbital data and stellar data. 
    # The orbital data is essential. The stellar data can be guessed/made up if necessary.
    # The orbital data comes from Villanova, whereas the stellar data comes from Windemuth

    orbit_data_found = False
    stellar_data_found = False

    # Load in the orbit parameters from the Villanova Kepler Eclipsing Binary Catalog
    # http://keplerebs.villanova.edu/
    orbit_data_path = p_databases("villanova_orbit_data_kepler.csv")
    orbit_data = np.genfromtxt(orbit_data_path, comments="#", delimiter=",", unpack=False)

    print('Searching for orbit data in Villanova catalog')
    # Search rows for this KIC
    for ii in range(0, len(orbit_data)):
        if (orbit_data[ii][0] == float(ID)):
            orbit_data_found = True
            print('Orbit data found from Villanova catalog')
            Pbin = orbit_data[ii][1] * days2sec  # Convert days->seconds
            bjd0 = orbit_data[ii][2] * days2sec  # Convert days->seconds
            pdepth = orbit_data[ii][3]
            sdepth = orbit_data[ii][4]
            pwidth = orbit_data[ii][5]
            swidth = orbit_data[ii][6]
            sep = orbit_data[ii][7]

            # Determine eccentricity and omega if a secondary eclipse is present
            if (swidth == -1):
                # No secondary, assume circular
                print('No secondary eclipse found, assuming a circular orbit')
                ecc = 0
                omega = 0
            else:
                # There is a secondary; estimate e and ω from eclipse separation/widths
                print('Secondary eclipse found, calculating eccentricity and omega')
                ecosw = np.pi / 2. * (sep - 1. / 2.)  # Approximation from eclipse separation
                esinw = (swidth - pwidth) / (swidth + pwidth)  # Approximation from width asymmetry
                ecc = (ecosw ** 2. + esinw ** 2.) ** 0.5
                omega = np.arctan2(esinw, ecosw)  # Radians

            # Collect orbit parameters for downstream use
            orbit_params = {
                "Pbin": Pbin,
                "bjd0": bjd0,
                "pdepth": pdepth,
                "sdepth": sdepth,
                "pwidth": pwidth,
                "swidth": swidth,
                "sep": sep,
                "e": ecc,
                "omega": omega
            }

    if (orbit_data_found == False):
        # If no orbit data, we cannot proceed reliably
        print('No orbit data found, cannot proceed')
    else:
        # Attempt to load stellar data
        print('Searching for stellar data in Windemuth catalog')
        stellar_data_path = p_databases("windemuth_stellar_data.csv")
        stellar_data = np.genfromtxt(stellar_data_path, comments="#", delimiter=" ", unpack=False)

        # Find the right star by ID
        for ii in range(0, len(stellar_data)):
            if (int(ID) == int(stellar_data[ii][0])):
                stellar_data_found = True
                # Assign stellar parameters (converted to SI using constants)
                mA = stellar_data[ii][7] * mSun_kg
                mB = stellar_data[ii][10] * mSun_kg
                RA = stellar_data[ii][13] * rSun_m
                RB = stellar_data[ii][16] * rSun_m
                metallicity = stellar_data[ii][1]
                flux_ratio = stellar_data[ii][19]

                print('Stellar data found in Windemuth catalog')

        # If no stellar data, set reasonable defaults and approximate flux ratio
        if (stellar_data_found == False):
            print('No stellar data found in Windemuth catalog. Setting default values')
            mA = 1 * mSun_kg
            mB = 0.5 * mSun_kg
            RA = 1 * rSun_m
            RB = 0.5 * rSun_m
            metallicity = 0
            flux_ratio = MassRadiusLuminosityRelation(mB, RB) / MassRadiusLuminosityRelation(mA, RA)

        # Construct the stellar_params dictionary (moved here to ensure variables are defined)
        stellar_params = {
            "mA": mA,
            "mB": mB,
            "rA": RA,
            "rB": RB,
            "met": metallicity,
            "frat": flux_ratio,
            "median_flux_err": -27,  # Placeholder; updated after loading light curve
        }

        # Prepare file path for cached raw data
        #check if Raw exists within the LightCurves folder
        _root = _resolve_base_dir(None)
        _out_root = _root / "LightCurves"
        raw_folder = _out_root / "Raw"
        os.makedirs(raw_folder, exist_ok=True)
        raw_filename = raw_folder / (ID + '_raw.csv')

        if (use_saved_data == True):
            # Load cached CSV if available
            if (os.path.exists(raw_filename) == True):
                saved_data = np.transpose(np.genfromtxt(raw_filename))
                timeOrig = saved_data[0]
                fluxOrig = saved_data[1]
                fluxErrOrig = saved_data[2]
                print('Loaded saved data for ' + ID)
            else:
                # Fall back to download path
                print('Tried to use saved data for ' + ID + ' but could not find it. Downloading from Lightkurve')
                use_saved_data = False

        if (use_saved_data == False):
            # Download from lightkurve
            print('Downloading data from lightkurve')

            # Query and download Kepler PDCSAP light curves, then stitch them
            search_result = lk.search_lightcurve('KIC ' + ID, mission='Kepler', cadence='long')
            lc_collection = search_result.download_all(quality_bitmask='hard')
            data_lightkurve = lc_collection.stitch()

            # Extract arrays (LightCurve.SAP_FLUX is deprecated after lightkurve 2.0)
            timeOrig = data_lightkurve['time'].value
            fluxOrig = data_lightkurve['pdcsap_flux'].value
            fluxErrOrig = data_lightkurve['pdcsap_flux_err'].value

            # Ensure numpy arrays
            timeOrig = np.array(timeOrig)
            fluxOrig = np.array(fluxOrig)
            fluxErrOrig = np.array(fluxErrOrig)

            # --- Remove NaNs, following original LoadData() behavior ---

            # 1) Drop rows where flux is NaN (time & flux together)
            good_flux = ~np.isnan(fluxOrig)
            timeOrig = timeOrig[good_flux]
            fluxOrig = fluxOrig[good_flux]

            # 2) Drop rows where fluxErr is NaN

            #    (in the original code this only affected fluxErr; we keep that logic)
            good_err = ~np.isnan(fluxErrOrig)
            fluxErrOrig = fluxErrOrig[good_err]

            # Optional sanity check; won't crash, just warns if something weird happens
            if not (len(timeOrig) == len(fluxOrig) == len(fluxErrOrig)):
                print(f"[WARN KIC {ID}] lengths differ after NaN removal: "
                      f"time={len(timeOrig)}, flux={len(fluxOrig)}, fluxErr={len(fluxErrOrig)}")

            # Normalize flux and errors (median=1)
            fluxErrOrig = fluxErrOrig / np.median(fluxOrig)
            fluxOrig = fluxOrig / np.median(fluxOrig)

            # Cache to CSV for future use
            np.savetxt(raw_filename, np.transpose([timeOrig, fluxOrig, fluxErrOrig]))

        # Calculate and record the median flux error
        median_flux_err = np.median(fluxErrOrig)
        stellar_params['median_flux_err'] = median_flux_err

        # Shift Kepler time system (to ~BJD-2450000) and convert to seconds
        timeOrig += 54833  # Puts the time in -55000 format.
        timeOrig *= days2sec  # Convert days -> seconds

        # Optionally remove eclipses from the light curve for certain analyses
        if remove_eclipses:  # KIC via unified RemoveEclipses
            timeCut, fluxCut, _ = RemoveEclipses(
                timeOrig=timeOrig,
                fluxOrig=fluxOrig,
                period=Pbin,
                bjd0=bjd0,
                prim_pos=0.0,
                sec_pos=sep,
                pwidth=pwidth,
                swidth=swidth,
                sep=sep,
                cuts="both",
                phase_folded="n",
            )
        else:
            timeCut, fluxCut = timeOrig, fluxOrig

        # Save phase plots (ORIGINAL + ECLIPSES REMOVED) for KIC run
        base = _resolve_base_dir(None)
        my_folder = base / 'LightCurves' / 'Figures' / DetrendingName
        my_folder.mkdir(parents=True, exist_ok=True)

        # 1) Original data, phase-folded
        try:
            fig, ax = plt.subplots(figsize=(10, 5))
            phase_orig = ((timeOrig - bjd0) / Pbin) % 1.0
            sc = ax.scatter(phase_orig, fluxOrig, s=3, marker=".", c=timeOrig)
            ax.set_xlabel("Phase of Binary (0 to 1)")
            ax.set_ylabel("Normalized (but not detrended) Flux")
            ax.set_title("Original Data")
            save_path_orig = my_folder / f"{mission}_{ID}_phase_folded_original_data.png"
            fig.savefig(os.path.abspath(save_path_orig), bbox_inches="tight", dpi=300)
            print(f"[saved] {os.path.abspath(save_path_orig)}")
            plt.close(fig)
        except Exception as e:
            print(f"[ERROR saving original phase plot for {mission} {ID}]: {e}")

        # 2) Eclipses removed, phase-folded (only if we actually removed them)
        if remove_eclipses and len(timeCut) > 0:
            try:
                fig2, ax2 = plt.subplots(figsize=(10, 5))
                phase_cut = ((timeCut - bjd0) / Pbin) % 1.0
                sc2 = ax2.scatter(phase_cut, fluxCut, s=3, marker=".", c=timeCut)
                ax2.set_xlabel("Phase of Binary (0 to 1)")
                ax2.set_ylabel("Normalized (but not detrended) Flux")
                ax2.set_title("Eclipses Removed")
                save_path_cut = my_folder / f"{mission}_{ID}_phase_folded_eclipses_removed.png"
                fig2.savefig(os.path.abspath(save_path_cut), bbox_inches="tight", dpi=300)
                print(f"[saved] {os.path.abspath(save_path_cut)}")
                plt.close(fig2)
            except Exception as e:
                print(f"[ERROR saving eclipses-removed phase plot for {mission} {ID}]: {e}")

        # Create the REBOUND simulation aligned with light curve start time
        sim = CreateReboundSim(Pbin, ecc, omega, mA, mB, RA, RB, bjd0, timeOrig[0])

        # Read starting orbital elements at the first data point
        # Simulation().calculate_orbit() is deprecated in Rebound v4; use sim.orbits()
        orbits = sim.orbits()
        theta_init = orbits[0].theta
        omega_init = orbits[0].omega
        P_init = orbits[0].P
        ecc_init = orbits[0].e

        # Persist starting params and timing diagnostics
        _root = _resolve_base_dir(None)
        folder_name = _root / "LightCurves" / "Processed" / str(DetrendingName)
        folder_name.mkdir(parents=True, exist_ok=True)

        # Build output path using Path operations
        binary_path = (
            folder_name /
            f"{mission}_{ID}_{DetrendingName}_binaryStartingParams.csv"
        )

        # Save a CSV with starting binary parameters for later modules
        with open(binary_path, "w") as binaryParamsFile:
            binaryParamsFile.write("mA (mSun)," + str(mA / mSun_kg) + "\n")
            binaryParamsFile.write("mB (mSun)," + str(mB / mSun_kg) + "\n")
            binaryParamsFile.write("RA (RSun)," + str(RA / rSun_m) + "\n")
            binaryParamsFile.write("RB (RSun)," + str(RB / rSun_m) + "\n")
            binaryParamsFile.write("bjd0 (Days - 2550000)," + str(bjd0 / days2sec - 55000) + "\n")
            binaryParamsFile.write("theta (deg)," + str(np.degrees(theta_init)) + "\n")
            binaryParamsFile.write("Pbin (days)," + str(P_init / days2sec) + "\n")
            binaryParamsFile.write("ecc," + str(ecc_init) + "\n")
            binaryParamsFile.write("omega (deg)," + str(np.degrees(omega_init)) + "\n")
            binaryParamsFile.close()

        # Kepler doesn't have sectors; keep API compatible with TESS loader
        sector_times = None

        return sim, timeOrig, fluxOrig, timeCut, fluxCut, orbit_params, stellar_params, sector_times


def LoadDataTIC(
    mission,
    ID,
    DetrendingName,
    remove_eclipses=True,
    use_saved_data=False,
    use_manual_cuts=True,
    interactive_cuts=False,
    cuts_csv=None,
):
    """
    Functionality:
        Load, flatten, normalize, and harmonize a TESS light curve; then validate the binary
        period and prepare downstream products (eclipse modeling, parameter persistence, and
        a REBOUND simulation). Pulls orbital/stellar metadata from ANTIC/Villanova where available,
        fills gaps with calculated estimates, and writes useful diagnostics/figures to disk.

    Arguments:
        mission (str): Mission identifier; expected "TIC" for this loader.
        ID (str or int): TIC identifier (numeric string or int).
        DetrendingName (str): Label used for output directories and saved artifacts.
        remove_eclipses (bool, optional): If True, produce an eclipses-removed light curve for plots.
        use_saved_data (bool, optional): If True and cached raw CSV exists, load from it instead of downloading.
        use_manual_cuts (bool, optional): If True, attempt to apply pre-recorded manual cuts
            from a cuts CSV.
        interactive_cuts (bool, optional): If True, launch the interactive manualCuts tool to
            define or update cuts before proceeding.
        cuts_csv (str or pathlib.Path or None, optional): Path to the cuts CSV. If None, both
            manualCuts and apply_manual_cuts default to UserGeneratedData/manual_cuts_TESS.csv.

    Returns:
        tuple:
            sim (rebound.Simulation): Initialized REBOUND simulation aligned to the light curve start time.
            timeOrigCopy (np.ndarray): Original time array (seconds) after manual cuts (copy kept for plotting/persistence).
            fluxOrigCopy (np.ndarray): Original normalized flux after manual cuts (copy kept for plotting/persistence).
            timeCut (np.ndarray): Time array with eclipses removed (from modelEclipse3).
            fluxCut (np.ndarray): Flux array with eclipses removed (from modelEclipse3).
            orbit_params (dict): Final orbital parameters (Pbin, bjd0, depths, widths, eclipse positions, sep, e, omega).
            stellar_params (dict): Stellar parameters (mA, mB, rA, rB, metallicity proxy, flux ratio, median flux err placeholder).
            sector_times (np.ndarray): Nx2 array of sector start/end times in seconds (or single span if cached path used).
    """

    # Helpers
    def _as_1d(a, dtype=float):
        """
        Convert input to a contiguous 1D NumPy array of the requested dtype.
        """
        return np.asarray(a, dtype=dtype).reshape(-1)

    # Track runtime for simple timing persistence
    start_time = TIME.time()

    # Path for cached raw light curve (TESS)
    _root = _resolve_base_dir(None)
    _out_root = _root / "LightCurves"
    raw_folder = _out_root / "Raw"
    os.makedirs(raw_folder, exist_ok=True)
    raw_filename = raw_folder / (str(ID) + "_raw.csv")

    # Load or download data
    lc_collection = None  # will hold sector-wise light curves if downloaded
    if use_saved_data and os.path.exists(raw_filename):
        # Load previously cached (already normalized) arrays
        saved_data = np.transpose(np.genfromtxt(raw_filename))
        timeOrig = np.array(saved_data[0], float)
        fluxOrig = np.array(saved_data[1], float)
        fluxErrOrig = np.array(saved_data[2], float)
        print(f"Loaded saved data for {mission} {ID}")
    else:
        # If asked to use cache but missing, fall back to download
        if use_saved_data:
            print(f"Tried to use saved data for {mission} {ID} but could not find it. Downloading from Lightkurve")

        print("Downloading data from lightkurve")
        # Query SPOC short-cadence products for TESS
        sr = lk.search_lightcurve(f"TIC {ID}", mission="TESS", author="SPOC", exptime="short")
        if len(sr) == 0:
            # No matching products found
            raise RuntimeError(f"No SPOC short cadence light curves found for TIC {ID}")

        # Download all matching sectors with a conservative bitmask
        lc_collection = sr.download_all(quality_bitmask="hard")
        print(f"Total number of sectors downloaded: {len(lc_collection)}")

        # Collect sector start/end times in seconds for reference
        sector_times = []
        for lc in lc_collection:
            sector_times.append([
                float(lc.time.value[0]) * days2sec,
                float(lc.time.value[-1]) * days2sec,
            ])
        sector_times = np.asarray(sector_times, float)

        # Stitch all sectors into a single LightCurve object
        data_lightkurve = lc_collection.stitch()

        # Extract time (days) and SAP flux/uncertainties
        timeOrig = np.array(data_lightkurve["time"].value, float)         # days
        fluxOrig = np.array(data_lightkurve["sap_flux"].value, float)
        fluxErrOrig = np.array(data_lightkurve["sap_flux_err"].value, float)

        # Keep only finite rows to avoid NaN propagation
        finite = np.isfinite(timeOrig) & np.isfinite(fluxOrig) & np.isfinite(fluxErrOrig)
        timeOrig, fluxOrig, fluxErrOrig = timeOrig[finite], fluxOrig[finite], fluxErrOrig[finite]

        # Normalize SAP by median to unity; protect against 0/NaN medians
        med_flux = float(np.nanmedian(fluxOrig))
        if not np.isfinite(med_flux) or med_flux == 0:
            med_flux = 1.0
        fluxErrOrig = fluxErrOrig / med_flux
        fluxOrig = fluxOrig / med_flux

        # Convert days -> seconds
        timeOrig *= days2sec

        # Persist a simple cache for faster future loads
        np.savetxt(raw_filename, np.transpose([timeOrig, fluxOrig, fluxErrOrig]))
        print(f"[saved raw] {os.path.abspath(raw_filename)}")

    # If we loaded from cache, approximate a single-span "sector_times" covering the data
    if "sector_times" not in locals():
        sector_times = np.array([[timeOrig.min(), timeOrig.max()]], float)

    # Keep a representative median flux uncertainty for dict outputs
    median_flux_err = float(np.nanmedian(fluxErrOrig))

    # Manual cuts: interactive or non-interactive, controlled by flags
    if use_manual_cuts:
        if interactive_cuts:
            print("Running interactive manualCuts to define or update cuts...")
            timeOrig, fluxOrig, fluxErrOrig = manualCuts(
                timeOrig,
                fluxOrig,
                fluxErrOrig,
                ID,
                days2sec=days2sec,
                cuts_csv=cuts_csv,
            )
        else:
            # Non-interactive: apply any pre-recorded cuts if the CSV and ID entry exist
            timeOrig, fluxOrig, fluxErrOrig = apply_manual_cuts(
                timeOrig,
                fluxOrig,
                fluxErrOrig,
                ID,
                cuts_csv=cuts_csv,
                days2sec=days2sec,
            )
    else:
        print("Skipping manual cuts (use_manual_cuts=False).")

    # Preserve copies for later plotting/persistence (original sampling)
    timeOrigCopy, fluxOrigCopy, fluxErrOrigCopy = np.copy(timeOrig), np.copy(fluxOrig), np.copy(fluxErrOrig)

    # Sort & chunk (by gaps)
    sortedTime, sortedFlux, sortedFluxErr = sorting(timeOrig, fluxOrig, fluxErrOrig)

    # chunk_by_gaps expects time in days; convert a copy for gap detection
    time_days_for_chunk = sortedTime / days2sec
    # gap threshold of 1 day for sector-edge/large-gap segmentation
    time_chunks, flux_chunks = chunk_by_gaps(time_days_for_chunk, sortedFlux, 1.0)
    _, fluxErr_chunks = chunk_by_gaps(time_days_for_chunk, sortedFluxErr, 1.0)

    # Flatten each chunk
    fluxQFlat, fluxErrQFlat, timeQFlat = [], [], []
    window_length_global = 0.5  # days (global fallback window for wotan-based flatten)

    for i in range(len(time_chunks)):
        time_chunk = time_chunks[i]
        flux_chunk = flux_chunks[i]
        err_chunk = fluxErr_chunks[i]
        if len(time_chunk) < 10:
            # Skip tiny fragments that are not robust to flattening
            continue

        # Mask potential eclipses/transits before estimating trend
        pre_mask = initial_eclipse_mask_time_domain(
            time_chunk,
            flux_chunk,
            min_dur_hr=0.5,
            max_dur_hr=12.0,
            depth_sigma=2.0,
            trend_window_days=2.0,
        )

        # Flatten chunk safely (guarding against failures and short windows)
        t_ok, f_flat_ok, e_ok = safe_flatten_chunk(
            time_chunk,
            flux_chunk,
            err_chunk,
            global_window_days=window_length_global,
            min_points_per_window=7,
            pre_mask=pre_mask,
        )
        # Accumulate processed segments
        timeQFlat.append(t_ok)
        fluxQFlat.append(f_flat_ok)
        fluxErrQFlat.append(e_ok if e_ok is not None else np.full_like(f_flat_ok, np.nan))

    # Concatenate all chunks into uniform arrays
    fluxQ = np.concatenate(fluxQFlat)
    fluxQErr = np.concatenate(fluxErrQFlat)
    timeQ = np.concatenate(timeQFlat) * days2sec  # seconds

    # Remove edges around gaps (seconds)
    dts = np.diff(timeQ)
    to_remove_mask = np.zeros(timeQ.shape, dtype=bool)
    no_gap = 121           # 2-min cadence nominal separation (in seconds)
    small_gap = 30 * 60    # 30 min
    big_gap = 3 * 60 * 60  # 3 hr

    for idx, dt in enumerate(dts):
        i, j = idx, idx + 1
        if dt > big_gap:
            remove_boundary_around_gap(i, j, 12 * 60 * 60, timeQ, to_remove_mask)
        elif dt > small_gap:
            remove_boundary_around_gap(i, j, 30 * 60, timeQ, to_remove_mask)
        elif dt > no_gap:
            remove_boundary_around_gap(i, j, 15 * 60, timeQ, to_remove_mask)

    # Keep only points far enough from detected gaps
    to_keep_mask = ~to_remove_mask
    cleanTimeLoc = timeQ[to_keep_mask]
    cleanFluxLoc = fluxQ[to_keep_mask]
    cleanFluxErrLoc = fluxQErr[to_keep_mask]

    # Quick raw diagnostic (optional)
    plt.figure(figsize=(10, 5))
    plt.plot(cleanTimeLoc / days2sec, cleanFluxLoc, ".", ms=1, color="blue", alpha=0.5)
    plt.title(f"Cleaned Light Curve for {mission} {ID}")
    plt.xlabel("Time (days)")
    plt.ylabel("Normalized Flux")
    plt.grid(True)
    plt.show()
    plt.close()

    # Catalogs & Params
    antic = False
    orbit_data_found = False
    stellar_data_found = False
    orbit_data_calculated = False
    stellar_data_calculated = False

    # Load ANTIC and Villanova summary CSVs for TESS EBs (packaged Databases)
    antic_data = pd.read_csv(p_databases("ANTIC_Catalogue_12_11_filtered.csv"))
    orbit_data = pd.read_csv(p_databases("villanova_orbit_data_tess.csv"))

    print("Searching for orbit data in ANTIC and Villanova catalogs")

    # Select rows for this TIC ID
    row_ANTIC = antic_data[antic_data["ID"] == int(ID)]
    row_Villanova = orbit_data[orbit_data["tess_id"] == int(ID)]

    # Initialize defaults
    Pbin = np.nan
    bjd0 = np.nan
    pdepth = sdepth = pwidth = swidth = prim_pos = sec_pos = sep = np.nan
    mA = mB = rA = rB = tA = tB = a = metallicity = flux_ratio = np.nan
    eccANTIC = omegaANTIC = np.nan

    # ANTIC path
    if len(row_ANTIC) == 1:
        antic = True
        print("Orbit and stellar data found in ANTIC")
        orbit_data_found = True

        # Orbital parameters
        Pbin = float(row_ANTIC.period.iloc[0] * days2sec)
        bjd0 = float(row_ANTIC.bjd0.iloc[0] * days2sec)
        pdepth = float(row_ANTIC.pdepth.iloc[0])
        sdepth = float(row_ANTIC.sdepth.iloc[0])
        pwidth = float(row_ANTIC.pwidth.iloc[0])
        swidth = float(row_ANTIC.swidth.iloc[0])
        prim_pos = float(row_ANTIC.tPE.iloc[0])
        sec_pos = float(row_ANTIC.tSE.iloc[0])
        sep = float(row_ANTIC.sep.iloc[0])

        # Stellar parameters
        stellar_data_found = True
        mA = float(row_ANTIC.MassP.iloc[0] * mSun_kg)
        mB = float(row_ANTIC.MassS.iloc[0] * mSun_kg)
        rA = float(row_ANTIC.RP.iloc[0] * rSun_m)
        rB = float(row_ANTIC.RS.iloc[0] * rSun_m)
        tA = np.nan
        tB = np.nan
        a = np.nan
        metallicity = float(row_ANTIC.z.iloc[0])
        flux_ratio = float(row_ANTIC.frat.iloc[0])
        eccANTIC = float(row_ANTIC.e.iloc[0])
        omegaANTIC = float(row_ANTIC.omega.iloc[0])

        orbit_stellar_params = {
            "Pbin": Pbin,
            "bjd0": bjd0,
            "pdepth": pdepth,
            "sdepth": sdepth,
            "pwidth": pwidth,
            "swidth": swidth,
            "prim_pos": prim_pos,
            "sec_pos": sec_pos,
            "sep": sep,
            "mA": mA,
            "mB": mB,
            "rA": rA,
            "rB": rB,
            "tA": tA,
            "tB": tB,
            "a": a,
            "met": metallicity,
            "frat": flux_ratio,
            "median_flux_err": median_flux_err,
        }

        nan_params = {
            k: v for k, v in orbit_stellar_params.items()
            if (v is None) or (isinstance(v, float) and not np.isfinite(v))
        }

        if len(nan_params) > 0:
            print("Further orbit/stellar info needed, searching Villanova")
            if len(row_Villanova) == 1:
                if "Pbin" in nan_params:
                    Pbin = float(row_Villanova.period.iloc[0] * days2sec)
                if "bjd0" in nan_params:
                    bjd0 = float(row_Villanova.bjd0.iloc[0] * days2sec)
                if "pdepth" in nan_params:
                    pdepth = float(row_Villanova.prim_depth_pf.iloc[0])
                if "sdepth" in nan_params:
                    sdepth = float(row_Villanova.sec_depth_pf.iloc[0])
                if "pwidth" in nan_params:
                    pwidth = float(row_Villanova.prim_width_pf.iloc[0])
                if "swidth" in nan_params:
                    swidth = float(row_Villanova.sec_width_pf.iloc[0])
                if "prim_pos" in nan_params:
                    prim_pos = float(row_Villanova.prim_pos_pf.iloc[0])
                if "sec_pos" in nan_params:
                    sec_pos = float(row_Villanova.sec_pos_pf.iloc[0])
                if "sep" in nan_params:
                    sep = (prim_pos + sec_pos) % 1.0

        # If essential orbital params are still missing, attempt BLS-based estimation
        if (not np.isfinite(Pbin)) or (not np.isfinite(bjd0)):
            print("No recorded value for period and/or bjd0, calculating now.")
            Pbin_bls, bjd0_bls, transit_depth, transit_duration_sec, meta_bls = iterative_bls_single_dip_search(
                cleanTimeLoc,
                cleanFluxLoc,
                cleanFluxErrLoc,
                DetrendingName,
                min_period_days=0.05,
                max_period_days=90.0,
                q_eff=None,
                pre_detrend="both",
                bic_delta=0.0,
                check_harmonics=False,
                plot_harmonics=False,
                presets_sequence=[HYPERFINE],
            )
            override_bls = False
            if not override_bls:
                if np.isfinite(Pbin_bls):
                    Pbin = Pbin_bls
                if np.isfinite(bjd0_bls):
                    bjd0 = bjd0_bls

        # PERIOD VALIDATION
        override_validation = False
        Pbin, timeVP, fluxVP, fluxErrVP, diagnostics = validate_period_filter3(
            cleanTimeLoc,
            cleanFluxLoc,
            cleanFluxErrLoc,
            Pbin,
            window_length_global,
            DetrendingName,
            ID,
            plot=True,
            override=override_validation,
            use_double_dip_logic=False,
        )

        if not diagnostics.get("period_validation", False):
            raise RuntimeError("Period validation failed in validate_period_filter3()")
        else:
            print(f"Period validation passed, proceeding with period: {Pbin / days2sec:.6f} days")
            print("Period diagnostics:", diagnostics)

            base = _resolve_base_dir(None)
            my_folder = base / "LightCurves" / "Data_Preparation" / DetrendingName
            my_folder.mkdir(parents=True, exist_ok=True)
            save_path_final = my_folder / f"Validated_Period_Extra_{ID}.png"
            fig, ax = plt.subplots(figsize=(10, 5))
            ph = (timeVP / Pbin) % 1.0
            sc = ax.scatter(ph, fluxVP, s=3, c=timeVP, cmap="viridis")
            ax.set_xlabel("Phase of Binary (0 to 1)")
            ax.set_ylabel("Normalized & Detrended Flux")
            ax.set_title("Validated Period (extra view)")
            ax.grid(True, ls=":")
            fig.colorbar(sc, ax=ax, label="Time (s)")
            fig.savefig(save_path_final, dpi=300, bbox_inches="tight")
            plt.close(fig)

            if not override_validation:
                timeVP, fluxVP, fluxErrVP = remove_spurious_deep_points(
                    cleanTimeLoc,
                    cleanFluxLoc,
                    cleanFluxErrLoc,
                    Pbin,
                    DetrendingName,
                    ID,
                    depth_threshold_fraction=0.75,
                    phase_step=0.01,
                )
            else:
                timeVP, fluxVP, fluxErrVP = cleanTimeLoc, cleanFluxLoc, cleanFluxErrLoc

        bjd0 = BJD0Check(bjd0, timeVP, fluxVP, fluxErrVP, Pbin, DetrendingName, ID)

        # Fill stellar parameters if missing
        if not np.isfinite(mA):
            mA = findMaAndRaAndTa(ID, paramreturned="mA")
        if not np.isfinite(rA):
            rA = findMaAndRaAndTa(ID, paramreturned="rA")
        if not np.isfinite(rB):
            phaseTime = (timeVP / Pbin) % 1.0
            min_index = np.argmin(fluxVP)
            phaseTime = (phaseTime - phaseTime[min_index] + 0.5) % 1.0
            phaseBinned, fluxBinned, fluxErrBinned = binData(phaseTime, fluxVP, fluxErrVP)
            rB = findRb(rA, phaseBinned, fluxBinned, fluxErrBinned)
            if not isinstance(rB, numbers.Real):
                rB = 0.5 * rSun_m
        if not np.isfinite(mB):
            mB = findMb(rB)
            if not isinstance(mB, numbers.Real):
                mB = 0.5 * mSun_kg
        if not np.isfinite(a):
            a = estimate_semi_major_axis(Pbin, mA, mB)
        if not np.isfinite(metallicity):
            metallicity = 0.0
        if not np.isfinite(flux_ratio):
            flux_ratio = MassRadiusLuminosityRelation(mB, rB) / MassRadiusLuminosityRelation(mA, rA)

    # Villanova-only path
    if (not orbit_data_found) and (len(row_Villanova) == 1):
        orbit_data_found = True
        print("Orbit data found entirely from Villanova")

        Pbin = float(row_Villanova.period.iloc[0] * days2sec)

        Pbin, timeSpurious, fluxSpurious, fluxErrSpurious, diagnostics = validate_period_filter3(
            cleanTimeLoc,
            cleanFluxLoc,
            cleanFluxErrLoc,
            Pbin,
            window_length_global,
            DetrendingName,
            ID,
            plot=True,
            override=False,
        )

        timeVP, fluxVP, fluxErrVP = remove_spurious_deep_points(
            timeSpurious,
            fluxSpurious,
            fluxErrSpurious,
            Pbin,
            DetrendingName,
            ID,
            depth_threshold_fraction=0.75,
            phase_step=0.01,
        )

        bjd0 = float(row_Villanova.bjd0.iloc[0] * days2sec)
        bjd0 = BJD0Check(bjd0, timeVP, fluxVP, fluxErrVP, Pbin, DetrendingName, ID)
        pdepth = float(row_Villanova.prim_depth_pf.iloc[0])
        sdepth = float(row_Villanova.sec_depth_pf.iloc[0])
        pwidth = float(row_Villanova.prim_width_pf.iloc[0])
        swidth = float(row_Villanova.sec_width_pf.iloc[0])
        prim_pos = float(row_Villanova.prim_pos_pf.iloc[0])
        sec_pos = float(row_Villanova.sec_pos_pf.iloc[0])
        sep = (prim_pos + sec_pos) % 1.0

        mA = mB = rA = rB = tA = tB = a = metallicity = flux_ratio = median_flux_err = eccANTIC = omegaANTIC = np.nan

        orbit_stellar_params = {
            "Pbin": Pbin,
            "bjd0": bjd0,
            "pdepth": pdepth,
            "sdepth": sdepth,
            "pwidth": pwidth,
            "swidth": swidth,
            "prim_pos": prim_pos,
            "sec_pos": sec_pos,
            "sep": sep,
            "mA": mA,
            "mB": mB,
            "rA": rA,
            "rB": rB,
            "tA": tA,
            "tB": tB,
            "a": a,
            "met": metallicity,
            "frat": flux_ratio,
            "median_flux_err": median_flux_err,
        }

    # Ensure orbit_stellar_params exists
    orbit_stellar_params = locals().get(
        "orbit_stellar_params",
        {
            "Pbin": Pbin,
            "bjd0": bjd0,
            "pdepth": pdepth,
            "sdepth": sdepth,
            "pwidth": pwidth,
            "swidth": swidth,
            "prim_pos": prim_pos,
            "sec_pos": sec_pos,
            "sep": sep,
        },
    )

    prim_pos = orbit_stellar_params["prim_pos"]
    sec_pos = orbit_stellar_params["sec_pos"]
    pwidth = orbit_stellar_params.get("pwidth", np.nan)
    swidth = orbit_stellar_params.get("swidth", np.nan)
    pwidth = pwidth if (np.isfinite(pwidth) and pwidth <= 0.3) else np.nan
    swidth = swidth if (np.isfinite(swidth) and swidth <= 0.3) else np.nan
    pdepth = orbit_stellar_params.get("pdepth", np.nan)
    sdepth = orbit_stellar_params.get("sdepth", np.nan)

    # Eclipse modeling
    (
        timeCut,
        fluxCut,
        fluxErrCut,
        prim_pos,
        sec_pos,
        pwidth,
        swidth,
        pdepth,
        sdepth,
        sep,
        ecc,
        omega,
        eccNoAssump,
        omegaNoAssump,
        ecoswNoAssump,
        esinwNoAssump,
        knownEclipse,
    ) = modelEclipse3(
        timeVP,
        fluxVP,
        fluxErrVP,
        Pbin,
        bjd0,
        sep,
        prim_pos,
        sec_pos,
        pwidth,
        swidth,
        pdepth,
        sdepth,
        rA,
        rB,
        tA,
        tB,
        a,
        DetrendingName=DetrendingName,
        ID=ID,
        plotting=True,
        vetting=True,
    )

    # Re-apply manual cuts to modeled arrays if requested
    if use_manual_cuts:
        timeCut, fluxCut, fluxErrCut = apply_manual_cuts(
            timeCut,
            fluxCut,
            fluxErrCut,
            ID,
            cuts_csv=cuts_csv,
            days2sec=days2sec,
        )

    # Compare derived e, omega to ANTIC values if available
    if np.isfinite(eccANTIC):
        if np.isclose(ecc, eccANTIC, atol=1e-5):
            print("Calculated and ANTIC eccentricities match!")
        else:
            print("Calculated eccentricity does not match ANTIC; using recorded value")
            ecc = eccANTIC
    else:
        print("No recorded value for ecc, proceeding with calculated value.")

    if np.isfinite(omegaANTIC):
        if np.isclose(omega, omegaANTIC, atol=1e-5):
            print("Calculated and ANTIC arguments of periapsis match!")
        else:
            print("Calculated omega does not match ANTIC; using recorded value")
            omega = omegaANTIC
    else:
        print("No recorded value for omega, proceeding with calculated value.")

    # Convenience: convert SI to solar units for logging
    calc_mA = mA / mSun_kg
    calc_mB = mB / mSun_kg
    calc_rA = rA / rSun_m
    calc_rB = rB / rSun_m

    if antic:
        ANTICmA = row_ANTIC.MassP.iloc[0] * mSun_kg
        ANTICmB = row_ANTIC.MassS.iloc[0] * mSun_kg
        ANTICrA = row_ANTIC.RP.iloc[0] * rSun_m
        ANTICrB = row_ANTIC.RS.iloc[0] * rSun_m
        antic_mA = ANTICmA / mSun_kg
        antic_mB = ANTICmB / mSun_kg
        antic_rA = ANTICrA / rSun_m
        antic_rB = ANTICrB / rSun_m
        antic_ecosw = row_ANTIC.ecosω.iloc[0]
        antic_esinw = row_ANTIC.esinω.iloc[0]

    # Final orbital parameters
    orbit_params = {
        "Pbin": Pbin,
        "bjd0": bjd0,
        "pdepth": pdepth,
        "sdepth": sdepth,
        "pwidth": pwidth,
        "swidth": swidth,
        "prim_pos": prim_pos,
        "sec_pos": sec_pos,
        "sep": sep,
        "e": ecc,
        "omega": omega,
    }

    # Final stellar parameters
    stellar_params = {
        "mA": mA,
        "mB": mB,
        "rA": rA,
        "rB": rB,
        "met": metallicity,
        "frat": flux_ratio,
        "median_flux_err": -27,  # placeholder to keep structure consistent
    }

    # Prepare output directories for figures and prepped data
    base = _resolve_base_dir(None)
    my_folder_Tess = base / "LightCurves" / "Data_Preparation" / DetrendingName
    my_folder_Tess.mkdir(parents=True, exist_ok=True)
    figs_dir = base / "LightCurves" / "Figures" / DetrendingName
    figs_dir.mkdir(parents=True, exist_ok=True)

    # Save an "original data" phase plot
    save_path_orig = os.path.join(my_folder_Tess, f"Original_Data_{ID}.png")
    save_path_figs = os.path.join(figs_dir, f"{mission}_{ID}_phase_folded_original_data.png")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.scatter(((timeOrigCopy - bjd0) / orbit_params["Pbin"]) % 1, fluxOrigCopy, s=3, marker=".", c=timeOrigCopy)
    ax.set_xlabel("Phase of Binary (0 to 1)")
    ax.set_ylabel("Normalized (but not detrended) Flux")
    ax.set_title("Original Data")
    for target_path in (save_path_figs, save_path_orig):
        try:
            abs_path = os.path.abspath(target_path)
            fig.savefig(abs_path, bbox_inches="tight", dpi=300)
            print(f"[saved] {abs_path}")
        except Exception as e:
            print(f"[ERROR saving] {abs_path}: {e}")
    plt.close(fig)

    if remove_eclipses:
        # Generate eclipses-removed plot for quick QA
        timeCutGraph, fluxCutGraph, non_nan_params_stored = RemoveEclipses(
            np.copy(timeOrigCopy),
            np.copy(fluxOrigCopy),
            Pbin,
            bjd0,
            prim_pos,
            sec_pos,
            pwidth,
            swidth,
            sep,
            cuts="both",
            phase_folded="n",
        )

        out_figs = os.path.join(figs_dir, f"{mission}_{ID}_phase_folded_eclipses_removed.png")
        out_prep = os.path.join(my_folder_Tess, f"Phase_Folded_Eclipses_Removed_{ID}.png")
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        ph2 = ((timeCutGraph - bjd0) / Pbin) % 1.0
        sc = ax2.scatter(ph2, fluxCutGraph, s=3, marker=".", c=timeCutGraph)
        ax2.set_xlabel("Phase of Binary (0 to 1)")
        ax2.set_ylabel("Normalized (but not detrended) Flux")
        ax2.set_title("Eclipses Removed")
        for target_path in (out_figs, out_prep):
            try:
                abs_path = os.path.abspath(target_path)
                fig2.savefig(abs_path, bbox_inches="tight", dpi=300)
                print(f"[saved] {abs_path}")
            except Exception as e:
                print(f"[ERROR saving] {target_path}: {e}")
        plt.close(fig2)

    # Rebound simulation
    print(
        "Creating rebound simulation with:",
        "Pbin:", Pbin / days2sec,
        "days, bjd0:", bjd0 / days2sec,
        "ecc:", ecc,
        "omega:", omega,
        "mA:", mA / mSun_kg,
        "mB:", mB / mSun_kg,
        "rA:", rA / rSun_m,
        "rB:", rB / rSun_m,
    )
    sim = CreateReboundSim(Pbin, ecc, omega, mA, mB, rA, rB, bjd0, timeOrigCopy[0])

    orbits = sim.orbits()
    theta_init = orbits[0].theta
    omega_init = orbits[0].omega
    P_init = orbits[0].P
    ecc_init = orbits[0].e

    _root = _resolve_base_dir(None)
    folder_name = _root / "LightCurves" / "Processed" / str(DetrendingName)
    folder_name.mkdir(parents=True, exist_ok=True)

    binary_path = folder_name / f"{mission}_{ID}_{DetrendingName}_binaryStartingParams.csv"

    with open(binary_path, "w") as binaryParamsFile:
        binaryParamsFile.write("mA (mSun)," + str(mA / mSun_kg) + "\n")
        binaryParamsFile.write("mB (mSun)," + str(mB / mSun_kg) + "\n")
        binaryParamsFile.write("RA (RSun)," + str(rA / rSun_m) + "\n")
        binaryParamsFile.write("RB (RSun)," + str(rB / rSun_m) + "\n")
        binaryParamsFile.write("bjd0 (Days - 2550000)," + str(bjd0 / days2sec - 55000) + "\n")
        binaryParamsFile.write("theta (deg)," + str(np.degrees(theta_init)) + "\n")
        binaryParamsFile.write("Pbin (days)," + str(P_init / days2sec) + "\n")
        binaryParamsFile.write("ecc," + str(ecc_init) + "\n")
        binaryParamsFile.write("omega (deg)," + str(np.degrees(omega_init)) + "\n")

    end_time = TIME.time()
    timing_path = folder_name / f"{mission}_{ID}_{DetrendingName}_LoadDataTICTiming.csv"
    with open(timing_path, "w") as fh:
        fh.write(f"Start time: {start_time}\n")
        fh.write(f"End time: {end_time}\n")
        fh.write(f"Total time: {end_time - start_time} seconds\n")

    return sim, timeOrigCopy, fluxOrigCopy, timeCut, fluxCut, orbit_params, stellar_params, sector_times


def _mad(x):
	'''
	Functionality:
		Compute the Median Absolute Deviation (MAD), a robust scale estimator.
	Arguments:
		x (array-like): Input data.
	Returns:
		float: MAD = median(|x - median(x)|).
	'''
	med = np.median(x)  # robust center
	return np.median(np.abs(x - med))  # robust spread


def estimate_cadence_seconds(time_days):
	'''
	Functionality:
		Estimate the sampling cadence in seconds using the median spacing of time stamps.
	Arguments:
		time_days (array-like): Time values in days.
	Returns:
		float: Cadence in seconds (median Δt * days2sec).
	'''
	# Convert to ndarray and compute median time step (days)
	dt_days = np.median(np.diff(np.asarray(time_days)))
	return float(dt_days * days2sec)  # days -> seconds


def initial_eclipse_mask_time_domain(
	time_days,
	flux,
	# Duration heuristics: CBP/EB eclipses are typically ~0.5–10 hours
	min_dur_hr=0.5,
	max_dur_hr=10.0,
	depth_sigma=4.0,          # how many sigma below baseline to count as eclipse
	expand_mult=1.6,          # widen masks beyond the measured width
	trend_window_days=2.0,    # very gentle pre-flatten window; make larger if needed
):
	'''
	Functionality:
		Return a boolean mask (True = exclude) flagging likely downward events (eclipses/transits)
		without prior period/epoch knowledge via gentle detrending + peak finding on inverted residuals.
	Arguments:
		time_days (array-like): Time values in days.
		flux (array-like): Flux values (arbitrary normalization).
		min_dur_hr (float): Minimum dip duration to consider (hours).
		max_dur_hr (float): Maximum dip duration to consider (hours).
		depth_sigma (float): Dip prominence threshold in units of MAD-based sigma.
		expand_mult (float): Factor to widen each detected dip mask beyond measured width.
		trend_window_days (float): Window length for gentle pre-flattening (days).
	Returns:
		np.ndarray (bool): Mask array (True where samples should be excluded).
	'''
	# Ensure 1-D float arrays and matching lengths
	time_days = np.asarray(time_days, dtype=float)
	flux = np.asarray(flux, dtype=float)
	assert time_days.ndim == 1 and flux.ndim == 1 and len(time_days) == len(flux)

	n = len(time_days)
	if n < 10:
		# Too few samples to be confident; return keep-all mask
		return np.zeros(n, dtype=bool)

	# 1) Gentle pre-flatten (prefer wotan if available) to estimate residuals
	_HAS_WOTAN = True
	if _HAS_WOTAN:
		# wotan expects window_length in days
		flat = wotan.flatten(time_days, flux, method="biweight",
							 window_length=float(trend_window_days),
							 return_trend=False)
		resid = flat - 1.0  # residuals around baseline ~ 1
	else:
		# Fallback: normalize by global median (crude)
		resid = flux / np.median(flux) - 1.0

	# 2) Robust noise scale via MAD; fallback to std if needed
	sigma_hat = 1.4826 * _mad(resid)
	if not np.isfinite(sigma_hat) or sigma_hat <= 0:
		sigma_hat = np.std(resid) if np.std(resid) > 0 else 1e-6

	# 3) Peak finding on inverted residuals (downward dips => positive peaks in -resid)
	cadence_sec = estimate_cadence_seconds(time_days)  # seconds per sample (robust)
	min_w_samples = max(1, int(np.floor((min_dur_hr * 3600.0) / cadence_sec)))  # min width in samples
	max_w_samples = max(min_w_samples + 1, int(np.ceil((max_dur_hr * 3600.0) / cadence_sec)))  # max width in samples

	inverted = -resid  # dips become peaks
	prominence = depth_sigma * sigma_hat  # prominence threshold (in residual units)

	# Guardrail for very quiet light curves
	if not np.isfinite(prominence) or prominence <= 0:
		prominence = 3e-4  # ~300 ppm minimum

	# Use scipy.signal.find_peaks with width constraint in samples
	peaks, props = find_peaks(
		inverted,
		prominence=prominence,
		width=(min_w_samples, max_w_samples)
	)

	mask = np.zeros(n, dtype=bool)  # start with all-False mask
	if len(peaks) == 0:
		return mask  # nothing detected

	# 4) Build widened masks around each detected dip using measured widths
	widths = props.get("widths", np.full_like(peaks, fill_value=min_w_samples, dtype=float))
	left_ips = props.get("left_ips", peaks - widths / 2.0)
	right_ips = props.get("right_ips", peaks + widths / 2.0)

	for L, R, W in zip(left_ips, right_ips, widths):
		# Expand each region by expand_mult to cover ingress/egress wings
		center = 0.5 * (L + R)
		half = 0.5 * float(W) * float(expand_mult)
		i0 = int(max(0, np.floor(center - half)))
		i1 = int(min(n, np.ceil(center + half)))
		if i1 > i0:
			mask[i0:i1] = True  # mark exclusion zone

	return mask
	

def _interp_nan(x, y, fill_value=None):
	'''
	Functionality:
		Linearly interpolate y over NaNs using x, padding ends with nearest finite values.
		For fully-NaN segments, use fill_value if provided; otherwise a reasonable default.
	Arguments:
		x (array-like): Monotonic coordinate array.
		y (array-like): Values with possible NaNs.
		fill_value (float or None): Fallback value for all-NaN segments; if None and all NaN,
		                            returns an array of ones (useful for flattened flux).
	Returns:
		np.ndarray: Interpolated y with NaNs filled.
	'''
	y = np.asarray(y, float)
	x = np.asarray(x, float)
	good = np.isfinite(y) & np.isfinite(x)  # indices with finite x and y
	if good.sum() == 0:
		# Nothing finite: fill with default or provided constant
		return np.full_like(y, 1.0 if fill_value is None else fill_value, dtype=float)
	# Copy and pad ends with nearest finite neighbor
	y_pad = y.copy()
	first = np.argmax(good)  # first finite index
	last  = len(y) - 1 - np.argmax(good[::-1])  # last finite index
	y_pad[:first] = y[good][0]
	y_pad[last+1:] = y[good][-1]
	# Interpolate interior NaNs
	bad = ~np.isfinite(y_pad)
	if bad.any():
		y_pad[bad] = np.interp(x[bad], x[good], y[good])
	return y_pad


def safe_flatten_chunk(time_chunk, flux_chunk, err_chunk=None,
					   global_window_days=0.5,
					   min_points_per_window=7,
					   pre_mask=None):
	'''
	Functionality:
		Flatten a light-curve chunk robustly while preserving all samples (no deletions),
		returning baseline≈1.0 flux without NaNs; uses wotan (biweight) if available,
		with guarded fallbacks.
	Arguments:
		time_chunk (array-like): Time values in days for this chunk.
		flux_chunk (array-like): Flux values for this chunk.
		err_chunk (array-like or None): Optional flux uncertainties aligned with flux_chunk.
		global_window_days (float): Upper bound for detrending window (days).
		min_points_per_window (int): Minimum samples required per detrending window.
		pre_mask (array-like or None): Boolean mask of samples to exclude from trend estimation.
	Returns:
		t (np.ndarray): Time array (days), original ordering restored.
		f_flat (np.ndarray): Flattened flux with baseline ~ 1 and no NaNs.
		e (np.ndarray or None): Error array reordered to match outputs (if provided).
	'''
	# Coerce inputs and preserve ordering info
	t = np.asarray(time_chunk, float)
	f = np.asarray(flux_chunk, float)

	# 1) Ensure inputs are finite (temporarily allow NaNs, to be interpolated)
	f[~np.isfinite(f)] = np.nan
	t[~np.isfinite(t)] = np.nan

	# Enforce strictly increasing time (rare corner cases from merges)
	order = np.argsort(t)
	t = t[order]
	f = f[order]
	if err_chunk is not None:
		e = np.asarray(err_chunk, float)[order]
	else:
		e = None

	# Fill NaNs in inputs (keep sample count intact)
	t = _interp_nan(t, t)  # identity interpolation to clear NaNs in t
	f = _interp_nan(t, f, fill_value=np.nanmedian(f))  # fill flux around its median

	# 2) Build a robust mask for trend estimation (do NOT drop samples)
	finite = np.isfinite(f) & np.isfinite(t)
	if pre_mask is None:
		pre_mask = np.zeros_like(finite, dtype=bool)
	mask = pre_mask | (~finite)  # exclude non-finite and pre-masked points from trend fit

	# 3) Choose a safe window length (days), respecting cadence and chunk span
	if len(t) > 1:
		dt = np.nanmedian(np.diff(t))  # robust cadence in days
		if not np.isfinite(dt) or dt <= 0:
			dt = (t[-1] - t[0]) / max(1, len(t)-1)  # fallback
	else:
		dt = global_window_days / 50.0  # arbitrary tiny step fallback for single-point chunks

	# Require at least min_points_per_window samples in any window
	min_window_days = max(global_window_days, dt * (min_points_per_window + 2))  # computed but not used further (kept)
	# Also cap the local window by 10% of chunk span, but never exceed global_window_days
	baseline_days = max(1e-10, t[-1] - t[0])
	window_local_days = min(0.10 * baseline_days, global_window_days)
	window_days = max(dt * (min_points_per_window + 2), min(window_local_days, global_window_days))
	window_days = max(window_days, dt * (min_points_per_window + 2), 3*dt)  # final safety guard

	# 4) Estimate trend using wotan (preferred); fallback to robust linear fit if needed
	try:
		f_flat, trend = wotan.flatten(t, f, method='biweight',
									  window_length=window_days,
									  return_trend=True,
									  mask=mask,
									  edge_cutoff=0)
	except Exception:
		# Fallback: robust linear fit on unmasked points
		ok = np.isfinite(f) & (~mask)
		if ok.sum() < 3:
			ok = np.isfinite(f)  # last resort: use all finite points
		coeffs = np.polyfit(t[ok], f[ok], 1)  # degree-1 trend
		trend = np.polyval(coeffs, t)
		f_flat = f / trend  # divide out trend

	# If trend has NaNs (can happen at edges), fill and recompute flattened flux
	if not np.all(np.isfinite(trend)):
		trend = _interp_nan(t, trend, fill_value=np.nanmedian(f))
		f_flat = f / trend

	# 5) Patch any NaNs remaining in flattened flux
	if not np.all(np.isfinite(f_flat)):
		f_flat = _interp_nan(t, f_flat, fill_value=1.0)

	# 6) Re-center baseline to ~1.0 using unmasked points if available
	out_mask = ~mask & np.isfinite(f_flat)
	if out_mask.sum() >= 5:
		med = np.nanmedian(f_flat[out_mask])
	else:
		med = np.nanmedian(f_flat)
	if np.isfinite(med) and med != 0:
		f_flat /= med
	else:
		# Final fallback to overall median if med is pathological
		f_flat = f_flat / (np.nanmedian(f_flat) if np.isfinite(np.nanmedian(f_flat)) else 1.0)

	# Ensure no NaNs remain after re-centering
	if not np.all(np.isfinite(f_flat)):
		f_flat = _interp_nan(t, f_flat, fill_value=1.0)

	# Restore original sample order
	inv = np.empty_like(order)
	inv[order] = np.arange(len(order))
	f_flat = f_flat[inv]
	t = t[inv]
	e = e[inv] if e is not None else None
	return t, f_flat, e


# calculate minimal phase distance accounting for wraparound at 0/1
def phase_distance(p1, p2):
	'''
	Functionality:
		Compute the minimal circular distance between two phases on [0,1) with wraparound.
	Arguments:
		p1 (float): First phase in [0,1) (not enforced).
		p2 (float): Second phase in [0,1) (not enforced).
	Returns:
		float: Minimal distance on the unit circle.
	'''
	# Direct difference vs wraparound complement; take the smaller
	return min(abs(p1 - p2), 1 - abs(p1 - p2))
	
	
# determine if a point is in or out of eclipse
def InOutEclipse(phase_orig, timeOrig, fluxOrig, prim_pos, sec_pos, pwidth, swidth, cuts):
	'''
	Functionality:
		Decide whether a single sample (phase, time, flux) lies outside the primary/secondary
		eclipse windows and, if so, return (time, flux); otherwise return (nan, nan).
	Arguments:
		phase_orig (float): Phase of the sample in [0,1).
		timeOrig (float): Time of the sample (same units as caller, typically seconds).
		fluxOrig (float): Flux value for the sample.
		prim_pos (float): Primary eclipse center phase.
		sec_pos (float): Secondary eclipse center phase.
		pwidth (float): Primary eclipse full width in phase units.
		swidth (float): Secondary eclipse full width in phase units.
		cuts (str): Which eclipse(s) to exclude: "both", "primary", or "secondary".
	Returns:
		tuple: (timeOrig, fluxOrig) if outside requested eclipse windows; otherwise (nan, nan).
	'''
	# make sure primary position and secondary position are floats
	prim_pos = float(prim_pos)
	sec_pos = float(sec_pos)

	# check which cuts to apply; do NOT recenter phases—use raw prim/sec positions
	# returns NaN pair for anything within an eclipse window
	if cuts.lower() == "both":
		# outside both eclipse windows?
		outside_primary = phase_distance(phase_orig, prim_pos) > pwidth / 2
		outside_secondary = phase_distance(phase_orig, sec_pos) > swidth / 2
		if outside_primary and outside_secondary:
			return timeOrig, fluxOrig
	elif cuts.lower() == "primary":
		# keep only samples outside primary
		if phase_distance(phase_orig, prim_pos) > pwidth / 2:
			return timeOrig, fluxOrig
	elif cuts.lower() == "secondary":
		# keep only samples outside secondary
		if phase_distance(phase_orig, sec_pos) > swidth / 2:
			return timeOrig, fluxOrig

	# if inside eclipse (per selected cuts), drop the point by returning NaNs
	return np.nan, np.nan


# main function to remove eclipses
def RemoveEclipses(timeOrig, fluxOrig, period, bjd0, prim_pos, sec_pos, pwidth, swidth, sep, cuts, phase_folded):
	'''
	Functionality:
		Remove samples that fall within primary/secondary eclipse windows from a time series.
		Supports already-folded series or raw times with given (period, bjd0).
	Arguments:
		timeOrig (np.ndarray): Time array (seconds if using raw times).
		fluxOrig (np.ndarray): Flux array (same length as timeOrig).
		period (float): Binary period (seconds).
		bjd0 (float): Reference epoch for phase folding (seconds).
		prim_pos (float): Primary eclipse center phase.
		sec_pos (float): Secondary eclipse center phase.
		pwidth (float): Primary eclipse full width in phase units.
		swidth (float): Secondary eclipse full width in phase units.
		sep (float): Primary–secondary phase separation (unused here, kept for API symmetry).
		cuts (str): Which eclipse(s) to remove: "both", "primary", or "secondary".
		phase_folded (str): 'y' if timeOrig already contains phases; 'n' to compute phases from times.
	Returns:
		tuple:
			timeClean (np.ndarray): Times with in-eclipse samples removed.
			fluxClean (np.ndarray): Flux with in-eclipse samples removed.
			not_nan_indices (tuple): Indices of retained samples (as returned by np.where).
	'''
	if phase_folded.lower() == 'n':
		# fold by provided ephemeris
		print('timeOrig: ' + str(timeOrig))
		phase_orig = ((timeOrig - bjd0) / period) % 1
		print('phase_orig: ' + str(phase_orig))
	elif phase_folded.lower() == 'y':
		# already folded (assumed shifted by bjd0 upstream)
		phase_orig = timeOrig % 1  # already folded, assuming already shifted by bjd0

	# apply eclipse filter using map across samples
	time, flux = zip(*map(
		InOutEclipse,
		phase_orig, timeOrig, fluxOrig,
		itertools.repeat(prim_pos), itertools.repeat(sec_pos),
		itertools.repeat(pwidth), itertools.repeat(swidth),
		itertools.repeat(cuts)
	))
	print('time after removal: ' + str(time))
	print('flux after removal: ' + str(flux))

	# ensure we are returning arrays
	timeCut = np.array(time)
	fluxCut = np.array(flux)

	# remove our NaN values (in-eclipse points)
	not_nan_indices = np.where(~np.isnan(timeCut))
	timeClean = timeCut[not_nan_indices]
	fluxClean = fluxCut[not_nan_indices]
	
	print('timeClean: ' + str(timeClean))
	print('fluxClean: ' + str(fluxClean))
	return timeClean, fluxClean, not_nan_indices

def get_available_cores():
	'''
	Functionality:
		Return the number of CPU cores available for multiprocessing, honoring SLURM if present.
	Arguments:
		None
	Returns:
		int: Core count (SLURM_CPUS_PER_TASK if set, else local cpu_count()).
	'''
	# Prefer SLURM-provided core count; otherwise use local machine count
	return int(os.environ.get("SLURM_CPUS_PER_TASK", cpu_count()))


def _bls_power_chunk(args):
	'''
	Functionality:
		Run BoxLeastSquares.power over a chunk of trial periods (with fixed durations array).
	Arguments:
		args (tuple): (time_days, flux, flux_err, period_chunk, durations)
			time_days (np.ndarray): Time in days.
			flux (np.ndarray): Flux array.
			flux_err (np.ndarray): Flux uncertainties.
			period_chunk (np.ndarray): Trial periods (days) for this worker.
			durations (np.ndarray): Durations (days), broadcastable to period_chunk.
	Returns:
		BoxLeastSquaresResults: Result from bls.power over the provided periods/durations.
	'''
	time_days, flux, flux_err, period_chunk, durations = args
	bls = BoxLeastSquares(time_days, flux, flux_err)  # instantiate BLS
	result = bls.power(period_chunk, durations)       # evaluate periodogram power
	return result


def _as_days_period(P_seconds):
	'''
	Functionality:
		Convert period(s) from seconds to days.
	Arguments:
		P_seconds (float or array-like): Period value(s) in seconds.
	Returns:
		np.ndarray: Period(s) in days.
	'''
	P_seconds = np.atleast_1d(np.array(P_seconds, dtype=float))
	return P_seconds / 86400.0


def _as_days_duration(D_seconds):
	'''
	Functionality:
		Convert duration(s) from seconds to days.
	Arguments:
		D_seconds (float or array-like): Duration value(s) in seconds.
	Returns:
		np.ndarray: Duration(s) in days.
	'''
	D_seconds = np.atleast_1d(np.array(D_seconds, dtype=float))
	return D_seconds / 86400.0


def _cores(n_processes=None):
	'''
	Functionality:
		Choose a reasonable number of worker processes for multiprocessing.
	Arguments:
		n_processes (int or None): If provided, ensure at least 1; else use (cpu_count - 1) fallback.
	Returns:
		int: Number of processes to use (>=1).
	'''
	if n_processes is not None:
		return int(max(1, n_processes))
	try:
		from os import cpu_count
		return max(1, (cpu_count() or 1) - 1)  # keep one core free if possible
	except Exception:
		return 1


def _parabolic_refine(x, y):
	'''
	Functionality:
		Refine the location of the maximum using quadratic (parabolic) interpolation around the peak.
	Arguments:
		x (np.ndarray): Sample locations (monotonic assumed).
		y (np.ndarray): Sample values; peak is sought at argmax(y).
	Returns:
		tuple: (x_peak, y_peak) refined vertex estimate; falls back to discrete max at edges or on failure.
	'''
	# index of discrete maximum
	i = int(np.argmax(y))
	if i == 0 or i == len(y) - 1:
		# cannot form a 3-point parabola at boundaries
		return x[i], y[i]
	# neighbors for quadratic fit
	x0, x1, x2 = x[i-1], x[i], x[i+1]
	y0, y1, y2 = y[i-1], y[i], y[i+1]
	denom = (x0 - 2*x1 + x2)
	if denom == 0:
		# degenerate parabola
		return x1, y1
	# vertex x-position from finite-difference parabola
	x_peak = x1 + 0.5 * ((y0 - y2) / denom)
	# optional y at vertex via least-squares quadratic fit
	A = np.array([[x0**2, x0, 1.0],
				  [x1**2, x1, 1.0],
				  [x2**2, x2, 1.0]], dtype=float)
	b = np.array([y0, y1, y2], dtype=float)
	try:
		a, bb, c = np.linalg.lstsq(A, b, rcond=None)[0]
		y_peak = a*x_peak**2 + bb*x_peak + c
	except Exception:
		# fallback to discrete center point if fit fails
		x_peak, y_peak = x1, y1
	return x_peak, y_peak


def _bls_best_over_qgrid_chunk(args):
	'''
	Functionality:
		Evaluate BLS power over a chunk of trial periods using a grid of duty cycles (q),
		where duration D = q * P. For each period, keep only the best (over q) power/depth/duration/t0.
	Arguments:
		args (tuple): (t_days, f, fe, P_days_chunk, q_grid)
			t_days (np.ndarray): Time (days).
			f (np.ndarray): Flux.
			fe (np.ndarray): Flux uncertainties.
			P_days_chunk (np.ndarray): Trial periods (days) for this worker.
			q_grid (np.ndarray): Duty cycle values to try.
	Returns:
		dict: {
			"period": np.ndarray (days),
			"power": np.ndarray,
			"depth": np.ndarray,
			"duration": np.ndarray (days),
			"t0": np.ndarray (days)
		} best-over-q arrays aligned to P_days_chunk.
	'''
	t_days, f, fe, P_days_chunk, q_grid = args
	bls = BoxLeastSquares(t_days, f, fe)  # instantiate once per chunk
	nP = len(P_days_chunk)
	# initialize "best over q" accumulators
	best_power    = np.full(nP, -np.inf, dtype=float)
	best_depth    = np.full(nP, np.nan,  dtype=float)
	best_duration = np.full(nP, np.nan,  dtype=float)
	best_t0       = np.full(nP, np.nan,  dtype=float)
	for q in q_grid:
		# duration grid for this q
		D_days = q * P_days_chunk
		# enforce D < P (paranoia; q should already ensure it)
		mask = D_days < P_days_chunk * (1.0 + 1e-12)
		if not np.any(mask):
			continue
		# compute BLS power at valid pairs
		res = bls.power(P_days_chunk[mask], D_days[mask])
		# stitch back into full-length arrays for comparison
		pow_full = np.full(nP, -np.inf, dtype=float)
		dep_full = np.full(nP, np.nan,  dtype=float)
		dur_full = np.full(nP, np.nan,  dtype=float)
		t0_full  = np.full(nP, np.nan,  dtype=float)
		pow_full[mask] = res.power
		dep_full[mask] = res.depth
		dur_full[mask] = res.duration
		t0_full[mask]  = res.transit_time
		# take element-wise best over q
		better = pow_full > best_power
		if np.any(better):
			best_power[better]    = pow_full[better]
			best_depth[better]    = dep_full[better]
			best_duration[better] = dur_full[better]
			best_t0[better]       = t0_full[better]
	return {
		"period": P_days_chunk,
		"power": best_power,
		"depth": best_depth,
		"duration": best_duration,
		"t0": best_t0
	}


def _bls_fixed_duration_chunk(args):
	'''
	Functionality:
		Evaluate BLS over a chunk of trial periods with per-period durations provided
		(same shape), returning power/depth/duration/t0 arrays aligned to the chunk.
	Arguments:
		args (tuple): (t_days, f, fe, P_days_chunk, D_days_chunk)
			t_days (np.ndarray): Time (days).
			f (np.ndarray): Flux.
			fe (np.ndarray): Flux uncertainties.
			P_days_chunk (np.ndarray): Trial periods (days) for this worker.
			D_days_chunk (np.ndarray): Trial durations (days), one per period.
	Returns:
		dict: {
			"period": np.ndarray (days),
			"power": np.ndarray,
			"depth": np.ndarray,
			"duration": np.ndarray (days),
			"t0": np.ndarray (days)
		} arrays aligned to P_days_chunk; periods with invalid D>=P carry -inf power.
	'''
	t_days, f, fe, P_days_chunk, D_days_chunk = args
	bls = BoxLeastSquares(t_days, f, fe)
	# enforce D < P, element-wise
	mask = D_days_chunk < P_days_chunk * (1.0 + 1e-12)
	if not np.any(mask):
		# return empty-like placeholders with -inf power to be ignored later
		nP = len(P_days_chunk)
		return {
			"period": P_days_chunk,
			"power": np.full(nP, -np.inf, dtype=float),
			"depth": np.full(nP, np.nan, dtype=float),
			"duration": np.full(nP, np.nan, dtype=float),
			"t0": np.full(nP, np.nan, dtype=float)
		}
	# subset valid (P, D) pairs
	P_use = P_days_chunk[mask]
	D_use = D_days_chunk[mask]
	res = bls.power(P_use, D_use)
	# stitch back into full arrays
	nP = len(P_days_chunk)
	pow_full = np.full(nP, -np.inf, dtype=float)
	dep_full = np.full(nP, np.nan,  dtype=float)
	dur_full = np.full(nP, np.nan,  dtype=float)
	t0_full  = np.full(nP, np.nan,  dtype=float)
	pow_full[mask] = res.power
	dep_full[mask] = res.depth
	dur_full[mask] = res.duration
	t0_full[mask]  = res.transit_time
	return {
		"period": P_days_chunk,
		"power": pow_full,
		"depth": dep_full,
		"duration": dur_full,
		"t0": t0_full
	}


def _try_harmonics_qgrid(bls, P_best_days, q_grid):
	'''
	Functionality:
		Given a candidate best period (days), test its first harmonic (2P) and subharmonic (P/2)
		over the same duty-cycle grid and return the period with the highest BLS power.
	Arguments:
		bls (BoxLeastSquares): Pre-initialized BLS object.
		P_best_days (float): Candidate best period (days).
		q_grid (np.ndarray): Duty cycles to test; duration D = q * P.
	Returns:
		float: Best period among {P, 2P, P/2} by maximum power.
	'''
	cands = [P_best_days, P_best_days * 2.0, P_best_days / 2.0]
	best = (-np.inf, P_best_days)  # (power, period)
	for P in cands:
		if not (np.isfinite(P) and P > 0):
			continue
		for q in q_grid:
			D = q * P
			res = bls.power(np.atleast_1d(P), np.atleast_1d(D))
			p = float(res.power[0])
			if p > best[0]:
				best = (p, float(P))
	return best[1]


def _try_harmonics_fixed(bls, P_best_days, q_at_best):
	'''
	Functionality:
		Given a candidate best period (days) and fixed duty cycle q_at_best, test {P, 2P, P/2}
		and return the period yielding the highest BLS power.
	Arguments:
		bls (BoxLeastSquares): Pre-initialized BLS object.
		P_best_days (float): Candidate best period (days).
		q_at_best (float): Duty cycle to hold fixed; duration D = q_at_best * P.
	Returns:
		float: Best period among {P, 2P, P/2} by maximum power.
	'''
	cands = [P_best_days, P_best_days * 2.0, P_best_days / 2.0]
	best = (-np.inf, P_best_days)  # (power, period)
	for P in cands:
		if not (np.isfinite(P) and P > 0):
			continue
		D = q_at_best * P
		if not (D < P):
			continue  # skip invalid duration
		res = bls.power(np.atleast_1d(P), np.atleast_1d(D))
		p = float(res.power[0])
		if p > best[0]:
			best = (p, float(P))
	return best[1]

# Coarse-to-fine search presets for BLS; control decimation, phase tolerance, and evaluation caps
COARSE = dict(decimate=12, phi_tol=0.35, max_evals=40_000, refine=False)
MEDIUM  = dict(decimate=6,  phi_tol=0.25, max_evals=60_000, refine=False)
SANE  = dict(decimate=1,  phi_tol=0.1, max_evals=160_000, refine=True)
FINE = dict(decimate=1,  phi_tol=0.01, max_evals=200_000, refine=True)
FINER = dict(decimate=1,  phi_tol=0.001, max_evals=260_000, refine=True)
FINEST = dict(decimate=1,  phi_tol=0.0001, max_evals=320_000, refine=True)
ULTRAFINE = dict(decimate=1, phi_tol=5e-5,  max_evals=500_000, refine=True)
HYPERFINE = dict(decimate=1, phi_tol=1e-5,  max_evals=800_000, refine=True)


def bls_ultrafast2( 
    time_s, 
    flux, 
    flux_err=None, 
    DetrendingName=None, 
    ID=None,                        # for file naming 
    min_period_days=0.05, 
    max_period_days=90.0, 
    q_eff=None,                 # single duty cycle; None => auto from cadence 
    decimate=6,                 # stride factor for *coarse* pass only (>=1) 
    phi_tol=0.25,               # phase tolerance -> controls df 
    max_evals=60_000,           # hard cap on coarse grid evaluations 
    refine=True,                # tiny 1D local refine around the top peak 
    # optional pre-detrending (BIC-gated) — used *before* search if hint provided 
    pre_detrend='none',         # 'none' | 'ellipsoidal' | 'reflection' | 'both' 
    Pbin_seconds_hint=None,     # needed for pre_detrend to be meaningful 
    bjd0_hint=0.0, 
    bic_delta=0.0, 
    # harmonic check 
    check_harmonics=False,      # compare P to 0.5P and 2P by BLS power 
    plot_harmonics=True,        # save folded plots for P, P/2, 2P (data only) 
    # plot controls 
    annotate_metric='bic',      # kept for API compat; unused in simple plots 
    plot_points_alpha=0.5 
): 
    '''
    Functionality:
        Perform a very fast BLS period search on a light curve with validation-safe scalar
        durations, optional pre-detrending using a binary hint period, optional harmonic
        checks (P/2, 2P), and optional local refinement around the best period. Returns
        quantities in seconds where applicable.

    Arguments:
        time_s (array-like): Time values in seconds.
        flux (array-like): Flux values (will be normalized internally).
        flux_err (array-like or None): Flux uncertainties (optional).
        DetrendingName (str or None): Name used for saving diagnostic plots.
        ID (str or int or None): Target identifier for file naming.
        min_period_days (float): Minimum period to search (days).
        max_period_days (float): Maximum period to search (days).
        q_eff (float or None): Effective duty cycle (duration/period); None auto-derives from cadence.
        decimate (int): Stride for coarse pass; >=1 (1 means no decimation).
        phi_tol (float): Phase tolerance factor controlling frequency grid spacing.
        max_evals (int): Hard cap on coarse grid evaluations.
        refine (bool): If True, do a fine 1D search around the coarse peak.
        pre_detrend (str): 'none'|'ellipsoidal'|'reflection'|'both' for optional pre-detrending.
        Pbin_seconds_hint (float or None): Binary period hint in seconds for pre-detrend models.
        bjd0_hint (float): Reference epoch hint for pre-detrending (seconds).
        bic_delta (float): BIC improvement threshold to accept detrending model removal.
        check_harmonics (bool): If True, compare power at P/2 and 2P to the best P.
        plot_harmonics (bool): If True, save simple phase-folded plots for P, P/2, 2P (data only).
        annotate_metric (str): Kept for compatibility; not used here.
        plot_points_alpha (float): Alpha for scatter plot points in folded plots.

    Returns:
        tuple:
            period_s (float): Best period in seconds.
            t0_s (float): Best epoch (transit time) in seconds (same zero-point as input time).
            depth (float): Estimated transit/eclipse depth (normalized units).
            duration_s (float): Estimated duration in seconds.
    '''

    # Helpers (validation-safe wrappers)
    def _safe_scalar_duration_for_periods(P_arr, q_guess, D_floor):
        '''
        Functionality:
            Compute a single safe scalar duration for an array of trial periods such that
            0 < D < 0.49 * min(P), guarding against pathological inputs.
        Arguments:
            P_arr (array-like): Period grid (days).
            q_guess (float): Duty cycle guess (dimensionless).
            D_floor (float): Minimum duration floor (days).
        Returns:
            float: A scalar duration (days) compatible with all periods in P_arr.
        '''
        P_arr = np.asarray(P_arr, dtype=float)
        P_arr = P_arr[np.isfinite(P_arr) & (P_arr > 0)]
        if P_arr.size == 0:
            raise ValueError("No valid periods in grid.")
        Pmin = float(np.min(P_arr))
        D = float(max(q_guess * Pmin, D_floor))
        if not np.isfinite(D) or D <= 0:
            D = float(max(D_floor, 1e-6))
        if D >= 0.49 * Pmin:
            D = 0.45 * Pmin
        return D

    def _safe_power_array(bls, P_arr, D_scalar):
        '''
        Functionality:
            Evaluate BLS power safely for an array of periods with a scalar duration,
            dropping/guarding invalid values.
        Arguments:
            bls (BoxLeastSquares): Prepared BLS object.
            P_arr (array-like): Periods (days).
            D_scalar (float): Duration (days).
        Returns:
            BoxLeastSquaresResults: Result from bls.power(P_arr_valid, D_scalar_sanitized).
        '''
        P_arr = np.asarray(P_arr, dtype=float)
        mask = np.isfinite(P_arr) & (P_arr > 0)
        P_arr = P_arr[mask]
        if P_arr.size == 0:
            raise ValueError("Empty/invalid period array for BLS.")
        D = float(D_scalar)
        Pmin = float(np.min(P_arr))
        if not np.isfinite(D) or D <= 0:
            D = 0.45 * Pmin
        elif D >= 0.49 * Pmin:
            D = 0.45 * Pmin
        return bls.power(P_arr, D)

    def _safe_power_scalar(bls, P_single, D_scalar):
        '''
        Functionality:
            Evaluate BLS power for a single period with a scalar duration, with bounds checks.
        Arguments:
            bls (BoxLeastSquares): Prepared BLS object.
            P_single (float): Trial period (days).
            D_scalar (float): Trial duration (days).
        Returns:
            BoxLeastSquaresResults: Single-period BLS evaluation.
        '''
        P = float(P_single)
        if not np.isfinite(P) or P <= 0:
            raise ValueError("Invalid scalar period for BLS.")
        D = float(D_scalar)
        if not np.isfinite(D) or D <= 0 or D >= 0.49 * P:
            D = 0.45 * P
        return bls.power(np.atleast_1d(P), D)

    # Preprocess
    t = np.asarray(time_s, dtype=float)  # time in seconds
    y = np.asarray(flux, dtype=float)    # flux values
    dy = None if flux_err is None else np.asarray(flux_err, dtype=float)

    # keep only finite rows across all provided arrays
    m = np.isfinite(t) & np.isfinite(y) & (np.ones_like(y, bool) if dy is None else np.isfinite(dy))
    t, y = t[m], y[m]; dy = (None if dy is None else dy[m])
    if t.size < 20:
        raise RuntimeError("Not enough points after filtering.")

    # standardize flux: subtract median, scale by robust std; avoids numerical issues
    y_med = np.nanmedian(y)
    y_std = np.nanstd(y - y_med)
    if not np.isfinite(y_std) or y_std <= 0:
        y_std = 1.0
    yN = (y - y_med) / y_std
    dyN = None if dy is None else (dy / y_std)

    # convert time to days for astropy BLS
    t_days_full = t / 86400.0

    # cadence (days) and data baseline (days)
    cad_days = np.nanmedian(np.diff(np.sort(t_days_full)))
    if not np.isfinite(cad_days) or cad_days <= 0:
        cad_days = 120.0 / 86400.0  # default 2-min cadence
    T_days = float(np.nanmax(t_days_full) - np.nanmin(t_days_full))
    if not np.isfinite(T_days) or T_days <= 0:
        raise ValueError("Invalid time baseline.")

    # Optional pre-detrending (BIC-gated)
    if pre_detrend != 'none' and Pbin_seconds_hint is not None:
        try:
            # Optional ellipsoidal variation removal
            if pre_detrend in ('ellipsoidal', 'both'):
                try:
                    d_flux, _, par = detrend_ellipsoidal(
                        time_s, yN, Pbin_seconds_hint,
                        bjd0=bjd0_hint,
                        bic_delta=bic_delta,
                        plot=True,
                        save_prefix=None,
                        detrending_name=DetrendingName,
                        return_model=True
                    )
                    if isinstance(par, dict) and par.get('removed', False):
                        yN = d_flux
                except NameError:
                    # detrend_ellipsoidal not defined in this context
                    pass
                except Exception:
                    # be robust to any modeling failure
                    pass
            # Optional reflection/emission removal
            if pre_detrend in ('reflection', 'both'):
                try:
                    d_flux, _, par = detrend_reflection(
                        time_s, yN, Pbin_seconds_hint,
                        bjd0=bjd0_hint,
                        bic_delta=bic_delta,
                        plot=True,
                        save_prefix=None,
                        detrending_name=DetrendingName,
                        return_model=True
                    )
                    if isinstance(par, dict) and par.get('removed', False):
                        yN = d_flux
                except NameError:
                    pass
                except Exception:
                    pass
        except Exception:
            pass

    # Coarse decimation
    if int(decimate) < 1:
        decimate = 1
    if decimate > 1:
        # stride-select a subset for very fast coarse scan
        sel = np.arange(0, t_days_full.size, int(decimate))
        t_days = t_days_full[sel]
        y_use = yN[sel]
        dy_use = None if dyN is None else dyN[sel]
    else:
        # use full set
        t_days, y_use, dy_use = t_days_full, yN, dyN

    # Frequency grid
    fmin = 1.0 / float(max_period_days)  # lowest frequency
    fmax = 1.0 / float(min_period_days)  # highest frequency
    if not (fmax > fmin):
        raise ValueError("min_period_days must be < max_period_days")

    # choose effective duty cycle if not provided
    if q_eff is None:
        q_eff = max(2.0 * cad_days / min_period_days, 0.004)  # >= two cadences; >=0.4%
        q_eff = min(q_eff, 0.12)  # cap to reasonable upper bound for duty cycle
    q_eff = float(q_eff)

    # phase-tolerance-driven frequency resolution
    df_by_phase = max((phi_tol * q_eff) / T_days, 1e-12)
    n_phase = int(np.ceil((fmax - fmin) / df_by_phase))
    n_eval = int(np.clip(n_phase, 256, max_evals))  # cap to avoid overwork
    f_grid = np.linspace(fmin, fmax, n_eval, endpoint=True)
    P_grid = 1.0 / f_grid  # trial periods (days)

    # construct a safe scalar duration for the whole grid
    D_floor = max(2.0 * cad_days, 1e-6)
    D_scalar = _safe_scalar_duration_for_periods(P_grid, q_eff, D_floor)

    # BLS coarse
    bls = BoxLeastSquares(t_days, y_use, dy_use)
    res = _safe_power_array(bls, P_grid, D_scalar)

    # select coarse best
    i_best = int(np.nanargmax(res.power))
    P_best = float(res.period[i_best])            # days
    t0_best = float(res.transit_time[i_best])     # days
    depth_best = float(res.depth[i_best])         # normalized
    dur_best = float(res.duration[i_best])        # days

    # Refine
    best_power = float(res.power[i_best])
    bls_full = BoxLeastSquares(t_days_full, yN, dyN)  # full-resolution BLS

    if refine:
        # local frequency window around coarse best
        f0 = 1.0 / P_best
        step = (f_grid[1] - f_grid[0]) if f_grid.size > 1 else df_by_phase
        f1 = max(f0 - 10 * step, fmin)
        f2 = min(f0 + 10 * step, fmax)
        if f2 <= f1:
            f2 = min(fmax, f1 + 5 * df_by_phase)
        n_ref = max(256, min(4096, 12 * (int((f2 - f1) / step) + 1)))
        f_ref = np.linspace(f1, f2, n_ref)
        P_ref = 1.0 / f_ref

        # recompute safe scalar duration for refined window
        D_ref_scalar = _safe_scalar_duration_for_periods(P_ref, q_eff, D_floor)

        # fine power sweep
        r2 = _safe_power_array(bls_full, P_ref, D_ref_scalar)
        j = int(np.nanargmax(r2.power))

        # small parabolic refine in frequency if interior point
        if 0 < j < (r2.period.size - 1):
            fx = 1.0 / r2.period[j-1:j+2]
            py = r2.power[j-1:j+2]
            denom = (fx[0] - 2*fx[1] + fx[2])
            if denom != 0 and np.all(np.isfinite([*fx, *py])):
                f_peak = float(fx[1] + 0.5 * ((py[0] - py[2]) / denom))
                f_lo, f_hi = float(min(fx[0], fx[2])), float(max(fx[0], fx[2]))
                f_peak = float(np.clip(f_peak, f_lo, f_hi))
                if np.isfinite(f_peak) and f_peak > 0:
                    P_peak = 1.0 / f_peak
                    try:
                        r3 = _safe_power_scalar(bls_full, P_peak, D_ref_scalar)
                        if float(r3.power[0]) > float(r2.power[j]):
                            r2, j = r3, 0
                    except Exception:
                        # if single-eval fails, keep r2
                        pass

        # adopt refined best
        P_best = float(r2.period[j])          # days
        t0_best = float(r2.transit_time[j])   # days
        depth_best = float(r2.depth[j])
        dur_best = float(r2.duration[j])      # days
        best_power = float(r2.power[j])

    # Plotting helper (simplified for harmonic check)
    def _plot_fold_with_models(period_s, label, suffix):
        '''
        Functionality:
            Save a simple phase-folded plot (data only) at a given trial period.
        Arguments:
            period_s (float): Period in seconds for plotting.
            label (str): Text label to include in the plot title (e.g., "P", "0.5P").
            suffix (str): Suffix for the filename.
        Returns:
            None
        '''
        period_d = period_s / 86400.0
        phase = ((t - t0_best * 86400.0) / period_s) % 1.0  # align to t0_best (seconds)
        order = np.argsort(phase)
        ph, yy = phase[order], yN[order]

        fig, ax = plt.subplots(figsize=(6.4, 4.0))
        ax.plot(ph, yy, '.', ms=2, alpha=plot_points_alpha)
        ax.set_xlabel("Phase")
        ax.set_ylabel("Normalized Flux")
        ax.set_title(f"Fold at {label}: {period_d:.6f} d")
        ax.axhline(0, ls=':', lw=1, alpha=0.5)
        ax.grid(True, ls=':', alpha=0.4)

        if DetrendingName is not None:
            base = _resolve_base_dir(None)
            my_folder = base / 'LightCurves' / 'Data_Preparation' / DetrendingName
            my_folder.mkdir(parents=True, exist_ok=True)
            target = ID or "target"
            fname = my_folder / f"{target}_harmonics_{suffix}.png"
            plt.savefig(fname, dpi=200, bbox_inches='tight')
        plt.close(fig)

    # Optional harmonic check (P, P/2, 2P)
    if check_harmonics and np.isfinite(P_best) and P_best > 0:
        # Plot baseline P (data-only) if requested
        if plot_harmonics:
            _plot_fold_with_models(P_best * 86400.0, "P", "P")

        # Freeze baseline to avoid mutation during loop
        P0_days = float(P_best)
        t0_0_days = float(t0_best)
        best_power_ini = float(best_power)

        # Initialize candidate with baseline
        cand_power = best_power_ini
        cand_P = P0_days
        cand_t0 = t0_0_days
        cand_depth = float(depth_best)
        cand_dur = float(dur_best)

        for mult in (0.5, 2.0):
            Ph = P0_days * mult  # test P/2 and 2P
            if not (min_period_days <= Ph <= max_period_days):
                continue
            try:
                D_h = _safe_scalar_duration_for_periods([Ph], q_eff, D_floor)
                rh = _safe_power_scalar(bls_full, Ph, D_h)

                if plot_harmonics:
                    suffix = f"{str(mult).replace('.','p')}P"
                    _plot_fold_with_models(Ph * 86400.0, f"{mult}P", suffix)

                pwr = float(rh.power[0])
                if pwr > cand_power:
                    # adopt improved harmonic
                    cand_power = pwr
                    cand_P = float(rh.period[0])
                    cand_t0 = float(rh.transit_time[0])
                    cand_depth = float(rh.depth[0])
                    cand_dur = float(rh.duration[0])
            except Exception:
                # ignore failures to keep robustness
                pass

        # Adopt the best candidate AFTER checking both harmonics
        best_power = cand_power
        P_best = cand_P
        t0_best = cand_t0
        depth_best = cand_depth
        dur_best = cand_dur

    # Return in seconds
    return (
        P_best * 86400.0,        # period_s
        t0_best * 86400.0,       # t0_s
        depth_best,              # depth (normalized)
        dur_best * 86400.0       # duration_s
    )


def _detect_single_dip_phase(
    phase, flux,
    expected_depth=None,            # from BLS (normalized units)
    expected_width_phase=None,      # duration_s / period_s
    n_bins=800,
    min_prom_frac=0.35,             # fraction of expected_depth for prominence
    sigma_mult=3.0,                 # robust noise sigma multiplier for fallback
    distance_mult=1.25              # min peak separation ~ width_bins * distance_mult
):
    '''
    Functionality:
        Detect whether a phase-folded light curve exhibits a single significant dip (eclipse/transit)
        by binning the phase, smoothing, inverting to convert dips to peaks, and applying a robust
        peak-finding routine with thresholds derived from expected depth/width or from robust noise.

    Arguments:
        phase (array-like): Phase values (will be wrapped to [0,1)).
        flux (array-like): Normalized flux values corresponding to phase.
        expected_depth (float or None): Expected dip depth (normalized units) to set prominence.
        expected_width_phase (float or None): Expected dip width as fraction of phase (duration/period).
        n_bins (int): Number of phase bins for median-binning.
        min_prom_frac (float): Fraction of expected_depth used as a prominence floor.
        sigma_mult (float): Multiplier on robust sigma for fallback prominence threshold.
        distance_mult (float): Minimum peak separation as a multiple of the expected width in bins.

    Returns:
        tuple:
            is_single (bool): True if exactly one significant dip is detected.
            n_dips (int): Number of detected dips.
            info (dict): Diagnostic info including bin centers, binned flux, inverted series,
                         thresholds, indices and properties of detected peaks.
    '''
    # wrap phases to [0,1)
    phase = np.asarray(phase, float) % 1.0
    flux  = np.asarray(flux,  float)

    # bin phases into n_bins using median in each bin
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    idx   = np.clip(np.digitize(phase, edges) - 1, 0, n_bins - 1)
    bflux = np.full(n_bins, np.nan)
    for k in range(n_bins):
        m = (idx == k)
        if np.any(m):
            bflux[k] = np.nanmedian(flux[m])

    # fill any NaNs with global median, then apply a simple wrap-around smoothing
    bflux = np.where(np.isfinite(bflux), bflux, np.nanmedian(bflux))
    bflux = 0.25*np.roll(bflux, -1) + 0.5*bflux + 0.25*np.roll(bflux, 1)

    # invert so dips become peaks after subtraction from baseline
    baseline = np.nanmedian(bflux)
    y = baseline - bflux  # inverted signal

    # robust noise estimate using MAD
    mad = np.nanmedian(np.abs(bflux - baseline))
    robust_sigma = 1.4826 * (mad if np.isfinite(mad) and mad > 0 else np.nanstd(bflux - baseline))

    # expected width in phase (if unavailable, use small default)
    if expected_width_phase is None or not np.isfinite(expected_width_phase):
        expected_width_phase = max(1.5 / n_bins, 0.002)  # tiny but > 0
    width_bins = int(max(2, expected_width_phase * n_bins))
    distance = int(max(width_bins * distance_mult, 3))  # min separation between peaks

    # prominence threshold combining expected depth and robust noise
    if expected_depth is None or not np.isfinite(expected_depth):
        prom = sigma_mult * (robust_sigma if np.isfinite(robust_sigma) else np.nanstd(y))
    else:
        prom = max(
            min_prom_frac * float(expected_depth),
            sigma_mult * (robust_sigma if np.isfinite(robust_sigma) else 0.0),
            1e-6
        )

    # try scipy's find_peaks; fall back to a simple contiguous-threshold detector
    peaks_idx = []
    try:
        from scipy.signal import find_peaks
        peaks_idx, props = find_peaks(
            y,
            prominence=prom,
            distance=distance,
            width=max(1, int(0.6 * width_bins))  # loose lower bound on width
        )
        prominences = props.get("prominences", np.array([]))
        widths = props.get("widths", np.array([]))
    except Exception:
        # fallback approach: contiguous runs above threshold
        thr = prom
        above = y > thr
        prominences = []
        widths = []
        k = 0
        while k < n_bins:
            if above[k]:
                start = k
                while k < n_bins and above[k]:
                    k += 1
                end = k
                center = (start + end - 1) // 2
                # enforce minimum distance from previous accepted center
                if len(peaks_idx) == 0 or (center - peaks_idx[-1]) >= distance:
                    peaks_idx.append(center)
                    prominences.append(np.nanmax(y[start:end]) if end > start else y[center])
                    widths.append(end - start)
            else:
                k += 1
        peaks_idx = np.array(peaks_idx, dtype=int)
        prominences = np.array(prominences, float)
        widths = np.array(widths, float)

    # number of detected dips
    n_dips = int(len(peaks_idx))

    # package diagnostics for downstream inspection/plots
    info = dict(
        n_bins=n_bins,
        width_bins=width_bins,
        distance=distance,
        prom_threshold=prom,
        robust_sigma=robust_sigma,
        peaks_idx=peaks_idx,
        prominences=prominences,
        widths=widths,
        binned_phase=np.linspace(0.5/n_bins, 1-0.5/n_bins, n_bins),
        binned_flux=bflux,
        inverted=y
    )
    return (n_dips == 1), n_dips, info


def iterative_bls_single_dip_search(
    time_s,
    flux,
    flux_err=None,
    DetrendingName=None,
    ID=None,
    min_period_days=0.05,
    max_period_days=90.0,
    presets_sequence=None,
    q_eff=None,
    pre_detrend='none',            # kept for API; NOT used during search
    Pbin_seconds_hint=None,        # kept for API
    bjd0_hint=0.0,
    bic_delta=0.0,
    check_harmonics=False,         # search logic not affected by detrending
    plot_harmonics=False,
    # dip-detection knobs
    detect_bins=800,
    min_prom_frac=0.35,
    sigma_mult=3.0,
    distance_mult=1.25,
    # POST-ONLY cleanup/detrending at {P/2, P, 2P}
    post_cleanup='both'            # 'none' | 'ellipsoidal' | 'reflection' | 'both'
):
    '''
    Functionality:
        Iteratively runs a coarse→fine BLS search using preset grids until a single
        significant dip is detected in the folded light curve. Optionally performs
        one-time post-clean detrending at {P/2, P, 2P} (ellipsoidal/reflection) and
        can generate comparison plots. Harmonics are checked by power only; detrending
        is applied after the final period choice.

    Arguments:
        time_s (array-like): Observation times in seconds.
        flux (array-like): Flux values (any normalization; internally standardized).
        flux_err (array-like or None): Flux uncertainties; optional.
        DetrendingName (str or None): Name used for output directories/files.
        ID (str|int|None): Target identifier for filenames.
        min_period_days (float): Minimum period to search (days).
        max_period_days (float): Maximum period to search (days).
        presets_sequence (list[dict] or None): Sequence of preset dicts (e.g., COARSE...FINEST).
        q_eff (float or None): Duty cycle guess; if None, auto-derived from cadence.
        pre_detrend (str): API placeholder (not used in search loop): 'none'|'ellipsoidal'|'reflection'|'both'.
        Pbin_seconds_hint (float or None): API placeholder for detrenders.
        bjd0_hint (float): Epoch hint (seconds) for detrenders.
        bic_delta (float): BIC threshold to accept detrending model removal.
        check_harmonics (bool): If True, BLS compares P vs P/2 vs 2P by power.
        plot_harmonics (bool): If True, saves folded data-only plots during search and post-clean models.
        detect_bins (int): Number of phase bins for dip detection.
        min_prom_frac (float): Minimum prominence as fraction of expected depth.
        sigma_mult (float): Robust sigma multiplier for fallback prominence threshold.
        distance_mult (float): Peak separation factor in bins (relative to width).
        post_cleanup (str): Post period-choice detrending: 'none'|'ellipsoidal'|'reflection'|'both'.

    Returns:
        tuple:
            period_s (float): Final period in seconds.
            t0_s (float): Estimated transit epoch in seconds (same zero-point as input times).
            depth (float): Estimated depth (normalized units).
            duration_s (float): Estimated duration in seconds.
            meta (dict): Metadata including preset used, detection info, and post-clean details if run.
    '''
    import numpy as np
    import matplotlib.pyplot as plt
    from pathlib import Path

    # Default preset ladder if none provided
    if presets_sequence is None:
        presets_sequence = [COARSE, MEDIUM, SANE, FINE, FINER, FINEST]

    # --- BASE-DIR OUTPUT ROOT (no signature change) ---
    _root = _resolve_base_dir(None)
    _out_root = _root / "LightCurves" / "Data_Preparation"
    if DetrendingName is not None:
        _out_dir = _out_root / str(DetrendingName)
    else:
        _out_dir = None
    if _out_dir is not None:
        _out_dir.mkdir(parents=True, exist_ok=True)

    # Helpers (post-only)
    def _apply_harmonic_detrend(time_s, yN, period_s, which, bic_delta, name, bjd0_hint):
        '''
        Functionality:
            Apply optional post-clean harmonic detrending (ellipsoidal/reflection/both)
            at a specified period, returning the cleaned flux and diagnostic info.

        Arguments:
            time_s (array-like): Times in seconds.
            yN (array-like): Normalized flux (zero-mean-ish) to detrend.
            period_s (float): Trial period (seconds) for harmonic model(s).
            which (str): 'none'|'ellipsoidal'|'reflection'|'both' detrend choice.
            bic_delta (float): BIC improvement threshold to accept detrending.
            name (str or None): Output folder suffix.
            bjd0_hint (float): Epoch (seconds) for detrenders.

        Returns:
            tuple:
                y_out (np.ndarray): Possibly detrended flux.
                info (dict): Details from detrending steps (params/errors).
        '''
        # Build output directory (base-dir aware)
        out_dir = (_out_root / str(name)) if name is not None else None
        if out_dir is not None:
            out_dir.mkdir(parents=True, exist_ok=True)
        base = ID or "target"  # filename stem

        y_out = yN
        info = {}

        # Optionally remove ellipsoidal variations
        if which in ('ellipsoidal', 'both'):
            try:
                save_prefix = None if out_dir is None else str(out_dir / f"{base}_ellip")
                d_flux, _, par = detrend_ellipsoidal(
                    time_s, y_out, period_s,
                    bjd0=bjd0_hint,
                    bic_delta=bic_delta,
                    plot=True,
                    save_prefix=save_prefix,          # where plots will be saved
                    detrending_name=name,
                    return_model=True
                )
                info['ellip'] = par
                if isinstance(par, dict) and par.get('removed', False):
                    y_out = d_flux
            except Exception as e:
                info['ellip_error'] = str(e)

        # Optionally remove reflection/emission
        if which in ('reflection', 'both'):
            try:
                save_prefix = None if out_dir is None else str(out_dir / f"{base}_refl")
                d_flux, _, par = detrend_reflection(
                    time_s, y_out, period_s,
                    bjd0=bjd0_hint,
                    bic_delta=bic_delta,
                    plot=True,
                    save_prefix=save_prefix,
                    detrending_name=name,
                    return_model=True
                )
                info['refl'] = par
                if isinstance(par, dict) and par.get('removed', False):
                    y_out = d_flux
            except Exception as e:
                info['refl_error'] = str(e)

        return y_out, info

    def _sine_flat_fit_stats(phase, y, dy=None):
        '''
        Functionality:
            Fit (i) flat model y=c and (ii) sinusoid y=c+a*sin(2πφ)+b*cos(2πφ),
            returning χ²_red and a BIC-like score for each, plus smooth curves.

        Arguments:
            phase (array-like): Phases in [0,1).
            y (array-like): Flux values aligned with phase.
            dy (array-like or None): Optional uncertainties.

        Returns:
            dict or None:
                flat: dict(chi2_red, bic)
                sine: dict(chi2_red, bic)
                ph_fine (np.ndarray), flat_curve (np.ndarray), sine_curve (np.ndarray)
        '''
        phase = np.asarray(phase, float); y = np.asarray(y, float)
        n = y.size
        if n < 5:
            return None
        if dy is None:
            w = np.ones_like(y)
        else:
            dy = np.asarray(dy, float)
            w = 1.0 / np.clip(dy, 1e-12, np.inf)**2

        X_flat = np.column_stack([np.ones(n)])
        X_sin  = np.column_stack([np.ones(n),
                                  np.sin(2*np.pi*phase),
                                  np.cos(2*np.pi*phase)])
        W = np.diag(w)

        def _fit(X):
            XT_W = X.T @ W
            beta = np.linalg.pinv(XT_W @ X) @ (XT_W @ y)
            yhat = X @ beta
            resid = y - yhat
            chi2 = float(np.sum((resid**2) * w))
            k = X.shape[1]
            dof = max(n - k, 1)
            chi2_red = chi2 / dof
            bic = chi2 + k * np.log(max(n,1))
            return beta, yhat, chi2_red, bic

        beta_f, _, chi2r_f, bic_f = _fit(X_flat)
        beta_s, _, chi2r_s, bic_s = _fit(X_sin)

        ph_fine = np.linspace(0, 1, 1000, endpoint=False)
        sine_curve = (beta_s[0]
                      + beta_s[1]*np.sin(2*np.pi*ph_fine)
                      + beta_s[2]*np.cos(2*np.pi*ph_fine))
        flat_curve = np.full_like(ph_fine, beta_f[0])
        return dict(
            flat=dict(chi2_red=chi2r_f, bic=bic_f),
            sine=dict(chi2_red=chi2r_s, bic=bic_s),
            ph_fine=ph_fine,
            flat_curve=flat_curve,
            sine_curve=sine_curve
        )

    def _post_plot_with_models(time_s, y_det, t0_s, period_s, tag, period_days,
                               out_dir, target, annotate_metric='bic', alpha_pts=0.5):
        '''
        Functionality:
            Fold cleaned data at period_s and plot points with flat/sine overlays;
            annotate and bold the preferred model by BIC (default) or χ²_red.
        '''
        phase = ((np.asarray(time_s, float) - t0_s) / period_s) % 1.0
        order = np.argsort(phase)
        ph, yy = phase[order], y_det[order]

        stats = _sine_flat_fit_stats(ph, yy, dy=None)

        fig, ax = plt.subplots(figsize=(6.4, 4.0))
        ax.plot(ph, yy, '.', ms=2, alpha=alpha_pts)
        ax.set_xlabel("Phase")
        ax.set_ylabel("Normalized Flux (post-clean)")
        ax.set_title(f"Post-clean fold at {tag} = {period_days:.6f} d")
        ax.axhline(0, ls=':', lw=1, alpha=0.5)
        ax.grid(True, ls=':', alpha=0.4)

        if stats is not None:
            f_bic, s_bic   = stats['flat']['bic'], stats['sine']['bic']
            f_chir, s_chir = stats['flat']['chi2_red'], stats['sine']['chi2_red']
            preferred = 'sine' if (annotate_metric or 'bic').lower() == 'bic' and s_bic < f_bic else \
                        ('sine' if s_chir < f_chir else 'flat')

            lw_flat = 2.5 if preferred == 'flat' else 1.5
            lw_sine = 2.5 if preferred == 'sine' else 1.5
            ax.plot(stats['ph_fine'], stats['flat_curve'], lw=lw_flat, alpha=0.9)
            ax.plot(stats['ph_fine'], stats['sine_curve'], lw=lw_sine, alpha=0.9)

            text = (
                "Model comparison (post-clean)\n"
                f"flat:  χ²_red={f_chir:.3f},  BIC={f_bic:.2f}\n"
                f"sine:  χ²_red={s_chir:.3f},  BIC={s_bic:.2f}\n"
                f"→ preferred: {preferred}"
            )
            ax.text(0.02, 0.02, text, transform=ax.transAxes,
                    ha='left', va='bottom', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.85, lw=0.5))

        if out_dir is not None:
            out_dir.mkdir(parents=True, exist_ok=True)
            fname = out_dir / f"{target}_postclean_{tag}.png"
            plt.savefig(fname, dpi=200, bbox_inches='tight')
        plt.close(fig)

    # Search loop (no detrending to choose period)
    best = None        # will store (period_s, t0_s, depth, duration_s)
    meta_best = None   # metadata for best attempt

    for preset in presets_sequence:
        # Run ultrafast BLS with current preset settings
        p_s, t0_s, depth, dur_s = bls_ultrafast2(
            time_s, flux, flux_err,
            DetrendingName=DetrendingName,
            ID=ID,
            min_period_days=min_period_days,
            max_period_days=max_period_days,
            q_eff=q_eff,
            pre_detrend='none',              # stable: do not detrend during search
            Pbin_seconds_hint=Pbin_seconds_hint,
            bjd0_hint=bjd0_hint,
            bic_delta=bic_delta,
            check_harmonics=check_harmonics, # optional P vs P/2 vs 2P power check
            plot_harmonics=plot_harmonics    # optional data-only plots
        )
        print('p_s: ' + str(p_s))  # debug progress

        # Phase-fold on found period and detect dips
        phase = ((np.asarray(time_s, float) - t0_s) / p_s) % 1.0
        is_single, n_dips, info = _detect_single_dip_phase(
            phase, np.asarray(flux, float),
            expected_depth=depth,
            expected_width_phase=(dur_s / p_s if (np.isfinite(dur_s) and np.isfinite(p_s) and p_s > 0) else None),
            n_bins=detect_bins,
            min_prom_frac=min_prom_frac,
            sigma_mult=sigma_mult,
            distance_mult=distance_mult
        )

        # Prepare meta-info for this pass
        meta = dict(
            preset_used=preset.copy(),
            period_s=p_s,
            t0_s=t0_s,
            depth=depth,
            duration_s=dur_s,
            single_dip=is_single,
            n_dips=n_dips,
            detect_info=info
        )

        # Update "best so far"
        best = (p_s, t0_s, depth, dur_s)
        meta_best = meta

        # If single dip achieved, optionally do post-clean detrending & plots
        if is_single:
            if post_cleanup != 'none':
                # Normalize once for detrenders
                y = np.asarray(flux, float)
                y_med = np.nanmedian(y)
                y_std = np.nanstd(y - y_med)
                if not np.isfinite(y_std) or y_std <= 0:
                    y_std = 1.0
                yN = (y - y_med) / y_std

                P_final_days = p_s / 86400.0  # for generating candidates
                candidates = []
                for mult, tag in [(0.5, "0p5P"), (1.0, "P"), (2.0, "2P")]:
                    Ph = P_final_days * mult
                    if min_period_days <= Ph <= max_period_days:
                        candidates.append((Ph, tag))

                cleanup_info = {}
                out_dir = _out_dir
                target = ID or "target"

                # Apply requested post-clean at each harmonic candidate
                for Ph, tag in candidates:
                    period_s = Ph * 86400.0
                    y_det, info_det = _apply_harmonic_detrend(
                        time_s=time_s, yN=yN, period_s=period_s,
                        which=post_cleanup, bic_delta=bic_delta,
                        name=DetrendingName, bjd0_hint=bjd0_hint
                    )
                    cleanup_info[tag] = info_det

                    # Post-clean diagnostic plots with model overlays
                    if plot_harmonics and out_dir is not None:
                        _post_plot_with_models(
                            time_s=time_s,
                            y_det=y_det,
                            t0_s=t0_s,
                            period_s=period_s,
                            tag=tag,
                            period_days=Ph,
                            out_dir=out_dir,
                            target=target,
                            annotate_metric='bic',
                            alpha_pts=0.5
                        )

                meta['post_cleanup'] = dict(method=post_cleanup, info=cleanup_info)

            # Return with meta if success
            return best + (meta,)

        # If not single and not the coarsest pass, try doubling the period as a quick fix
        if n_dips > 1 and preset is not COARSE:
            p2 = 2.0 * p_s  # double-period candidate
            if (min_period_days * 86400.0) <= p2 <= (max_period_days * 86400.0):
                phase2 = ((np.asarray(time_s, float) - t0_s) / p2) % 1.0
                is_single2, n_dips2, info2 = _detect_single_dip_phase(
                    phase2, np.asarray(flux, float),
                    expected_depth=depth,
                    expected_width_phase=(dur_s / p2 if (np.isfinite(dur_s) and np.isfinite(p2) and p2 > 0) else None),
                    n_bins=detect_bins,
                    min_prom_frac=min_prom_frac,
                    sigma_mult=sigma_mult,
                    distance_mult=distance_mult
                )
                if is_single2:
                    meta2 = dict(
                        preset_used=preset.copy(),
                        period_s=p2,
                        t0_s=t0_s,
                        depth=depth,
                        duration_s=dur_s,
                        single_dip=True,
                        n_dips=n_dips2,
                        detect_info=info2,
                    )
                    if post_cleanup != 'none':
                        # Normalize once
                        y = np.asarray(flux, float)
                        y_med = np.nanmedian(y)
                        y_std = np.nanstd(y - y_med)
                        if not np.isfinite(y_std) or y_std <= 0:
                            y_std = 1.0
                        yN = (y - y_med) / y_std

                        P_final_days = p2 / 86400.0
                        candidates = []
                        for mult, tag in [(0.5, "0p5P"), (1.0, "P"), (2.0, "2P")]:
                            Ph = P_final_days * mult
                            if min_period_days <= Ph <= max_period_days:
                                candidates.append((Ph, tag))

                        cleanup_info = {}
                        out_dir = _out_dir
                        target = ID or "target"

                        for Ph, tag in candidates:
                            period_s = Ph * 86400.0
                            y_det, info_det = _apply_harmonic_detrend(
                                time_s=time_s, yN=yN, period_s=period_s,
                                which=post_cleanup, bic_delta=bic_delta,
                                name=DetrendingName, bjd0_hint=bjd0_hint
                            )
                            cleanup_info[tag] = info_det
                            if plot_harmonics and out_dir is not None:
                                _post_plot_with_models(
                                    time_s=time_s, y_det=y_det, t0_s=t0_s,
                                    period_s=period_s, tag=tag, period_days=Ph,
                                    out_dir=out_dir, target=target,
                                    annotate_metric='bic', alpha_pts=0.5
                                )
                        meta2['post_cleanup'] = dict(method=post_cleanup, info=cleanup_info)

                    return (p2, t0_s, depth, dur_s, meta2)

    # If we exit the loop without a single dip, return the best (finest) result with a note
    meta_best['note'] = "Single dip not achieved; returning the finest-pass result (no post-clean)."
    return best + (meta_best,)

# Small utilities
def _sine_phase_model(phase, A, phi, C):
    '''
    Functionality:
        Evaluate a single-harmonic sinusoidal model on phase: A*sin(2π*phase + phi) + C.
    Arguments:
        phase (array-like or float): Phases in [0,1) (not enforced).
        A (float): Amplitude of sinusoid.
        phi (float): Phase offset (radians).
        C (float): Constant offset.
    Returns:
        np.ndarray or float: Model values at given phase(s).
    '''
    # Simple sinusoidal component often used for reflection/ellipsoidal proxies
    return A * np.sin(2 * np.pi * phase + phi) + C


def _wrap_dist(phase, center):
    '''
    Functionality:
        Compute the smallest wrap-aware distance between a phase and a center on the unit circle.
    Arguments:
        phase (array-like or float): Phase(s) in [0,1) (not enforced).
        center (float): Center phase in [0,1) (not enforced).
    Returns:
        np.ndarray or float: Minimal circular distance(s) in [0,0.5].
    '''
    # Map difference to (-0.5, 0.5] then take absolute value
    return np.abs((phase - center + 0.5) % 1.0 - 0.5)


def _gauss_primary_model(phase, depth, mu, sigma, C):
    '''
    Functionality:
        Primary eclipse proxy using a wrapped Gaussian dip centered at phase mu:
        C - depth * exp(-0.5 * (d/sigma)^2), where d is wrap-aware phase distance.

    Arguments:
        phase (array-like or float): Phase(s) in [0,1) (not enforced).
        depth (float): Positive depth of the eclipse (amplitude of the dip).
        mu (float): Center phase of the eclipse.
        sigma (float): Width parameter of the Gaussian in phase units.
        C (float): Baseline level.

    Returns:
        np.ndarray or float: Modeled flux values at provided phase(s).
    '''
    d = _wrap_dist(phase, mu)  # wrap-aware distance to center
    # Gaussian dip subtracted from baseline C; clip sigma to avoid division by zero
    return C - depth * np.exp(-0.5 * (d / np.clip(sigma, 1e-6, None)) ** 2)


def _initial_guesses_sine(phase, flux):
    '''
    Functionality:
        Provide robust initial guesses (A0, phi0, C0) for a single-harmonic sinusoid
        y ≈ C + A*sin(2π*phase + phi), using percentile-based amplitude and
        a complex-exponential projection for the phase.

    Arguments:
        phase (array-like): Phases corresponding to flux.
        flux (array-like): Flux values.

    Returns:
        tuple:
            A0 (float): Initial amplitude guess (≥ ~0).
            phi0 (float): Initial phase offset guess (radians).
            C0 (float): Initial constant offset (median of flux).
    '''
    # Baseline guess from median
    C0 = np.nanmedian(flux)
    # Peak-to-peak robust amplitude estimate
    amp_pp = np.nanpercentile(flux, 95) - np.nanpercentile(flux, 5)
    A0 = 0.5 * amp_pp if (np.isfinite(amp_pp) and amp_pp > 0) else (np.nanstd(flux) or 1e-4)
    # Phase from projection onto the unit phasor exp(i*2π*phase)
    z = np.exp(1j * 2 * np.pi * phase)
    proj = np.nansum((flux - C0) * z)
    phi0 = -np.angle(proj)
    return A0, phi0, C0
    
    
def _fit_sine_on_phase(phase, flux, mask=None, sigma=3.0, max_iter=5, p0=None):
    '''
    Functionality:
        Robustly fit a sinusoid to phase-folded data with iterative sigma-clipping:
            model = A * sin(2π*phase + phi) + C

    Arguments:
        phase (array-like): Phase values (arbitrary range is OK; not strictly enforced to [0,1)).
        flux (array-like): Flux values corresponding to `phase`.
        mask (array-like of bool or None): If provided, True marks samples initially included.
        sigma (float): Sigma multiplier used for iterative clipping on residuals.
        max_iter (int): Maximum number of clipping/fit iterations.
        p0 (tuple or None): Initial guesses (A, phi, C). If None, guessed via `_initial_guesses_sine`.

    Returns:
        tuple:
            popt (np.ndarray[3]): Best-fit parameters (A, phi, C).
            good_mask (np.ndarray[bool]): Final mask of samples used in the fit after clipping.
    '''
    # Ensure arrays
    phase = np.asarray(phase)
    flux  = np.asarray(flux)

    # Start from finite data only
    good = np.isfinite(phase) & np.isfinite(flux)

    # Apply optional external mask
    if mask is not None:
        good &= mask

    # If mask removes everything, fall back to finite-only
    if not np.any(good):
        good = np.isfinite(phase) & np.isfinite(flux)

    # Initial parameter guess if not supplied
    if p0 is None:
        p0 = _initial_guesses_sine(phase[good], flux[good])

    popt = np.array(p0, dtype=float)

    # Iterative fit + sigma clip loop
    for _ in range(max_iter):
        try:
            # Nonlinear least squares fit
            popt, _ = curve_fit(_sine_phase_model, phase[good], flux[good], p0=popt, maxfev=20000)
        except Exception:
            # If fit fails, keep the last params and break
            break

        # Compute residuals over *all* points to evaluate clip on global distribution
        resid = flux - _sine_phase_model(phase, *popt)

        # Robust scale with MAD on the "good" subset
        med = np.nanmedian(resid[good])
        mad = np.nanmedian(np.abs(resid[good] - med))
        if not (np.isfinite(mad) and mad > 0):
            # Fallback to std → convert to MAD-equivalent
            s = np.nanstd(resid[good])
            mad = (s / 1.4826) if (np.isfinite(s) and s > 0) else 1e-6

        # Sigma clipping threshold
        thr = sigma * 1.4826 * mad

        # New mask after clipping
        new_good = good & (np.abs(resid - med) <= thr)

        # Stop if the mask no longer changes
        if new_good.sum() == good.sum() and np.all(new_good == good):
            break
        good = new_good

    return popt, good


def _fit_primary_gaussian(phase, flux, window_half_width=0.2):
    '''
    Functionality:
        Fit a wrapped Gaussian dip to the deepest feature near minimum flux to
        model the *primary* eclipse in phase.

        Model:
            f(phase) = C - depth * exp(-0.5 * (wrap_dist(phase, mu) / sigma)^2)

    Arguments:
        phase (array-like): Phase samples.
        flux  (array-like): Flux samples aligned with `phase`.
        window_half_width (float): Half-width (in phase units) for local fit window around the min.

    Returns:
        tuple or None:
            (depth, mu, sigma, C) on success, where
                depth > 0, mu in [0,1), sigma > 0, C baseline.
            None on failure.
    '''
    # Fail fast on very small inputs
    if len(phase) < 10:
        return None

    # Baseline and seed guesses from the minimum
    C0 = np.nanmedian(flux)
    idx_min = int(np.nanargmin(flux))
    mu0 = float(phase[idx_min])                                 # center near the min
    depth0 = float(np.clip(C0 - np.nanmin(flux), 1e-8, None))   # dip amplitude (positive)
    sigma0 = 0.02                                               # initial narrow width

    # Restrict to local window to avoid fitting the secondary/other features
    d = _wrap_dist(phase, mu0)
    local = d <= window_half_width
    p_use = phase[local]; f_use = flux[local]
    if p_use.size < 8:
        # Fallback: use entire curve if local window too small
        p_use, f_use = phase, flux

    # Parameter vector and bounds
    p0 = [depth0, mu0, sigma0, C0]
    bounds = ([0.0, -np.inf, 1e-4, -np.inf],       # depth ≥ 0, sigma > 0
              [1.0,  np.inf, 0.3,   np.inf])       # practical caps for stability

    try:
        # Constrained fit
        popt, _ = curve_fit(_gauss_primary_model, p_use, f_use, p0=p0, bounds=bounds, maxfev=20000)
        depth, mu, sigma, C = map(float, popt)
        # Wrap mu to [0,1) for consistency
        mu = ((mu % 1.0) + 1.0) % 1.0
        # Clamp sigma to reasonable bounds
        sigma = float(np.clip(sigma, 1e-6, 0.2))
        return depth, mu, sigma, C
    except Exception:
        return None


def _primary_mask_from_fit(phase, mu, sigma, k_sigma=2.5):
    '''
    Functionality:
        Construct a boolean mask that is True *inside* the primary eclipse region
        modeled by a Gaussian centered at `mu` with width `sigma` (scaled by k_sigma).

    Arguments:
        phase (array-like): Phase values.
        mu (float): Center of the primary eclipse in phase units.
        sigma (float): Gaussian sigma in phase units (>0).
        k_sigma (float): Multiple of sigma used to define the eclipse band.

    Returns:
        np.ndarray[bool]: True where samples lie within k_sigma * sigma of `mu`.
    '''
    # Ensure nonzero width and return inclusion mask
    return _wrap_dist(phase, mu) <= (k_sigma * max(float(sigma), 1e-6))


def _bic(y, yhat, k):
    '''
    Functionality:
        Compute the Bayesian Information Criterion (BIC) under Gaussian errors:
            BIC = n * ln(RSS/n) + k * ln(n)

    Arguments:
        y (array-like): Observed values.
        yhat (array-like): Model-predicted values.
        k (int): Number of free parameters in the model.

    Returns:
        float: BIC value (smaller is better). Returns +inf if not enough data.
    '''
    y = np.asarray(y); yhat = np.asarray(yhat)
    finite = np.isfinite(y) & np.isfinite(yhat)
    n = finite.sum()
    if n <= k + 1:
        # Not enough degrees of freedom
        return np.inf
    rss = np.nansum((y[finite] - yhat[finite])**2)
    rss = max(rss, 1e-30)  # guard against log(0)
    return n * np.log(rss / n) + k * np.log(n)


def _ensure_dir(path):
    '''
    Functionality:
        Ensure the parent directory for `path` exists; create it if needed.

    Arguments:
        path (str or None): A file path (not a directory). If None/empty, do nothing.

    Returns:
        None
    '''
    if path and len(path) > 0:
        os.makedirs(os.path.dirname(path), exist_ok=True)


# Plotting helpers
def _plot_primary_gaussian(phase, flux, gauss_params, save_path=None, show=False, title_suffix=""):
    '''
    Functionality:
        Plot phased flux and (optionally) the fitted primary Gaussian dip; shade the
        primary mask region (±2.5σ by default). Useful for QA.

    Arguments:
        phase (array-like): Phase values.
        flux (array-like): Flux values.
        gauss_params (tuple or None): (depth, mu, sigma, C); if None, plot data only.
        save_path (str or None): If provided, save figure to this path.
        show (bool): If True, display the figure interactively.
        title_suffix (str): Extra text appended to plot title.

    Returns:
        None
    '''
    plt.figure(figsize=(9, 4.5))
    # Raw points
    plt.scatter(phase, flux, s=4, alpha=0.6, label='Phased flux')

    # Dense phase grid for smooth model curve
    ph_dense = np.linspace(0, 1, 2000)
    if gauss_params is not None:
        depth, mu, sigma, C = gauss_params
        model_dense = _gauss_primary_model(ph_dense, depth, mu, sigma, C)
        plt.plot(ph_dense, model_dense, lw=2, label=f'Primary Gaussian fit (μ={mu:.3f}, σ={sigma:.3f})')

        # Shade the k-sigma band around the primary center
        k = 2.5
        left = (mu - k * sigma) % 1.0
        right = (mu + k * sigma) % 1.0
        if left < right:
            plt.axvspan(left, right, alpha=0.15, label='Primary mask')
        else:
            # Wrapped case
            plt.axvspan(0, right, alpha=0.15)
            plt.axvspan(left, 1, alpha=0.15, label='Primary mask')

    plt.xlabel("Phase")
    plt.ylabel("Flux")
    plt.title(f"Primary Gaussian fit{title_suffix}")
    plt.legend(loc='best')

    # Save if requested
    if save_path:
        _ensure_dir(save_path)
        plt.savefig(save_path, bbox_inches='tight', dpi=200)
    if show:
        plt.show()
    plt.close()


def _plot_sine_fit(phase, flux, popt, mask=None, save_path=None, show=False, title="Sine fit"):
    '''
    Functionality:
        Plot phased data and the fitted sine curve. Optionally display which points
        were used in the fit vs masked.

    Arguments:
        phase (array-like): Phase values.
        flux (array-like): Flux values.
        popt (tuple or None): Best-fit parameters (A, phi, C); if None, plot data only.
        mask (array-like of bool or None): If provided, True means "used in fit".
        save_path (str or None): If provided, save figure to this path.
        show (bool): If True, display figure interactively.
        title (str): Plot title.

    Returns:
        None
    '''
    plt.figure(figsize=(9, 4.5))

    if mask is None:
        # No mask → plot all points uniformly
        plt.scatter(phase, flux, s=4, alpha=0.6, label='Phased flux')
    else:
        # Split into used vs masked
        used = mask
        plt.scatter(phase[~used], flux[~used], s=4, alpha=0.3, label='Masked (primary)')
        plt.scatter(phase[used],  flux[used],  s=4, alpha=0.8, label='Used for fit')

    # Dense curve for model overlay
    ph_dense = np.linspace(0, 1, 2000)
    if popt is not None:
        A, phi, C = popt
        plt.plot(ph_dense, _sine_phase_model(ph_dense, A, phi, C), lw=2,
                 label=f'Fit: A={A:.4g}, φ={phi:.3f}')

    plt.xlabel("Phase")
    plt.ylabel("Flux")
    plt.title(title)
    plt.legend(loc='best')

    # Save if requested
    if save_path:
        _ensure_dir(save_path)
        plt.savefig(save_path, bbox_inches='tight', dpi=200)
    if show:
        plt.show()
    plt.close()


def _wrap_bands(mu, half_width, phase_min, phase_max):
    '''
    Functionality:
        Compute visible (left, right) intervals of a band centered at `mu` with
        half-width `half_width` for a given plot/view window [phase_min, phase_max],
        accounting for wrapping by ±1 in phase.

    Arguments:
        mu (float): Center phase of the band.
        half_width (float): Half-width of the band (phase units).
        phase_min (float): Lower bound of visible phase axis.
        phase_max (float): Upper bound of visible phase axis.

    Returns:
        list[tuple[float, float]]: Visible intervals [(L, R), ...] intersecting the window.
    '''
    # Consider the band centered at mu shifted by -1, 0, +1 so it appears in-window
    candidates = [mu - 1.0, mu, mu + 1.0]
    bands = []
    for m in candidates:
        left  = m - half_width
        right = m + half_width
        # Intersect the band with the visible window
        L = max(left, phase_min)
        R = min(right, phase_max)
        if L < R:
            bands.append((L, R))
    return bands

def _plot_trend_and_detrended_with_mask(
    phase, flux, trend, primary_params, k_sigma,
    multiplicative, detrend_C,
    out_prefix, title_core="", show=False
):
    '''
    Functionality:
        Produce a pair of diagnostic plots:
          1) Trend over the raw phased flux (with shaded primary mask band),
          2) Detrended flux (same band shading).
        Detrending is performed to generate the second plot using the same
        prescription as in the detrenders (additive or multiplicative).

    Arguments:
        phase (array-like): Phase values of the light curve.
        flux (array-like): Raw flux values.
        trend (array-like): Trend model values aligned with phase/flux.
        primary_params (tuple or None): (depth, mu, sigma, C) describing primary; if None, no band.
        k_sigma (float): Width multiplier for shaded band (k * sigma).
        multiplicative (bool): If True, plot detrended as flux / (trend / C); else subtract (trend - C).
        detrend_C (float): C parameter from the sine model; used to center multiplicative detrending.
        out_prefix (str): File path prefix (directory will be created if needed).
        title_core (str): Title prefix used in both plots.
        show (bool): If True, display figures interactively.

    Returns:
        None
    '''
    # Construct detrended vector exactly as used in detrenders
    if multiplicative:
        detrended = flux / np.clip(trend / detrend_C, 1e-8, None)
    else:
        detrended = flux - (trend - detrend_C)

    # Establish axis range for shading computations
    pmin, pmax = np.nanmin(phase), np.nanmax(phase)

    # Figure 1: trend over raw flux with primary band
    fig1 = plt.figure(figsize=(10, 5))
    ax1 = fig1.add_subplot(111)
    ax1.scatter(phase, flux, s=8, alpha=0.7, label='Flux', linewidths=0)

    # Plot a clean trend line by sorting phases
    order = np.argsort(phase)
    ax1.plot(phase[order], trend[order], lw=1.5, label='Sine trend', zorder=3)

    if primary_params is not None:
        _, mu_p, sig_p, _ = primary_params
        half_width = float(k_sigma) * float(sig_p)
        # Shade all visible segments accounting for wrapping
        for L, R in _wrap_bands(mu_p, half_width, pmin, pmax):
            ax1.axvspan(L, R, color='tab:orange', alpha=0.25, label='Primary mask')
        # Deduplicate legend entries
        handles, labels = ax1.get_legend_handles_labels()
        uniq = dict(zip(labels, handles))
        ax1.legend(uniq.values(), uniq.keys(), loc='best')
    else:
        ax1.legend(loc='best')

    ax1.set_xlabel('Phase')
    ax1.set_ylabel('Flux')
    ax1.set_title(f'{title_core} — trend over flux')

    f1 = out_prefix + '_trend_over_flux.png'
    _ensure_dir(f1)  # minimal fix: pass the file path, not dirname
    fig1.savefig(f1, bbox_inches='tight', dpi=150)
    if show:
        plt.show()
    plt.close(fig1)

    # Figure 2: detrended flux with same band shading
    fig2 = plt.figure(figsize=(10, 5))
    ax2 = fig2.add_subplot(111)
    ax2.scatter(phase, detrended, s=8, alpha=0.7, label='Detrended flux', linewidths=0)

    if primary_params is not None:
        _, mu_p, sig_p, _ = primary_params
        half_width = float(k_sigma) * float(sig_p)
        for L, R in _wrap_bands(mu_p, half_width, pmin, pmax):
            ax2.axvspan(L, R, color='tab:orange', alpha=0.25, label='Primary mask')
        handles, labels = ax2.get_legend_handles_labels()
        uniq = dict(zip(labels, handles))
        ax2.legend(uniq.values(), uniq.keys(), loc='best')
    else:
        ax2.legend(loc='best')

    ax2.set_xlabel('Phase')
    ax2.set_ylabel('Flux (detrended)')
    ax2.set_title(f'{title_core} — detrended')

    f2 = out_prefix + '_detrended.png'
    _ensure_dir(f2)  # minimal fix: pass the file path, not dirname
    fig2.savefig(f2, bbox_inches='tight', dpi=150)
    if show:
        plt.show()
    plt.close(fig2)


def detrend_ellipsoidal(
    time_s, flux, Pbin_s, bjd0=0.0,
    mask_primary=True, primary_k_sigma=2.5, primary_window=0.2,
    sigma_clip=3.0, max_iter=5,
    multiplicative=False, bic_delta=0.0,
    plot=True, show=False, save_prefix=None, return_model=True, detrending_name=None
):
    '''
    Functionality:
        Remove ellipsoidal variation (sinusoid at half the binary period, Pbin/2) by
        robustly fitting y ≈ a*sin(2πφ) + b*cos(2πφ) + c to the light curve folded at
        P = Pbin/2, while masking ONLY the primary eclipse. Applies a BIC-based decision:
            ΔBIC = BIC_const - BIC_sine
        If ΔBIC >= bic_delta, subtract (or divide) the sinusoid; otherwise, keep flux.

    Arguments:
        time_s (array-like): Time stamps in seconds.
        flux (array-like): Flux values.
        Pbin_s (float): Binary period in seconds.
        bjd0 (float): Reference epoch in seconds for phase folding.
        mask_primary (bool): If True, mask primary eclipse using a local Gaussian fit.
        primary_k_sigma (float): Mask half-width multiplier (k*σ) around the primary center.
        primary_window (float): Local window half-width for the Gaussian fit (phase units).
        sigma_clip (float): Sigma threshold for iterative residual clipping during fit.
        max_iter (int): Max iterations for clipping.
        multiplicative (bool): If True, apply multiplicative removal (divide trend/c); else subtract (trend - c).
        bic_delta (float): Threshold on ΔBIC to accept sinusoid removal.
        plot (bool): If True, save a comparison plot of sine vs constant fits.
        show (bool): If True, display the plot interactively.
        save_prefix (str or None): Filename stem for saved figures (directory auto-created).
        return_model (bool): If True, return (detrended, trend, params); else return only detrended.
        detrending_name (str or None): Subdirectory suffix under ../LightCurves/Data_Preparation/.

    Returns:
        If return_model:
            tuple:
                detrended (np.ndarray): Flux after removing accepted trend (or original if rejected).
                trend (np.ndarray): Fitted trend evaluated at all samples.
                params (dict): Details (A, phi, C, period_used_s, removed flag, BICs, primary_gauss).
        Else:
            detrended (np.ndarray): As above.
    '''
    # Inputs to arrays
    time_s = np.asarray(time_s, float)
    flux   = np.asarray(flux,   float)

    # Ellipsoidal modulation period is Pbin/2
    P_trend = float(Pbin_s) / 2.0

    # Phase for the trend model
    phase = ((time_s - bjd0) / P_trend) % 1.0

    # Build primary-eclipse mask, if requested
    primary_params = None
    primary_mask = None
    if mask_primary:
        try:
            primary_params = _fit_primary_gaussian(phase, flux, window_half_width=primary_window)
        except Exception:
            primary_params = None
        if primary_params is not None:
            _, mu_p, sig_p, _ = primary_params
            try:
                primary_mask = _primary_mask_from_fit(phase, mu_p, sig_p, k_sigma=primary_k_sigma)
            except Exception:
                primary_mask = None

    # Design matrix: sin, cos, constant at φ = (time - bjd0)/P_trend
    two_pi_phi = 2.0 * np.pi * phase
    X = np.column_stack([np.sin(two_pi_phi), np.cos(two_pi_phi), np.ones_like(two_pi_phi)])

    # Valid points: finite and not in primary mask
    valid = np.isfinite(flux) & np.isfinite(phase)
    if primary_mask is not None:
        valid &= (~primary_mask)

    y = flux.copy()

    # Iterative sigma-clipping on residuals with linear least squares
    for _ in range(max_iter):
        sel = valid & np.isfinite(y)
        if sel.sum() < 10:
            break
        a, b, c = np.linalg.lstsq(X[sel], y[sel], rcond=None)[0]
        yhat = (X @ np.array([a, b, c]))
        resid = y - yhat
        s = np.nanstd(resid[sel])
        if not np.isfinite(s) or s == 0:
            break
        new_sel = sel & (np.abs(resid) < sigma_clip * s)
        if new_sel.sum() == sel.sum():
            break
        valid = new_sel

    # Final fit on kept points; fallback to median constant if underdetermined
    sel = valid & np.isfinite(y)
    if sel.sum() >= 3:
        a, b, c = np.linalg.lstsq(X[sel], y[sel], rcond=None)[0]
    else:
        a, b, c = 0.0, 0.0, float(np.nanmedian(y[sel]) if sel.any() else np.nanmedian(y))

    # Trend evaluated everywhere
    trend = (X @ np.array([a, b, c]))

    # BIC comparison on the *used* subset
    y_used = y[sel]
    yhat_sine = trend[sel]
    const_level = float(np.nanmedian(y_used))
    yhat_const  = np.full_like(y_used, const_level)

    def _bic_local(ytrue, ypred, k):
        '''
        Functionality:
            Compute a simple BIC-like score for a k-parameter model.
    
        Arguments:
            ytrue (array-like): Observed data.
            ypred (array-like): Model prediction.
            k (int): Number of free parameters in the model.
    
        Returns:
            float:
                BIC score. Lower is better. Returns inf if insufficient data.
        '''
        n = ytrue.size
        if n <= k or n == 0:
            return np.inf
        rss = np.nansum((ytrue - ypred)**2)
        rss = max(rss, 1e-300)
        return n * np.log(rss / n) + k * np.log(n)

    bic_sine  = _bic_local(y_used, yhat_sine, k=3)
    bic_const = _bic_local(y_used, yhat_const, k=1)
    delta = float(bic_const - bic_sine)  # positive favors sine

    # Apply decision (subtract or divide the oscillatory part)
    if delta >= bic_delta:
        if multiplicative:
            detrended = flux / np.clip(trend / c, 1e-12, None)
        else:
            detrended = flux - (trend - c)
        removed = True
    else:
        detrended = flux.copy()
        removed = False

    # Optional plot
    if plot:
        base_dir = _resolve_base_dir(None)
        out_dir = os.path.join(base_dir, "LightCurves", "Data_Preparation")
        if detrending_name:
            out_dir = os.path.join(out_dir, detrending_name)
        os.makedirs(out_dir, exist_ok=True)

        base = os.path.basename(save_prefix) if save_prefix else (detrending_name if detrending_name else "run")
        out_prefix = os.path.join(out_dir, f"{base}_ellipsoidal")

        ph = phase % 1.0
        sorter = np.argsort(ph)
        ph_s, f_s, tr_s = ph[sorter], flux[sorter], trend[sorter]

        # Small phase-bin helper for a smoother data overlay
        def _phase_bin(x, y, nbins=180, robust=True):
            '''
            Functionality:
                Bin data by phase and compute a representative value per bin.
        
            Arguments:
                x (array-like): Phase values in [0,1).
                y (array-like): Flux or other values corresponding to x.
                nbins (int): Number of phase bins.
                robust (bool): If True use median, else mean.
        
            Returns:
                (np.ndarray, np.ndarray):
                    Bin centers (phase), binned values.
            '''
            edges = np.linspace(0.0, 1.0, nbins + 1)
            idx = np.digitize(x, edges) - 1
            xc, yc = [], []
            for i in range(nbins):
                seli = (idx == i)
                if not np.any(seli):
                    continue
                yi = y[seli]
                xc.append(0.5*(edges[i] + edges[i+1]))
                yc.append(np.nanmedian(yi) if robust else np.nanmean(yi))
            return np.array(xc), np.array(yc)

        xb, yb = _phase_bin(ph_s, f_s, nbins=180, robust=True)
        preferred = 'sine' if bic_sine <= bic_const else 'flat'
        title = f"Ellipsoidal @ P = {P_trend/86400:.6f} d"

        fig, ax = plt.subplots(figsize=(8.6, 4.6))
        ax.plot(ph_s, f_s, '.', ms=1.8, alpha=0.35, label='data (points)')
        if xb.size:
            ax.plot(xb, yb, lw=1.6, alpha=0.9, label='data (binned)')
        ax.plot(ph_s, tr_s, lw=2.4 if preferred=='sine' else 1.2, alpha=0.95,
                label=f"sine fit (BIC={bic_sine:.2f})")
        ax.hlines(const_level, 0, 1, linewidth=2.4 if preferred=='flat' else 1.2,
                  alpha=0.95, label=f"constant (BIC={bic_const:.2f})")

        # Shade ±kσ around primary if available
        if primary_params is not None:
            _, mu_p, sig_p, _ = primary_params
            w = primary_k_sigma * sig_p
            for center in [mu_p % 1.0, (mu_p % 1.0) - 1, (mu_p % 1.0) + 1]:
                ax.axvspan(center - w, center + w, color='k', alpha=0.05, lw=0)

        ax.set_xlim(0, 1)
        ax.set_xlabel("Phase (folded at P/2)")
        ax.set_ylabel("Flux")
        ax.set_title(title)
        ax.grid(True, ls=':', alpha=0.35)
        ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), borderaxespad=0.0, framealpha=0.95)
        info = f"Preferred: {preferred}\nApplied removal: {'YES' if removed else 'NO'}"
        ax.text(0.01, 0.02, info, transform=ax.transAxes, ha='left', va='bottom', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, lw=0.5))
        plt.tight_layout(rect=[0, 0, 0.82, 1])
        plt.savefig(out_prefix + "_compare.png", dpi=220, bbox_inches='tight')
        if show:
            plt.show()
        plt.close(fig)

    if return_model:
        # Convert (a,b,c) into amplitude/phase for reference
        A = float(np.hypot(a, b))
        phi = float(np.arctan2(b, a))
        params = dict(
            A=A, phi=phi, C=float(c), period_used_s=float(P_trend), bjd0=float(bjd0),
            removed=removed, bic_sine=float(bic_sine), bic_const=float(bic_const),
            delta_bic=delta,
            primary_gauss=(dict(depth=primary_params[0], mu=primary_params[1], sigma=primary_params[2], C=primary_params[3])
                           if primary_params else None)
        )
        return detrended, trend, params
    return detrended


def detrend_reflection(
    time_s, flux, Pbin_s, bjd0=0.0,
    mask_primary=True, primary_k_sigma=2.5, primary_window=0.2,
    sigma_clip=3.0, max_iter=5,
    multiplicative=False, bic_delta=0.0,
    plot=True, show=False, save_prefix=None, return_model=True, detrending_name=None
):
    '''
    Functionality:
        Remove reflection/emission modulation (sinusoid at the *binary period*, Pbin)
        with the same robust linear strategy used for ellipsoidal detrending, but
        folding at P = Pbin. Only the primary eclipse is masked. A BIC-based decision
        controls whether to apply the removal.

    Arguments:
        time_s (array-like): Time stamps in seconds.
        flux (array-like): Flux values.
        Pbin_s (float): Binary period in seconds.
        bjd0 (float): Reference epoch in seconds for phase folding.
        mask_primary (bool): If True, mask primary eclipse using a Gaussian fit.
        primary_k_sigma (float): Mask half-width multiplier.
        primary_window (float): Local window half-width for the Gaussian fit (phase units).
        sigma_clip (float): Sigma threshold for iterative residual clipping.
        max_iter (int): Max iterations for clipping.
        multiplicative (bool): If True, divide trend/c; else subtract (trend - c).
        bic_delta (float): Threshold on ΔBIC to accept sinusoid removal.
        plot (bool): If True, save comparison plot of sine vs constant fits.
        show (bool): If True, display plot interactively.
        save_prefix (str or None): Filename stem for saved figures.
        return_model (bool): If True, return (detrended, trend, params).
        detrending_name (str or None): Subdirectory suffix for saved outputs.

    Returns:
        If return_model:
            tuple:
                detrended (np.ndarray): Flux after removal (or original if rejected).
                trend (np.ndarray): Fitted trend evaluated at all samples.
                params (dict): Details (A, phi, C, period_used_s, removed flag, BICs, primary_gauss).
        Else:
            detrended (np.ndarray): As above.
    '''
    # Inputs to arrays
    time_s = np.asarray(time_s, float)
    flux   = np.asarray(flux,   float)

    # Reflection modulation at P_trend = Pbin
    P_trend = float(Pbin_s)

    # Phase at Pbin
    phase = ((time_s - bjd0) / P_trend) % 1.0

    # Primary mask construction (optional)
    primary_params = None
    primary_mask = None
    if mask_primary:
        try:
            primary_params = _fit_primary_gaussian(phase, flux, window_half_width=primary_window)
        except Exception:
            primary_params = None
        if primary_params is not None:
            _, mu_p, sig_p, _ = primary_params
            try:
                primary_mask = _primary_mask_from_fit(phase, mu_p, sig_p, k_sigma=primary_k_sigma)
            except Exception:
                primary_mask = None

    # Design matrix for sine+cosine+constant at φ = (time - bjd0)/Pbin
    two_pi_phi = 2.0 * np.pi * phase
    X = np.column_stack([np.sin(two_pi_phi), np.cos(two_pi_phi), np.ones_like(two_pi_phi)])

    # Build valid set and iterative clipping loop
    valid = np.isfinite(flux) & np.isfinite(phase)
    if primary_mask is not None:
        valid &= (~primary_mask)
    y = flux.copy()

    for _ in range(max_iter):
        sel = valid & np.isfinite(y)
        if sel.sum() < 10:
            break
        a, b, c = np.linalg.lstsq(X[sel], y[sel], rcond=None)[0]
        yhat = (X @ np.array([a, b, c]))
        resid = y - yhat
        s = np.nanstd(resid[sel])
        if not np.isfinite(s) or s == 0:
            break
        new_sel = sel & (np.abs(resid) < sigma_clip * s)
        if new_sel.sum() == sel.sum():
            break
        valid = new_sel

    # Final fit or fallback
    sel = valid & np.isfinite(y)
    if sel.sum() >= 3:
        a, b, c = np.linalg.lstsq(X[sel], y[sel], rcond=None)[0]
    else:
        a, b, c = 0.0, 0.0, float(np.nanmedian(y[sel]) if sel.any() else np.nanmedian(y))

    # Evaluate trend
    trend = (X @ np.array([a, b, c]))

    # BIC comparison (sine vs constant) on used subset
    y_used = y[sel]
    yhat_sine = trend[sel]
    const_level = float(np.nanmedian(y_used))
    yhat_const  = np.full_like(y_used, const_level)

    def _bic_local(ytrue, ypred, k):
        '''
        Functionality:
            Compute a simple BIC-like score for a model with k parameters.
    
        Arguments:
            ytrue (array-like): Observed data.
            ypred (array-like): Model predictions.
            k (int): Number of free parameters.
    
        Returns:
            float:
                BIC score (lower is better). Returns inf if insufficient data.
        '''
        n = ytrue.size
        if n <= k or n == 0:
            return np.inf
        rss = np.nansum((ytrue - ypred)**2)
        rss = max(rss, 1e-300)
        return n * np.log(rss / n) + k * np.log(n)

    bic_sine  = _bic_local(y_used, yhat_sine, k=3)
    bic_const = _bic_local(y_used, yhat_const, k=1)
    delta = float(bic_const - bic_sine)  # positive → sine preferred

    # Apply or reject removal
    if delta >= bic_delta:
        if multiplicative:
            detrended = flux / np.clip(trend / c, 1e-12, None)
        else:
            detrended = flux - (trend - c)
        removed = True
    else:
        detrended = flux.copy()
        removed = False

    # Optional plot output
    if plot:
        base_dir = _resolve_base_dir(None)
        out_dir = os.path.join(base_dir, "LightCurves", "Data_Preparation")
        if detrending_name:
            out_dir = os.path.join(out_dir, detrending_name)
        os.makedirs(out_dir, exist_ok=True)

        base = os.path.basename(save_prefix) if save_prefix else (detrending_name if detrending_name else "run")
        out_prefix = os.path.join(out_dir, f"{base}_reflection")

        ph = phase % 1.0
        sorter = np.argsort(ph)
        ph_s, f_s, tr_s = ph[sorter], flux[sorter], trend[sorter]

        # Small phase-binner
        def _phase_bin(x, y, nbins=180, robust=True):
            '''
            Functionality:
                Bin data by phase and compute a single representative value per bin.
        
            Arguments:
                x (array-like): Phase values in [0,1).
                y (array-like): Data values aligned with x.
                nbins (int): Number of phase bins to compute.
                robust (bool): If True use median per bin, else mean.
        
            Returns:
                (np.ndarray, np.ndarray):
                    Bin centers (phase), binned values.
            '''
            edges = np.linspace(0.0, 1.0, nbins + 1)
            idx = np.digitize(x, edges) - 1
            xc, yc = [], []
            for i in range(nbins):
                seli = (idx == i)
                if not np.any(seli):
                    continue
                yi = y[seli]
                xc.append(0.5*(edges[i] + edges[i+1]))
                yc.append(np.nanmedian(yi) if robust else np.nanmean(yi))
            return np.array(xc), np.array(yc)

        xb, yb = _phase_bin(ph_s, f_s, nbins=180, robust=True)
        preferred = 'sine' if bic_sine <= bic_const else 'flat'
        title = f"Reflection @ P = {P_trend/86400:.6f} d"

        fig, ax = plt.subplots(figsize=(8.6, 4.6))
        ax.plot(ph_s, f_s, '.', ms=1.8, alpha=0.35, label='data (points)')
        if xb.size:
            ax.plot(xb, yb, lw=1.6, alpha=0.9, label='data (binned)')
        ax.plot(ph_s, tr_s, lw=2.4 if preferred=='sine' else 1.2, alpha=0.95,
                label=f"sine fit (BIC={bic_sine:.2f})")
        ax.hlines(const_level, 0, 1, linewidth=2.4 if preferred=='flat' else 1.2,
                  alpha=0.95, label=f"constant (BIC={bic_const:.2f})")

        # Mark primary band if available
        if primary_params is not None:
            _, mu_p, sig_p, _ = primary_params
            w = primary_k_sigma * sig_p
            for center in [mu_p % 1.0, (mu_p % 1.0) - 1, (mu_p % 1.0) + 1]:
                ax.axvspan(center - w, center + w, color='k', alpha=0.05, lw=0)

        ax.set_xlim(0, 1)
        ax.set_xlabel("Phase (folded at P)")
        ax.set_ylabel("Flux")
        ax.set_title(title)
        ax.grid(True, ls=':', alpha=0.35)
        ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0), borderaxespad=0.0, framealpha=0.95)
        info = f"Preferred: {preferred}\nApplied removal: {'YES' if removed else 'NO'}"
        ax.text(0.01, 0.02, info, transform=ax.transAxes, ha='left', va='bottom', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, lw=0.5))
        plt.tight_layout(rect=[0, 0, 0.82, 1])
        plt.savefig(out_prefix + "_compare.png", dpi=220, bbox_inches='tight')
        if show:
            plt.show()
        plt.close(fig)

    if return_model:
        # Provide amplitude/phase summary too
        A = float(np.hypot(a, b))
        phi = float(np.arctan2(b, a))
        params = dict(
            A=A, phi=phi, C=float(c), period_used_s=float(P_trend), bjd0=float(bjd0),
            removed=removed, bic_sine=float(bic_sine), bic_const=float(bic_const),
            delta_bic=delta,
            primary_gauss=(dict(depth=primary_params[0], mu=primary_params[1], sigma=primary_params[2], C=primary_params[3])
                           if primary_params else None)
        )
        return detrended, trend, params
    return detrended


# estimate eclipse width for initial guess to be read into curvefit (veryyyy janky, but it works well enough)
def estimate_eclipse_width(phase, flux, eclipse_center, threshold=0.5, depth=None):
    '''
    Functionality:
        Estimate the eclipse width (in phase) using the full width at a fraction of the
        eclipse depth (default = FWHM when threshold=0.5). Works on phase-binned data.

    Arguments:
        phase (array-like): Sorted phase array in [0, 1) (assumed binned).
        flux (array-like): Binned flux values corresponding to `phase`.
        eclipse_center (float): Estimated eclipse center phase.
        threshold (float): Fraction of the depth at which the width is measured (0–1).
        depth (float or None): If provided, use this depth; otherwise computed from data.

    Returns:
        float: Estimated width in phase units, with a minimum of 0.0005.
    '''
    # Compute a default depth if not provided
    if depth is None:
        min_flux = np.min(flux)                  # minimum flux in eclipse
        baseline = np.median(flux)               # baseline (out-of-eclipse) flux
        depth = baseline - min_flux              # eclipse depth

    # Define a flux cutoff at the requested fraction of depth
    baseline = np.median(flux)
    cutoff = baseline - threshold * depth

    # Identify indices that are below the cutoff → "in eclipse"
    in_eclipse = flux < cutoff
    eclipse_indices = np.where(in_eclipse)[0]

    # If nothing is below the cutoff, return a small default width
    if len(eclipse_indices) == 0:
        return 0.01

    # Find index nearest the provided eclipse center
    eclipse_center_idx = np.argmin(np.abs(phase - eclipse_center))

    # Walk left from the center until we exit the eclipse region
    left = eclipse_center_idx
    while left > 0 and flux[left] < cutoff:
        left -= 1

    # Walk right from the center until we exit the eclipse region
    right = eclipse_center_idx
    while right < len(flux) - 1 and flux[right] < cutoff:
        right += 1

    # Width is the phase span from left edge to right edge
    width = phase[right] - phase[left]

    # Correct for wrap-around if span is negative (e.g., eclipse straddles 0/1)
    if width < 0:
        width += 1.0

    # Ensure a positive minimum
    return max(width, 0.0005)


# Kepler's Third Law for semi-major axis (AU)
def estimate_semi_major_axis(P_sec, Ma, Mb):
    '''
    Functionality:
        Estimate the binary semi-major axis (in AU) using Kepler's third law:
            a^3 = (P_years)^2 * (M_total / M_sun)
        where a is in AU, P_years in years, and M_total in solar masses.

    Arguments:
        P_sec (float): Orbital period in seconds.
        Ma (float): Primary mass in kilograms.
        Mb (float): Secondary mass in kilograms.

    Returns:
        float: Semi-major axis in astronomical units (AU).

    Raises:
        ValueError: If period or masses are outside sensible bounds.
    '''
    M_sun = 1.9885e30  # kg

    # Convert seconds → days for sanity checks
    P_days = P_sec / 60 / 60 / 24
    if not (0 < P_days < 1e4):                    # very broad constraint
        raise ValueError(f"Period out of bounds: {P_days} days")
    if Ma <= 0 or Mb <= 0:                        # physical requirement
        raise ValueError(f"Masses must be positive. Got Ma={Ma}, Mb={Mb}")

    # Convert to years and solar-mass units
    P_yrs = P_days / 365.25
    M_total = (Ma + Mb) / M_sun

    # Kepler's law in solar units with a in AU
    a_cubed = P_yrs**2 * M_total
    return a_cubed**(1/3)


# Empirical secondary Teff estimate, veryyyyyyy simple estimation from some paper that I can no longer find LOL so we will not be using this
# place holder function for now, don't really need Teff anymore
def empirical_Teff(M):
    '''
    Functionality:
        Very rough placeholder empirical Teff(M) relation. Not used for analysis
        (kept for compatibility / legacy). Piecewise power-law based on mass.

    Arguments:
        M (float): Mass in kilograms.

    Returns:
        float: Estimated effective temperature in Kelvin.

    Raises:
        ValueError: If mass is non-positive.
    '''
    M_sun = 1.9885e30  # kg
    M_solar = M / M_sun

    # Physical sanity
    if M_solar <= 0:
        raise ValueError("Mass must be positive.")

    # Crude piecewise mapping (placeholder)
    if M_solar < 0.43:
        return 3500 * (M_solar / 0.43)**0.8
    elif M_solar < 2.0:
        return 5800 * (M_solar)**0.6
    else:
        return 9000 * (M_solar)**0.3


def initialGuess3(timeData, fluxData, fluxErrData,
                  Pbin, bjd0, bounds,
                  prim_pos, sec_pos, pwidth, swidth, pdepth, sdepth,
                  DetrendingName,
                  ID, locating,
                  bin_width=None, plotting=False,
                  abs_time_sec=None):
    '''
    Functionality:
        Provide initial guesses for eclipse parameters for curve fitting. Operates for
        either primary or secondary eclipse depending on `locating`. For the primary,
        if key parameters are missing, it can run a BLS (on absolute time if given)
        to estimate period, epoch, and duration; secondary uses phase-domain heuristics.

    Arguments:
        timeData (array-like): Phase or time array (phase expected for width/position ops).
        fluxData (array-like): Flux array.
        fluxErrData (array-like or None): Flux uncertainties or None.
        Pbin (float): Binary period in seconds.
        bjd0 (float): Reference epoch in seconds (used to convert t0 to phase).
        bounds (tuple): ((min_depth, min_width, min_pos), (max_depth, max_width, max_pos)) bounds for sanity.
        prim_pos (float or None): Primary phase center guess (phase or seconds).
        sec_pos (float or None): Secondary phase center guess (phase or seconds).
        pwidth (float or None): Primary width guess in phase units.
        swidth (float or None): Secondary width guess in phase units.
        pdepth (float or None): Primary depth guess in normalized flux units.
        sdepth (float or None): Secondary depth guess in normalized flux units.
        DetrendingName (str): Tag for file naming.
        ID (str or int): Target identifier, used in filenames.
        locating (str): 'primary' or 'secondary' to choose the branch.
        bin_width (float or None): Optional bin width used only for plotting figure labels.
        plotting (bool): If True, save diagnostic plots for guesses.
        abs_time_sec (array-like or None): Absolute time (seconds) to enable BLS in primary branch.

    Returns:
        For locating == 'primary':
            tuple: (depth, position, width)
        For locating == 'secondary':
            tuple: (depth, position, width, bin_width_used)
    '''

    # Local helpers
    def _label_for_x(x):
        '''
        Functionality:
            Choose a simple axis label based on data range.
    
        Arguments:
            x (array-like): Values to inspect.
    
        Returns:
            str: "Phase" if in [0,1], else "Time (days)".
        '''
        if np.nanmin(x) >= 0.0 and np.nanmax(x) <= 1.0:
            return "Phase"
        return "Time (days)"
    
    
    def _wrap_dist(ph, c):
        '''
        Functionality:
            Compute minimum circular distance between phase values.
    
        Arguments:
            ph (float or array-like): Phase(s) in [0,1).
            c (float): Reference phase in [0,1).
    
        Returns:
            array-like:
                Wrapped absolute distance on the unit circle.
        '''
        d = np.abs(ph - c)
        return np.minimum(d, 1.0 - d)

    # Convert inputs and mask non-finite flux/err (keep time as-is if different length)
    timeData = np.asarray(timeData, float)
    fluxData = np.asarray(fluxData, float)
    fluxErrData = None if fluxErrData is None else np.asarray(fluxErrData, float)

    finite = np.isfinite(fluxData)
    if fluxErrData is not None:
        finite &= np.isfinite(fluxErrData)
    fluxData_clean = fluxData[finite]
    fluxErr_clean = (fluxErrData[finite] if fluxErrData is not None else None)
    time_clean = timeData[finite] if timeData.size == fluxData.size else timeData

    # Guard against all-NaN flux
    if fluxData_clean.size == 0:
        if locating.lower() == 'secondary':
            return 1e-3, 0.5, 0.02, (bin_width if bin_width is not None else 0.001)
        else:
            return 0.01, 0.5, 0.01

    # PRIMARY
    if locating.lower() == 'primary':
        # If prim_pos was mistakenly given in seconds, transform to phase (best effort)
        if prim_pos is not None and (prim_pos < 0 or prim_pos > 1) and prim_pos is not np.nan:
            try:
                idx_min_all = int(np.nanargmin(fluxData_clean))           # index of deepest point
                ref_phase = time_clean[idx_min_all] if np.isfinite(time_clean[idx_min_all]) else 0.0
            except Exception:
                ref_phase = 0.0
            prim_pos = ((prim_pos / Pbin) - ref_phase + 0.5) % 1.0        # map to [0,1)

        # Track which parameters are missing
        primary_params = {"prim_pos": prim_pos, "pwidth": pwidth, "pdepth": pdepth}
        nan_params = {k: v for k, v in primary_params.items()
                      if (v is None) or (isinstance(v, float) and np.isnan(v))}

        # If any of {center, width, depth} missing → try BLS on absolute time
        if len(nan_params) > 0:
            t_for_bls = abs_time_sec if abs_time_sec is not None else timeData

            # Check if BLS is safe to run (needs time baseline, not just phase)
            t_days = np.asarray(t_for_bls, dtype=float) / 86400.0
            t_days = t_days[np.isfinite(t_days)]
            if t_days.size >= 3:
                span = np.nanmax(t_days) - np.nanmin(t_days)              # overall baseline
                cad = np.nanmedian(np.diff(np.sort(t_days)))              # effective cadence
            else:
                span, cad = 0.0, np.nan

            bls_ok = True
            if not np.isfinite(cad) or cad <= 0:
                cad = 120.0 / 86400.0                                     # default 2-min cadence
            if span < 10.0 * cad:
                # Looks too much like phase values; only proceed if absolute time provided
                bls_ok = (abs_time_sec is not None)

            if bls_ok:
                # Use ultrafast single-dip search (returns seconds)
                bls_period_sec, t0_sec, transit_depth, transit_duration_sec, meta_bls = iterative_bls_single_dip_search(
                    t_for_bls, fluxData, fluxErrData,
                    DetrendingName=DetrendingName,
                    min_period_days=0.05, max_period_days=90.0,
                    q_eff=None,
                    pre_detrend='both',         # BIC-gated; harmless if no hints
                    bic_delta=0.0,
                    check_harmonics=True,
                    plot_harmonics=False,
                    presets_sequence=[HYPERFINE]
                )

                # Convert duration to phase width estimate
                width_from_bls = np.clip(transit_duration_sec / float(Pbin), 1e-5, 0.3)

                # Phase center from t0 and bjd0 if available; otherwise midpoint fallback
                if "prim_pos" in nan_params:
                    if bjd0 is not None and np.isfinite(bjd0):
                        position = ((t0_sec - bjd0) / float(Pbin) + 0.5) % 1.0
                    else:
                        position = 0.5
                else:
                    position = prim_pos

                # Robust depth: prefer BLS depth if sane, else measure from data
                phaseTimeBinned, fluxBinned = timeData, fluxData
                baseline = float(np.nanmedian(fluxBinned))
                if np.isfinite(position) and np.isfinite(baseline) and np.any(np.isfinite(phaseTimeBinned)):
                    win = 3.0 * (width_from_bls if np.isfinite(width_from_bls) and width_from_bls > 0 else 0.02)
                    win = np.clip(win, 0.01, 0.10)                         # constrain window
                    mask_win = _wrap_dist(phaseTimeBinned % 1.0, position) <= win
                    if np.any(mask_win) and np.sum(np.isfinite(fluxBinned[mask_win])) >= 5:
                        local_min = float(np.nanpercentile(fluxBinned[mask_win], 1))
                    else:
                        local_min = float(np.nanpercentile(fluxBinned, 1))
                else:
                    local_min = float(np.nanpercentile(fluxBinned, 1))
                depth_robust = float(np.clip(baseline - local_min, 1e-5, 0.9))

                depth_bls = float(transit_depth) if np.isfinite(transit_depth) else np.nan
                depth = depth_bls if (np.isfinite(depth_bls) and 1e-5 <= depth_bls <= 0.9) else depth_robust

                width = width_from_bls if "pwidth" in nan_params else pwidth
            else:
                # Cannot run BLS — keep provided or fallback heuristics
                position = 0.5 if ("prim_pos" in nan_params and bjd0 is not None) else prim_pos
                width = pwidth
                depth = pdepth
        else:
            # No missing parameters — accept provided values
            position, width, depth = prim_pos, pwidth, pdepth

        # Use arrays as-is for locating minimum and width
        phaseTimeBinned, fluxBinned, fluxErrBinned = timeData, fluxData, fluxErrData

        # Position guard and refinement to actual deepest point if available
        if (position is None) or np.isnan(position) or (position < bounds[0][2]) or (position > bounds[1][2]):
            try:
                idx_min = int(np.nanargmin(fluxBinned))
                pos_candidate = phaseTimeBinned[idx_min]
                position = pos_candidate if np.isfinite(pos_candidate) else (0.5 if (bjd0 is not None) else 0.5)
            except Exception:
                position = 0.5 if (bjd0 is not None) else 0.5
        else:
            try:
                idx_min = int(np.nanargmin(fluxBinned))
                ref = phaseTimeBinned[idx_min]
                if np.isfinite(ref):
                    position = ref
            except Exception:
                pass

        # Width sanity with fallback to threshold-based estimate
        if (width is None) or np.isnan(width) or (width < bounds[0][1]) or (width > bounds[1][1]):
            try:
                width = estimate_eclipse_width(phaseTimeBinned, fluxBinned, position, threshold=0.25)
            except Exception:
                width = 0.01
            width = min(0.1, max(width, 1e-4))

        # Depth sanity using robust baseline−min
        if (depth is None) or np.isnan(depth) or (depth < bounds[0][0]) or (depth > bounds[1][0]):
            baseline = float(np.nanmedian(fluxBinned))
            local_min = float(np.nanpercentile(fluxBinned, 1))
            depth = float(np.clip(baseline - local_min, 1e-5, 0.9))

        # Final safety on position
        if not np.isfinite(position):
            print(f"[initialGuess3] Warning: position NaN for {ID}; forcing to 0.5")
            position = 0.5

        # Optional diagnostic plot
        if plotting:
            base = _resolve_base_dir(None)
            my_folder = base / 'LightCurves' / 'Data_Preparation' / DetrendingName
            my_folder.mkdir(parents=True, exist_ok=True)
            save_path = os.path.join(my_folder, f'Primary_Eclipse_Estimate_{ID}.png')

            plt.figure(figsize=(10, 5))
            plt.scatter(timeData, fluxData, s=1, color='black', label='Data')
            plt.axvline(x=position, color='blueviolet', linestyle='--', linewidth=2,
                        label='Primary Eclipse Position')
            plt.xlabel(_label_for_x(timeData))
            plt.ylabel('Flux')
            plt.title('Primary Eclipse Position and Estimated Depth')
            plt.legend()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.show()
            plt.close()

        return depth, position, width

    # SECONDARY
    elif locating.lower() == 'secondary':
        # Keep current arrays for phase-domain estimates
        bin_width_dynamic = bin_width
        phaseTimeBinned, fluxBinned, fluxErrBinned = timeData, fluxData, fluxErrData

        # If sec_pos given in seconds, convert relative to primary (best effort)
        if sec_pos is not None and (sec_pos < 0 or sec_pos > 1) and sec_pos is not np.nan:
            sec_pos = ((sec_pos / Pbin) - (prim_pos if prim_pos is not None else 0.0)) % 1.0

        # Track missing secondary parameters
        secondary_params = {"sec_pos": sec_pos, "swidth": swidth, "sdepth": sdepth}
        nan_params = {k: v for k, v in secondary_params.items()
                      if (v is None) or (isinstance(v, float) and np.isnan(v))}

        # Early guard for empty/non-finite series
        n_good_flux = int(np.sum(np.isfinite(fluxBinned)))
        if (fluxBinned.size == 0) or (n_good_flux == 0):
            position = (0.5 if ("sec_pos" in nan_params) else sec_pos)
            width = (0.02 if ("swidth" in nan_params) else swidth)
            depth = (1e-3 if ("sdepth" in nan_params) else sdepth)
            if (width is None) or (not np.isfinite(width)) or (width <= 0):
                width = 0.02
            width = float(np.clip(width, 1e-4, 0.1))
            if (depth is None) or (not np.isfinite(depth)) or (depth <= 0):
                depth = 1e-3
            depth = float(np.clip(depth, 1e-5, 0.5))
            if (position is None) or (not np.isfinite(position)):
                position = 0.5
            return depth, position, width, (bin_width_dynamic if bin_width_dynamic is not None else 0.001)

        # If any missing, estimate from phase-binned minima and widths
        if len(nan_params) > 0:
            try:
                idx_min = int(np.nanargmin(fluxBinned))        # phase of deepest feature
                pos_candidate = phaseTimeBinned[idx_min]
            except Exception:
                pos_candidate = np.nan

            if "sec_pos" in nan_params:
                position = pos_candidate if np.isfinite(pos_candidate) else 0.5
            else:
                position = sec_pos

            if "swidth" in nan_params:
                try:
                    width = estimate_eclipse_width(phaseTimeBinned, fluxBinned, position, 0.25)
                except Exception:
                    width = 0.02
                width = min(0.1, max(width, 1e-4))
            else:
                width = swidth

            if "sdepth" in nan_params:
                baseline = float(np.nanmedian(fluxBinned))
                if np.isfinite(position) and np.any(np.isfinite(phaseTimeBinned)):
                    win = 3.0 * (width if np.isfinite(width) and width > 0 else 0.02)
                    win = np.clip(win, 0.01, 0.10)
                    mask_win = _wrap_dist(phaseTimeBinned % 1.0, position) <= win
                    if np.any(mask_win) and np.sum(np.isfinite(fluxBinned[mask_win])) >= 5:
                        local_min = float(np.nanpercentile(fluxBinned[mask_win], 1))
                    else:
                        local_min = float(np.nanpercentile(fluxBinned, 1))
                else:
                    local_min = float(np.nanpercentile(fluxBinned, 1))
                depth = float(np.clip(baseline - local_min, 1e-5, 0.5))
            else:
                depth = sdepth
        else:
            # All provided → accept
            position, width, depth = sec_pos, swidth, sdepth

        # Final guards/clamps
        if (position is None) or (not np.isfinite(position)):
            position = 0.5
        if (width is None) or (not np.isfinite(width)) or (width <= 0):
            width = 0.02
        width = float(np.clip(width, 1e-4, 0.1))
        if (depth is None) or (not np.isfinite(depth)) or (depth <= 0):
            depth = 1e-3
        depth = float(np.clip(depth, 1e-5, 0.5))

        # Optional diagnostic
        if plotting:
            root = _resolve_base_dir(None)
            my_folder = root / 'LightCurves' / 'Data_Preparation' / str(DetrendingName)
            my_folder.mkdir(parents=True, exist_ok=True)
            save_path = my_folder / f'Secondary_Eclipse_Scanning_{ID}.png'

            plt.figure(figsize=(10, 5))
            plt.scatter(phaseTimeBinned, fluxBinned, s=1, color='black', alpha=0.6, label='Binned Data')
            try:
                minFlux = phaseTimeBinned[int(np.nanargmin(fluxBinned))]
                if np.isfinite(minFlux):
                    plt.axvline(x=minFlux, color='blueviolet', linestyle='--', linewidth=2, label='Minimum Flux')
            except Exception:
                pass

            scan_start, scan_end = 0.15, 0.85
            actual_min, actual_max = np.nanmin(phaseTimeBinned), np.nanmax(phaseTimeBinned)
            if np.isfinite(actual_min) and actual_min > 0:
                plt.axvspan(0, actual_min, color='red', alpha=0.2, label='Cut Region')
            if np.isfinite(actual_max) and actual_max < 1:
                plt.axvspan(actual_max, 1, color='red', alpha=0.2 if (np.isfinite(actual_min) and actual_min > 0) else 0.25)
            scan_visible_min = max(actual_min, scan_start) if np.isfinite(actual_min) else scan_start
            scan_visible_max = min(actual_max, scan_end) if np.isfinite(actual_max) else scan_end
            if scan_visible_min < scan_visible_max:
                plt.axvspan(scan_visible_min, scan_visible_max, color='yellow', alpha=0.3, label='Scanned Region')

            plt.xlabel('Phase')
            plt.ylabel('Flux')
            plt.title('Secondary Eclipse Scanning and Cut Regions')
            plt.legend()
            plt.xlim(0, 1)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.show()
            plt.close()

        return depth, position, width, (bin_width_dynamic if bin_width_dynamic is not None else 0.001)


def _fit_with_optional_binning(x, y, yerr, model_func, p0, bounds,
                               bin_width_for_retry=0.001,
                               do_once=True, gtol=1e-8):
    '''
    Functionality:
        Attempt a bounded non-linear least-squares fit (curve_fit) on (x,y).
        If it fails, rebin the data once using binData (if available) and retry.

    Arguments:
        x (array-like): Independent variable.
        y (array-like): Dependent variable.
        yerr (array-like or None): Uncertainties (used only to pass through to binData).
        model_func (callable): f(x, *params) model to fit.
        p0 (sequence): Initial parameter guesses.
        bounds (2-tuple): (lower_bounds, upper_bounds) for parameters.
        bin_width_for_retry (float): Bin width passed to binData for the second attempt.
        do_once (bool): If True, only one rebin retry; otherwise only first raw attempt.
        gtol (float): Gradient tolerance for curve_fit (TRF).

    Returns:
        tuple:
            popt (np.ndarray or None): Best-fit params, or None on failure.
            used_binning (bool): True if the returned fit used binned data.
            x_used (np.ndarray): X values used in the successful fit attempt (or original on failure).
            y_used (np.ndarray): Y values used in the successful fit attempt (or original on failure).
            yerr_used (np.ndarray or None): Yerr used in the successful attempt (or original/fallback).
    '''

    # First attempt on raw data
    try:
        popt, _ = so.curve_fit(model_func, x, y, p0=p0, method='trf', bounds=bounds, gtol=gtol)
        return popt, False, x, y, yerr
    except Exception:
        pass

    # Retry with binning if enabled
    if do_once:
        try:
            _bin = globals().get('binData', None)
            if _bin is None:
                raise RuntimeError("binData is not available in the current namespace.")
            x_b, y_b, yerr_b = _bin(x, y, yerr, bin_width=bin_width_for_retry)
            if len(x_b) >= max(8, len(p0) + 3):  # ensure at least enough points
                popt, _ = so.curve_fit(model_func, x_b, y_b, p0=p0, method='trf',
                                       bounds=bounds, gtol=gtol)
                return popt, True, x_b, y_b, yerr_b
        except Exception:
            pass

    # If both attempts fail, return None and the original arrays
    return None, False, x, y, yerr


def _secondary_sweep_with_optional_binning(x, y, yerr, bounds_gauss,
                                           sdepthGuess, swidthGuess,
                                           phase_grid,
                                           bin_width_for_retry=0.001,
                                           do_once=True, gtol=1e-8):
    '''
    Functionality:
        Sweep a grid of secondary-eclipse centers in phase; for each center, fit a
        Gaussian eclipse model and pick the parameters with the minimal reduced χ².
        If no center fits, rebin once and retry the sweep.

    Arguments:
        x (array-like): Phase values (or x-axis in phase space).
        y (array-like): Flux values.
        yerr (array-like or None): Flux errors.
        bounds_gauss (2-tuple): Bounds for gaussianModel parameters (depth, width, center).
        sdepthGuess (float): Initial depth guess.
        swidthGuess (float): Initial width (phase) guess.
        phase_grid (array-like): Candidate eclipse centers in phase to scan.
        bin_width_for_retry (float): Bin width for a single retry via binData.
        do_once (bool): If True, allow a single rebin attempt.
        gtol (float): Gradient tolerance for scipy curve_fit.

    Returns:
        tuple:
            best_params_or_None (np.ndarray or None): Best-fit params for gaussianModel or None.
            used_binning_flag (bool): True if result came from binned retry.
            x_used (np.ndarray): X array used in the final attempt.
            y_used (np.ndarray): Y array used in the final attempt.
            yerr_used (np.ndarray or None): Yerr array used.
            best_rchi2 (float): Best reduced χ² achieved (inf if no fit).
    '''

    def _scan(xu, yu, eu):
        '''
        Functionality:
            Fit a Gaussian model centered at each trial phase and keep the best fit.
    
        Arguments:
            xu (array-like): Phase or time values.
            yu (array-like): Data values to fit.
            eu (array-like or None): Uncertainties; if None, unweighted fit.
    
        Returns:
            (best_params, best_rchi2):
                best_params : array or None
                    Fitted Gaussian parameters [depth, width, center].
                best_rchi2 : float
                    Lowest reduced chi² found.
        '''
        # Try fitting for each candidate center; keep the one with lowest reduced χ²
        best_params = None
        best_rchi2 = np.inf
        for phase in phase_grid:
            p0_gauss = [sdepthGuess, swidthGuess, phase]  # [depth, width, center]
            try:
                params, _ = so.curve_fit(gaussianModel, xu, yu,
                                         p0=p0_gauss, method='trf', bounds=bounds_gauss, gtol=gtol)
                yhat = gaussianModel(xu, *params)
                r = yu - yhat
                chi2 = np.sum((r / np.clip(eu, 1e-12, None))**2) if eu is not None else np.sum(r**2)
                rchi2 = chi2 / max(1, (len(yu) - len(params)))
                if rchi2 < best_rchi2:
                    best_rchi2 = rchi2
                    best_params = params
            except Exception:
                continue
        return best_params, best_rchi2

    # First pass: raw arrays
    params, best_rchi2 = _scan(x, y, yerr)
    if params is not None:
        return params, False, x, y, yerr, best_rchi2

    # Optional single retry with binned data
    if do_once:
        try:
            _bin = globals().get('binData', None)
            if _bin is None:
                raise RuntimeError("binData is not available in the current namespace.")
            xb, yb, eb = _bin(x, y, yerr, bin_width=bin_width_for_retry)
            if len(xb) >= 10:  # ensure enough points
                params, best_rchi2 = _scan(xb, yb, eb)
                if params is not None:
                    return params, True, xb, yb, eb, best_rchi2
        except Exception:
            pass

    # If everything fails, return None and infinities appropriately
    return None, False, x, y, yerr, np.inf


def modelEclipse3(
    timeArray, fluxArray, fluxArrayErr,
    Pbin, bjd0, sep,
    prim_pos, sec_pos, pwidth, swidth, pdepth, sdepth,
    Ra, Rb, Ta=None, Tb=None, a=None,
    DetrendingName=None,
    ID=None, plotting=True,
    bin_width=0.0001, eclipsePrior=True, vetting=True
):
    '''
    Functionality:
        Fit primary and secondary eclipses in a binary light curve using two simple models
        (Gaussian and tanh-with-flat-baseline), choose the preferred model for the primary
        via BIC, search/fit the secondary on the primary-masked data, and (optionally)
        vet the secondary to derive orbital parameters (ecc, omega, etc.). Returns eclipse-
        removed series and fitted parameters for downstream analysis.

    Arguments:
        timeArray (array-like, seconds): Absolute observation times in seconds.
        fluxArray (array-like): Normalized flux values (baseline ≈ 1).
        fluxArrayErr (array-like or None): Flux uncertainties or None.
        Pbin (float, seconds): Binary period (s).
        bjd0 (float, seconds): Reference epoch (s) used for phase folding.
        sep (float): Phase separation between primary and secondary (rough initial).
        prim_pos (float): Primary eclipse center position (phase or seconds if >1).
        sec_pos (float): Secondary eclipse center position (phase or seconds if >1).
        pwidth (float): Primary eclipse width in phase (initial guess).
        swidth (float): Secondary eclipse width in phase (initial guess).
        pdepth (float): Primary eclipse depth (initial guess; normalized flux units).
        sdepth (float): Secondary eclipse depth (initial guess; normalized flux units).
        Ra (float): Primary radius (meters).
        Rb (float): Secondary radius (meters).
        Ta (float or None): Primary effective temperature (optional).
        Tb (float or None): Secondary effective temperature (optional).
        a (float or None): Semi-major axis (optional; meters or AU per downstream usage).
        DetrendingName (str or None): Label for plots/outputs.
        ID (str or None): Target identifier for plots/filenames.
        plotting (bool): If True, save diagnostic plots for fits.
        bin_width (float): Default rebin width (phase units) for one-time retry on fit failure.
        eclipsePrior (bool): If True and bjd0/prim_pos are finite, use prior-aware phasing.
        vetting (bool): If True, run secondary-eclipse vetting to derive (ecc, omega, ...).

    Returns (if vetting=True):
        (
            AbsoluteTimeCutBoth (np.ndarray, seconds),  # absolute times with both eclipses removed
            fluxCutBoth (np.ndarray),                   # flux with both eclipses removed
            fluxErrCutBoth (np.ndarray or None),        # matching errors or None
            prim_pos (float),                           # fitted primary center (phase, centered to 0 after return)
            sec_pos (float),                            # fitted secondary center (phase)
            pwidth (float),                             # fitted primary width (phase)
            swidth (float),                             # fitted secondary width (phase)
            pdepth (float),                             # fitted primary depth
            sdepth (float),                             # fitted secondary depth
            sep (float),                                # fitted phase separation |Δphase| in [0, 0.5]
            ecc (float), omega (float),                 # fitted eccentricity and argument of periapsis
            eccNoAssump (float), omegaNoAssump (float), # non-assuming versions from vetting
            ecoswNoAssump (float), esinwNoAssump (float),
            knownEclipse (str)                          # classification: 'none'|'primary'|'secondary'|'both'
        )

    Returns (if vetting=False):
        (
            timeCut (np.ndarray, phase),   # primary-masked phase array (not absolute times)
            fluxCut (np.ndarray),          # matching flux
            fluxErrCut (np.ndarray or None),
            bics (dict)                    # {'gaussian':..., 'straight':..., 'tanh':...} for secondary tests
        )
    '''
    # Local aliases (assumes these exist in module scope)
    classify_known_eclipse_local = classify_known_eclipse
    initialGuess3_local          = initialGuess3
    _fit_with_optional_binning_l = _fit_with_optional_binning
    gaussianModel_local          = gaussianModel
    tanh_transit_flat_local      = tanh_transit_flat
    RemoveEclipses_local         = RemoveEclipses
    _secondary_sweep_optbin_l    = _secondary_sweep_with_optional_binning
    vet_secondary_eclipse_local  = vet_secondary_eclipse
    straightModel_local          = straightModel

    # Fallback for days2sec if not in scope
    try:
        days2sec
    except NameError:
        days2sec = 86400.0

    # Coerce bin width for fallback retry
    bw = bin_width
    retry_bin_width = 0.001 if (bw is None or (not np.isfinite(bw)) or (bw <= 0)) else float(bw)

    # Arrays
    t  = np.asarray(timeArray, float)
    y  = np.asarray(fluxArray, float)
    ye = None if fluxArrayErr is None else np.asarray(fluxArrayErr, float)

    # Phase definition
    invP = 1.0 / Pbin
    _use_prior = bool(eclipsePrior) and np.isfinite(bjd0) and np.isfinite(prim_pos)

    if _use_prior:
        knownEclipse = classify_known_eclipse_local(prim_pos, sec_pos)
        print('knownEclipse:', knownEclipse)
        phaseTime = ((t - bjd0) * invP + 0.5) % 1.0
    else:
        knownEclipse = "none"
        phaseTime = (t * invP) % 1.0
        if np.any(np.isfinite(y)):
            idx_min = int(np.nanargmin(y))
            phaseTime = (phaseTime - phaseTime[idx_min] + 0.5) % 1.0

    # Bounds (depth, width, center)
    lower  = np.array([1e-5, 1e-5, 0.25], float)
    upper  = np.array([0.99, 0.3,  0.75], float)
    bounds = (lower, upper)

    # Primary initial guesses
    pdepthGuess = primLocGuess = pwidthGuess = None
    if knownEclipse.lower() in ("none", "primary", "both"):
        if (prim_pos is not None) and (not np.isnan(prim_pos)) and (prim_pos > 1):
            prim_pos = ((prim_pos / Pbin) + 0.5) % 1.0

        pdepthGuess, primLocGuess, pwidthGuess = initialGuess3_local(
            phaseTime, y, ye,
            Pbin, bjd0, bounds,
            prim_pos, sec_pos, pwidth, swidth, pdepth, sdepth, DetrendingName, ID,
            locating='primary', bin_width=retry_bin_width, plotting=plotting,
            abs_time_sec=t
        )

    if (pdepthGuess is None) or (not np.isfinite(pdepthGuess)) or (pdepthGuess <= 0) or (pdepthGuess > 0.99):
        med = float(np.nanmedian(y))
        p01 = float(np.nanpercentile(y, 1))
        pdepthGuess = float(np.clip(med - p01, 1e-5, 0.9))
    if (primLocGuess is None) or (not np.isfinite(primLocGuess)):
        primLocGuess = 0.5
    primLocGuess = float(np.clip(primLocGuess, bounds[0][2], bounds[1][2]))
    if (pwidthGuess is None) or (not np.isfinite(pwidthGuess)) or (pwidthGuess <= 0):
        pwidthGuess = 0.01
    pwidthGuess = float(np.clip(pwidthGuess, bounds[0][1], min(bounds[1][1], 0.2)))

    print(f"Initial primary guesses - depth: {pdepthGuess}, loc: {primLocGuess}, width: {pwidthGuess}")

    if np.isfinite(pwidthGuess) and (pwidthGuess > 0):
        w0_gauss = pwidthGuess / 5.0
        w0_tanh  = pwidthGuess
    else:
        w0_gauss = 0.01
        w0_tanh  = 0.01

    try:
        print(f"[modelEclipse3] phaseTime range: {float(np.nanmin(phaseTime)):.4f}..{float(np.nanmax(phaseTime)):.4f}, "
              f"y median: {float(np.nanmedian(y)):.5f}, y min: {float(np.nanmin(y)):.5f}")
    except Exception:
        pass

    print("\n=== [DEBUG] Gaussian Fit Arguments ===")
    print(f"phaseTime shape: {phaseTime.shape}")
    print(f"y shape: {y.shape}")
    print(f"ye shape: {None if ye is None else ye.shape}")
    print(f"Model: gaussianModel_local")
    print(f"p0: {[pdepthGuess, w0_gauss, primLocGuess]}")
    print(f"bounds: {bounds}")
    print(f"retry_bin_width: {retry_bin_width}")
    print(f"do_once=True, gtol=1e-8")

    popt_g, used_bin_g, xg, yg, yeg = _fit_with_optional_binning_l(
        phaseTime, y, ye,
        gaussianModel_local,
        p0=[pdepthGuess, w0_gauss, primLocGuess],
        bounds=bounds, bin_width_for_retry=retry_bin_width, do_once=True, gtol=1e-8
    )

    popt_t, used_bin_t, xt, yt, yet = _fit_with_optional_binning_l(
        phaseTime, y, ye,
        tanh_transit_flat_local,
        p0=[pdepthGuess, w0_tanh, primLocGuess],
        bounds=bounds, bin_width_for_retry=retry_bin_width, do_once=True, gtol=1e-8
    )

    if (popt_g is None) and (popt_t is None):
        raise RuntimeError("Primary fit failed even after one binning retry.")

    _clip = np.clip
    _sum  = np.sum
    _log  = np.log

    if popt_g is not None:
        pdepth_gaus, sigma_g, prim_pos_gaus = popt_g
        pwidth_gaus = 5.0 * sigma_g
        yg_model = gaussianModel_local(xg, *popt_g)
        resid_g  = yg - yg_model
        k_g = 3
        n_g = yg.size
        denom_g  = _clip((yeg if yeg is not None else 1.0), 1e-12, None)
        chi2_g   = _sum((resid_g / denom_g)**2)
        rchi2_g  = chi2_g / max(1, (n_g - k_g))
        bic_gaussian = chi2_g + k_g * _log(max(1, n_g))
    else:
        bic_gaussian = np.inf
        rchi2_g      = np.inf

    if popt_t is not None:
        pdepth_tanh, pwidth_tanh, prim_pos_tanh = popt_t
        yt_model = tanh_transit_flat_local(xt, *popt_t)
        resid_t  = yt - yt_model
        k_t = 3
        n_t = yt.size
        denom_t  = _clip((yet if yet is not None else 1.0), 1e-12, None)
        chi2_t   = _sum((resid_t / denom_t)**2)
        rchi2_t  = chi2_t / max(1, (n_t - k_t))
        bic_tanh = chi2_t + k_t * _log(max(1, n_t))
    else:
        bic_tanh = np.inf
        rchi2_t  = np.inf

    if bic_gaussian < bic_tanh:
        print("Gaussian model is preferred for primary eclipse.")
        pdepth = float(pdepth_gaus)
        pwidth = float(pwidth_gaus)
        pwidth_ecc = float(pwidth_gaus)
        prim_pos = float(prim_pos_gaus)
        best_prim_model = "gaussianModel"
    else:
        print("Tanh model is preferred for primary eclipse.")
        pdepth = float(pdepth_tanh)
        pwidth = float(np.clip(1.75 * pwidth_tanh, bounds[0][1], min(bounds[1][1], 0.2)))
        pwidth_ecc = float(pwidth_tanh)
        prim_pos = float(prim_pos_tanh)
        best_prim_model = "tanhModel"

    # --- BASE-DIR OUTPUT (plot path) ---
    if plotting:
        _root = _resolve_base_dir(None)
        my_folder = _root / 'LightCurves' / 'Data_Preparation' / str(DetrendingName if DetrendingName is not None else "default")
        _ensure_parent(my_folder / "stub.txt")  # ensure directory
        save_path = my_folder / f'Primary_Eclipse_Fit_{ID}.png'

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        ax1.scatter(phaseTime, y, s=3, color='black', label='Data', rasterized=True)
        ax1.axhline(1, color='gray', linestyle='--', linewidth=2, label='Baseline Flux')
        ax1.set(title='Primary Eclipse Centered', xlabel='Phase', ylabel='Flux')
        ax1.legend(loc='best')

        ax2.scatter(phaseTime, y, s=3, color='black', label='Data', rasterized=True)
        try:
            if popt_g is not None:
                ax2.plot(phaseTime, gaussianModel_local(phaseTime, *popt_g), linewidth=2, label='Best Gaussian')
        except Exception:
            pass
        try:
            if popt_t is not None:
                ax2.plot(phaseTime, tanh_transit_flat_local(phaseTime, *popt_t), linewidth=2, label='Best Tanh')
        except Exception:
            pass

        ax2.axhline(1, color='gray', linestyle='--', linewidth=2)
        ax2.set(
            title=f'Primary Fit at Phase {prim_pos:.3f} \n rχ²(Gauss)={rchi2_g:.3f}, rχ²(Tanh)={rchi2_t:.3f}',
            xlabel='Phase', ylabel='Flux'
        )
        ax2.legend(loc='best')
        try:
            plt.tight_layout()
            fig.savefig(str(save_path), dpi=300, bbox_inches='tight')
            plt.close(fig)
        except Exception:
            try:
                plt.close(fig)
            except Exception:
                pass

    # Helper
    def _wrapped_phase_distance(p1, p2):
        '''
        Functionality:
            Compute circular distance between two phases in [0,1).

        Arguments:
            p1, p2 (float or array-like): Phase values.

        Returns:
            array-like:
                Minimum wrapped distance.
        '''
        d = np.abs(p1 - p2)
        return np.minimum(d, 1.0 - d)

    max_phase_distance = 0.05

    temp_sec_pos = sec_pos if not np.isnan(sec_pos) else 0.5
    _ = _wrapped_phase_distance(0.0, temp_sec_pos)

    timeCut, fluxCut, valid_mask = RemoveEclipses_local(
        phaseTime, y, Pbin, bjd0, prim_pos, sec_pos, pwidth, swidth, sep,
        cuts='primary', phase_folded='y'
    )
    idx_primary = valid_mask if isinstance(valid_mask, np.ndarray) else valid_mask[0]
    fluxErrCut = None if ye is None else ye[idx_primary]
    phaseTimeCut = (timeCut - 0.5) % 1.0

    bounds_gauss = (
        np.array([1e-4, 1e-4, 0.25], float),
        np.array([1,     0.3,  0.75], float)
    )

    for attempt in range(100):
        sdepthGuess, secLocGuess, swidthGuess, bin_width_dynamic = initialGuess3_local(
            phaseTimeCut, fluxCut, fluxErrCut,
            Pbin, bjd0, bounds_gauss,
            prim_pos, sec_pos, pwidth, swidth, pdepth, sdepth, DetrendingName,
            ID, locating='secondary', bin_width=retry_bin_width, plotting=plotting,
            abs_time_sec=t[idx_primary] if idx_primary is not None else t
        )

        argmin_local = int(np.argmin(fluxCut))
        minFluxPhase = phaseTimeCut[argmin_local]
        phase_distance = _wrapped_phase_distance(1.0, minFluxPhase)

        if phase_distance >= max_phase_distance:
            break

        if best_prim_model == "gaussianModel":
            pwidth += float(sigma_g)
        else:
            pwidth += 0.25 * float(pwidth)
        print(f"Increasing pwidth to {float(pwidth):.5f} due to nearby secondary")

        if pwidth > 0.1:
            print("Warning: pwidth expansion exceeded limit. Breaking loop.")
            break

        phaseTime = ((t - bjd0) * invP) % 1.0
        timeCut, fluxCut, valid_mask = RemoveEclipses_local(
            phaseTime, y, Pbin, bjd0, prim_pos, np.nan, pwidth, swidth, sep,
            cuts='primary', phase_folded='y'
        )
        idx_primary = valid_mask if isinstance(valid_mask, np.ndarray) else valid_mask[0]
        fluxErrCut = None if ye is None else ye[idx_primary]
        phaseTimeCut = (timeCut - 0.5) % 1.0

        sdepthGuess = secLocGuess = swidthGuess = np.nan

    print(f"Initial secondary guesses - depth: {sdepthGuess}, loc: {secLocGuess}, width: {swidthGuess}")

    phaseTimeCutBinned = phaseTimeCut
    fluxArrayCutBinned = fluxCut
    fluxArrayErrCutBinned = fluxErrCut
    scanning_range = np.linspace(0.25, 0.75, 200, endpoint=False)

    (bestfit_params, used_bin_sec, x_used, y_used, ye_used, best_rchi2) = _secondary_sweep_optbin_l(
        phaseTimeCutBinned, fluxArrayCutBinned, fluxArrayErrCutBinned,
        bounds_gauss,
        sdepthGuess, swidthGuess,
        scanning_range,
        bin_width_for_retry=retry_bin_width,
        do_once=True, gtol=1e-8
    )

    if bestfit_params is not None:
        sdepth, sigma_s, sec_pos = bestfit_params
        swidth = 4.0 * float(sigma_s)
    else:
        raise ValueError("No successful fits found in the secondary phase sweep, even after one binning retry.")

    if vetting:
        sep = abs((0.0 - sec_pos + 0.5) % 1.0 - 0.5)
        print(f"sep after fitting: {float(sep):.5f}, prim_pos: {float(prim_pos):.5f}, sec_pos: {float(sec_pos):.5f}")

        (result, ecc, omega, eccNoAssump, omegaNoAssump,
         ecoswNoAssump, esinwNoAssump) = vet_secondary_eclipse_local(
            x_used, y_used, ye_used,
            sec_pos, sdepth, Ra, Rb, Ta=Ta, Tb=Tb, a=a,
            period_days=Pbin / days2sec, bjd0=bjd0, sep=sep,
            pwidth=pwidth, swidth=swidth, prim_pos=prim_pos,
            pdepth=pdepth, pwidth_ecc=pwidth_ecc,
            DetrendingName=DetrendingName, ID=ID
        )
        print("vet secondary eclipse result:", result)

        prim_pos = (prim_pos - 0.5) % 1.0

        sec_pos = float(result["phase_secondary"])
        sdepth  = float(result["depth_fit"])
        swidth  = float(result["width_fit"])

        phaseTime_full = ((t - bjd0) * invP) % 1.0
        timeCutBoth, fluxCutBoth, valid_mask_both = RemoveEclipses_local(
            phaseTime_full, y, Pbin, bjd0, prim_pos, sec_pos, pwidth, swidth, sep,
            cuts='both', phase_folded='y'
        )
        idx_both = valid_mask_both if isinstance(valid_mask_both, np.ndarray) else valid_mask_both[0]
        fluxErrCutBoth = None if ye is None else ye[idx_both]
        AbsoluteTimeCutBoth = t[idx_both]

        print(f"Fitted Primary: loc={float(prim_pos)}, width={float(pwidth)}, depth={float(pdepth)}")
        print(f"Fitted Secondary: loc={float(sec_pos)}, width={float(swidth)}, depth={float(sdepth)}")

        return (
            AbsoluteTimeCutBoth, fluxCutBoth, fluxErrCutBoth,
            prim_pos, sec_pos, pwidth, swidth, pdepth, sdepth,
            sep, ecc, omega, eccNoAssump, omegaNoAssump, ecoswNoAssump, esinwNoAssump,
            knownEclipse
        )

    # Secondary-only BICs if not vetting
    p0_gauss_for_bic = [float(sdepth), max(float(swidth) / 6.0, 1e-4), float(sec_pos)]

    try:
        popt_straight, _ = so.curve_fit(
            straightModel_local, x_used, y_used,
            p0=[0, 1], method='trf', bounds=[[-1, 0], [1, 2]], gtol=1e-8
        )
    except Exception:
        popt_straight = None

    try:
        popt_tanh2, _ = so.curve_fit(
            tanh_transit_flat_local, x_used, y_used,
            p0=p0_gauss_for_bic, method='trf', bounds=bounds_gauss, gtol=1e-8
        )
    except Exception:
        popt_tanh2 = None

    def _compute_bic(model_func, params, x, y, yerr):
        '''
        Functionality:
            Compute a simple BIC-like score for a fitted model.

        Arguments:
            model_func (callable): Model function f(x, *params).
            params (array-like or None): Model parameter values.
            x, y (array-like): Data coordinates and values.
            yerr (array-like or None): Uncertainties; if None, unweighted.

        Returns:
            float:
                BIC-like score (lower is better). Returns inf if params is None.
        '''
        if params is None:
            return np.inf
        yhat = model_func(x, *params)
        r    = y - yhat
        if (yerr is None) or (yerr.size != y.size):
            denom = 1.0
        else:
            denom = np.clip(yerr, 1e-12, None)
        chi2 = np.sum((r / denom)**2)
        k    = len(params); n = y.size
        return chi2 + k * np.log(max(1, n))

    bic_gauss    = _compute_bic(gaussianModel_local,      p0_gauss_for_bic, x_used, y_used, ye_used)
    bic_straight = _compute_bic(straightModel_local,      popt_straight,    x_used, y_used, ye_used)
    bic_tanh     = _compute_bic(tanh_transit_flat_local,  popt_tanh2,       x_used, y_used, ye_used)

    bics = {'gaussian': float(bic_gauss), 'straight': float(bic_straight), 'tanh': float(bic_tanh)}
    return timeCut, fluxCut, fluxErrCut, bics



def periodCheck(Pbin, timeData, fluxData, fluxErrData, Rb, Ra):
    '''
    Functionality:
        Phase-folds the light curve on a candidate period (Pbin), bins it,
        fits a Gaussian to the primary eclipse (centered to phase ~0.5),
        and checks for evidence of a secondary eclipse with a depth consistent
        with the simple blackbody approximation depth ≈ (Rb/Ra)^2.
        If a plausible secondary is found outside the primary window, the period
        is accepted as-is. If a plausible secondary is found only within the
        primary window, the function assumes the BLS period was halved and returns
        2*Pbin. Otherwise, it returns Pbin.

    Arguments:
        Pbin        (float): Candidate binary period in the same time units as timeData.
        timeData    (array): Time array (seconds or days; must be consistent with Pbin).
        fluxData    (array): Flux array (normalized or raw; used comparatively).
        fluxErrData (array): Flux uncertainty array (unused here but kept for API parity).
        Rb          (float): Secondary radius (same units as Ra).
        Ra          (float): Primary radius.

    Returns:
        float: Validated/adjusted period:
               - Pbin if a plausible secondary eclipse is outside the primary window
                 or no secondary is found at all.
               - 2*Pbin if a plausible secondary signature appears only within the
                 primary window, suggesting the BLS period was halved.
    '''

    # phase fold the data over the candidate period
    phaseFoldedTime = ((timeData) / Pbin) % 1

    # bin data using binning helper; use an arbitrary bin size of 0.005 in phase
    _bin = globals().get('binData', None)
    if _bin is None:
        raise RuntimeError("binData is not available in the current namespace.")
    phaseTimeBinned, fluxArrayBinned, fluxArrayErrBinned = _bin(
        phaseFoldedTime, fluxData, fluxErrData, 0.005
    )

    # find the minimum of the binned flux (proxy for primary eclipse center)
    min_flux_index = np.argmin(fluxArrayBinned)
    min_flux_phase = phaseTimeBinned[min_flux_index]
    min_flux_value = fluxArrayBinned[min_flux_index]

    # shift so the primary center is at phase 0.5 for symmetric inspection
    primMiddlePFTime = (phaseTimeBinned - min_flux_phase + 0.5) % 1

    # quick diagnostic plot to visually confirm primary centered near 0.5
    try:
        plt.figure(figsize=(10, 5))
        plt.scatter(primMiddlePFTime, fluxArrayBinned, s=3)
        plt.xlabel('Phase (shifted)')
        plt.ylabel('Binned Flux')
        plt.title('Phase Folded Data with Primary in Middle')
        plt.show()
        plt.close()
    except Exception:
        try:
            plt.close()
        except Exception:
            pass

    # fit a Gaussian dip to the primary eclipse region
    initial_guess = [min_flux_value, 0.01, 0.5]
    bounds = ([0.0001, 0.0005, 0.4], [1, 0.1, 0.6])
    try:
        bestfit_flat, covariance_flat = so.curve_fit(
            gaussianModel,
            primMiddlePFTime,
            fluxArrayBinned,
            p0=initial_guess,
            method='trf',
            bounds=bounds,
            gtol=1e-8
        )
    except RuntimeError as e:
        print(f"Curve fitting failed: {e}")
        return Pbin

    # extract best-fit parameters and convert width (sigma) -> generous total width
    best_depth = bestfit_flat[0]
    best_width = bestfit_flat[1] * 8
    best_position = bestfit_flat[2]

    # expected secondary depth from simple area ratio (blackbody-like)
    expectedSecondaryDepth = (Rb / Ra) ** 2

    # look for secondary-like depths OUTSIDE the primary width window
    outside_primary = (
        (primMiddlePFTime > (best_position + best_width / 2)) |
        (primMiddlePFTime < (best_position - best_width / 2))
    )
    secondary_flux = fluxArrayBinned[outside_primary]
    secondary_phase = primMiddlePFTime[outside_primary]
    secondary_depths = 1 - secondary_flux
    secondary_depths = secondary_depths[secondary_depths > 0]

    if len(secondary_depths) > 0:
        within_threshold = np.any(
            np.abs(secondary_depths - expectedSecondaryDepth) < 0.25 * expectedSecondaryDepth
        )
    else:
        within_threshold = False

    if within_threshold:
        print(
            f"Secondary eclipse candidate found with depth around "
            f"{expectedSecondaryDepth:.4f} at phase {best_position:.4f} with width {best_width:.4f}"
        )
        return Pbin
    else:
        print("No secondary eclipse candidate found outside of the primary, checking within.")

    within_primary_mask = (
        (primMiddlePFTime >= (best_position - best_width / 2)) &
        (primMiddlePFTime <= (best_position + best_width / 2))
    )
    within_primary_flux = fluxArrayBinned[within_primary_mask]
    within_primary_phase = primMiddlePFTime[within_primary_mask]
    within_primary_depths = 1 - within_primary_flux
    within_primary_depths = within_primary_depths[within_primary_depths > 0]

    if len(within_primary_depths) > 0:
        within_primary_threshold = np.any(
            np.abs(within_primary_depths - expectedSecondaryDepth) < 0.25 * expectedSecondaryDepth
        )
    else:
        within_primary_threshold = False

    if within_primary_threshold == True:
        print(
            f"Secondary eclipse candidate found within primary width with depth around "
            f"{expectedSecondaryDepth:.4f} at phase {best_position:.4f} with width {best_width:.4f}"
        )
        print("BLS period has been halved, doubling now")
        PbinDoubled = 2 * Pbin
        return PbinDoubled

    print("No secondary eclipse candidate found within the primary width, no secondary eclipse detected.")
    return Pbin

    
def phase_fold(time, flux, period, bjd0=0):
    '''
    Functionality:
        Compute orbital phase in [0,1) for each timestamp given a period and epoch.
    Arguments:
        time (array-like): Time values (same units as `period` and `bjd0`).
        flux (array-like): Flux values (unused, accepted for API symmetry).
        period (float): Signal period in the same units as `time`.
        bjd0 (float, optional): Reference epoch in the same units as `time`. Default 0.
    Returns:
        numpy.ndarray: Phase array in [0,1) computed as ((time - bjd0) % period) / period.
    '''
    phase = ((time - bjd0) % period) / period
    return phase


def merge_wrap_dips(phase, flux, dips, tol=0.05):
    '''
    Functionality:
        Merge duplicate dip detections that occur near the phase wrap boundaries
        (i.e., near 0 and 1), keeping only the deeper one if both sides are present.
    Arguments:
        phase (array-like): Phase values in [0,1); only indices at `dips` are inspected.
        flux (array-like): Flux values aligned with `phase`.
        dips (array-like of int): Indices of detected dips in the original arrays.
        tol (float, optional): Phase neighborhood near 0 and 1 considered wrap-adjacent.
                              Default 0.05.
    Returns:
        numpy.ndarray: Possibly reduced dip-index array after merging wrap-adjacent duplicates.
    '''
    dips = np.asarray(dips, dtype=int)  # ensure ndarray for safe fancy indexing
    if len(dips) < 2:
        return dips

    ph = (phase[dips] % 1.0)
    near0 = np.where(ph < tol)[0]            # positions in 'dips'
    near1 = np.where(ph > 1.0 - tol)[0]      # positions in 'dips'

    if near0.size and near1.size:
        # pick the deepest (min flux) candidate on each side
        best0_pos = near0[np.argmin(flux[dips[near0]])]
        best1_pos = near1[np.argmin(flux[dips[near1]])]
        # keep the deeper of the two; drop all other boundary dips
        keep_pos = best0_pos if flux[dips[best0_pos]] < flux[dips[best1_pos]] else best1_pos

        # build mask: keep everything except boundary dips we didn't select
        keep_mask = np.ones(len(dips), dtype=bool)
        to_drop = np.concatenate([near0, near1])
        to_drop = to_drop[to_drop != keep_pos]
        keep_mask[to_drop] = False
        return dips[keep_mask]

    # nothing to merge
    return dips


def detect_dips(phase, flux, height, width, distance):
    '''
    Functionality:
        Detect downward excursions ("dips") by finding peaks on the inverted
        (negative) flux after sorting by phase; map detections back to original indices.
    Arguments:
        phase (array-like): Phase values (expected in [0,1), not strictly required).
        flux (array-like): Flux values aligned with `phase`.
        height (float): Minimum peak height on -flux (i.e., depth threshold).
        width (float or (float, float)): Peak width constraint (in samples) for `find_peaks`.
        distance (int): Minimum separation (in samples) between detected peaks.
    Returns:
        (numpy.ndarray, dict): Tuple of (dip_indices_in_original_order, properties_dict).
    '''
    # Sort by phase to ensure correct spacing logic
    sort_idx = np.argsort(phase)
    sorted_phase = phase[sort_idx]
    sorted_flux = flux[sort_idx]

    peaks, properties = find_peaks(-sorted_flux, height=height, width=width, distance=distance)

    # Convert peak indices back to original indices if needed
    original_peaks = sort_idx[peaks]

    return original_peaks, properties


def validate_period_filter3(
    time,
    flux,
    fluxErr,
    bls_period,                # seconds (can be None)
    window_length,
    DetrendingName,
    ID,
    bin_width=0.0001,
    plot=False,
    spurious_only_if_single=True,
    override=False,
    *,
    # BEHAVIOR SWITCHES
    accept_initial_pbin=False,         # if False => ignore given Pbin and locally re-search
    local_window_days='relative50',    # float (days) OR str e.g. "relative25" for ±25% of P
    global_min_days=0.05,              # floor if no/invalid Pbin
    global_max_days=90.0,              # ceiling if no/invalid Pbin
    use_double_dip_logic=True,         # run 2× fold + Case A/B/C/D/E; else primary-only validation
    do_bic_modeling=True               # run modelEclipse3 for shape/BIC classification
):
    '''
    Functionality:
        Validate (or refine) a candidate period by (1) seeding from a provided BLS
        period or a local/global BLS re-search, (2) folding and counting dips at P
        (primary) and optionally at 2P (secondary), (3) optionally computing simple
        shape-model BICs, and (4) applying minimal decision logic (cases A–E) to
        accept P or switch to 2P. Produces diagnostic plots/prints and a rich
        diagnostics dict. Core behavior/logic unchanged.

    Arguments:
        time (array-like): Time stamps in seconds.
        flux (array-like): Flux values aligned with `time`.
        fluxErr (array-like or None): Flux uncertainties aligned with `time`.
        bls_period (float or None): Seed period in seconds; if None/invalid, do global search.
        window_length (any): Unused placeholder (kept for API compatibility).
        DetrendingName (str): Label for output directory/plots.
        ID (str or int): Target identifier for file naming.
        bin_width (float, optional): Phase bin width for internal helpers (default 0.0001).
        plot (bool, optional): If True, save diagnostic fold plots.
        spurious_only_if_single (bool, optional): Enable spurious-point cleaner only if the
            *first* primary pass finds exactly one dip (default True).
        override (bool, optional): If True, short-circuit and return `bls_period` with diagnostics.
        accept_initial_pbin (bool, kw-only, default False): If False and `bls_period` valid, do local re-search.
        local_window_days (float or str, kw-only, default 'relative50'): ±window for local re-search; e.g. 'relative25'.
        global_min_days (float, kw-only, default 0.05): Global-search minimum (days) when no valid seed.
        global_max_days (float, kw-only, default 90.0): Global-search maximum (days) when no valid seed.
        use_double_dip_logic (bool, kw-only, default True): Also analyze 2× fold and apply cases A–E.
        do_bic_modeling (bool, kw-only, default True): Run `modelEclipse3` (vetting off) for BICs of simple shapes.

    Returns:
        (float, numpy.ndarray, numpy.ndarray, numpy.ndarray, dict):
            Pbin_sec: Validated/selected period in seconds (may match/refine/double the seed).
            time_out: Echo of input `time`.
            flux_out: Echo of input `flux`.
            fluxErr_out: Echo of input `fluxErr`.
            diagnostic_info: Dict with keys including
                'period_validation', 'decision' (days), 'dip_counts',
                'bics', 'best_model', 'flags', 'reason',
                'double_logic_used', 'bls_period_eff_days', 'double_period_days',
                'refinement_periods_sec', 'refinement_notes', 'seed',
                plus optional post-harmonics fields.

    '''
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    import scipy.optimize as so
    from pathlib import Path

    # Constants
    try:
        days2sec
    except NameError:
        days2sec = 86400.0

    # --- BASE-DIR OUTPUT ROOT (no signature change) ---
    _root = _resolve_base_dir(None)
    my_folder = _root / "LightCurves" / "Data_Preparation" / str(DetrendingName)
    my_folder.mkdir(parents=True, exist_ok=True)

    # EARLY BYPASS 
    if override:
        diagnostic_info = {
            'period_validation': True,
            'decision': (bls_period / days2sec) if (bls_period is not None and np.isfinite(bls_period)) else np.nan,
            'dip_counts': [0, np.nan if not use_double_dip_logic else 0],
            'bics': {'gaussian': np.nan, 'straight': np.nan, 'tanh': np.nan},
            'best_model': 'N/A',
            'flags': {'secondary': True, 'best_model': 'N/A'},
            'reason': 'Period validation override (no cleaning, no modeling).',
            'double_logic_used': bool(use_double_dip_logic),
            'bls_period_eff_days': (bls_period / days2sec) if (bls_period is not None and np.isfinite(bls_period)) else np.nan,
            'double_period_days': (2 * bls_period / days2sec) if (use_double_dip_logic and bls_period is not None and np.isfinite(bls_period)) else np.nan,
            'refinement_periods_sec': [np.nan],
            'refinement_notes': ['override'],
            'seed': {'source': 'override', 'min_days': np.nan, 'max_days': np.nan, 'picked_days': np.nan}
        }
        return bls_period, time, flux, fluxErr, diagnostic_info

    # helper: unified phase cleaner
    def clean_phase_series(
        phase,
        flux,
        fluxErr,
        DetrendingName,
        depth_fraction=0.75,
        phase_step=0.01,
        sigma_pos=2.0,
        sigma_neg=25.0,
        enable_spurious=True,
        min_keep_points=100,
        min_keep_frac=0.05,
        debug=False
    ):
        '''
        Functionality:
            Two-stage phase-domain cleaner for folded light curves.
    
        Arguments:
            phase (array-like): Phase values in [0,1).
            flux (array-like): Flux values.
            fluxErr (array-like or None): Errors; if None, zeros used.
            DetrendingName (str): Label for diagnostics.
            depth_fraction, phase_step, sigma_pos, sigma_neg : Tuning parameters.
            enable_spurious (bool): Enable stage-1 spurious removal.
            min_keep_points, min_keep_frac : Minimum data retention rules.
            debug (bool): Print diagnostic messages.
    
        Returns:
            (phase_clean, flux_clean, fluxErr_clean, keep_mask):
                Cleaned arrays and boolean mask of retained points.
        '''
        N = len(flux)
        if N == 0:
            return phase, flux, fluxErr, np.zeros(0, dtype=bool)

        use_spurious = bool(enable_spurious)
        phase_span = float(np.nanmax(phase) - np.nanmin(phase)) if N else 0.0
        if phase_span < 2.5 * phase_step:
            use_spurious = False

        if use_spurious:
            # pass base_dir so diagnostics land under the same root
            phase_c1, flux_c1, err_c1, keep_mask1 = remove_spurious_deep_points_binned_phase(
                phase, flux, fluxErr if fluxErr is not None else np.zeros_like(flux),
                DetrendingName, ID,
                depth_fraction=depth_fraction,
                phase_step=phase_step
            )
            if (keep_mask1 is None) or (keep_mask1.sum() < max(min_keep_points//2, int(min_keep_frac * N))):
                if debug:
                    print("[cleaner] Stage-1 removed too much; falling back to pass-through.")
                phase_c1, flux_c1, err_c1 = phase, flux, fluxErr
                keep_mask1 = np.ones(N, dtype=bool)
        else:
            phase_c1, flux_c1, err_c1 = phase, flux, fluxErr
            keep_mask1 = np.ones(N, dtype=bool)

        f1 = np.asarray(flux_c1, float)
        med = np.nanmedian(f1)
        mad = np.nanmedian(np.abs(f1 - med))
        sigma_rob = 1.4826 * mad
        keep_mask = keep_mask1.copy()

        if (not np.isfinite(sigma_rob)) or (sigma_rob < 1e-12):
            if debug:
                print("[cleaner] sigma_rob degenerate; using percentile clamp.")
            hi = np.nanpercentile(f1, 99.5)
            good_sigma = (f1 <= hi) | ~np.isfinite(f1)
        else:
            z = (f1 - med) / sigma_rob
            good_sigma = (z < sigma_pos) & (z > -sigma_neg)
            good_sigma |= ~np.isfinite(z)

        keep_mask_indices = np.where(keep_mask1)[0]
        keep_mask[keep_mask_indices] &= good_sigma

        finite_all = np.isfinite(phase) & np.isfinite(flux) & (np.ones_like(flux, dtype=bool) if fluxErr is None else np.isfinite(fluxErr))
        keep_mask &= finite_all

        min_needed = max(min_keep_points, int(min_keep_frac * N))
        if keep_mask.sum() < min_needed:
            if debug:
                print(f"[cleaner] Kept {keep_mask.sum()}<{min_needed}; relaxing thresholds once.")
            if (not np.isfinite(sigma_rob)) or (sigma_rob < 1e-12):
                keep_mask = keep_mask1 & finite_all
            else:
                z = ((np.asarray(flux_c1, float) - med) / sigma_rob)
                relaxed = (z < max(2.0, 6.0)) & (z > -max(25.0, 60.0))
                relaxed |= ~np.isfinite(z)
                keep_mask[:] = keep_mask1
                keep_mask[keep_mask_indices] &= relaxed
                keep_mask &= finite_all
                if keep_mask.sum() < min_needed:
                    if debug:
                        print("[cleaner] Still too few; reverting to stage-1 keep set.")
                    keep_mask = keep_mask1 & finite_all

        return phase[keep_mask], flux[keep_mask], (fluxErr[keep_mask] if fluxErr is not None else np.zeros(keep_mask.sum())), keep_mask

    timeVP = time.copy()
    fluxVP = flux.copy()
    fluxErrVP = fluxErr.copy()
    flags = {'secondary': False}

    # helper: fold & analyze
    def fold_and_analyze(
        time,
        flux,
        period,
        DetrendingName,
        ThresholdDips=2,
        return_cleaned_time_flux=False,
        precleaned=None,
        enable_spurious=True
    ):
        '''
        Functionality:
            Fold a light curve on `period`, shift deepest dip off edges, clean, detect dips
            (with spacing retries), and do a local Gaussian diagnostic fit.
    
        Arguments:
            time (array-like): Time values (seconds or days; consistent with `period`).
            flux (array-like): Flux values.
            period (float): Folding period (same units as `time`).
            DetrendingName (str): Label for diagnostics/paths.
            ThresholdDips (int): 1 for primary-only, 2 for primary+secondary policy.
            return_cleaned_time_flux (bool): Also return cleaned time/flux arrays.
            precleaned (dict or None): Optional dict with 'flux','fluxErr','cleaned_time'.
            enable_spurious (bool): Enable stage-1 spurious-removal in cleaner.
    
        Returns:
            dict:
                {
                  'phase': phase_clean,
                  'flux': flux_clean,
                  'fluxErr': fluxErr_clean,
                  'dips': dips,
                  'period': period,
                  ['cleaned_time','cleaned_flux','cleaned_fluxErr' if requested]
                }
        '''
        import numpy as np
        import scipy.optimize as so

        phase = (time / period) % 1

        # shift primary away from edges
        shifted_phase = phase.copy()
        shift_step = 0.05
        max_attempts = int(1 / shift_step)
        attempts = 0
        while attempts < max_attempts:
            deepest_indices = np.argsort(flux)[:3]
            deepest_phases = shifted_phase[deepest_indices] % 1
            if not (np.any(np.isclose(deepest_phases, 0, atol=0.05)) or
                    np.any(np.isclose(deepest_phases, 1, atol=0.05))):
                break
            shifted_phase = (shifted_phase + shift_step) % 1
            attempts += 1
        phase = shifted_phase
        if attempts > 0:
            print(f"Applied phase shift of {shift_step * attempts:.3f} to move primary away from phase edges.")

        # cleaning
        if precleaned is None:
            df = 0.75 if ThresholdDips == 1 else 0.80
            phase_clean, flux_clean, fluxErr_clean, keep_mask = clean_phase_series(
                phase, flux, fluxErr if fluxErr is not None else np.zeros_like(flux),
                DetrendingName, depth_fraction=df, phase_step=0.01, enable_spurious=True, debug=True
            )
        else:
            flux_clean = precleaned['flux']
            fluxErr_clean = precleaned['fluxErr']
            cleaned_time = precleaned['cleaned_time']
            phase_clean = (cleaned_time / period) % 1
            keep_mask = np.ones_like(flux_clean, dtype=bool)

        # too few points → re-estimate with global search
        if len(flux_clean) < 5:
            print("Too few points after cleaning; BLS to re-estimate period.")
            period, *_, meta_bls = iterative_bls_single_dip_search(
                time, flux, fluxErr, DetrendingName,
                min_period_days=global_min_days, max_period_days=global_max_days,
                q_eff=None, pre_detrend='both', bic_delta=0.0,
                check_harmonics=False, plot_harmonics=False,
                presets_sequence=[HYPERFINE]
            )
            return fold_and_analyze(
                time, flux, period, DetrendingName,
                ThresholdDips=1, return_cleaned_time_flux=return_cleaned_time_flux,
                enable_spurious=enable_spurious
            )

        # dip detection with spacing retries
        min_flux_val = np.min(flux_clean)
        obs_depth = 1 - min_flux_val
        dip_phase = phase_clean[np.argmin(flux_clean)] % 1
        min_phase_floor = 1e-2
        factors = [1.0, 2.0, 3.0] if ThresholdDips == 1 else [1.5, 2.5, 3.5]
        chosen = None
        last_attempt = None

        for f in factors:
            width_est = estimate_eclipse_width(phase_clean, flux_clean, dip_phase, 0.1, obs_depth)
            min_spacing_phase = max(min_phase_floor, f * width_est)
            distance = int(np.ceil(min_spacing_phase * len(phase_clean)))
            threshold_depth = (0.75 if ThresholdDips == 1 else 0.80) * obs_depth
            height = 1 - threshold_depth
            dips, _ = detect_dips(phase_clean, flux_clean, height=-height, width=width_est, distance=distance)
            dips = merge_wrap_dips(phase_clean, flux_clean, dips, tol=0.05)
            last_attempt = (dips, width_est, min_spacing_phase, distance, f)
            accept = (len(dips) <= (1 if ThresholdDips == 1 else 2))
            print(f"[dips] try factor={f:.2f} distance={distance} → N_dips={len(dips)} (pass={'PRIMARY' if ThresholdDips==1 else 'SECONDARY'})")
            if accept:
                chosen = last_attempt
                break

        if chosen is None:
            chosen = last_attempt

        dips, width_est, min_spacing_phase, distance, factor_used = chosen
        print(f"[dips] accepted factor={factor_used:.2f} width_est={width_est:.6f} min_spacing_phase={min_spacing_phase:.6f} distance={distance} N_dips={len(dips)}")

        # local gaussian modeling around primary dip (diagnostic)
        dip_center = phase_clean[np.argmin(flux_clean)] % 1
        mask = (phase_clean > dip_center - 0.1) & (phase_clean < dip_center + 0.1)
        x_dip = phase_clean[mask]
        y_dip = flux_clean[mask]
        if len(x_dip) > 5:
            try:
                popt_gauss, _ = so.curve_fit(
                    gaussianModel, x_dip, y_dip,
                    p0=[obs_depth, max(width_est / 2.355, 1e-4), dip_center],
                    maxfev=10000
                )
                _ = np.sum((y_dip - gaussianModel(x_dip, *popt_gauss)) ** 2) / max(1, (len(y_dip) - 3))
            except Exception as e:
                print(f"Gaussian fit failed: {e}")

        result_dict = {
            'phase': phase_clean,
            'flux': flux_clean,
            'fluxErr': fluxErr_clean,
            'dips': dips,
            'period': period,
        }
        if return_cleaned_time_flux:
            result_dict['cleaned_time'] = time[keep_mask]
            result_dict['cleaned_flux'] = flux[keep_mask]
            result_dict['cleaned_fluxErr'] = (np.zeros_like(flux) if fluxErr is None else fluxErr)[keep_mask]
        return result_dict

    # normalize local_window_days
    def _resolve_local_window_days_arg(local_window_days, bls_period):
        '''
        Functionality:
            Convert `local_window_days` argument into a usable numeric window size.
            Allows absolute values (e.g., 10.0) or relative strings like "relativeXX"
            meaning 50% of the detected BLS period (in days).
    
        Arguments:
            local_window_days (float or str): Window size in days, or "relativeXX".
            bls_period (float or None): BLS period in seconds (or None if unavailable).
    
        Returns:
            float:
                Window size in days. Defaults to 10.0 if parsing fails or period invalid.
        '''
        if isinstance(local_window_days, str) and local_window_days.lower().startswith("relative"):
            try:
                frac = float(local_window_days.lower().replace("relative", "")) / 100.0
            except Exception:
                frac = 0.50  # default 50% if parse fails
            if bls_period is not None and np.isfinite(bls_period) and bls_period > 0:
                p_days = bls_period / days2sec
                return max(0.0, frac * p_days)
            else:
                return 10.0
        else:
            try:
                return float(local_window_days)
            except Exception:
                return 10.0

    # Seed period selection
    seed_info = {'source': None, 'min_days': None, 'max_days': None, 'picked_days': None}
    trusted_seconds = (bls_period is not None) and np.isfinite(bls_period) and (bls_period > 0)
    local_win_days_val = _resolve_local_window_days_arg(local_window_days, bls_period)

    need_local_search = (not accept_initial_pbin) and trusted_seconds
    need_global_search = (not trusted_seconds)

    if need_global_search:
        print("[seed] No/invalid initial period → global BLS search.")
        seed_min_days = global_min_days
        seed_max_days = global_max_days
        newP, *_, _meta = iterative_bls_single_dip_search(
            time, flux, fluxErr, DetrendingName,
            min_period_days=seed_min_days, max_period_days=seed_max_days,
            q_eff=None, pre_detrend='both', bic_delta=0.0,
            check_harmonics=False, plot_harmonics=False,
            presets_sequence=[HYPERFINE]
        )
        if np.isfinite(newP):
            bls_period_seed = float(newP)
            seed_info.update({'source': 'global_search', 'min_days': seed_min_days, 'max_days': seed_max_days,
                              'picked_days': bls_period_seed / days2sec})
        else:
            bls_period_seed = max(global_min_days, 0.5 * (global_min_days + global_max_days)) * days2sec
            seed_info.update({'source': 'global_fallback', 'min_days': seed_min_days, 'max_days': seed_max_days,
                              'picked_days': bls_period_seed / days2sec})

    elif need_local_search:
        p_days = bls_period / days2sec
        seed_min_days = max(global_min_days, p_days - local_win_days_val)
        seed_max_days = min(global_max_days, p_days + local_win_days_val)
        if seed_min_days >= seed_max_days:
            seed_min_days = max(global_min_days, p_days * 0.5)
            seed_max_days = min(global_max_days, p_days * 1.5)
        print(f"[seed] Using provided Pbin as a prior. Local BLS search in [{seed_min_days:.6f}, {seed_max_days:.6f}] d (Δ={local_win_days_val:.6f} d).")
        newP, *_, _meta = iterative_bls_single_dip_search(
            time, flux, fluxErr, DetrendingName,
            min_period_days=seed_min_days, max_period_days=seed_max_days,
            q_eff=None, pre_detrend='both', bic_delta=0.0,
            check_harmonics=False, plot_harmonics=False,
            presets_sequence=[HYPERFINE]
        )
        if np.isfinite(newP):
            bls_period_seed = float(newP)
            seed_info.update({'source': 'local_search', 'min_days': seed_min_days, 'max_days': seed_max_days,
                              'picked_days': bls_period_seed / days2sec})
        else:
            bls_period_seed = bls_period
            seed_info.update({'source': 'local_failed_fallback_to_given', 'min_days': seed_min_days, 'max_days': seed_max_days,
                              'picked_days': bls_period_seed / days2sec})
    else:
        bls_period_seed = bls_period
        seed_info.update({'source': 'provided_as_is', 'min_days': np.nan, 'max_days': np.nan,
                          'picked_days': bls_period_seed / days2sec})

    # Main passes
    result = {}
    dip_counts = []
    refinement_periods = []
    refinement_notes = [f"seed:{seed_info['source']}"]

    # PRIMARY
    primary = fold_and_analyze(
        time, flux, bls_period_seed,
        DetrendingName,
        ThresholdDips=1,
        return_cleaned_time_flux=True,
        precleaned=None,
        enable_spurious=(not spurious_only_if_single)
    )
    curr_period = primary['period']  # seconds
    curr_dips = len(primary['dips'])
    refinement_periods.append(curr_period)
    refinement_notes.append(f"init:{curr_dips} dips")

    # Enable spurious removal only if exactly one dip on the first pass (policy)
    if spurious_only_if_single and curr_dips == 1:
        print("First pass found exactly one dip — enabling spurious-point removal and re-running primary pass.")
        primary = fold_and_analyze(
            time, flux, curr_period,
            DetrendingName,
            ThresholdDips=1,
            return_cleaned_time_flux=True,
            precleaned=None,
            enable_spurious=True
        )
        curr_period = primary['period']
        curr_dips = len(primary['dips'])
        refinement_periods.append(curr_period)
        refinement_notes.append("init_rerun_spurious:on")

    # If >1 dip, iterative refinement
    if curr_dips > 1:
        print(f"Primary found {curr_dips} dips at seed period. Entering BLS refinement loop.")
        try:
            newP, *_, meta_bls = iterative_bls_single_dip_search(
                time, flux, fluxErr, DetrendingName,
                min_period_days=global_min_days, max_period_days=global_max_days,
                q_eff=None, pre_detrend='both', bic_delta=0.0,
                check_harmonics=False, plot_harmonics=False,
                presets_sequence=[HYPERFINE]
            )
            if np.isfinite(newP):
                curr_period = float(newP)
                primary = fold_and_analyze(
                    time, flux, curr_period, DetrendingName,
                    ThresholdDips=1, return_cleaned_time_flux=True,
                    enable_spurious=False
                )
                curr_dips = len(primary['dips'])
                refinement_periods.append(curr_period)
                refinement_notes.append(f"bls_full:{curr_dips} dips")
        except Exception as e:
            print(f"BLS refinement (full) failed: {e}")

        # small frequency-space refinements
        def make_refine_grids(
            curr_period_sec, time,
            q_min=0.01, phi_tol=0.1,
            k=10, oversamp=8, levels=7,
            df_min=None, max_points=150_000, merge=False
        ):
            '''
            Functionality:
                Build multi-level frequency/period refinement grids around a candidate period.
        
            Arguments:
                curr_period_sec (float): Current best period (seconds).
                time (array-like): Observation times (seconds).
                q_min (float): Min transit duty cycle used in df heuristic.
                phi_tol (float): Phase tolerance factor for df heuristic.
                k (int): Half-width in bins on each level (total ~2k+1).
                oversamp (int): Frequency oversampling per level.
                levels (int): Number of refinement levels.
                df_min (float or None): Stop if df < df_min (in cycles/day).
                max_points (int): Cap grid size per level (downsample if exceeded).
                merge (bool): If True, return a single merged unique period grid.
        
            Returns:
                list[np.ndarray]:
                    List of period arrays (seconds), or single merged array if merge=True.
            '''
            t_days = (np.max(time) - np.min(time)) / 86400.0
            if t_days <= 0 or not np.isfinite(t_days):
                return [np.array([curr_period_sec])]
            f0 = 1.0 / (curr_period_sec / 86400.0)
            df0 = max((phi_tol * q_min) / t_days, 1e-14)
            grids = []
            for lvl in range(levels):
                df = df0 / (oversamp ** lvl)
                if df_min is not None and df < df_min:
                    break
                f_grid = f0 + np.arange(-k, k + 1, dtype=float) * df
                f_grid = f_grid[f_grid > 0]
                if f_grid.size < 3:
                    continue
                P_grid = 86400.0 / f_grid
                if P_grid.size > max_points:
                    step = int(np.ceil(P_grid.size / max_points))
                    P_grid = P_grid[::step]
                grids.append(P_grid)
            if merge:
                if not grids:
                    return [np.array([curr_period_sec])]
                pg = np.unique(np.concatenate(grids))
                return [pg]
            return grids

        for lvl, P_grid in enumerate(make_refine_grids(curr_period, time)):
            if curr_dips <= 1:
                break
            try:
                newP, *_, meta_bls = iterative_bls_single_dip_search(
                    time, flux, fluxErr, DetrendingName,
                    min_period_days=global_min_days, max_period_days=global_max_days,
                    q_eff=None, pre_detrend='both', bic_delta=0.0,
                    check_harmonics=False, plot_harmonics=False,
                    presets_sequence=[HYPERFINE]
                )
                if np.isfinite(newP):
                    prev_period = curr_period
                    curr_period = float(newP)
                    primary = fold_and_analyze(
                        time, flux, curr_period, DetrendingName,
                        ThresholdDips=1, return_cleaned_time_flux=True,
                        enable_spurious=False
                    )
                    curr_dips = len(primary['dips'])
                    refinement_periods.append(curr_period)
                    refinement_notes.append(f"freq_refine_lvl{lvl}:{curr_dips} dips (grid={len(P_grid)})")
                    if abs(curr_period - prev_period) / curr_period < 1e-8:
                        print("Refinement converged; stopping.")
                        break
            except Exception as e:
                print(f"BLS refinement (level {lvl}) failed: {e}")
                continue

    # Store primary result
    result['bls'] = primary
    bls_period_eff = primary['period']  # seconds
    dip_counts.append(len(primary['dips']))

    # Prepare cleaned arrays
    time_clean = primary.get('cleaned_time', time)
    flux_clean = primary.get('cleaned_flux', flux)
    fluxErr_clean = primary.get('cleaned_fluxErr', (np.zeros_like(flux) if fluxErr is None else fluxErr))

    # SECONDARY @ 2× (only if enabled)
    if use_double_dip_logic:
        double_period = 2 * bls_period_eff
        precleaned_for_double = {'flux': flux_clean, 'fluxErr': fluxErr_clean, 'cleaned_time': time_clean}
        res_double = fold_and_analyze(
            time_clean, flux_clean, double_period,
            DetrendingName,
            ThresholdDips=2,
            return_cleaned_time_flux=False,
            precleaned=precleaned_for_double,
            enable_spurious=False
        )
        result['double'] = res_double
        dip_counts.append(len(res_double['dips']))
    else:
        result['double'] = None
        dip_counts.append(np.nan)  # secondary not evaluated

    # Optional plot
    if plot:
        save_path = my_folder / f'BLS_Double_Period_{ID}.png'
        plt.figure(figsize=(10, 6))
        ax = plt.gca()
        ax.set_title("Folded Light Curve", fontsize=14)
        ax.plot(result['bls']['phase'], result['bls']['flux'], '.', ms=3, alpha=0.5,
                label=f"BLS Period ({len(result['bls']['dips'])} dip{'s' if len(result['bls']['dips']) > 1 else ''})")
        for i, dip in enumerate(result['bls']['dips']):
            dip_phase = result['bls']['phase'][dip] % 1
            ax.plot(dip_phase, result['bls']['flux'][dip], marker='*', markersize=15,
                    label=f"BLS Dip at {dip_phase:.4f}" if i == 0 else None)

        if use_double_dip_logic and result['double'] is not None:
            ax.plot(result['double']['phase'], result['double']['flux'], '.', ms=3, alpha=0.4,
                    label=f"Double Period ({len(result['double']['dips'])} dip{'s' if len(result['double']['dips']) > 1 else ''})")
            for dip in result['double']['dips']:
                dip_phase = result['double']['phase'][dip] % 1
                ax.plot(dip_phase, result['double']['flux'][dip], marker='*', markersize=15,
                        label=f"Double Dip at {dip_phase:.4f}")

        ax.axhline(1, linestyle='--', linewidth=1)
        ax.set_xlabel("Phase"); ax.set_ylabel("Normalized Flux")
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend(loc='best', fontsize=10)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show(); plt.close()

    # Model primary eclipse (diagnostic BICs)
    if do_bic_modeling:
        time_sec, flux_sec, fluxErr_sec, bics = modelEclipse3(
            time, flux, fluxErr, bls_period_eff, 0, None,
            np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
            None, None, None, None, None,
            DetrendingName=DetrendingName, ID=ID, plotting=True,
            bin_width=None, eclipsePrior=False, vetting=False
        )
        best_model = min(bics, key=bics.get)
    else:
        bics = {'gaussian': np.nan, 'tanh': np.nan, 'straight': np.nan}
        best_model = 'unknown'

    flags['best_model'] = best_model

    # Decision logic (minimal change)
    Pbin = bls_period_eff
    reason = "Default: BLS period used."
    period_validation = False

    if use_double_dip_logic:
        # Existing Case A/B/C/D/E logic
        if dip_counts[0] == 1 and dip_counts[1] == 2:
            period_validation = True
            if best_model in ['gaussian', 'tanh']:
                Pbin = bls_period_eff
                reason = "Case A: Secondary eclipse detected after primary removal → original period."
                flags['secondary'] = True
            elif best_model == 'straight':
                d0, d1 = result['double']['dips'][0], result['double']['dips'][1]
                delta_flux = abs(result['double']['flux'][d0] - result['double']['flux'][d1])
                if delta_flux < 0.05:
                    if (2 * bls_period_eff) / days2sec < 10:
                        Pbin = 2 * bls_period_eff
                        reason = "Case B: Equal-depth dips, short period, no secondary → double period."
                        flags['secondary'] = False
                    else:
                        Pbin = bls_period_eff
                        reason = "Case C: Equal-depth dips, long period, no secondary → original period."
                        flags['secondary'] = False
                else:
                    reason = "Case E: Unequal dips with straight fit → keep original period."
                    flags['secondary'] = False
        elif dip_counts[0] == 1 and dip_counts[1] == 1:
            period_validation = True
            Pbin = bls_period_eff
            reason = "Case D: One dip in both folds — adopt original period."
        else:
            reason = "Double-dip logic used; defaulting to BLS period after checks."
    else:
        # Primary-only validation
        if dip_counts[0] == 1:
            period_validation = True
            Pbin = bls_period_eff
            reason = "Primary-only validation: one dip at BLS period; double-dip logic disabled."
            flags['secondary'] = None
        else:
            reason = "Primary-only validation: >1 dip at BLS period; consider refinement or tighter search."
            flags['secondary'] = None

    diagnostic_info = {
        'period_validation': period_validation,
        'decision': Pbin / days2sec,
        'dip_counts': dip_counts,
        'bics': bics,
        'best_model': best_model,
        'flags': flags,
        'reason': reason,
        'double_logic_used': bool(use_double_dip_logic),
        'bls_period_eff_days': bls_period_eff / days2sec,
        'double_period_days': ((2 * bls_period_eff) / days2sec) if use_double_dip_logic else np.nan,
        'refinement_periods_sec': refinement_periods,
        'refinement_notes': refinement_notes,
        'seed': seed_info
    }

    # Post-validation harmonics (diagnostic)
    try:
        min_days = max(global_min_days, (Pbin / days2sec) * 0.25)
        max_days = min(global_max_days, (Pbin / days2sec) * 4.0)
        _, _, _, _, meta_h = iterative_bls_single_dip_search(
            time, flux, fluxErr, DetrendingName,
            min_period_days=min_days,
            max_period_days=max_days,
            q_eff=None, pre_detrend='both', bic_delta=0.0,
            check_harmonics=True, plot_harmonics=bool(plot),
            presets_sequence=[HYPERFINE]
        )
        harmonics_best_sec = (meta_h.get('best_period_sec') if isinstance(meta_h, dict) else np.nan)
        harmonics_notes = (meta_h.get('notes') if isinstance(meta_h, dict) else None)
        diagnostic_info['post_harmonics_checked'] = True
        diagnostic_info['post_harmonics_best_days'] = (harmonics_best_sec / days2sec) if np.isfinite(harmonics_best_sec) else np.nan
        if harmonics_notes is not None:
            diagnostic_info['post_harmonics_notes'] = harmonics_notes
    except Exception as _e:
        diagnostic_info['post_harmonics_checked'] = False
        diagnostic_info['post_harmonics_error'] = str(_e)

    return Pbin, timeVP, fluxVP, fluxErrVP, diagnostic_info


def remove_spurious_deep_points(
    time, flux, flux_err, Pbin, DetrendingName, ID,
    depth_threshold_fraction=0.75,
    phase_step=0.01,
    width_sigma_mult=3.0,
    save_phase_diagnostic=True,
    debug=False
):
    '''
    Functionality:
        Identify and remove *out-of-eclipse* points that are spuriously deep by:
        (1) folding the data on Pbin to phase, (2) fitting a single Gaussian-like
        eclipse to locate its center/width, (3) defining a circular in-phase mask
        for “in-eclipse” samples, (4) computing a depth-based threshold between
        the in-eclipse minimum and the out-of-eclipse baseline, and (5) removing
        only those points outside the eclipse window that lie deeper than the
        threshold. Plots (time view + optional phase view) are saved for QA.
        Core behavior and math are unchanged.

    Arguments:
        time (array-like): Timestamps (same units as Pbin).
        flux (array-like): Flux values aligned with `time`.
        flux_err (array-like or None): Flux uncertainties aligned with `time`.
        Pbin (float): Period in the same units as `time`.
        DetrendingName (str): Label used for output directory/filenames.
        ID (str or int): Target identifier for filenames.

    Returns:
        (time_clean, flux_clean, flux_err_clean) with out-of-eclipse deep points removed.
    '''
    import numpy as np
    import matplotlib.pyplot as plt
    import scipy.optimize as so
    from pathlib import Path

    base = _resolve_base_dir(None)
    out_dir = base / "LightCurves" / "Data_Preparation" / str(DetrendingName)
    out_dir.mkdir(parents=True, exist_ok=True)

    def calculate_reduced_chi_squared(residuals, errors, num_params):
        e = np.asarray(errors if errors is not None else np.zeros_like(residuals), float)
        bad = ~np.isfinite(e) | (e <= 0)
        if np.any(bad):
            robust_sigma = 1.4826 * np.nanmedian(np.abs(residuals - np.nanmedian(residuals)))
            if not np.isfinite(robust_sigma) or robust_sigma <= 0:
                robust_sigma = np.nanstd(residuals) if np.isfinite(np.nanstd(residuals)) else 1.0
            e = np.where(bad, robust_sigma, e)
        chi2 = np.nansum((residuals / e) ** 2)
        dof  = max(1, len(residuals) - int(num_params))
        return chi2 / dof

    try:
        gaussianModel
    except NameError:
        def gaussianModel(phi, A, mu, sigma, offset):
            return A * np.exp(-0.5 * ((phi - mu) / sigma) ** 2) + offset

    phi = (np.asarray(time) % Pbin) / Pbin
    f   = np.asarray(flux, float)
    fe  = np.asarray(flux_err if flux_err is not None else np.zeros_like(f), float)

    offsets     = float(np.nanmedian(f))
    A_guess     = float(np.nanmin(f) - offsets)
    sigma_guess = 0.02
    phase_guesses = np.arange(0.0, 1.0, float(max(phase_step, 1e-3)))

    best_fit = None
    best_params = None
    best_chi2_red = np.inf

    for mu_guess in phase_guesses:
        try:
            p0 = [A_guess, float(mu_guess), float(sigma_guess), offsets]
            popt, _ = so.curve_fit(
                gaussianModel, phi, f, p0=p0,
                sigma=fe, absolute_sigma=True,
                bounds=([-np.inf, 0.0, 1e-4, -np.inf],
                        [0.0,     1.0, 0.25, np.inf]),
                maxfev=20000
            )
            model_f = gaussianModel(phi, *popt)
            chi2r   = calculate_reduced_chi_squared(f - model_f, fe, len(popt))
            if chi2r < best_chi2_red:
                best_chi2_red = chi2r
                best_params   = popt
                best_fit      = model_f
        except:
            continue

    if best_params is None:
        return time, flux, flux_err

    A, mu, sigma, offset = [float(x) for x in best_params]
    sigma = abs(sigma)
    hwidth = float(width_sigma_mult * sigma)

    dphi = np.abs(((phi - mu + 0.5) % 1.0) - 0.5)
    in_eclipse = dphi <= hwidth
    if not np.any(in_eclipse):
        return time, flux, flux_err

    out_eclipse = ~in_eclipse

    eclipse_min = float(np.nanmin(f[in_eclipse]))
    baseline    = float(np.nanmedian(f[out_eclipse])) if np.any(out_eclipse) else float(np.nanmedian(f))
    thr = eclipse_min + (1.0 - float(depth_threshold_fraction)) * (baseline - eclipse_min)
    thr = float(np.clip(thr, eclipse_min, baseline))

    deep_outliers = out_eclipse & (f <= thr)

    save_time = out_dir / f"Spurious_Signals_Removed_TIME_{ID}.png"
    order_t = np.argsort(time)
    plt.figure(figsize=(10, 5))
    plt.scatter(np.asarray(time)[order_t], f[order_t], s=6)
    if np.sum(deep_outliers):
        plt.scatter(np.asarray(time)[deep_outliers], f[deep_outliers], s=18, color='red')
    plt.savefig(save_time, dpi=300, bbox_inches='tight')
    plt.close()

    if save_phase_diagnostic:
        save_phase = out_dir / f"Spurious_Signals_Removed_PHASE_{ID}.png"
        order_p = np.argsort(phi)
        plt.figure(figsize=(10, 5))
        plt.scatter(phi[order_p], f[order_p], s=6)
        if best_fit is not None:
            plt.plot(phi[order_p], np.asarray(best_fit)[order_p], color='black', lw=2)
        plt.axhline(thr, color='red', ls='--')
        plt.savefig(save_phase, dpi=300, bbox_inches='tight')
        plt.close()

    keep = ~deep_outliers
    return np.asarray(time)[keep], f[keep], fe[keep]


def remove_spurious_deep_points_binned_phase(
    binned_phase, folded_flux, folded_flux_err, DetrendingName, ID,
    depth_fraction=0.75, phase_step=0.01
):
    '''
    Functionality:
        Operate in (possibly binned) phase space to remove out-of-eclipse spurious deep
        points. Fits a Gaussian to the folded curve to locate the eclipse, defines a
        circular in-phase eclipse mask, and removes points outside the mask that are
        deeper than a threshold fraction of the eclipse depth. Saves a diagnostic plot.

    Arguments:
        binned_phase (array-like): Phase array in [0, 1).
        folded_flux (array-like): Flux values aligned with binned_phase.
        folded_flux_err (array-like): Flux uncertainties aligned with binned_phase (zeros allowed).
        DetrendingName (str): Label for output directory naming.
        ID (str|int): Target identifier for filenames.
        depth_fraction (float, optional): Fraction (0–1) of eclipse depth that sets removal threshold.
        phase_step (float, optional): Phase step for scanning trial centers.

    Returns:
        (numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray):
            phase_kept: Phase values with spurious points removed.
            flux_kept: Flux values with same mask applied.
            flux_err_kept: Flux errors with same mask applied.
            keep_mask: Boolean mask indicating kept samples.
    '''
    # --- helpers ---
    def calculate_reduced_chi_squared(residuals, errors, num_params):
        errors = np.where(errors == 0, 1e-10, errors)
        chi_squared = np.sum((residuals / errors) ** 2)
        return chi_squared / max((len(residuals) - num_params), 1)

    phase = np.copy(binned_phase)
    best_fit = None
    best_chi2_red = np.inf
    best_params = None

    offsets = np.median(folded_flux)
    A_guess = np.min(folded_flux) - offsets
    sigma_guess = 0.001
    phase_guesses = np.arange(0, 1, phase_step)

    for mu_guess in phase_guesses:
        try:
            p0 = [A_guess, sigma_guess, mu_guess]
            popt, _ = so.curve_fit(gaussianModel, phase, folded_flux, p0=p0, method='trf', gtol=1e-8)
            model_flux = gaussianModel(phase, *popt)
            chi2_red = calculate_reduced_chi_squared(folded_flux - model_flux, folded_flux_err, len(popt))
            if chi2_red < best_chi2_red:
                best_chi2_red = chi2_red
                best_params = popt
                best_fit = model_flux
        except Exception:
            continue

    if best_params is None:
        print("No successful Gaussian fit found. Returning original data.")
        keep_mask = np.ones_like(phase, dtype=bool)
        return phase, folded_flux, folded_flux_err, keep_mask

    A, sigma, mu = best_params
    sigma = abs(sigma)

    # HWHM doubled (matches prior behavior)
    eclipse_width = 2 * np.sqrt(2 * np.log(2)) * sigma

    dphi = np.abs(((phase - mu + 0.5) % 1.0) - 0.5)
    in_eclipse_mask = dphi <= eclipse_width
    out_of_eclipse_mask = ~in_eclipse_mask

    if not np.any(in_eclipse_mask):
        print(f"No data points found within eclipse region at center={mu:.4f}, width={eclipse_width:.4f}.")
        keep_mask = np.ones_like(phase, dtype=bool)
        return phase, folded_flux, folded_flux_err, keep_mask

    eclipse_min = np.nanmin(folded_flux[in_eclipse_mask])
    baseline = np.nanmedian(folded_flux[out_of_eclipse_mask])

    threshold = eclipse_min + (1.0 - depth_fraction) * (baseline - eclipse_min)
    threshold = float(np.clip(threshold, eclipse_min, baseline))

    deep_outliers = out_of_eclipse_mask & (folded_flux <= threshold)

    # --- base-dir aware output paths (no signature change) ---
    base = _resolve_base_dir(None)
    my_folder = base / 'LightCurves' / 'Data_Preparation' / str(DetrendingName)
    _ensure_parent(my_folder / 'dummy.txt')  # ensures parent dirs exist

    save_path = my_folder / f'Spurious_Signals_Removed_{ID}.png'

    # Plot
    plt.figure(figsize=(10, 5))
    plt.scatter(phase, folded_flux, s=5, label='Flux Data')
    plt.scatter(phase[deep_outliers], folded_flux[deep_outliers], s=20, color='red', label='Removed Points')
    if best_fit is not None:
        order = np.argsort(phase)
        plt.plot(np.sort(phase), np.asarray(best_fit)[order], lw=2, label='Best Gaussian Fit')
    plt.axhline(threshold, color='red', linestyle='--', label=f'Removal Threshold ({threshold*100:.0f}%)')
    plt.xlabel('Phase')
    plt.ylabel('Flux')
    plt.title('Phase-Folded Binned Light Curve with Gaussian Fit')
    plt.legend()
    plt.grid(True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    keep_mask = ~deep_outliers
    return phase[keep_mask], folded_flux[keep_mask], folded_flux_err[keep_mask], keep_mask


def BJD0Check(bjd0, timeData, fluxData, fluxErrData, Pbin, DetrendingName, ID, bin_width=1e-5, base_dir=None):
    '''
    Functionality:
        Validate or repair bjd0 so that the primary eclipse aligns at phase ~0 or ~1.
        If invalid (including NaN), set bjd0 to the absolute time of minimum flux, then
        shift by whole periods to the first primary epoch ≤ the start of the data. Saves
        a side-by-side plot comparing the original and proposed folds.

    Arguments:
        bjd0 (float or None): Reference epoch in seconds (may be NaN/None).
        timeData (array-like): Time stamps in seconds.
        fluxData (array-like): Normalized flux aligned with timeData.
        fluxErrData (array-like or None): Flux uncertainties aligned with timeData.
        Pbin (float): Orbital period in seconds.
        DetrendingName (str): Label for output directory naming.
        ID (str|int): Target identifier for filenames.
        bin_width (float, optional): Phase bin width for diagnostic folds.
        base_dir (str|pathlib.Path or None, optional): Root directory for outputs (plots).

    Returns:
        float:
            Final (possibly updated) bjd0 in seconds.
    '''
    print(f"Checking BJD0: {bjd0} with period: {Pbin} seconds")

    def _canonicalize_epoch_from_min(t_min, t_start, pbin):
        k = np.floor((t_start - t_min) / pbin)
        return t_min + k * pbin

    try:
        days2sec
    except NameError:
        days2sec = 86400.0

    # Base-dir aware output path
    root = _resolve_base_dir(None)
    my_folder = root / 'LightCurves' / 'Data_Preparation' / str(DetrendingName)
    _ensure_parent(my_folder / 'dummy.txt')  # ensure parent dirs exist

    # Validate finite bjd0
    is_bjd0_finite = (bjd0 is not None) and np.isfinite(bjd0)
    if is_bjd0_finite:
        try:
            phaseFoldedTime = phase_fold(timeData, fluxData, Pbin, bjd0)
            phaseTimeBinned, fluxArrayBinned, _ = binData(phaseFoldedTime, fluxData, fluxErrData, bin_width)

            min_flux_phase = float(phaseTimeBinned[int(np.argmin(fluxArrayBinned))])
            if np.isclose(min_flux_phase, 0, atol=0.01) or np.isclose(min_flux_phase, 1, atol=0.01):
                print("BJD0 is valid, primary eclipse is at phase 0 or 1.")
                final_bjd0 = bjd0

                shifted_bjd0 = bjd0 + (min_flux_phase * Pbin)
                shiftedPhaseFoldedTime = phase_fold(timeData, fluxData, Pbin, shifted_bjd0)
                phaseTimeBinned_shifted, fluxArrayBinned_shifted, _ = binData(
                    shiftedPhaseFoldedTime, fluxData, fluxErrData, bin_width
                )

                save_path = my_folder / f'BJD0Validation_{ID}.png'
                _ensure_parent(save_path)
                plt.figure(figsize=(6, 5))
                plt.title(f"Phase-folded with Valid BJD0 (Shifted) at {final_bjd0 / days2sec:.2f} Days")
                plt.plot(phaseTimeBinned_shifted, fluxArrayBinned_shifted, '.', ms=3)
                plt.axhline(1, color='black', linestyle='--', label='Baseline')
                plt.legend()
                plt.xlabel("Phase")
                plt.ylabel("Normalized Flux")
                plt.grid(True)
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close()
                return final_bjd0
            else:
                print("BJD0 finite but appears invalid; realigning.")
        except Exception as e:
            print(f"[BJD0Check] Warning: validation fold failed for finite bjd0; will realign. Error: {e}")

    # Realign path
    try:
        t_min_flux = float(timeData[int(np.nanargmin(fluxData))])
    except Exception:
        t_min_flux = float(np.nanmedian(timeData))
        print("[BJD0 realign] Warning: could not locate a clear primary; using median time instead.")

    bjd0_aligned = t_min_flux
    t_start = float(np.nanmin(timeData))
    bjd0_new = _canonicalize_epoch_from_min(bjd0_aligned, t_start, Pbin)
    phase_at_min = ((t_min_flux - bjd0_new) / Pbin + 0.5) % 1.0
    print(f"Suggested new BJD0: {bjd0_new:.5f} (Phase at min: {phase_at_min:.5f})")
    final_bjd0 = bjd0_new

    # Build folds for comparison
    newPhaseFoldedTime = phase_fold(timeData, fluxData, Pbin, bjd0_new)
    try:
        phaseTimeBinned_new, fluxArrayBinned_new, _ = binData(newPhaseFoldedTime, fluxData, fluxErrData, bin_width)
    except Exception:
        phaseTimeBinned_new, fluxArrayBinned_new = newPhaseFoldedTime, fluxData

    try:
        original_bjd0_for_plot = bjd0 if ((bjd0 is not None) and np.isfinite(bjd0)) else bjd0_new
        originalPhaseFoldedTime = phase_fold(timeData, fluxData, Pbin, original_bjd0_for_plot)
        phaseTimeBinned_orig, fluxArrayBinned_orig, _ = binData(
            originalPhaseFoldedTime, fluxData, fluxErrData, bin_width
        )
    except Exception:
        phaseTimeBinned_orig, fluxArrayBinned_orig = originalPhaseFoldedTime, fluxData

    save_path = my_folder / f'Original_Proposed_BJD0_{ID}.png'
    _ensure_parent(save_path)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    try:
        old_days = (bjd0 / days2sec) if ((bjd0 is not None) and np.isfinite(bjd0)) else float("nan")
    except Exception:
        old_days = float("nan")

    ax1.set_title(f"Original BJD0 at {old_days:.2f} Days")
    try:
        ax1.plot(phaseTimeBinned_orig, fluxArrayBinned_orig, '.', ms=3)
    except Exception:
        ax1.text(0.5, 0.5, "Original phases unavailable", ha='center', va='center', transform=ax1.transAxes)
    ax1.axhline(1, color='black', linestyle='--')
    ax1.set_xlabel("Phase"); ax1.set_ylabel("Normalized Flux"); ax1.grid(True)

    ax2.set_title(f"New Proposed BJD0 at {final_bjd0 / days2sec:.2f} Days")
    ax2.plot(phaseTimeBinned_new, fluxArrayBinned_new, '.', ms=3)
    ax2.axhline(1, color='black', linestyle='--')
    ax2.set_xlabel("Phase"); ax2.set_ylabel("Normalized Flux"); ax2.grid(True)

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    return final_bjd0


def manualCuts(
    timeData,
    fluxData,
    fluxErr,
    target_id,
    days2sec=86400,
    On=True,
    cuts_csv=None,
    base_dir_override=None,
):
    """
    Functionality:
        Interactive tool to apply and persist manual time-window cuts (in days) for a
        target. Existing cuts (if any) are applied first, then you may add more. All
        cuts are saved to CSV. Returns arrays after cuts.

    Arguments:
        timeData (array-like): Time stamps in seconds.
        fluxData (array-like): Normalized flux aligned with timeData.
        fluxErr (array-like): Flux uncertainties aligned with timeData.
        target_id (str|int): Identifier used to lookup/store cuts in the CSV.
        days2sec (float, optional): Seconds per day. Default 86400.
        On (bool, optional): If False, returns inputs unchanged.
        cuts_csv (str|pathlib.Path|None, optional):
            Path to the cuts CSV. If None, uses the default
            UserGeneratedData/manual_cuts_TESS.csv under the workspace root
            (base_dir()).
        base_dir_override (str|pathlib.Path|None, optional):
            Optional override for the workspace root when cuts_csv is relative.
            If None, relative paths are resolved against base_dir().
    """
    if not On:
        print("Manual cuts disabled. Returning original data.")
        return timeData, fluxData, fluxErr

    # --- Resolve cuts_path under the new architecture ---
    if cuts_csv is None:
        # Default: UserGeneratedData/manual_cuts_TESS.csv (writable, workspace-scoped)
        cuts_path = p_user_data("manual_cuts_TESS.csv")
    else:
        cuts_path = Path(cuts_csv)
        if not cuts_path.is_absolute():
            root = Path(base_dir_override) if base_dir_override is not None else base_dir()
            cuts_path = root / cuts_path

    _ensure_parent(cuts_path)

    # --- Existing logic follows, unchanged except using cuts_path ---
    if cuts_path.exists():
        df = pd.read_csv(cuts_path, dtype={'ID': str, 'Cuts': str})
        df['ID'] = df['ID'].astype(str).str.strip()
    else:
        df = pd.DataFrame(columns=['ID', 'Cuts'])

    target_id_str = str(target_id).strip()
    old_cuts_list = []
    idx = None

    if target_id_str in df['ID'].values:
        idx = df.index[df['ID'] == target_id_str][0]
        old_cuts_str = df.at[idx, 'Cuts']
        if pd.notna(old_cuts_str) and old_cuts_str.strip() != '':
            for pair in old_cuts_str.split(';'):
                parts = pair.strip().split(',')
                if len(parts) == 2:
                    try:
                        old_cuts_list.append([float(parts[0]), float(parts[1])])
                    except Exception:
                        pass
            # Apply existing cuts
            for cut in old_cuts_list:
                mask = ((timeData / days2sec) < cut[0]) | ((timeData / days2sec) > cut[1])
                timeData = timeData[mask]
                fluxData = fluxData[mask]
                fluxErr = fluxErr[mask]
            add_more = input("Existing cuts applied. Add more? (y/n): ").strip().lower()
            if add_more != 'y':
                print("Using existing cuts only.")
                return timeData, fluxData, fluxErr
        else:
            add_now = input("No cuts recorded yet. Add manual cuts now? (y/n): ").strip().lower()
            if add_now != 'y':
                print("No cuts made. Returning original data.")
                return timeData, fluxData, fluxErr
    else:
        print(f"No prior entry for target {target_id_str}. Creating one.")
        df = pd.concat([df, pd.DataFrame([{'ID': target_id_str, 'Cuts': ''}])], ignore_index=True)
        idx = df.index[df['ID'] == target_id_str][0]

    # Interactive session (unchanged)
    print("Beginning manual cut vetting...")
    daysData = (timeData[-1] - timeData[0]) / days2sec
    timeSpan = float(input(f"How many days at a time would you like to view? (Total: {daysData:.2f}): "))
    chunks = int(np.ceil(daysData / timeSpan))
    cuts = []

    for i in range(chunks):
        start = (timeData[0] / days2sec) + i * timeSpan
        end = start + timeSpan
        mask = ((timeData / days2sec) >= start) & ((timeData / days2sec) < end)

        if not np.any(mask):
            print(f"Skipping round {i+1} with no data.")
            continue

        print(f"Round {i + 1} of {chunks}")
        plt.figure(figsize=(10, 4))
        plt.plot((timeData / days2sec)[mask], fluxData[mask], '.', ms=1)
        plt.title(f"Data from {start:.2f} to {end:.2f} days")
        plt.xlabel("Days"); plt.ylabel("Normalized Flux"); plt.grid(True)
        plt.show(); plt.close()

        if input("Cut any regions? (y/n): ").strip().lower() == 'y':
            user_input = input("Enter cuts as start,end; start,end; ... (in days): ")
            try:
                local_cuts = []
                for pair in user_input.split(';'):
                    parts = pair.strip().split(',')
                    if len(parts) != 2:
                        raise ValueError(f"Invalid cut format: '{pair}'")
                    cstart, cend = float(parts[0]), float(parts[1])
                    if cstart >= cend:
                        raise ValueError(f"Start must be < end: [{cstart}, {cend}]")
                    local_cuts.append([cstart, cend])
                for cut in local_cuts:
                    mask2 = ((timeData / days2sec) < cut[0]) | ((timeData / days2sec) > cut[1])
                    timeData = timeData[mask2]
                    fluxData = fluxData[mask2]
                    fluxErr = fluxErr[mask2]
                cuts.extend(local_cuts)
                print("Cuts recorded and applied.")
            except Exception as e:
                print(f"Error parsing cuts: {e}")
        else:
            print("No cuts for this chunk.")

    def cuts_to_tuples(cuts_list):
        return [(round(c[0], 5), round(c[1], 5)) for c in cuts_list]

    old_cuts_set = set(cuts_to_tuples(old_cuts_list))
    unique_new_cuts = [c for c in cuts if (round(c[0], 5), round(c[1], 5)) not in old_cuts_set]
    combined_cuts = old_cuts_list + unique_new_cuts

    cut_str = '; '.join(f"{c[0]:.5f},{c[1]:.5f}" for c in combined_cuts)
    df.at[idx, 'Cuts'] = cut_str
    df.to_csv(cuts_path, index=False)

    print(f"Final cuts saved for {target_id_str}: {combined_cuts}")
    if len(timeData) == 0 or len(fluxData) == 0:
        print(f"Warning: All data was cut for {target_id_str}. Returning empty arrays.")
        return np.array([]), np.array([]), np.array([])

    return timeData, fluxData, fluxErr


def apply_manual_cuts(
    timeData,
    fluxData,
    fluxErr,
    target_id,
    cuts_csv=None,
    days2sec=86400,
    base_dir_override=None,
):
    """
    Functionality:
        Apply pre-recorded manual time-window cuts to a target’s light curve using a
        CSV file (non-interactive). If the CSV does not exist, the target is not
        present, or no cuts are listed, the input data are returned unchanged.

    Arguments:
        timeData (array-like): Time values (typically in seconds; interpreted using `days2sec`).
        fluxData (array-like): Flux values aligned with `timeData`.
        fluxErr (array-like): Flux uncertainties aligned with `timeData`.
        target_id (str|int): Target identifier used to look up cuts in the CSV.
        cuts_csv (str|pathlib.Path|None, optional):
            Path to the cuts CSV. If None, uses the default
            UserGeneratedData/manual_cuts_TESS.csv under the workspace root
            (base_dir()).
        days2sec (float, optional):
            Seconds-per-day factor for converting cut values (which are stored in days).
        base_dir_override (str|pathlib.Path|None, optional):
            If provided and `cuts_csv` is relative, it is resolved against this
            directory instead of base_dir().

    Returns:
        (numpy.ndarray, numpy.ndarray, numpy.ndarray):
            time_out: Time array after applying cuts.
            flux_out: Flux array after applying cuts.
            fluxErr_out: Flux uncertainties after applying cuts.
    """

    # --- Resolve cuts_path under the new architecture ---
    if cuts_csv is None:
        # Default: workspace/UserGeneratedData/manual_cuts_TESS.csv
        cuts_path = p_user_data("manual_cuts_TESS.csv")
    else:
        cuts_path = Path(cuts_csv)
        if not cuts_path.is_absolute():
            root = Path(base_dir_override) if base_dir_override is not None else base_dir()
            cuts_path = root / cuts_path

    # Ensure the directory exists even if the CSV doesn't
    _ensure_parent(cuts_path)

    # If the CSV does not exist, create an empty template and return unchanged data
    if not cuts_path.exists():
        print(f"CSV file {cuts_path} does not exist. Creating empty cuts file and returning original data.")
        df_empty = pd.DataFrame(columns=["ID", "Cuts"])
        df_empty.to_csv(cuts_path, index=False)
        return timeData, fluxData, fluxErr

    # From here on, we know cuts_path exists
    df = pd.read_csv(cuts_path, dtype={"ID": str, "Cuts": str})
    df["ID"] = df["ID"].astype(str).str.strip()
    target_id_str = str(target_id).strip()

    if target_id_str not in df["ID"].values:
        print(f"No cuts found for target {target_id_str}. Returning original data.")
        return timeData, fluxData, fluxErr

    cuts_raw = df.loc[df["ID"] == target_id_str, "Cuts"].values[0]
    if not isinstance(cuts_raw, str) or cuts_raw.strip() == "":
        print(f"No valid cuts recorded for target {target_id_str}.")
        return timeData, fluxData, fluxErr

    # Parse CSV cut ranges
    cut_ranges = []
    for entry in cuts_raw.split(";"):
        parts = entry.strip().split(",")
        if len(parts) == 2:
            try:
                cut_ranges.append([float(parts[0]), float(parts[1])])
            except ValueError:
                continue

    if not cut_ranges:
        print(f"No valid cut ranges for target {target_id_str}.")
        return timeData, fluxData, fluxErr

    print(f"Applying cuts for target {target_id_str}: {cut_ranges}")

    # Apply cuts
    for c_start, c_end in cut_ranges:
        mask = ((timeData / days2sec) < c_start) | ((timeData / days2sec) > c_end)
        timeData = timeData[mask]
        fluxData = fluxData[mask]
        if fluxErr is not None:
            fluxErr = fluxErr[mask]

    if len(timeData) == 0:
        print(f"Warning: All data removed for target {target_id_str}. Returning empty arrays.")
        return np.array([]), np.array([]), np.array([])

    return timeData, fluxData, fluxErr



def write_or_update_csv(
    file_path, ID,
    calc_mA, calc_mB, calc_rA, calc_rB,
    calc_ecc, calc_omega,
    antic_mA, antic_mB, antic_rA, antic_rB, eccANTIC, omegaANTIC,
    eccNoAssump, omegaNoAssump, ecoswNoAssump, esinwNoAssump,
    antic_ecosw, antic_esinw, num_sectors,
    base_dir=None,
):
    """
    Functionality:
        Create or update a CSV entry for a target, storing both calculated and ANTIC
        parameter estimates. If the file does not exist, a header is created. If the
        target already exists, its row is replaced.

    Arguments:
        file_path (str): Path to output CSV. If relative, it is resolved against
            `base_dir` if provided, otherwise against the workspace root (base_dir()).
        ID (str|int): Target identifier used as row key.
        calc_* (floats): Calculated masses/radii/eccentricity/omega values.
        antic_* (floats): ANTIC catalog masses/radii/eccentricity/omega values.
        ecoswNoAssump, esinwNoAssump (float): No-assumption parameter estimates.
        num_sectors (int): Number of TESS sectors.
        base_dir (str|pathlib.Path or None): Root for resolving relative file paths.

    Returns:
        None
    """
    # Resolve the root for relative paths: explicit base_dir > workspace base_dir()
    if base_dir is not None:
        root = Path(base_dir).expanduser().resolve()
    else:
        root = base_dir()  # workspace root (cwd or STANLEY_WORKDIR)

    out_path = Path(file_path)
    if not out_path.is_absolute():
        out_path = root / out_path

    _ensure_parent(out_path)

    header = [
        "ID", "mA (CalcAssump)", "mB (CalcAssump)", "RA (CalcAssump)", "RB (CalcAssump)",
        "ecc (CalcAssump)", "omega (CalcAssump)",
        "mA (ANTIC)", "mB (ANTIC)", "RA (ANTIC)", "RB (ANTIC)", "ecc (ANTIC)", "omega (ANTIC)",
        "ecc (CalcNoAssump)", "omega (CalcNoAssump)", "ecosw (CalcNoAssump)", "esinw (CalcNoAssump)",
        "ecosw (ANTIC)", "esinw (ANTIC)", "num_sectors"
    ]

    new_row = [
        ID, calc_mA, calc_mB, calc_rA, calc_rB,
        calc_ecc, calc_omega,
        antic_mA, antic_mB, antic_rA, antic_rB, eccANTIC, omegaANTIC,
        eccNoAssump, omegaNoAssump, ecoswNoAssump, esinwNoAssump,
        antic_ecosw, antic_esinw, num_sectors
    ]

    rows = []
    if out_path.exists():
        with out_path.open("r", newline="") as f:
            rows = list(csv.reader(f))
    else:
        rows.append(header)

    # Replace or append entry
    found = False
    for i, row in enumerate(rows):
        if row and row[0] == str(ID):
            rows[i] = [str(x) for x in new_row]
            found = True
            break
    if not found:
        rows.append([str(x) for x in new_row])

    with out_path.open("w", newline="") as f:
        csv.writer(f).writerows(rows)



# Primary star parameter retrieval with retries & sanity checks
def findMaAndRaAndTa(ID, paramreturned, *,
                     max_attempts=6,          # total tries
                     base_sleep=5.0,          # seconds; will be jittered
                     timeout_per_try=60.0,    # unused by astroquery, kept for symmetry
                     use_solar_fallback=True  # if True, return solar-like defaults on failure
):
    '''
    Functionality:
        Query TIC/MAST for a target’s stellar mass, radius, and Teff with retries
        and generous sanity checks. Returns one or all of (mA [kg], rA [m], tA [K]),
        as requested via `paramreturned`. On repeated failures, optionally returns
        solar-like defaults.

    Arguments:
        ID (str|int): Target identifier; normalized to "TIC <ID>" if not already.
        paramreturned (str): One of {'ma','ra','ta','all'} selecting which value(s) to return.
        max_attempts (int, optional): Maximum number of query attempts. Default 6.
        base_sleep (float, optional): Base seconds for exponential backoff with jitter. Default 5.0.
        timeout_per_try (float, optional): Placeholder; not used by astroquery. Default 60.0.
        use_solar_fallback (bool, optional): If True, return solar-like defaults after exhausting
            retries; otherwise raise. Default True.

    Returns:
        float | tuple:
            If paramreturned == 'ma': returns mA [kg]
            If paramreturned == 'ra': returns rA [m]
            If paramreturned == 'ta': returns tA [K]
            If paramreturned == 'all': returns (mA [kg], rA [m], tA [K])

    Notes:
        - Uses astroquery.mast Catalogs.query_object("TIC ...", catalog="TIC").
        - Assumes symbols like Catalogs, RemoteServiceError, HTTPError, ConnectionError, Timeout,
          random, TIME, and np are already imported by the caller’s environment.
        - Applies very generous sanity ranges; values outside trigger retries/fallbacks.
    '''

    # Local, tiny guards so this runs cleanly in any environment (cluster/local/pip)
    import random as _rand
    try:
        from astroquery.exceptions import RemoteServiceError as _RemoteServiceError
    except Exception:
        _RemoteServiceError = Exception
    try:
        from requests.exceptions import HTTPError as _HTTPError, ConnectionError as _ConnectionError, Timeout as _Timeout
    except Exception:
        _HTTPError = _ConnectionError = _Timeout = Exception

    # Constants
    M_sun = mSun_kg
    R_sun = rSun_m
    T_sun = 5772.0 # K

    # Helpers
    def _query_tic(tic_string):
        '''
        Functionality:
            Query TIC catalog metadata for a given identifier.
    
        Arguments:
            tic_string (str): e.g., "TIC 123456789".
    
        Returns:
            astropy.table.Table:
                Query result table (may be length 0 if no match).
        '''
        # astroquery will handle the service call
        return Catalogs.query_object(tic_string, catalog="TIC")

    # Accept either integer/str; normalize to "TIC 12345"
    tic_str = str(ID).strip()
    if not tic_str.upper().startswith("TIC"):
        tic_str = f"TIC {tic_str}"

    # Retry loop
    last_err = None
    for attempt in range(1, max_attempts + 1):
        try:
            catalog_data = _query_tic(tic_str)
            if len(catalog_data) == 0:
                raise ValueError(f"No data found for {tic_str}")

            star = catalog_data[0]

            # Robust field extraction (astroquery can return masked/None)
            def _safe_float(x):
                '''
                Functionality:
                    Convert input to float, returning NaN if invalid.
    
                Arguments:
                    x: value or masked/None.
    
                Returns:
                    float: finite value or np.nan.
                '''
                try:
                    v = float(x)
                    if np.isnan(v) or np.isinf(v):
                        return np.nan
                    return v
                except Exception:
                    return np.nan

            mA_val = _safe_float(star.get('mass', np.nan))
            rA_val = _safe_float(star.get('rad',  np.nan))
            tA_val = _safe_float(star.get('Teff', np.nan))

            # Apply defaults if missing
            if np.isnan(mA_val): mA_val = 1.0  # [Msun]
            if np.isnan(rA_val): rA_val = 1.0  # [Rsun]
            if np.isnan(tA_val): tA_val = T_sun  # [K]

            # Convert to SI
            mA = mA_val * M_sun
            rA = rA_val * R_sun
            tA = tA_val

            # Sanity ranges (very generous)
            if not (0.05 <= mA / M_sun <= 100.0):
                raise ValueError(f"Unrealistic mass value: {mA/M_sun:.3g} M_sun")
            if not (0.05 <= rA / R_sun <= 100.0):
                raise ValueError(f"Unrealistic radius value: {rA/R_sun:.3g} R_sun")
            if not (1000.0 <= tA <= 50000.0):
                raise ValueError(f"Unrealistic Teff: {tA:.0f} K")

            # Success
            paramreturned = str(paramreturned).lower()
            if paramreturned == 'ma':
                return mA
            elif paramreturned == 'ra':
                return rA
            elif paramreturned == 'ta':
                return tA
            elif paramreturned == 'all':
                return mA, rA, tA
            else:
                raise ValueError(f"paramreturned must be one of 'ma','ra','ta','all' (got {paramreturned!r})")

        except (_RemoteServiceError, _HTTPError, _ConnectionError, _Timeout) as e:
            # Transient / network / service errors → backoff & retry
            last_err = e
            sleep_s = base_sleep * (2 ** (attempt - 1)) * (0.75 + 0.5 * _rand.random())
            print(f"[WARN] MAST query failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {sleep_s:.1f}s...")
            TIME.sleep(sleep_s)
            continue
        except Exception as e:
            # Data/validation errors — retrying usually won't help unless it was a temporary bad page
            last_err = e
            if attempt < max_attempts:
                sleep_s = base_sleep * (0.75 + 0.5 * _rand.random())
                print(f"[WARN] TIC parse/validation error (attempt {attempt}/{max_attempts}): {e}. Retrying in {sleep_s:.1f}s...")
                TIME.sleep(sleep_s)
                continue
            break

    # Fallbacks after exhausting retries
    if use_solar_fallback:
        print(f"[WARN] Falling back to solar-like defaults for {tic_str} after {max_attempts} attempts. Last error: {last_err}")
        mA, rA, tA = (1.0 * M_sun, 1.0 * R_sun, T_sun)
        paramreturned = str(paramreturned).lower()
        if paramreturned == 'ma':
            return mA
        elif paramreturned == 'ra':
            return rA
        elif paramreturned == 'ta':
            return tA
        elif paramreturned == 'all':
            return mA, rA, tA

    # If you prefer to hard-fail rather than fallback:
    raise RuntimeError(f"Could not retrieve TIC params for {tic_str} after {max_attempts} attempts. Last error: {last_err}")


# Secondary radius from eclipse depth
def findRb(Ra, phaseBinned, fluxBinned, fluxErrBinned):
    '''
    Functionality:
        Estimate the secondary radius Rb from the eclipse depth by fitting both a
        Gaussian and a tanh-with-flat-baseline model to the primary-centered binned
        eclipse. The model with lower reduced χ² determines the depth d, and
        Rb = sqrt(d) * Ra.

    Arguments:
        Ra (float): Primary radius (meters).
        phaseBinned (array-like): Binned phase with primary near 0.5.
        fluxBinned (array-like): Binned flux aligned with phaseBinned.
        fluxErrBinned (array-like): Binned flux errors aligned with phaseBinned.

    Returns:
        float:
            Estimated secondary radius Rb (meters).
    '''
    R_sun = 6.957e8  # m

    bounds = ([0.0001, 0.0001, 0.25], [1, 0.3, 0.75])
    p0 = [1 - np.min(fluxBinned),
          estimate_eclipse_width(phaseBinned, fluxBinned, phaseBinned[np.argmin(fluxBinned)], threshold=0.25),
          0.5]
    bestfit_flat, _ = so.curve_fit(gaussianModel, phaseBinned, fluxBinned, p0=p0, method='trf', bounds=bounds, gtol=1e-8)
    pdepth_gaus, sigma, _ = bestfit_flat

    bestfit_flat_tanh, _ = so.curve_fit(tanh_transit_flat, phaseBinned, fluxBinned, p0=p0, method='trf', bounds=bounds, gtol=1e-8)
    pdepth_tanh, _, _ = bestfit_flat_tanh

    resid_g  = fluxBinned - gaussianModel(phaseBinned, *bestfit_flat)
    resid_t  = fluxBinned - tanh_transit_flat(phaseBinned, *bestfit_flat_tanh)
    k_g, k_t = len(bestfit_flat), len(bestfit_flat_tanh)
    n = len(fluxBinned)
    chi2_g = np.sum((resid_g / fluxErrBinned) ** 2)
    chi2_t = np.sum((resid_t / fluxErrBinned) ** 2)
    rchi2_g = chi2_g / max(1, n - k_g)
    rchi2_t = chi2_t / max(1, n - k_t)

    depth = pdepth_gaus if rchi2_g < rchi2_t else pdepth_tanh
    if Ra > 1000 * R_sun:
        raise ValueError(f"Ra too large: {Ra} m. Check units.")

    return np.sqrt(depth) * Ra


def findMb(Rb):
    '''
    Functionality:
        Estimate the secondary mass Mb from its radius Rb using two mass–radius
        power-law scalings (low-mass: R~M^0.8, high-mass: R~M^0.53). Choose the
        high-mass branch if M>1 Msun; otherwise low-mass.

    Arguments:
        Rb (float): Secondary radius (meters).

    Returns:
        float:
            Estimated secondary mass Mb (kilograms).
    '''
    M_sun = 1.9885e30  # kg
    R_sun = 6.957e8    # m

    if Rb > 100 * R_sun:
        raise ValueError(f"Unrealistic Rb: {Rb} m")

    Rb_solar = Rb / R_sun
    xi_low_mass = 0.8
    xi_high_mass = 0.53

    mass_guess_low  = Rb_solar ** (1 / xi_low_mass)
    mass_guess_high = Rb_solar ** (1 / xi_high_mass)

    Mb_solar = mass_guess_high if mass_guess_high > 1 else mass_guess_low
    if not (0.001 < Mb_solar < 100):
        raise ValueError(f"Unrealistic mass estimate: {Mb_solar} M_sun")

    return Mb_solar * M_sun



# chunk our data, useful for quicker detrending (wotan can be slow)
def chunk_by_gaps(time, flux, gap_threshold=0.5):
    '''
    Functionality:
        Split a time series into contiguous chunks wherever a time gap exceeds
        `gap_threshold` days. Input is auto-interpreted as seconds if values look
        larger than one day.

    Arguments:
        time (array-like): Time values; if likely seconds (> 86400), are converted
            to days for gap detection (outputs remain in input units).
        flux (array-like): Flux values aligned with time.
        gap_threshold (float, optional): Gap size in days that defines a split.

    Returns:
        (list[numpy.ndarray], list[numpy.ndarray]):
            time_chunks: List of time-array chunks (same units as input).
            flux_chunks: List of flux-array chunks aligned with time_chunks.
    '''
    # Convert copy for gap finding; keep originals for return slicing
    time_in = np.asarray(time)
    flux_in = np.asarray(flux)

    if time_in[0] > 86400:
        # interpret as seconds for gap detection only
        time_days = time_in / (86400.0 if 'days2sec' not in globals() else days2sec)
    else:
        time_days = time_in

    time_diffs = np.diff(time_days)
    gap_indices = np.where(time_diffs > gap_threshold)[0]

    time_chunks, flux_chunks = [], []
    start_idx = 0
    for gap_idx in gap_indices:
        end_idx = gap_idx + 1
        time_chunks.append(time_in[start_idx:end_idx])
        flux_chunks.append(flux_in[start_idx:end_idx])
        start_idx = end_idx

    time_chunks.append(time_in[start_idx:])
    flux_chunks.append(flux_in[start_idx:])
    return time_chunks, flux_chunks


# chunk our data with errors, useful for quicker detrending (wotan can be slow)
def chunk_by_gaps2(time, flux, fluxErr, gap_threshold=0.5):
    '''
    Functionality:
        Split a time series (with flux and flux errors) into contiguous chunks
        wherever there is a time gap larger than `gap_threshold` days.

    Arguments:
        time (array-like): Time values in seconds; internally converted to days for
            gap detection and converted back to seconds for the returned chunks.
        flux (array-like): Flux values aligned with `time`.
        fluxErr (array-like): Flux uncertainties aligned with `time`.
        gap_threshold (float, optional): Gap size in days that defines a split.
            Default 0.5.

    Returns:
        (list[numpy.ndarray], list[numpy.ndarray], list[numpy.ndarray]):
            time_chunks: List of time-array chunks in seconds.
            flux_chunks: List of flux-array chunks.
            fluxErr_chunks: List of flux-error-array chunks.
    '''
    # ensure arrays
    time = np.asarray(time)
    flux = np.asarray(flux)
    fluxErr = np.asarray(fluxErr)

    # make sure we are in days as the gap_threshold is defined by days
    time_days = time / DAYS2SEC

    # compute time differences to locate our gaps
    time_diffs = np.diff(time_days)

    # identify the indices where the gaps occur
    gap_indices = np.where(time_diffs > gap_threshold)[0]

    # initialize our lists for chunks
    time_chunks = []
    flux_chunks = []
    fluxErr_chunks = []

    # split our data at the gap indices
    start_idx = 0
    for gap_idx in gap_indices:
        end_idx = gap_idx + 1  # the next chunk starts after the gap
        time_chunks.append(time_days[start_idx:end_idx])
        flux_chunks.append(flux[start_idx:end_idx])
        fluxErr_chunks.append(fluxErr[start_idx:end_idx])
        start_idx = end_idx  # move start index to new chunk

    # append the last chunk
    time_chunks.append(time_days[start_idx:])
    flux_chunks.append(flux[start_idx:])
    fluxErr_chunks.append(fluxErr[start_idx:])

    # make sure we are returning our time_chunks in seconds, not days
    time_chunks = [chunk * DAYS2SEC for chunk in time_chunks]

    return time_chunks, flux_chunks, fluxErr_chunks


def Detrending_Quadratic(timeFinal, fluxFinal, threshold=0.5, *,
                         base_dir=None, diagnostic=False, id_label=None, detrend_plot_subdir="Quad_Detrend_Testing"):
    '''
    Functionality:
        Quadratically detrend a light curve in contiguous chunks split by time gaps
        larger than `threshold` (days). Each chunk is median-normalized, fitted with
        a quadratic in time, and divided by the fit.

    Arguments:
        timeFinal (array-like): Time array (seconds or days; used directly by polyfit).
        fluxFinal (array-like): Flux array aligned with timeFinal.
        threshold (float, optional): Gap size (days) used by chunk_by_gaps to split
            the data. Default 0.5.
        base_dir (Path-like or None): Root directory for outputs (cluster/local/pip).
        diagnostic (bool): If True, save per-chunk diagnostic plots.
        id_label (str|None): Optional label for plot titles.
        detrend_plot_subdir (str): Subdirectory name for diagnostic plots.

    Returns:
        (numpy.ndarray, numpy.ndarray):
            timeQ: Concatenated time values of detrended chunks (same units as input).
            fluxQ: Concatenated quadratically-detrended, median-normalized flux.
    '''
    # create empty lists to store our quadratically detrended data, note we detrend in chunks
    timeQ = []
    fluxQ = []

    timeFinal = np.asarray(timeFinal)
    fluxFinal = np.asarray(fluxFinal)

    start = timeFinal[0]
    end = timeFinal[-1]

    # kept (unused) for minimal change
    window_mask = ((timeFinal >= start) * (timeFinal < end))

    # create our chunks (fixed: call the correct function name)
    time_chunks, flux_chunks, _ = chunk_by_gaps2(timeFinal, fluxFinal, np.ones_like(fluxFinal), threshold)

    # optional output location
    if diagnostic:
        base = _resolve_base_dir(None)
        outdir = base / detrend_plot_subdir
        outdir.mkdir(parents=True, exist_ok=True)

    # loop through each chunk
    for jj in range(len(time_chunks)):
        # sanity check, remove any nans
        save_array = ~np.isnan(flux_chunks[jj][:])
        # create our chunks within the windows
        window_time = time_chunks[jj][save_array]
        window_flux = flux_chunks[jj][save_array]
        # detrend the chunk by the median first
        if window_flux.size:
            window_flux = window_flux / np.median(window_flux)

        # check if we can ignore this section because there's no data
        if len(window_time) > 0 and len(window_flux) > 0:
            try:
                # fit data, could use errors on data points here to get better fit if we wanted
                params = np.polyfit(window_time, window_flux, 2)
                quad_fit = np.poly1d(params)

                # compute the fit model at the data points
                predicted = quad_fit(window_time)

                # correct the points
                flat_window_flux = window_flux / predicted

                # put them back in the original data
                flatFlux = flat_window_flux

                timeQ.append(window_time)
                fluxQ.append(flatFlux)

                # diagnostics (write under base_dir if requested)
                if diagnostic:
                    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(15, 5))

                    axes[0].scatter(window_time / DAYS2SEC, window_flux, marker='.', linestyle='')
                    axes[0].plot(window_time / DAYS2SEC, predicted,
                                 label=f"{round(params[0], 4)}x^2 + {round(params[1], 4)}x + {round(params[2], 4)}")
                    axes[0].set_ylabel("Normalized Flux")
                    axes[0].axhline(1, dashes=[1, 1, 1, 1], color='gray')
                    axes[0].set_xlim(window_time[0] / DAYS2SEC, window_time[-1] / DAYS2SEC)
                    axes[0].legend()

                    axes[1].scatter(window_time / DAYS2SEC, flat_window_flux, marker='.', alpha=1, linestyle='', zorder=1000)
                    axes[1].axhline(1, dashes=[1, 1, 1, 1], color='gray')
                    axes[1].set_ylabel("Quadratically detrended")
                    axes[1].set_xlim(window_time[0] / DAYS2SEC, window_time[-1] / DAYS2SEC)
                    plt.xlabel("Time (days)")

                    title = f"{id_label}" if id_label is not None else ""
                    if title:
                        fig.suptitle(title)

                    save_path = outdir / f'Chunk_{jj + 1}.png'
                    _ensure_parent(save_path)
                    plt.savefig(save_path, dpi=200, bbox_inches='tight')
                    plt.close()
            # if there is a problem with the fitting process, throw an error
            except Exception as e:
                print(f"Error fitting quadratic to chunk {jj + 1}: {e}")
        # if the chunk is empty, skip it
        else:
            print(f"Skipping chunk {jj + 1} because it's empty.")

    # make sure we are returning arrays
    timeQ = np.array(np.concatenate(timeQ)) if len(timeQ) else np.array([])
    fluxQ = np.array(np.concatenate(fluxQ)) if len(fluxQ) else np.array([])

    return timeQ, fluxQ


# function to sort arrays
def sorting(timeOrig, fluxOrig, fluxErrFlat, phaseOrig=None):
    '''
    Functionality:
        Sort the provided arrays by time and return the sorted arrays. If a phase
        array is provided, it is sorted in the same order and returned as well.

    Arguments:
        timeOrig (array-like): Time values to sort by.
        fluxOrig (array-like): Flux values aligned with timeOrig.
        fluxErrFlat (array-like): Flux errors aligned with timeOrig.
        phaseOrig (array-like or None): Optional phase array aligned with timeOrig.

    Returns:
        If phaseOrig is None:
            (numpy.ndarray, numpy.ndarray, numpy.ndarray):
                sortedTime, sortedFlux, sortedFluxErr
        Else:
            (numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray):
                sortedTime, sortedFlux, sortedPhase, sortedFluxErr
    '''
    sorted_indices = np.argsort(timeOrig)

    sortedTime = timeOrig[sorted_indices]
    sortedFlux = fluxOrig[sorted_indices]
    sortedFluxErr = fluxErrFlat[sorted_indices]

    if phaseOrig is not None:
        sortedPhase = phaseOrig[sorted_indices]
        return sortedTime, sortedFlux, sortedPhase, sortedFluxErr
    else:
        return sortedTime, sortedFlux, sortedFluxErr


# function to remove data around a gap as the detrending process can cause hooks to appear
def remove_boundary_around_gap(i, j, boundary, sortedTime, to_remove_mask):
    '''
    Functionality:
        Mark samples for removal within a symmetric boundary window around a detected
        time gap between indices i and j.

    Arguments:
        i (int): Index of the last sample before the gap.
        j (int): Index of the first sample after the gap.
        boundary (float): Half-width of the exclusion window (same units as time).
        sortedTime (array-like): Monotonically increasing time array.
        to_remove_mask (array-like of bool): Boolean mask updated in place.

    Returns:
        None: The function updates `to_remove_mask` in place.
    '''
    # take time before and after gap
    time_before_gap = sortedTime[i]
    time_after_gap = sortedTime[j]

    # use logical AND (`&`) is used instead of `*`
    mask = (sortedTime >= (time_before_gap - boundary)) & (sortedTime <= (time_after_gap + boundary))

    # Update the mask
    to_remove_mask[mask] = True


# these are our options for models, as of right now the gaussian model works well
# Tanh-based smooth transit model, note that width is not in terms of phase
def tanh_transit(x, depth, width, location):
    '''
    Functionality:
        Smooth tanh transit profile without a flat bottom.

    Arguments:
        x (array-like): Phase-like coordinate.
        depth (float): Transit depth (0–1).
        width (float): Scale factor controlling transition steepness.
        location (float): Center location.

    Returns:
        numpy.ndarray: Model flux values.
    '''
    z = width * (x - location)
    return 1 - depth * (1 - np.tanh(z)**2)


# these are our options for models, as of right now the gaussian model works well
# Tanh-based smooth transit model, note that width is not in terms of phase
# need a flat bottom, overall this function has proved to be more accurate than tanh_transit
def tanh_transit_flat(x, depth, width, location, sharpness=500.0):
    '''
    Functionality:
        Flat-bottom tanh transit: two sharp tanh edges define a box-like eclipse,
        scaled to have peak drop ≈ `depth`.

    Arguments:
        x (array-like): Phase-like coordinate.
        depth (float): Transit depth (0–1).
        width (float): Full width of the flat region.
        location (float): Center location of the eclipse.
        sharpness (float, optional): Edge sharpness multiplier. Default 500.0.

    Returns:
        numpy.ndarray: Model flux values.
    '''
    left  = np.tanh((x - (location - width/2.0)) * sharpness)
    right = np.tanh((x - (location + width/2.0)) * sharpness)
    return 1.0 - depth * 0.5 * (left - right)  # peak drop ≈ depth


def gaussianModel(x, scaleFactor, sigma, mu):
    '''
    Functionality:
        Gaussian-shaped eclipse model around center `mu` with width `sigma`
        and scale `scaleFactor`, subtracted from unity.

    Arguments:
        x (array-like): Phase-like coordinate.
        scaleFactor (float): Eclipse depth scaling (0–1).
        sigma (float): Gaussian width (in same units as x).
        mu (float): Eclipse center.

    Returns:
        numpy.ndarray: Model flux values as 1 - scaleFactor * exp(-0.5*((x-mu)/sigma)^2).
    '''
    return 1 - scaleFactor * np.exp(-0.5 * ((x - mu) / (sigma)) ** 2)


# straight line model used to compare against gaussian
def straightModel(x, m, b):
    '''
    Functionality:
        Simple straight-line model m*x + b (baseline comparator).

    Arguments:
        x (array-like): Independent variable.
        m (float): Slope.
        b (float): Intercept.

    Returns:
        numpy.ndarray: Linear model values.
    '''
    return m * x + b


def gaussianStraight(timeData, fluxData, fluxErrData, sec_pos, swidth, sdepth,
                     DetrendingName, ID, *, base_dir=None):
    '''
    Functionality:
        Statistically test for a secondary eclipse by fitting (i) a Tanh flat-bottom
        eclipse model and (ii) a straight line to the input data (assumed to have
        primaries removed), then comparing BIC scores against a provided Gaussian
        parameter set. Saves a diagnostic plot and returns the best model decision.

    Arguments:
        timeData (array-like): Phase-like x-values (same units used during fitting).
        fluxData (array-like): Flux values aligned with timeData.
        fluxErrData (array-like): Flux uncertainties aligned with timeData.
        sec_pos (float): Initial secondary-center phase/location guess.
        swidth (float): Initial secondary width (phase units); Gaussian σ ≈ swidth/6.
        sdepth (float): Initial secondary depth (fractional).
        DetrendingName (str): Folder label for saving diagnostics.
        ID (str|int): Target identifier used in filenames.
        base_dir (Path-like or None): Root directory for outputs.

    Returns:
        (bool, str, float, float, float, float, float, float, float):
            secondaryFound: True if a non-linear eclipse model is preferred.
            best_model: 'Gaussian', 'Tanh', or 'Straight Line'.
            sec_pos: Adopted secondary center (phase) if non-linear; else NaN.
            swidth: Adopted secondary full width (phase) if non-linear; else NaN.
            sdepth: Adopted depth if non-linear; else NaN.
            swidth_ecc: Width proxy for eccentricity checks (phase) if non-linear; else NaN.

        Notes:
            Reduced-χ² values for Gaussian, Straight, and Tanh are also included in
            the tuple via the BIC() return (kept for backward-compatibility).
    '''
    # gaussian parameters (use provided sec_pos/swidth/sdepth as the working set)
    bestfit_flat = [sdepth, swidth/6, sec_pos]  # [scale factor, sigma, mu]

    # fit using the tanh model
    p0 = [sdepth, swidth/6, sec_pos]  # initial guess for depth, width(sigma-like), location
    try:
        bestfit_flat_tanh, covariance_flat_tanh = so.curve_fit(
            tanh_transit_flat, timeData, fluxData,
            p0=p0, method='trf',
            bounds=[[0.00001, 0.00001, 0], [1, 0.3, 1]],
            gtol=1e-8
        )
    except RuntimeError as e:
        print(f"Curve fitting failed for Gaussian: {e}")
        return False

    # now do it for a straight line in the same region
    p0 = [0, 1]  # initial guess for slope and intercept
    try:
        bestfit_flat_straight, covariance_flat_straight = so.curve_fit(
            straightModel, timeData, fluxData,
            p0=p0, method='trf',
            bounds=[[-1, 0], [1, 2]],
            gtol=1e-8
        )
    except RuntimeError as e:
        print(f"Curve fitting failed for straight line: {e}")
        return False

    # compute BICs and decision
    (secondaryFound, best_model,
     reduced_chi_squared_gaussianOG, reduced_chi_squared_straight, reduced_chi_squared_tanh,
     sec_pos, swidth, sdepth, swidth_ecc) = BIC(
        timeData, fluxData, fluxErrData,
        bestfit_flat, bestfit_flat_straight, bestfit_flat_tanh
    )

    # Output directory under base_dir for portability
    base = _resolve_base_dir(None)
    my_folder = base / 'LightCurves' / 'Data_Preparation' / DetrendingName
    my_folder.mkdir(parents=True, exist_ok=True)
    save_path = my_folder / f'Secondary_Eclipse_Candidate_{ID}.png'

    # Plot diagnostic
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(timeData, fluxData, label='Binned Data', s=3, color='black')
    ax.plot(timeData, gaussianModel(timeData, *bestfit_flat), label='Best Fit Gaussian', linewidth=2)
    ax.plot(timeData, straightModel(timeData, *bestfit_flat_straight), label='Best Fit Straight Line', linewidth=2)
    ax.plot(timeData, tanh_transit_flat(timeData, *bestfit_flat_tanh), label='Best Fit Tanh', linewidth=2)
    ax.set_xlabel('Time (BJD)')
    ax.set_ylabel('Flux')
    ax.set_title(
        f'Secondary Eclipse Candidate at Phase {bestfit_flat[2]:.3f}\n'
        f'Reduced Chi-squared (Gaussian): {reduced_chi_squared_gaussianOG:.3f}, '
        f'Reduced Chi-squared (Straight Line): {reduced_chi_squared_straight:.3f}, '
        f'Reduced Chi-squared (Tanh): {reduced_chi_squared_tanh:.3f}'
    )
    ax.legend()
    _ensure_parent(save_path)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    return secondaryFound, best_model, sec_pos, swidth, sdepth, swidth_ecc


def BIC(timeData, fluxData, fluxErrData, gaussianParams, straightParams, tanhParams):
    '''
    Functionality:
        Compute BIC for three candidate models (Gaussian eclipse, Straight line,
        Tanh flat-bottom eclipse) on the same dataset and apply tie-breaking logic
        to select a preferred model and corresponding secondary parameters.

    Arguments:
        timeData (array-like): Independent variable (phase-like or time).
        fluxData (array-like): Flux values aligned with timeData.
        fluxErrData (array-like): Flux uncertainties aligned with timeData.
        gaussianParams (list[float]): [depth, sigma, mu] for gaussianModel (used directly).
        straightParams (list[float]): [m, b] for straightModel.
        tanhParams (list[float]): [depth, width_like_sigma, location] for tanh_transit_flat.

    Returns:
        (bool, str, float, float, float, float, float, float, float):
            secondaryFound: Whether a non-linear eclipse model is selected.
            best_model: 'Gaussian', 'Tanh', or 'Straight Line'.
            reduced_chi_squared_gaussianOG: Reduced χ² for Gaussian.
            reduced_chi_squared_straight: Reduced χ² for Straight line.
            reduced_chi_squared_tanh: Reduced χ² for Tanh.
            sec_pos: Adopted center (phase) if eclipse model selected; else NaN.
            swidth: Adopted full width (phase) if eclipse model selected; else NaN.
            sdepth: Adopted depth if eclipse model selected; else NaN.
            swidth_ecc: Width proxy used for eccentricity checks if eclipse model selected; else NaN.
    '''
    eps = 1e-9  # small tolerance for tie detection

    residuals_gaussianOG = fluxData - gaussianModel(timeData, *gaussianParams)
    k_gaussianOG = len(gaussianParams); ngaussianOG = len(fluxData)
    chi_squared_gaussianOG = np.sum((residuals_gaussianOG / fluxErrData)**2)
    reduced_chi_squared_gaussianOG = chi_squared_gaussianOG / max(1, (ngaussianOG - k_gaussianOG))
    bic_gaussianOG = chi_squared_gaussianOG + k_gaussianOG * np.log(max(1, ngaussianOG))

    residuals_straight = fluxData - straightModel(timeData, *straightParams)
    k_straight = len(straightParams); nstraight = len(fluxData)
    chi_squared_straight = np.sum((residuals_straight / fluxErrData)**2)
    reduced_chi_squared_straight = chi_squared_straight / max(1, (nstraight - k_straight))
    bic_straight = chi_squared_straight + k_straight * np.log(max(1, nstraight))

    residuals_tanh = fluxData - tanh_transit_flat(timeData, *tanhParams)
    k_tanh = len(tanhParams); ntanh = len(fluxData)
    chi_squared_tanh = np.sum((residuals_tanh / fluxErrData)**2)
    reduced_chi_squared_tanh = chi_squared_tanh / max(1, (ntanh - k_tanh))
    bic_tanh = chi_squared_tanh + k_tanh * np.log(max(1, ntanh))

    print(f"BIC Gaussian: {bic_gaussianOG}, BIC Straight Line: {bic_straight}, BIC Tanh: {bic_tanh}")
    print(f"secondary width: {tanhParams[1] * 1.25}")

    # tie logic
    bics = {'Gaussian': bic_gaussianOG, 'Straight': bic_straight, 'Tanh': bic_tanh}
    min_bic = min(bics.values())
    winners = [name for name, val in bics.items() if abs(val - min_bic) <= eps]

    # 1. if Straight is tied or best
    if 'Straight' in winners:
        secondaryFound = False
        best_model = 'Straight Line'
        sec_pos = swidth = swidth_ecc = sdepth = np.nan
        print("BIC tie includes Straight Line — defaulting to Straight Line model.")
        return (secondaryFound, best_model,
                reduced_chi_squared_gaussianOG, reduced_chi_squared_straight, reduced_chi_squared_tanh,
                sec_pos, swidth, sdepth, swidth_ecc)

    # 2. tie between 2 that are not Straight → use Tanh
    if len(winners) == 2 and 'Straight' not in winners:
        secondaryFound = True
        best_model = 'Tanh'
        sec_pos = tanhParams[2]
        swidth = max(0.005, tanhParams[1] * 1.75)
        swidth_ecc = tanhParams[1] * 1.25
        sdepth = tanhParams[0]
        print("BIC tie between Gaussian and Tanh — defaulting to Tanh model.")
        return (secondaryFound, best_model,
                reduced_chi_squared_gaussianOG, reduced_chi_squared_straight, reduced_chi_squared_tanh,
                sec_pos, swidth, sdepth, swidth_ecc)

    # 3. otherwise continue with original logic
    if bic_gaussianOG < bic_straight and bic_gaussianOG < bic_tanh:
        secondaryFound = True
        if (gaussianParams[1] * 4) > 0.09 and (tanhParams[1] * 1.25) < 0.09:
            best_model = 'Tanh'
            sec_pos = tanhParams[2]
            swidth = tanhParams[1] * 1.75
            swidth_ecc = tanhParams[1] * 1.25
            sdepth = tanhParams[0]
            print("Gaussian width is unusually large, reverting to Tanh model.")
        elif (gaussianParams[1] * 4) > 0.09 and (tanhParams[1] * 1.25) > 0.09:
            secondaryFound = False
            best_model = 'Straight Line'
            sec_pos = swidth = swidth_ecc = sdepth = np.nan
            print("Straight line model is preferred due to large Gaussian and Tanh widths.")
        elif (gaussianParams[1] * 4) < 0.001 and (tanhParams[1] * 1.25) > 0.00001:
            secondaryFound = True
            best_model = 'Tanh'
            sec_pos = tanhParams[2]
            swidth = max(0.005, tanhParams[1] * 1.75)
            swidth_ecc = tanhParams[1] * 1.25
            sdepth = tanhParams[0]
            print("Gaussian width is unusually small, reverting to Tanh model.")
        elif (gaussianParams[1] * 4) < 0.001 and (tanhParams[1] * 1.25) < 0.00001:
            secondaryFound = False
            best_model = 'Straight Line'
            sec_pos = swidth = swidth_ecc = sdepth = np.nan
            print("Straight line model is preferred due to small Gaussian and Tanh widths.")
        else:
            best_model = 'Gaussian'
            sec_pos = gaussianParams[2]
            swidth = gaussianParams[1] * 5
            swidth_ecc = gaussianParams[1] * 4
            sdepth = gaussianParams[0]
            print("Gaussian model is preferred.")
    elif bic_straight < bic_gaussianOG and bic_straight < bic_tanh:
        secondaryFound = False
        best_model = 'Straight Line'
        sec_pos = swidth = swidth_ecc = sdepth = np.nan
        print("Straight line model is preferred.")
    elif bic_tanh < bic_gaussianOG and bic_tanh < bic_straight:
        if (tanhParams[1] * 1.25) > 1.0 or (tanhParams[1] * 1.25) < 0.00001:
            secondaryFound = False
            best_model = 'Straight Line'
            sec_pos = swidth = swidth_ecc = sdepth = np.nan
            print("Straight line model is preferred due to unrealistic Tanh width.")
        else:
            secondaryFound = True
            best_model = 'Tanh'
            sec_pos = tanhParams[2]
            swidth = max(0.005, tanhParams[1] * 1.75)
            swidth_ecc = tanhParams[1] * 1.25
            sdepth = tanhParams[0]
            print("Tanh model is preferred.")

    return (secondaryFound, best_model,
            reduced_chi_squared_gaussianOG, reduced_chi_squared_straight, reduced_chi_squared_tanh,
            sec_pos, swidth, sdepth, swidth_ecc)


def solve_for_X(t_sec, t_pri, P):
    '''
    Functionality:
        Solve X - sin(X) = 2π (t_sec - t_pri) / P for X using a Brent root finder.
        (This is Equation 5.68 in Hilditch for relating primary and secondary eclipse
        timing in an eccentric orbit.)

    Arguments:
        t_sec (float): Time of secondary eclipse.
        t_pri (float): Time of primary eclipse.
        P (float): Orbital period.

    Returns:
        float:
            The solution X in radians, constrained to [0, 2π].

    Raises:
        RuntimeError:
            If the solver fails to converge.
    '''
    lhs = 2 * np.pi * (t_sec - t_pri) / P

    def f(X):
        '''Return X − sin(X) − LHS for the root-finding step.'''
        return X - np.sin(X) - lhs

    sol = so.root_scalar(f, method='brentq', bracket=[0, 2 * np.pi])
    if sol.converged:
        return sol.root
    else:
        raise RuntimeError("Root finding for X did not converge.")


def estimate_e_and_omega(t_sec, t_pri, period_days, pwidth_ecc, swidth_ecc,
                         max_e=0.98, grid_N=400, xtol=1e-10, rtol=1e-10):
    '''
    Functionality:
        Estimate orbital eccentricity (e) and argument of periastron (omega) from
        (i) the secondary–primary timing offset and (ii) primary/secondary eclipse
        width diagnostics. Uses a scalar root on a consistency equation between
        linearized ecos(omega) and esin(omega) targets; falls back to linearized
        closed-form when a valid bracket or solution is not found.

    Arguments:
        t_sec (float): Time of secondary eclipse (same units as period_days).
        t_pri (float): Time of primary eclipse (same units as period_days).
        period_days (float): Orbital period in days.
        pwidth_ecc (float): Primary eclipse width proxy (phase) for eccentric case.
        swidth_ecc (float): Secondary eclipse width proxy (phase) for eccentric case.
        max_e (float): Upper bound for eccentricity search (default 0.98).
        grid_N (int): Number of grid samples for coarse bracketing (default 400).
        xtol (float): Absolute tolerance for Brent root finder (default 1e-10).
        rtol (float): Relative tolerance for Brent root finder (default 1e-10).

    Returns:
        (float, float, float, float, dict):
            e: Estimated eccentricity in [0, max_e].
            omega: Argument of periastron (radians, in [-pi, pi]).
            ecosw: e * cos(omega).
            esinw: e * sin(omega).
            diagnostics: Dictionary with keys such as:
                - 'method' (e.g., 'brentq', 'linearized_fallback', 'timing_only_fallback')
                - 'bracket' (if used), 'delta', 'R', and linear targets.
    '''
    # sanitize inputs
    P = float(period_days)
    if P <= 0 or not np.isfinite(P):
        raise ValueError("estimate_e_and_omega: invalid period_days")

    # wrap secondary-primary phase offset into (-0.5, 0.5]
    dphi = ((t_sec - t_pri) / P) % 1.0
    if dphi > 0.5:
        dphi -= 1.0

    # phase offset from exact half-phase (delta ≈ ecos(omega)/π)
    delta = dphi - 0.5

    # widths
    pW = float(pwidth_ecc)
    sW = float(swidth_ecc)
    if (not np.isfinite(pW)) or (not np.isfinite(sW)) or (pW <= 0) or (sW <= 0):
        pW = np.nan
        sW = np.nan
    R = (sW / pW) if (np.isfinite(pW) and np.isfinite(sW)) else np.nan

    # linearized targets
    ecosw_lin = np.pi * delta
    esinw_lin = (R - 1.0) / (R + 1.0) if (np.isfinite(R) and R > 0) else np.nan
    have_both = np.isfinite(esinw_lin)

    # scalar equation for e
    def equation_for_e(e):
        '''
        Functionality:
            Scalar equation used to solve for eccentricity `e` given either:
            - ecos(ω) only, or
            - both ecos(ω) and esin(ω).

        Arguments:
            e (float): Trial eccentricity value.

        Returns:
            float:
                Residual of the constraint equation. Root occurs at the correct `e`.
        '''
        if e <= 0:
            return -abs(ecosw_lin) if not have_both else -math.sqrt(ecosw_lin**2 + esinw_lin**2)
        if have_both:
            return (ecosw_lin**2 + esinw_lin**2) - e**2
        else:
            return (abs(ecosw_lin)) - e

    # try endpoints
    f_lo = equation_for_e(0.0)
    f_hi = equation_for_e(max_e)

    if abs(f_lo) < 1e-14:
        e = 0.0
        omega = 0.0
        ecosw = e * np.cos(omega)
        esinw = e * np.sin(omega)
        return e, omega, ecosw, esinw, {"method": "endpoint_e=0", "delta": delta, "R": R}

    if abs(f_hi) < 1e-10:
        e = max_e
        if have_both and e > 0:
            omega = math.atan2(esinw_lin/e, ecosw_lin/e)
        else:
            omega = 0.0
        ecosw = e * np.cos(omega)
        esinw = e * np.sin(omega)
        return e, omega, ecosw, esinw, {"method": "endpoint_e=max_e", "delta": delta, "R": R}

    # coarse sign-change bracket
    e_grid = np.linspace(0.0, max_e, grid_N+1)
    f_grid = np.array([equation_for_e(ev) for ev in e_grid])
    sign = np.sign(f_grid)
    idx = np.where(sign[:-1] * sign[1:] < 0)[0]

    if idx.size > 0:
        lo = e_grid[idx[0]]
        hi = e_grid[idx[0]+1]
        try:
            sol = so.root_scalar(equation_for_e, bracket=[lo, hi],
                                 method='brentq', xtol=xtol, rtol=rtol, maxiter=200)
            e = float(sol.root)
            if have_both and e > 0:
                omega = math.atan2(esinw_lin/e, ecosw_lin/e)
            elif e > 0:
                c = np.clip(ecosw_lin / e, -1.0, 1.0)
                omega = 0.0 if c >= 0 else np.pi
            else:
                omega = 0.0
            ecosw = e * np.cos(omega)
            esinw = e * np.sin(omega)
            return e, omega, ecosw, esinw, {"method": "brentq", "bracket": [lo, hi], "delta": delta, "R": R}
        except Exception:
            pass

    # linearized fallback (both) or timing-only fallback
    if np.isfinite(esinw_lin):
        e_lin = float(np.hypot(ecosw_lin, esinw_lin))
        e = min(max(e_lin, 0.0), max_e)
        omega = math.atan2(esinw_lin, ecosw_lin) if e > 0 else 0.0
        ecosw = e * np.cos(omega)
        esinw = e * np.sin(omega)
        return e, omega, ecosw, esinw, {
            "method": "linearized_fallback",
            "reason": "no_sign_change",
            "delta": delta, "R": R,
            "ecosw_lin": ecosw_lin, "esinw_lin": esinw_lin
        }
    else:
        e = min(max(abs(ecosw_lin), 0.0), max_e)
        omega = 0.0 if ecosw_lin >= 0 else np.pi
        ecosw = e * np.cos(omega)
        esinw = e * np.sin(omega)
        return e, omega, ecosw, esinw, {
            "method": "timing_only_fallback",
            "reason": "widths_invalid_or_missing",
            "delta": delta, "R": R,
            "ecosw_lin": ecosw_lin, "esinw_lin": esinw_lin
        }

def estimate_eclipse_width_phase_circular(Ra, Rb, a_AU):
    '''
    Functionality:
        Estimate the secondary eclipse width in phase for a circular orbit using
        a simple geometric chord-length approximation: width ≈ (Ra + Rb) / (2π a).

    Arguments:
        Ra (float): Primary radius in meters.
        Rb (float): Secondary radius in meters.
        a_AU (float): Semi-major axis in astronomical units.

    Returns:
        float: Approximate eclipse width in phase units (dimensionless).
    '''
    if a_AU is None or not np.isfinite(a_AU) or a_AU <= 0:
        return np.nan
    a_m = a_AU * AU2M  # convert semi-major axis to meters
    swidth = (Ra + Rb) / (2 * np.pi * a_m)
    return swidth


def vet_secondary_eclipse(
    timeData, fluxData, fluxErrData,
    sec_pos,
    sdepth,
    Ra, Rb, Ta=None, Tb=None, a=None,
    period_days=None,
    bjd0=None,
    sep=None, pwidth=None, swidth=None,
    prim_pos=None,
    pdepth=None,
    pwidth_ecc=None,
    DetrendingName=None, ID=None,
    *, base_dir=None
):
    '''
    Functionality:
        Vet a candidate secondary eclipse for physical plausibility using:
        (i) phase placement, (ii) depth sanity, and (iii) model-selection via BIC
        between eclipse-like (Gaussian/Tanh) and linear models. If an eclipse-like
        model is preferred, derive (e, ω) using simple diagnostics and also via a
        no-assumption timing/width estimator.

    Arguments:
        timeData (array-like): X-values (typically phase or time) for the cutout.
        fluxData (array-like): Flux values aligned with timeData.
        fluxErrData (array-like): Flux uncertainties aligned with timeData.
        sec_pos (float): Candidate secondary center (phase).
        sdepth (float): Candidate secondary depth (fractional).
        Ra (float): Primary radius in meters.
        Rb (float): Secondary radius in meters.
        Ta (float|None): Primary temperature (unused placeholder).
        Tb (float|None): Secondary temperature (unused placeholder).
        a (float|None): Semi-major axis in AU (used if no secondary found to estimate width).
        period_days (float|None): Orbital period in days (used for e–ω estimation).
        bjd0 (float|None): Reference epoch (unused in current logic).
        sep (float|None): Measured primary–secondary separation in phase (if available).
        pwidth (float|None): Primary width (phase) (unused here).
        swidth (float|None): Secondary width (phase), initial guess for fits.
        prim_pos (float|None): Primary phase (unused here).
        pdepth (float|None): Primary depth (unused here).
        pwidth_ecc (float|None): Primary width proxy (phase) for eccentric diagnostics.
        DetrendingName (str|None): Folder label for saving diagnostics.
        ID (str|int|None): Target identifier for filenames.
        base_dir (Path-like or None): Root directory for outputs (cluster/local/pip).

    Returns:
        (dict, float, float, float, float, float, float):
            result: Dictionary with keys:
                - 'valid' (bool),
                - 'reason' (str, ' | '-joined),
                - 'phase_secondary' (float),
                - 'width_fit' (float),
                - 'depth_fit' (float),
                - 'expected_depth_max' (None),
                - 'passes_phase_check' (bool),
                - 'passes_depth_check' (bool),
                - 'BIC_check' (bool).
            ecc: Eccentricity estimated from simple diagnostics (or 0 if none).
            omega: Argument of periastron in radians (or 0).
            eccNoAssump: Eccentricity from estimate_e_and_omega (fallback-friendly).
            omegaNoAssump: Omega from estimate_e_and_omega (radians).
            ecoswNoAssump: e*cos(omega) from estimate_e_and_omega.
            esinwNoAssump: e*sin(omega) from estimate_e_and_omega.
    '''
    # initialize result, reason, ecc, and omega
    result = {
        "valid": False,
        "reason": "",
        "phase_secondary": None,
        "width_fit": None,
        "depth_fit": None,
        "expected_depth_max": None,
        "passes_phase_check": False,
        "passes_depth_check": False,
        "BIC_check": None,
    }

    result["reason"] = []
    ecc = 0
    omega = 0

    # phase check (not disqualifying if outside)
    if 0.4 <= float(sec_pos) <= 0.6:
        result["passes_phase_check"] = True
    else:
        result["passes_phase_check"] = False
        result["reason"].append("Phase offset suggests eccentric orbit or false detection")

    # depth check (temperature-independent sanity)
    expected_depth_max = None
    result["expected_depth_max"] = expected_depth_max
    if (sdepth is not None) and np.isfinite(sdepth) and (0.0005 < float(sdepth) < 1.0):
        result["passes_depth_check"] = True
    else:
        result["passes_depth_check"] = False
        result["reason"].append("Fitted depth outside a sensible [0,1) fractional range")

    # BIC-based model selection (pass base_dir through for portable outputs)
    secondaryFound, best_model, sec_pos, swidth, sdepth, swidth_ecc = gaussianStraight(
        timeData, fluxData, fluxErrData, sec_pos, swidth, sdepth, DetrendingName, ID, base_dir=base_dir
    )

    if secondaryFound is True:
        result["BIC_check"] = True

        # simple diagnostics (will yield nan if inputs missing; acceptable)
        ecosw = np.pi/2 * (float(sep) - 0.5) if (sep is not None and np.isfinite(sep)) else np.nan
        if (swidth_ecc is not None and pwidth_ecc is not None
                and np.isfinite(swidth_ecc) and np.isfinite(pwidth_ecc)
                and (swidth_ecc + pwidth_ecc) != 0):
            esinw = (swidth_ecc - pwidth_ecc) / (swidth_ecc + pwidth_ecc)
        else:
            esinw = np.nan

        if np.isfinite(ecosw) and np.isfinite(esinw):
            ecc = np.hypot(ecosw, esinw)
            omega = np.arctan2(esinw, ecosw)  # radians
            omega_deg = np.degrees(omega)
        else:
            ecc = 0.0
            omega = 0.0
            omega_deg = 0.0

        # no-assumption estimator (timing/width) — requires period_days and valid widths
        if (period_days is not None and np.isfinite(period_days) and period_days > 0
                and pwidth_ecc is not None and swidth_ecc is not None):
            t_sec = float(sec_pos) * float(period_days)
            t_pri = 0.0
            eccNoAssump, omegaNoAssump, ecoswNoAssump, esinwNoAssump, ewDiagnostic = estimate_e_and_omega(
                t_sec, t_pri, period_days, pwidth_ecc, swidth_ecc
            )
        else:
            eccNoAssump = omegaNoAssump = ecoswNoAssump = esinwNoAssump = 0.0

    else:
        result["BIC_check"] = False
        result["reason"].append("Straight line model preferred over Gaussian or Tanh")
        ecc = 0
        omega = 0
        omega_deg = 0
        sec_pos = 0.5

        # derive a simple amplitude and width for bookkeeping
        phaseTimeCutBinned, fluxArrayCutBinned, fluxArrayErrCutBinned = binData(timeData, fluxData, fluxErrData)
        mask = (phaseTimeCutBinned > sec_pos - 0.05) & (phaseTimeCutBinned < sec_pos + 0.05)
        if np.any(mask):
            sdepth = 1.0 - np.min(fluxArrayCutBinned[mask])
        # width estimate (circular approx) if a is available
        swidth = swidth_ecc = estimate_eclipse_width_phase_circular(Ra, Rb, a)
        sep = 0.5

        eccNoAssump = 0
        omegaNoAssump = 0
        ecoswNoAssump = 0
        esinwNoAssump = 0

    # populate result
    result["phase_secondary"] = sec_pos
    result["depth_fit"] = sdepth
    result["width_fit"] = swidth

    print(f"Estimated eccentricity: {float(ecc):.10f}, omega (degrees): {float(omega_deg):.10f} "
          f"using separation {sep} and widths {pwidth_ecc}, {swidth_ecc}")

    if result["BIC_check"]:
        result["valid"] = True
        result["reason"].append("Plausible secondary eclipse")

    result["reason"] = " | ".join(result["reason"])

    return result, ecc, omega, eccNoAssump, omegaNoAssump, ecoswNoAssump, esinwNoAssump


def binData(phaseTime, fluxArray, fluxArrayErr, bin_width=0.00001):
    '''
    Functionality:
        Bin phase-folded data over [0, 1) using fixed-width bins, returning
        per-bin mean phase, mean flux, and mean flux error (via RMS/√N).

    Arguments:
        phaseTime (array-like): Phase (or time already modulo period). Will be wrapped to [0,1).
        fluxArray (array-like): Flux values aligned with phaseTime.
        fluxArrayErr (array-like): Flux uncertainties aligned with phaseTime.
        bin_width (float): Bin width in phase units (default 1e-5).

    Returns:
        (numpy.ndarray, numpy.ndarray, numpy.ndarray):
            phaseTimeBinned: Mean phase of each non-empty bin.
            fluxArrayBinned: Mean flux per non-empty bin.
            fluxArrayErrBinned: Mean flux error per non-empty bin (= sqrt(sum(err^2))/N).
    '''
    import numpy as np
    phaseTime = np.asarray(phaseTime, dtype=float)
    fluxArray = np.asarray(fluxArray, dtype=float)
    fluxArrayErr = np.asarray(fluxArrayErr, dtype=float)

    # wrap phases to [0, 1)
    phaseTime = np.mod(phaseTime, 1.0)

    # define bin edges and centers over [0, 1)
    start, end = 0.0, 1.0
    nbins = int(np.ceil((end - start) / bin_width))
    bin_edges = start + np.arange(nbins + 1) * bin_width
    bin_centers = bin_edges[:-1] + bin_width / 2.0

    # digitize
    bin_indices = np.digitize(phaseTime, bin_edges) - 1
    bin_indices = np.clip(bin_indices, 0, len(bin_centers) - 1)

    # allocate
    flux_sum = np.zeros_like(bin_centers)
    flux_err_sq_sum = np.zeros_like(bin_centers)
    count = np.zeros_like(bin_centers)
    time_sum = np.zeros_like(bin_centers)

    # accumulate
    np.add.at(flux_sum,        bin_indices, fluxArray)
    np.add.at(flux_err_sq_sum, bin_indices, fluxArrayErr**2)
    np.add.at(count,           bin_indices, 1)
    np.add.at(time_sum,        bin_indices, phaseTime)

    # reduce
    valid = count > 0
    phaseTimeBinned    = time_sum[valid] / count[valid]
    fluxArrayBinned    = flux_sum[valid] / count[valid]
    fluxArrayErrBinned = np.sqrt(flux_err_sq_sum[valid]) / count[valid]

    return phaseTimeBinned, fluxArrayBinned, fluxArrayErrBinned


def binDataRealTime(time, fluxArray, bin_width=30 * 60, min_points_per_bin=10, gap_threshold=120 * 15):
    '''
    Functionality:
        Bin *time-domain* data with gap-awareness. The series is split at large gaps,
        each segment is binned on a fixed time grid, and bins with at least
        `min_points_per_bin` samples are kept.

    Arguments:
        time (array-like): Timestamps (seconds recommended) to be binned.
        fluxArray (array-like): Flux values aligned with time.
        bin_width (float): Bin width in time units (default 1800 s).
        min_points_per_bin (int): Minimum samples required to keep a bin (default 10).
        gap_threshold (float): Gap size (same units as time) that splits segments (default 1800 s).

    Returns:
        (numpy.ndarray, numpy.ndarray):
            time_binned_final: Mean time per kept bin across all segments.
            flux_binned_final: Mean flux per kept bin across all segments.
    '''
    import numpy as np

    # convert to numpy
    time = np.asarray(time, dtype=float)
    fluxArray = np.asarray(fluxArray, dtype=float)

    # sort by time
    sort_idx = np.argsort(time)
    time = time[sort_idx]
    fluxArray = fluxArray[sort_idx]

    # split on large gaps
    time_diff = np.diff(time)
    gap_indices = np.where(time_diff > gap_threshold)[0]
    segment_edges = np.concatenate(([0], gap_indices + 1, [len(time)]))

    time_binned_list = []
    flux_binned_list = []

    # process each segment independently
    for i in range(len(segment_edges) - 1):
        seg_start = segment_edges[i]
        seg_end = segment_edges[i + 1]

        t_seg = time[seg_start:seg_end]
        f_seg = fluxArray[seg_start:seg_end]

        if len(t_seg) < min_points_per_bin:
            continue

        # segment-local bin edges
        start = np.min(t_seg)
        end = np.max(t_seg)
        bin_edges = np.arange(start, end + bin_width, bin_width)
        bin_centers = bin_edges[:-1] + bin_width / 2

        # digitize and clip
        bin_indices = np.digitize(t_seg, bin_edges) - 1
        num_bins = len(bin_centers)
        bin_indices = np.clip(bin_indices, 0, num_bins - 1)

        # allocate
        flux_sum = np.zeros(num_bins)
        count = np.zeros(num_bins)
        time_sum = np.zeros(num_bins)

        # accumulate
        np.add.at(flux_sum, bin_indices, f_seg)
        np.add.at(count,    bin_indices, 1)
        np.add.at(time_sum, bin_indices, t_seg)

        # keep sufficiently populated bins
        valid = count >= min_points_per_bin
        timeBinned = time_sum[valid] / count[valid]
        fluxBinned = flux_sum[valid] / count[valid]

        time_binned_list.append(timeBinned)
        flux_binned_list.append(fluxBinned)

    # concatenate results from all segments
    time_binned_final = np.concatenate(time_binned_list) if time_binned_list else np.array([])
    flux_binned_final = np.concatenate(flux_binned_list) if flux_binned_list else np.array([])

    return time_binned_final, flux_binned_final


def classify_known_eclipse(prim_pos, sec_pos):
    '''
    Functionality:
        Classify an eclipse state based on availability of primary/secondary
        eclipse phase centers.

    Arguments:
        prim_pos (float or numpy.nan): Primary eclipse phase; NaN if unknown.
        sec_pos (float or numpy.nan): Secondary eclipse phase; NaN if unknown.

    Returns:
        str: One of {'none', 'primary', 'secondary', 'both', 'unknown'}.
    '''
    import numpy as np

    if np.isnan(prim_pos) and np.isnan(sec_pos):
        return "none"
    elif (not np.isnan(prim_pos)) and np.isnan(sec_pos):
        return "primary"
    elif np.isnan(prim_pos) and (not np.isnan(sec_pos)):
        return "secondary"
    elif (not np.isnan(prim_pos)) and (not np.isnan(sec_pos)):
        return "both"
    else:
        return "unknown"


def CBStabilityLimit(m1, m2, eb, ab):
    '''
    Functionality:
        Compute the Holman & Wiegert (1999, Eq. 3) critical semi-major axis for
        circumBINARY orbital stability and return it in the same units as `ab`.

    Arguments:
        m1 (float): Primary mass (arbitrary units; only the ratio matters).
        m2 (float): Secondary mass (same units as m1).
        eb (float): Binary eccentricity.
        ab (float): Binary semi-major axis (output will scale with this).

    Returns:
        float: Critical semi-major axis a_c (same units as `ab`).
    '''
    # CircumBINARY stability limit
    # Calculated using Holman & Wiegert, 1999, their equation 3
    pm = -0  # coefficient uncertainty toggle (kept at 0 → ignore)
    u = m2 / (m1 + m2)  # mass ratio
    # Critical radius in units of ab (rc), then scale by ab to get ac
    rc = ((1.6 + pm * 0.04)
          + (5.1 + pm * 0.05) * eb
          + (-2.22 + pm * 0.11) * eb**2.
          + (4.12 + pm * 0.09) * u
          + (-4.27 + pm * 0.17) * eb * u
          + (-5.09 + pm * 0.11) * u**2.
          + (4.61 + pm * 0.36) * eb**2. * u**2.)
    ac = rc * ab
    return ac


def CBPrecessionPeriod(Pin, Pout, MA, MB, deltaI):
    '''
    Functionality:
        Compute the nodal precession period for a circumbinary configuration, using
        the provided analytic expression. All inputs are expected in SI-compatible
        units (seconds for periods, kilograms for masses, radians for angles).

    Arguments:
        Pin (float): Inner binary period (seconds).
        Pout (float): Circumbinary orbit period (seconds).
        MA (float): Mass of primary (kg).
        MB (float): Mass of secondary (kg).
        deltaI (float): Mutual inclination (radians).

    Returns:
        float: Precession period (seconds).
    '''
    import numpy as np
    # everything is inputted in SI units
    Pprec = (4. / 3.) * (Pout**7. / Pin**4.)**(1. / 3.) * (MA + MB)**2. / (MA * MB) * 1. / np.cos(deltaI)
    return Pprec


def calcOrbitalElementsOverTime_nbody(
    reboundSim,
    reference=-1,
    returnData=False,
    plotResults=True,
    outputTimeLeft=False,
    checkSlowSims=False,
    tMax=4*YEARS2SEC,
    tStep=1*DAYS2SEC
):
    '''
    Functionality:
        Integrate a copy of a REBOUND simulation and record orbital elements,
        Cartesian positions, and times at fixed steps from t=0 to tMax. Optionally
        plot orbits and return the sampled data products.

    Arguments:
        reboundSim (rebound.Simulation): Initialized simulation to copy and evolve.
        reference (int): Unused placeholder retained for API compatibility.
        returnData (bool): If True, return (orbitalElements, positions, timeArray).
        plotResults (bool): If True, produce an orbit plot at start and a summary plot after.
        outputTimeLeft (bool): If True, print periodic completion updates.
        checkSlowSims (bool): If True, break early if a step becomes much slower (heuristic).
        tMax (float): Total integration duration (seconds).
        tStep (float): Output/integration step size (seconds).

    Returns:
        tuple or None:
            If returnData is True:
                (orbitalElements, positions, timeArray)
                - orbitalElements: list over time of lists of REBOUND Orbit objects (length N-1 each).
                - positions: numpy.ndarray of shape (n_times, N, 3) with [x,y,z] per body.
                - timeArray: numpy.ndarray of times (seconds) corresponding to each output.
            If returnData is False:
                None (data only plotted/printed).
    '''
    if rebound is None:
        raise ImportError("rebound is required for calcOrbitalElementsOverTime_nbody")

    # This function runs rebound and calculates the orbital elements over time
    tempSim = reboundSim.copy()

    N = tempSim.N  # number of bodies
    print("N-body calculations of the " + str(N) + " body orbital elements over " + str(tMax/YEARS2SEC) + " years")

    if (plotResults == True):
        # Create an initial plot of the orbits
        fig = rebound.OrbitPlot(tempSim, color=True, unitlabel="[AU]", slices=True)

    # put everything to the centre of mass
    tempSim.move_to_com()

    # p is a reference to the positions and velocities of all three bodies
    p = tempSim.particles

    # Integrate the system up to tMax in steps of tStep, such that after each tStep we save the orbital elements
    orbitalElements = []
    timeArray = []
    positions = []  # store the x and z positions
    tau_a_array_in = []
    tau_a_array_out = []
    tempSim.t = 0

    timeMarker = tMax / 1000.
    timeMarkerStep = tMax / 1000.
    realTimeNote = TIME.time()

    checkSlowSims = 0

    while tempSim.t < tMax:
        # you first get the intial orbital elements before there is any integration
        p = tempSim.particles

        # Simulation().calculate_orbit() is deprecated; use orbits()
        orbits = tempSim.orbits()

        orbitalElements_row = []
        positions_row = []
        for ii in range(0, N):
            if (ii < N - 1):  # remember that there are only N-1 orbits, whilst N bodies
                orbitalElements_row.append(orbits[ii])
            positions_row.append([p[ii].x, p[ii].y, p[ii].z])
        orbitalElements.append(orbitalElements_row)
        positions.append(positions_row)
        timeArray.append(tempSim.t)
        tempSim.integrate(tempSim.t + tStep)

        if (outputTimeLeft == True):
            # print out an update
            if (tempSim.t > timeMarker):
                print(str(timeMarker / tMax * 100.) + " per cent completed")
                timeMarker += timeMarkerStep
                realTimeTaken = TIME.time() - realTimeNote
                realTimeNote = TIME.time()

            # if we have hit 10 % then change the timestep marker from 1% increments to 10%
            if (timeMarker / tMax * 100. == 10.):
                timeMarkerStep = tMax / 10.

        if (checkSlowSims == True):
            # heuristic slow-sim check
            if (tempSim.t / tMax > 0.2):
                if (TIME.time() - realTimeNote > 5. * realTimeTaken):
                    print('Shit is slowing down, break')
                    break

    # Convert the timeArray from a list to a np array
    timeArray = np.array(timeArray)

    if (plotResults == True):
        plotOrbitalElementsOverTime_nbody(orbitalElements, timeArray, units="normal", newFig=False)

    if (returnData == True):
        return orbitalElements, np.array(positions), np.array(timeArray)


def plotPositionsOverTime(positions, time, units):
    '''
    Functionality:
        Plot body trajectories in both the inertial and a corotating reference frame.
        Produces two figures with X–Z, X–Y, and Z–Y projections (points by default).

    Arguments:
        positions (array-like): Shape (n_times, N, 3) array-like with Cartesian
            coordinates [x, y, z] for each body at each sampled time.
        time (array-like): Times corresponding to rows in `positions` (unused in plots,
            kept for API symmetry).
        units (str): Either "natural" (distances scaled by 1/au2m) or any other
            string to plot in raw units (typically meters).

    Returns:
        None: Creates matplotlib figures and plots; does not return a value.
    '''
    colourArray = ['b', 'r', 'g', 'm', 'b', 'y', 'c']
    plotPoints = 1  # 0 = plot lines, 1 = plot points (good for very long sims)

    if (units == "natural"):
        lengthScale = 1/AU2M
    else:
        lengthScale = 1

    # Plot the orbits (inertial frame)
    N = len(positions[0]) + 1

    fig = plt.figure(figsize=(8, 8))
    plt.suptitle('Inertial reference frame')
    for ii in range(0, N-1):
        x_pos = np.array([x[ii][0] for x in positions[:]])
        y_pos = np.array([x[ii][1] for x in positions[:]])
        z_pos = np.array([x[ii][2] for x in positions[:]])

        plt.subplot(2, 2, 1)  # top left
        if (plotPoints == 1):
            plt.scatter(x_pos/AU2M/lengthScale, z_pos/AU2M/lengthScale, c=colourArray[ii])
        else:
            plt.plot(x_pos/AU2M/lengthScale, z_pos/AU2M/lengthScale, c=colourArray[ii])
        plt.scatter(x_pos[0]/AU2M/lengthScale, z_pos[0]/AU2M/lengthScale, marker="*", s=50, c=colourArray[ii])
        plt.ylabel("Z (AU)")
        plt.xlabel("X (AU)")
        plt.axis("equal")

        plt.subplot(2, 2, 3)  # bottom left
        if (plotPoints == 1):
            plt.scatter(x_pos/AU2M/lengthScale, y_pos/AU2M/lengthScale, c=colourArray[ii])
        else:
            plt.plot(x_pos/AU2M/lengthScale, y_pos/AU2M/lengthScale, c=colourArray[ii])
        plt.scatter(x_pos[0]/AU2M/lengthScale, y_pos[0]/AU2M/lengthScale, marker="*", s=50, c=colourArray[ii])
        plt.ylabel("Y (AU)")
        plt.xlabel("X (AU)")
        plt.axis("equal")

        plt.subplot(2, 2, 4)  # bottom right
        if (plotPoints == 1):
            plt.scatter(z_pos/AU2M/lengthScale, y_pos/AU2M/lengthScale, c=colourArray[ii])
        else:
            plt.plot(z_pos/AU2M/lengthScale, y_pos/AU2M/lengthScale, c=colourArray[ii])
        plt.scatter(z_pos[0]/AU2M/lengthScale, y_pos[0]/AU2M/lengthScale, marker="*", s=50, c=colourArray[ii])
        plt.ylabel("Y (AU)")
        plt.xlabel("Z (AU)")
        plt.axis("equal")

    # Now do the corotating frame
    fig = plt.figure(figsize=(8, 8))
    plt.suptitle('Rotating reference frame')

    # calculate the angle theta for each position in the array
    x_pos_1 = np.array([x[1][0] for x in positions[:]])
    y_pos_1 = np.array([x[1][1] for x in positions[:]])
    theta_1 = np.arctan2(y_pos_1, x_pos_1)

    # rotate all the bodies back by this
    for ii in range(0, N-1):
        x_pos = np.array([x[ii][0] for x in positions[:]])
        y_pos = np.array([x[ii][1] for x in positions[:]])
        z_pos = np.array([x[ii][2] for x in positions[:]])
        x_pos_rot = x_pos * np.cos(theta_1) + y_pos * np.sin(theta_1)
        y_pos_rot = -x_pos * np.sin(theta_1) + y_pos * np.cos(theta_1)
        z_pos_rot = z_pos  # no change

        plt.subplot(2, 2, 1)  # top left
        if (plotPoints == 1):
            plt.scatter(x_pos_rot/AU2M/lengthScale, z_pos_rot/AU2M/lengthScale, c=colourArray[ii])
        else:
            plt.plot(x_pos_rot/AU2M/lengthScale, z_pos_rot/AU2M/lengthScale, c=colourArray[ii])
        plt.scatter(x_pos_rot[0]/AU2M/lengthScale, z_pos_rot[0]/AU2M/lengthScale, marker="*", s=50, c=colourArray[ii])
        plt.ylabel("Z (AU)")
        plt.xlabel("X (AU)")
        plt.axis("equal")

        plt.subplot(2, 2, 3)  # bottom left
        if (plotPoints == 1):
            plt.scatter(x_pos_rot/AU2M/lengthScale, y_pos_rot/AU2M/lengthScale, c=colourArray[ii])
        else:
            plt.plot(x_pos_rot/AU2M/lengthScale, y_pos_rot/AU2M/lengthScale, c=colourArray[ii])
        plt.scatter(x_pos_rot[0]/AU2M/lengthScale, y_pos_rot[0]/AU2M/lengthScale, marker="*", s=50, c=colourArray[ii])
        plt.ylabel("Y (AU)")
        plt.xlabel("X (AU)")
        plt.axis("equal")

        plt.subplot(2, 2, 4)  # bottom right
        if (plotPoints == 1):
            plt.scatter(z_pos_rot/AU2M/lengthScale, y_pos_rot/AU2M/lengthScale, c=colourArray[ii])
        else:
            plt.plot(z_pos_rot/AU2M/lengthScale, y_pos_rot/AU2M/lengthScale, c=colourArray[ii])
        plt.scatter(z_pos_rot[0]/AU2M/lengthScale, y_pos_rot[0]/AU2M/lengthScale, marker="*", s=50, c=colourArray[ii])
        plt.ylabel("Y (AU)")
        plt.xlabel("Z (AU)")
        plt.axis("equal")


def plotOrbitalElementsOverTime_nbody(orbitalElements, time, units="normal", newFig=False):
    '''
    Functionality:
        Plot standard orbital elements versus time for each orbit in an evolved
        REBOUND simulation output. Optionally includes resonant angles, mutual
        inclinations, Kozai elements, and period ratios (kept disabled by default).

    Arguments:
        orbitalElements (list): List over time of lists of REBOUND Orbit objects.
            At each time step the list has length N-1 (for N bodies).
        time (array-like): Times (seconds) corresponding to each element snapshot.
        units (str): If "natural", rescale time and lengths to natural units
            (timeScale=2π/years2sec, lengthScale=1/au2m). Otherwise, use raw units.
        newFig (bool): If True, could open new figures per-orbit (kept inactive
            here; plotting uses one figure per orbit by default).

    Returns:
        None: Produces matplotlib figures; no values are returned.
    '''
    # This function will typically be used with the above one to plot them over time
    N = len(orbitalElements[0]) + 1

    plotResonantAngles = 0
    plotPeriodRatios = 0
    plotMutualInclinations = 0
    plotKozaiElements = 0

    # If only 2 bodies, disable the special plots
    if (N < 3):
        plotMutualInclinations = 0
        plotResonantAngles = 0
        plotKozaiElements = 0
        plotPeriodRatios = 0

    if (units == "natural"):
        timeScale = 2.*np.pi/YEARS2SEC
        lengthScale = 1./AU2M
    else:
        timeScale = 1.
        lengthScale = 1.

    time = time / timeScale  # scale time for downstream axis choice

    # Choose axis in days or years
    if (np.max(time) < 2*YEARS2SEC):
        timeAxis = time/DAYS2SEC
        timeAxisLabel = "time (days)"
    else:
        timeAxis = time/YEARS2SEC
        timeAxisLabel = "time (years)"

    # Loop through each orbit and plot orbital elements
    for ii in range(0, N-1):
        fig = plt.figure(figsize=(17, 9))

        ax = plt.subplot(331)
        ax.set_ylabel("Period (days)")
        ax.set_title('starting value = ' + str(orbitalElements[0][ii].P/DAYS2SEC/timeScale))
        plt.plot(timeAxis, np.array([x[ii].P for x in orbitalElements[:]])/DAYS2SEC/timeScale)

        ax = plt.subplot(332)
        ax.set_ylabel("eccentricity")
        ax.set_title('starting value = ' + str(orbitalElements[0][ii].e))
        plt.plot(timeAxis, np.array([x[ii].e for x in orbitalElements[:]]))

        ax = plt.subplot(333)
        ax.set_ylabel("Inclination (deg)")
        ax.set_title('starting value = ' + str(np.degrees(orbitalElements[0][ii].inc)))
        plt.plot(timeAxis, np.degrees(np.array([x[ii].inc for x in orbitalElements[:]])))

        ax = plt.subplot(334)
        ax.set_ylabel("Omega (deg)")
        ax.set_title('starting value = ' + str(np.degrees(orbitalElements[0][ii].Omega)))
        plt.plot(timeAxis, np.degrees(np.array([x[ii].Omega for x in orbitalElements[:]])))

        ax = plt.subplot(335)
        ax.set_ylabel("omega (deg)")
        ax.set_title('starting value = ' + str(np.degrees(orbitalElements[0][ii].omega)))
        plt.plot(timeAxis, np.degrees(np.array([x[ii].omega for x in orbitalElements[:]])))

        ax = plt.subplot(336)
        ax.set_ylabel("f (deg)")
        ax.set_title('starting value = ' + str(np.degrees(orbitalElements[0][ii].f)))
        plt.plot(timeAxis, np.degrees(np.array([x[ii].f for x in orbitalElements[:]])))

        ax = plt.subplot(337)
        ax.set_ylabel("semi-major axis (AU)")
        ax.set_xlabel(timeAxisLabel)
        ax.set_title('starting value = ' + str(orbitalElements[0][ii].a/AU2M/lengthScale))
        plt.plot(timeAxis, np.array([x[ii].a for x in orbitalElements[:]])/AU2M/lengthScale)

        ax = plt.subplot(338)
        ax.set_ylabel("theta (deg)")
        ax.set_xlabel(timeAxisLabel)
        ax.set_title('starting value = ' + str(np.degrees(orbitalElements[0][ii].theta)))
        plt.plot(timeAxis, np.degrees(np.array([x[ii].theta for x in orbitalElements[:]])))

        ax = plt.subplot(339)
        ax.set_ylabel("lambda (deg)")
        ax.set_xlabel(timeAxisLabel)
        ax.set_title('starting value = ' + str(np.degrees(orbitalElements[0][ii].l)))
        plt.plot(timeAxis, np.degrees(np.array([x[ii].l for x in orbitalElements[:]])))

        plt.plot()

    # Optional advanced plots (kept disabled by default)
    if (plotResonantAngles == 1):
        pass
    if (plotMutualInclinations == 1):
        pass
    if (plotKozaiElements == 1):
        pass
    if (plotPeriodRatios == 1):
        pass


def ConvertOrbitsToReboundSim(mass, orbits):
    '''
    Functionality:
        Build a REBOUND Simulation from arrays of masses and Keplerian elements.
        Assumes elements are given per-orbit as [P, e, inc_deg, Omega_deg, omega_deg, T_peri].

    Arguments:
        mass (array-like): Body masses [kg] of length N (first is central mass).
        orbits (array-like): List/array of length N-1; each item is a 6-list
            [period_s, e, inc_deg, Omega_deg, omega_deg, T_peri_s].

    Returns:
        rebound.Simulation: Simulation with units ('s','m','kg'), central body
        added first, followed by N-1 orbiters initialized from those elements.
    '''
    if rebound is None:
        raise ImportError("rebound is required for ConvertOrbitsToReboundSim")

    sim = rebound.Simulation()
    sim.units = ('s', 'm', 'kg')
    N = len(orbits)

    period = []
    for ii in range(N):
        period.append(orbits[ii][0])

    a = PeriodToSemiMajorAxis(mass, period)

    sim.add(m=mass[0])
    for ii in range(1, N + 1):
        sim.add(
            m=mass[ii],
            a=a[ii - 1],
            e=orbits[ii - 1][1],
            inc=np.radians(orbits[ii - 1][2]),
            Omega=np.radians(orbits[ii - 1][3]),
            omega=np.radians(orbits[ii - 1][4]),
            T=orbits[ii - 1][5],
        )
    return sim
    
    
def PeriodToSemiMajorAxis(mass, P):
    '''
    Functionality:
        Convert orbital periods to semi-major axes using Kepler’s third law with
        cumulative central mass for each successive body.

    Arguments:
        mass (array-like): Masses [kg] of all bodies (length N).
        P (array-like): Periods [s] for bodies 1..N-1 (length N-1).

    Returns:
        numpy.ndarray: Semi-major axes [m] for bodies 1..N-1 (length N-1).
    '''
    N = len(mass)
    a = np.array(P, dtype=float) * 0.0
    for ii in range(0, N - 1):
        a[ii] = (P[ii]**2 * G_Nm2pkg2 * np.sum(mass[0:ii + 2]) / (4. * np.pi**2))**(1. / 3.)
    return a


def SemiMajorAxisToPeriod(mass, a):
    '''
    Functionality:
        Convert semi-major axes to periods using Kepler’s third law with
        cumulative central mass for each successive body.

    Arguments:
        mass (array-like): Masses [kg] of all bodies (length N).
        a (array-like): Semi-major axes [m] for bodies 1..N-1 (length N-1).

    Returns:
        numpy.ndarray: Periods [s] for bodies 1..N-1 (length N-1).
    '''
    N = len(mass)
    P = np.array(a, dtype=float) * 0.0
    for ii in range(0, N - 1):
        P[ii] = (a[ii]**3 * 4. * np.pi**2 / (G_Nm2pkg2 * np.sum(mass[0:ii + 2])))**0.5
    return P


def Search_CalcTransitSigma(flux, time, timeMin, timeMax):
    '''
    Functionality:
        Compute a rough “detection sigma” for a transit within a time window by
        comparing the mean flux in the window to the global standard deviation.

    Arguments:
        flux (array-like): Flux time series (arbitrary units).
        time (array-like): Time stamps [s] aligned with `flux`.
        timeMin (float): Window start [days, in BJD-55000].
        timeMax (float): Window end [days, in BJD-55000].

    Returns:
        (float, numpy.ndarray, numpy.ndarray):
            sigma: |mean(window_flux)| / std(global_flux).
            timeCut: Times within the window [s].
            fluxCut: Flux within the window (mean-subtracted).
    '''
    timeMin2 = timeMin * days2sec + 55000 * days2sec
    timeMax2 = timeMax * days2sec + 55000 * days2sec

    flux = flux - np.mean(flux)
    sel = (time > timeMin2) & (time < timeMax2)
    fluxCut = flux[sel]
    timeCut = time[sel]
    standardDeviation = np.std(flux)
    sigma = np.abs(np.mean(fluxCut) / standardDeviation) if len(fluxCut) else 0.0

    fig = plt.figure()
    ax = fig.add_subplot(111)
    if len(timeCut):
        ax.scatter(timeCut / days2sec - 55000, fluxCut)
    ax.plot([timeMin, timeMax], [np.mean(flux), np.mean(flux)])
    ax.set_xlim([timeMin, timeMax])
    if len(fluxCut):
        ax.set_ylim([np.min(fluxCut), np.max(fluxCut)])

    return sigma, timeCut, fluxCut


def Search_WholeLightCurveDetectionSigma(time, flux, TTarray, TDarray, transitDurationAllowance, minimaType):
    '''
    Functionality:
        Estimate a whole-light-curve detection significance by aggregating flux
        in windows around predicted transit mid-times and comparing to global
        noise. Also returns per-transit statistics.

    Arguments:
        time (array-like): Time stamps [s].
        flux (array-like): Flux series aligned with `time`.
        TTarray (array-like): Transit mid-times [s] for each expected transit.
        TDarray (array-like): Transit durations [s] for each expected transit.
        transitDurationAllowance (float): Scale factor for the duration window.
        minimaType (int): Baseline choice (4: global mean; 5: local mean; 6: OOT mean).

    Returns:
        (float, float, float, numpy.ndarray, numpy.ndarray):
            detectionSigma: |mean(all windows)| / std(global flux).
            detectionConsistency: Placeholder consistency metric (0.5 as used).
            meanAllWindowFlux: Mean flux across all collected windows.
            individualTransitMeanFluxArray: Mean flux per transit window.
            individualTransitSigmaArray: |mean(window)| / std(global flux) per transit.
    '''
    numTransits = len(TTarray)
    individualTransitMeanFluxArray = []
    hittingAGapCount = 0
    totalWindowFlux = np.array([])
    totalWindowTime = np.array([])

    meanGlobal = np.mean(flux)
    standardDeviation = np.std(flux) if np.std(flux) > 0 else 1.0

    for ii in range(0, len(TTarray)):
        modifiedTD = TDarray[ii] * transitDurationAllowance
        tempTime, tempFlux, meanUsed = Search_IndividualTransitRelativeFlux(
            time, flux, TTarray[ii], modifiedTD, minimaType, meanGlobal, cadence=1.0
        )[:3]
        if (len(tempFlux) > 0):
            individualTransitMeanFluxArray.append(np.mean(tempFlux))
            totalWindowFlux = np.append(totalWindowFlux, tempFlux)
            totalWindowTime = np.append(totalWindowTime, tempTime)
        else:
            hittingAGapCount += 1
            individualTransitMeanFluxArray.append(0)

    transitIndex = np.linspace(0, len(individualTransitMeanFluxArray) - 1, len(individualTransitMeanFluxArray))
    individualTransitMeanFluxArray = np.array(individualTransitMeanFluxArray)
    individualTransitSigmaArray = np.abs(individualTransitMeanFluxArray / standardDeviation)

    detectionSigma = np.abs(np.mean(totalWindowFlux) / standardDeviation) if len(totalWindowFlux) else 0.0
    detectionConsistency = 0.5

    return detectionSigma, detectionConsistency, (np.mean(totalWindowFlux) if len(totalWindowFlux) else 0.0), individualTransitMeanFluxArray, individualTransitSigmaArray


def Search_IndividualTransitRelativeFlux(time, flux, TT, TD, minimaType, meanGlobal, cadence):
    '''
    Functionality:
        Slide a window of width TD over the local light curve to find the
        lowest-mean-flux segment (candidate transit), then measure flux relative
        to a chosen baseline (global/local/out-of-transit).

    Arguments:
        time (array-like): Time stamps [s] (full light curve or pre-cut window).
        flux (array-like): Flux aligned with `time`.
        TT (float): Reference time (not strictly used for pre-cut; kept for API).
        TD (float): Transit duration [s]; defines window width.
        minimaType (int): 4: global mean; 5: local mean; 6: mean of OOT samples.
        meanGlobal (float): Global mean flux (used when minimaType==4).
        cadence (float): Approx. sampling cadence [s] (used for sizing, here only in comments).

    Returns:
        (numpy.ndarray, numpy.ndarray, float, numpy.ndarray, numpy.ndarray, float):
            individualTransitTime: Time samples within the chosen window.
            individualTransitFlux: Flux within that window minus chosen baseline.
            meanUsed: Baseline value actually used.
            outOfTransitTime: Times outside selected window (for minimaType==6).
            outOfTransitFlux: Flux outside selected window (for minimaType==6).
            ratioInOutTransitPoints: N_in / N_out if minimaType==6 else sentinel.
    '''
    meanUsed = -27
    standardDeviation = np.std(flux) if np.std(flux) > 0 else 1.0

    timeCut = time
    fluxCut = flux
    outOfTransitTime = np.array([])
    outOfTransitFlux = np.array([])
    ratioInOutTransitPoints = -27

    # Number of indices in a TD-wide window (cadence guard)
    if cadence is None or not np.isfinite(cadence) or cadence <= 0:
        # fallback to median spacing
        if len(time) > 1:
            cadence = float(np.median(np.diff(time)))
        else:
            cadence = TD
    transitWindowLength = max(1, int(round(TD / (.98 * cadence))))

    if len(timeCut) > transitWindowLength:
        # rolling window means (advance in index by 1)
        fullIndex = np.arange(len(timeCut))
        rollingWindowMeanFlux = []
        for jj in range(0, len(timeCut)):
            # window by time, not by fixed index count (original behavior)
            temp_index = fullIndex[(timeCut >= timeCut[jj]) & (timeCut <= timeCut[jj] + TD)]
            if len(temp_index) == 0:
                rollingWindowMeanFlux.append(np.inf)
                continue
            temp = fluxCut[temp_index]
            temp = temp[np.isfinite(temp)]
            rollingWindowMeanFlux.append(np.mean(temp))
            if temp_index[-1] == fullIndex[-1]:
                break

        rollingWindowMeanFlux = np.array(rollingWindowMeanFlux)
        if not len(rollingWindowMeanFlux[np.isfinite(rollingWindowMeanFlux)]):
            return np.array([]), np.array([]), meanUsed, outOfTransitTime, outOfTransitFlux, ratioInOutTransitPoints

        windowWithLowestMeanFlux = np.nanargmin(rollingWindowMeanFlux)
        sel = (timeCut >= timeCut[windowWithLowestMeanFlux]) & (timeCut <= timeCut[windowWithLowestMeanFlux] + TD)
        window_idx = np.where(sel)[0]
        individualTransitTime = timeCut[window_idx]

        if minimaType == 4:
            meanUsed = meanGlobal
            individualTransitFlux = fluxCut[window_idx] - meanGlobal
        elif minimaType == 5:
            meanLocal = np.mean(fluxCut)
            meanUsed = meanLocal
            individualTransitFlux = fluxCut[window_idx] - meanLocal
        elif minimaType == 6:
            remaining_idx = np.setdiff1d(np.arange(len(fluxCut)), window_idx, assume_unique=False)
            outOfTransitTime = time[remaining_idx.astype(int)]
            outOfTransitFlux = flux[remaining_idx.astype(int)]
            meanRemaining = np.mean(outOfTransitFlux) if len(outOfTransitFlux) else 1.0
            meanUsed = meanRemaining
            individualTransitFlux = fluxCut[window_idx] - meanRemaining
            ratioInOutTransitPoints = (len(individualTransitFlux) / len(remaining_idx)) if len(remaining_idx) else 99999.0
        else:
            # default to global mean
            meanUsed = meanGlobal
            individualTransitFlux = fluxCut[window_idx] - meanGlobal
    else:
        individualTransitFlux = np.array([])
        individualTransitTime = np.array([])

    return individualTransitTime, individualTransitFlux, meanUsed, outOfTransitTime, outOfTransitFlux, ratioInOutTransitPoints


def Search_DeepestTransitFinder(systemName, systemType, transitDuration, minimaType, numBestTransits):
    '''
    Functionality:
        Load a system’s time/flux arrays and find the N deepest unique transit
        events by scanning the full light curve and ranking per-event
        significance.

    Arguments:
        systemName (str): Identifier passed to RealSystemLibrary.
        systemType (str): Dataset/type selector for RealSystemLibrary.
        transitDuration (float): Transit window width [seconds] per trial.
        minimaType (int): Baseline mode passed to the per-transit metric.
        numBestTransits (int): Number of top events to return.

    Returns:
        (numpy.ndarray, numpy.ndarray):
            array_of_transitTimes: Mid-times [s] (BJD) of the selected events.
            array_of_sigma: Corresponding significance metric for each event.
    '''
    # Load in the time and flux array for a given systemName
    simTT_init, Pbin, timeOrig, fluxOrig, phaseOrig, timeCut, fluxCut, phaseCut, bjd0, pwidth, swidth, sep, metallicity, flux_ratio = RealSystemLibrary(systemName, systemType)
    fluxCut = np.array(fluxCut)
    timeCut = np.array(timeCut) * days2sec

    array_of_transitTimes, array_of_sigma = Search_DeepestTransitFinder2(
        timeCut, fluxCut, transitDuration, minimaType, numBestTransits
    )
    return array_of_transitTimes, array_of_sigma


def Search_DeepestTransitFinder2(timeArray, fluxArray, transitDuration, minimaType, numBestTransits):
    '''
    Functionality:
        Slide a fixed-duration window across the entire light curve, compute a
        per-window “depth/sigma” metric, and select the top-N deepest unique
        events, enforcing a minimum temporal separation.

    Arguments:
        timeArray (array-like): Time stamps [s].
        fluxArray (array-like): Flux values aligned with `timeArray`.
        transitDuration (float): Window width [s] for each trial segment.
        minimaType (int): Baseline mode used by Search_IndividualTransitRelativeFlux.
        numBestTransits (int): Number of best unique events to pick.

    Returns:
        (list, list):
            array_of_transitTimes: List of selected transit mid-times [s].
            array_of_sigma: List of corresponding per-event metrics.
    '''
    sigmaList = []
    transitTimeList = []
    simCount = 0
    numTimeSteps = len(timeArray)
    startTime = TIME.time()

    # Precompute global mean and cadence estimate for the call below
    meanGlobal = float(np.mean(fluxArray)) if len(fluxArray) else 0.0
    cadence_est = float(np.median(np.diff(timeArray))) if len(timeArray) > 1 else transitDuration

    # Loop through every time step (coarse search)
    for ii in range(0, numTimeSteps):
        t0 = timeArray[ii]
        # Use the updated signature (with meanGlobal & cadence)
        it_time, it_flux, meanUsed, oot_t, oot_f, ratio = Search_IndividualTransitRelativeFlux(
            timeArray, fluxArray, t0, transitDuration, minimaType, meanGlobal, cadence_est
        )
        # metric = |mean(window)| / std(global)
        std_glob = np.std(fluxArray) if np.std(fluxArray) > 0 else 1.0
        sigma_val = (abs(np.mean(it_flux)) / std_glob) if len(it_flux) else 0.0
        sigmaList.append(sigma_val)
        # store the mid time of the window we just evaluated (here: center on t0 + TD/2 for consistency)
        transitTimeList.append(t0 + 0.5 * transitDuration)

        # Progress bar (rough ETA)
        simCount += 1
        percentageComplete = 100. * (simCount + 1) / (numTimeSteps if numTimeSteps else 1)
        elapsedTime = TIME.time() - startTime
        totalTime = elapsedTime / (percentageComplete / 100.) if percentageComplete > 0 else 0
        remainingTime = totalTime - elapsedTime

        if (remainingTime < 60):
            sys.stdout.write("Remaining time (sec): %.2f, %d%% completed   \r" % (remainingTime, percentageComplete))
        elif (remainingTime < 3600):
            sys.stdout.write("Remaining time (min): %.2f, %d%% completed   \r" % (remainingTime / 60., percentageComplete))
        elif (remainingTime < 86400):
            sys.stdout.write("Remaining time (hrs): %.2f, %d%% completed   \r" % (remainingTime / 3600., percentageComplete))
        else:
            sys.stdout.write("Remaining time (days): %.2f, %d%% completed   \r" % (remainingTime / 86400., percentageComplete))
        sys.stdout.flush()

    # Convert to array and sanitize NaNs
    sigmaListCut = np.array(sigmaList)
    sigmaListCut[np.isnan(sigmaListCut)] = 0

    # Find the best N transits, enforcing uniqueness via a time-exclusion window
    tempSigmaList = np.copy(sigmaListCut)
    nextTransitInterval = 2 * days2sec  # enforce >~1-day uniqueness on either side
    array_of_sigmaIndex = []
    array_of_sigma = []
    array_of_transitTimes = []

    for ii in range(0, numBestTransits):
        if not len(tempSigmaList):
            break
        array_of_sigma.append(np.max(tempSigmaList))
        idx = int(np.argmax(tempSigmaList))
        array_of_sigmaIndex.append(idx)
        array_of_transitTimes.append(transitTimeList[idx])
        print('Best transit #' + str(ii) +
              ' has sigma = ' + str(array_of_sigma[ii]) +
              ' at transit time = ' + str(array_of_transitTimes[ii] / days2sec - 55000) +
              ', index = ' + str(idx))

        # Remove nearby solutions within the exclusion window
        sel = (timeArray < array_of_transitTimes[ii] + nextTransitInterval / 2) & \
              (timeArray > array_of_transitTimes[ii] - nextTransitInterval / 2)
        tempSigmaList[sel] = -27

    # Quick diagnostic plot: entire light curve + highlighted best windows
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    if len(timeArray):
        ax.scatter(timeArray / days2sec - 55000, fluxArray, color='b')
        ax.set_xlabel('Time (BJD-55000)')
        ax.set_ylabel('Detrended flux with eclipses')
        for ii in range(0, len(array_of_transitTimes)):
            t_sel = (timeArray > array_of_transitTimes[ii] - transitDuration / 2) & \
                    (timeArray < array_of_transitTimes[ii] + transitDuration / 2)
            ax.scatter(timeArray[t_sel] / days2sec - 55000, fluxArray[t_sel], color='r')

    # No explicit return in original; keeping compatibility.
    # If you want explicit returns:
    # return array_of_transitTimes, array_of_sigma


def MassRadiusTemperatureRelation(mass, radius):
    '''
    Functionality:
        Estimate stellar effective temperature from mass and radius by first
        computing luminosity via Eker et al. (2015) relations and then applying
        the Stefan–Boltzmann scaling.

    Arguments:
        mass (float): Stellar mass [kg].
        radius (float): Stellar radius [m].

    Returns:
        float: Effective temperature [K].
    '''
    # You input the mass and radius; luminosity via Eker+2015 -> Teff via σT^4
    L = MassRadiusLuminosityRelation(mass, radius)  # solar luminosity
    Teff = 5777 * (L / (radius / rSun_m)**2.)**(1. / 4.)
    return Teff  # Kelvin


def MassRadiusLuminosityRelation(mass, radius):
    '''
    Functionality:
        Compute stellar luminosity (in solar units) from mass and radius using
        piecewise fits from Eker et al. (2015).

    Arguments:
        mass (float): Stellar mass [kg].
        radius (float): Stellar radius [m]. (Unused in the current fit, kept for API.)

    Returns:
        float: Luminosity in units of L_sun.
    '''
    # Piecewise mass–luminosity relation per Eker+2015
    M = mass / mSun_kg
    R = radius / rSun_m  # not used in the formulae below, retained for API symmetry

    if (M <= 1.05):  # lower limit ~0.38 Msun
        log10L = 4.841 * np.log10(M) - 0.026
    elif (M <= 2.4):
        log10L = 4.328 * np.log10(M) - 0.002
    elif (M <= 7):
        log10L = 3.962 * np.log10(M) + 0.120
    elif (M < 32):
        log10L = 2.726 * np.log10(M) + 1.237
    else:
        log10L = 2.726 * np.log10(M) + 1.237  # extrapolate last branch

    L = 10**log10L
    return L  # solar luminosity


def CalculateTransitDuration(reboundSim, timeFinal, detrendingPlanetPeriod=-27):
    '''
    Functionality:
        Estimate a representative planet transit duration across the light curve
        span by integrating a copy of the REBOUND simulation and computing both
        an analytic (Kostov-style) and a numerical (velocity-based) duration at
        discrete epochs. Returns the numerical duration series and times.

    Arguments:
        reboundSim (rebound.Simulation): Initialized system (binary + planet optional).
        timeFinal (array-like): Observation time span [s]; only first/last used.
        detrendingPlanetPeriod (float): Planet period [s] for duration model.
            If -27, adopt P_p = 6.27 * P_bin.

    Returns:
        (numpy.ndarray, numpy.ndarray):
            duration_array_numerical: Estimated transit durations [s] at sampled times.
            time_array: Sample times [s] corresponding to each duration estimate.
    '''
    if rebound is None:
        raise ImportError("rebound is required for CalculateTransitDuration")

    tempSim = reboundSim.copy()

    timeStart = timeFinal[0]
    timeEnd = timeFinal[-1]

    # Get the orbital elements
    mA = tempSim.particles[0].m
    mB = tempSim.particles[1].m
    rA = tempSim.particles[0].r
    rB = tempSim.particles[1].r
    rp = 5 * rEarth_m
    orbits = tempSim.orbits()
    Pbin = orbits[0].P
    abin = orbits[0].a
    ebin = orbits[0].e
    omegabin = orbits[0].omega

    # Get the planet parameters
    if (detrendingPlanetPeriod == -27):
        Pp = Pbin * 6.27  # default period ratio
    else:
        Pp = detrendingPlanetPeriod
    # Planet semi-major axis
    ap = (Pp**2. * G_Nm2pkg2 * (mA + mB) / (4 * np.pi**2.))**(1. / 3.)

    # Constants for the analytic (Kostov) duration estimate
    fm = mB**3. / (mA + mB)**2.
    A = 1. / (mA + mB)**(1. / 3.)
    B = 2 * rA * (Pp / (2 * np.pi * G_Nm2pkg2))**(1. / 3.)
    C = -1 * fm**(1. / 3.) * (Pp / Pbin)**(1. / 3.) * 1. / (1 - ebin**2.)**0.5

    # Sample at every 1/50 of the binary period for speed
    timeStep = Pbin / 50

    time_array = np.array([])
    f_array = np.array([])
    theta_array = np.array([])
    M_array = np.array([])
    l_array = np.array([])
    duration_array_kostov = np.array([])
    duration_array_numerical = np.array([])
    vxstar_array = np.array([])
    vxplanet_array = np.array([])

    # Integrate and compute durations
    while tempSim.t < timeEnd:
        tempSim.integrate(tempSim.t + timeStep)
        orbits = tempSim.orbits()

        # Time and orbital phases
        time_array = np.append(time_array, tempSim.t)
        f_array = np.append(f_array, orbits[0].f)
        theta_array = np.append(theta_array, orbits[0].theta)
        M_array = np.append(M_array, orbits[0].M)
        l_array = np.append(l_array, orbits[0].l)

        # Analytic duration (Kostov-style; diagnostic)
        x = (ebin * np.sin(omegabin) + np.sin(theta_array[-1] + omegabin))
        duration_kostov = A * B / (1 + A * C * x)
        duration_array_kostov = np.append(duration_array_kostov, duration_kostov)

        # Numerical duration from relative velocity (preferred)
        vxstar = tempSim.particles[0].vx
        vxstar_array = np.append(vxstar_array, vxstar)
        vxplanet = -2 * np.pi * ap / Pp
        vxplanet_array = np.append(vxplanet_array, vxplanet)
        duration_numerical = np.min([np.abs(2 * (rA + rp) / (vxplanet - vxstar)), 0.5 * Pbin])
        duration_array_numerical = np.append(duration_array_numerical, duration_numerical)

    # Optional diagnostic plots (kept True to preserve original behavior)
    do_plotting = True
    if (do_plotting == True):
        fig = plt.figure()

        ax = fig.add_subplot(331)
        ax.plot(time_array / days2sec - 55000, np.degrees(f_array))
        ax.set_ylabel('f (deg)')
        ax.set_xlabel('time (days - 55000)')

        ax = fig.add_subplot(332)
        ax.plot(time_array / days2sec - 55000, np.degrees(theta_array))
        ax.set_ylabel('theta (deg)')
        ax.set_xlabel('time (days - 55000)')

        ax = fig.add_subplot(333)
        ax.plot(time_array / days2sec - 55000, np.degrees(M_array))
        ax.set_ylabel('M (deg)')
        ax.set_xlabel('time (days - 55000)')

        ax = fig.add_subplot(334)
        ax.plot(time_array / days2sec - 55000, np.degrees(l_array))
        ax.set_ylabel('l (deg)')
        ax.set_xlabel('time (days - 55000)')

        ax = fig.add_subplot(335)
        ax.plot(time_array / days2sec - 55000, duration_array_kostov / hours2sec)
        ax.set_ylabel('Transit duration (Kostov, hours)')
        ax.set_xlabel('time (days - 55000)')

        ax = fig.add_subplot(336)
        ax.plot(time_array / days2sec - 55000, duration_array_numerical / hours2sec)
        ax.set_ylabel('Transit duration (numerical, hours)')
        ax.set_xlabel('time (days - 55000)')

        ax = fig.add_subplot(337)
        ax.plot(time_array / days2sec - 55000, vxstar_array)
        ax.plot(time_array / days2sec - 55000, vxplanet_array)
        ax.set_ylabel('vx_star')
        ax.set_xlabel('time (days - 55000)')

    return duration_array_numerical, time_array


def CalculatePeriodThetaSearchGrid(
    mA, mB, RA, RB, Pbin, ebin,
    method='adaptive period',
    durationFactor_thetap=3,
    durationFactor_P=3,
    minValue=2.2,
    maxValue=4.1,
    boundsType="stability limit ratio",
    length_of_data=None
):
    '''
    Functionality:
        Build a joint grid over trial orbital period (P) and planet phase angle (θ_p)
        for a circumbinary search. Period bounds are set either by multiples of the
        binary apoapse (“stability limit ratio”) or by explicit time ranges. The θ_p
        grid spacing is tied to the minimum expected transit duration to avoid
        oversampling ingress/egress beyond necessity. Returns a list of [P, θ_p-grid]
        pairs for downstream searches.

    Arguments:
        mA (float): Primary star mass [kg].
        mB (float): Secondary star mass [kg].
        RA (float): Primary star radius [m].
        RB (float): Secondary star radius [m]. (Unused in current spacing; kept for API.)
        Pbin (float): Binary period [s].
        ebin (float): Binary eccentricity.
        method (str): 'adaptive period' (flat θ_p grid at each P)
                      or 'adaptive period theta' (θ_p grid adapts with P).
        durationFactor_thetap (float): Multiplier for θ_p-step ~ (duration / P).
        durationFactor_P (float): Multiplier for ΔP from window overlap condition.
        minValue (float): Lower bound spec (meaning depends on boundsType).
        maxValue (float): Upper bound spec (meaning depends on boundsType).
        boundsType (str): One of:
            - "stability limit ratio to stability limit ratio"
            - "stability limit ratio to years"
            - "years to years"
            - "days to days"
        length_of_data (float or None): Total baseline length [s]. If None, assume
            Kepler-like 4 years in ΔP calculation.

    Returns:
        list[[float, numpy.ndarray]]: A list of entries [P_value, grid_thetap_at_P],
            where P_value is in seconds and grid_thetap_at_P is a 1-D array of θ_p
            values in radians spanning [0, 2π].
    '''
    abin = PeriodToSemiMajorAxis([mA, mB], [Pbin])[0]
    print('abin (AU) = ' + str(abin / au2m))
    aA = mB / (mA + mB) * abin
    aB = mA / (mA + mB) * abin

    if (boundsType == "stability limit ratio to stability limit ratio"):
        a_min = minValue * abin * (1 + ebin)
        a_max = maxValue * abin * (1 + ebin)
        P_min = SemiMajorAxisToPeriod([mA, mB], [a_min])[0]
        P_max = SemiMajorAxisToPeriod([mA, mB], [a_max])[0]
    elif (boundsType == "stability limit ratio to years"):
        a_min = minValue * abin * (1 + ebin)
        P_min = SemiMajorAxisToPeriod([mA, mB], [a_min])[0]
        P_max = maxValue * years2sec
        a_max = PeriodToSemiMajorAxis([mA, mB], [P_max])[0]
    elif (boundsType == "years to years"):
        P_min = minValue * years2sec
        a_min = PeriodToSemiMajorAxis([mA, mB], [P_min])[0]
        P_max = maxValue * years2sec
        a_max = PeriodToSemiMajorAxis([mA, mB], [P_max])[0]
    elif (boundsType == "days to days"):
        P_min = minValue * days2sec
        a_min = PeriodToSemiMajorAxis([mA, mB], [P_min])[0]
        P_max = maxValue * days2sec
        a_max = PeriodToSemiMajorAxis([mA, mB], [P_max])[0]
    else:
        # fallback to stability ratio bounds
        a_min = minValue * abin * (1 + ebin)
        a_max = maxValue * abin * (1 + ebin)
        P_min = SemiMajorAxisToPeriod([mA, mB], [a_min])[0]
        P_max = SemiMajorAxisToPeriod([mA, mB], [a_max])[0]

    print('P_min (days) = ' + str(P_min / days2sec))
    print('P_max (days) = ' + str(P_max / days2sec))

    VA = 2 * np.pi * aA / Pbin  # primary star orbital speed (circular approx)

    # Characteristic minimum transit duration at the extrema
    Vp_max = 2 * np.pi * a_min / P_min
    Vp_max_new = 2 * np.pi * a_max / P_max
    transit_duration_min = 2 * RA / (Vp_max + VA)
    transit_duration_min_new = 2 * RA / (Vp_max_new + VA)

    # Joint grid container
    grid_periodANDtheta = []

    # Prepare θ_p stepping for 'adaptive period'
    if (method == 'adaptive period'):
        delta_thetap_orig = np.radians(360. * durationFactor_thetap * transit_duration_min / P_min)
        delta_thetap_new = np.radians(360. * durationFactor_thetap * transit_duration_min_new / P_max)
        print("delta_thetap_orig = %f deg" % (np.rad2deg(delta_thetap_orig)))
        print("delta_thetap_new  = %f deg" % (np.rad2deg(delta_thetap_new)))
        delta_thetap = max(delta_thetap_new, 1e-6)
        thetap_steps = int(2 * np.pi / delta_thetap + 1)
        base_thetap = np.linspace(0, 2 * np.pi, thetap_steps)

    grid_thetap = []  # will append per-P θ_p grids

    # Variable-ΔP loop
    P_value = P_min
    grid_P_variableWindowDeltaP = []
    delta_P_array = []
    targetWindow_variable_array = []
    while (P_value < P_max):
        # Compute a window tied to transit-duration at this P
        ap = (P_value**2. * G_Nm2pkg2 * (mA + mB) / (4 * np.pi**2.))**(1. / 3.)
        Vp = 2 * np.pi * ap / P_value
        transit_duration = 2 * RA / (Vp + VA)
        targetWindow_variable_value = durationFactor_P * transit_duration

        # ΔP such that cumulative period drift across the baseline ~ window
        if length_of_data is None:
            delta_P_value = P_value * 2 * targetWindow_variable_value / (4 * years2sec)
        else:
            delta_P_value = P_value * 2 * targetWindow_variable_value / (length_of_data)

        P_value = P_value + delta_P_value
        grid_P_variableWindowDeltaP.append(P_value)
        delta_P_array.append(delta_P_value)
        targetWindow_variable_array.append(targetWindow_variable_value)

        if (method == 'adaptive period'):
            grid_thetap.append(base_thetap)
        if (method == 'adaptive period theta'):
            Vp_max_adaptive = 2 * np.pi * ap / P_value
            transit_duration_min_adaptive = 2 * RA / (Vp_max_adaptive + VA)
            delta_thetap_adaptive = max(np.radians(360. * durationFactor_thetap * transit_duration_min_adaptive / P_value), 1e-6)
            thetap_steps_adaptive = int(2 * np.pi / delta_thetap_adaptive + 1)
            grid_thetap.append(np.linspace(0, 2 * np.pi, thetap_steps_adaptive))

        grid_periodANDtheta.append([P_value, grid_thetap[-1]])

    # Keep list-of-lists to preserve variable sizes
    return grid_periodANDtheta


def CalculateEccentricityOmegaSearchGrid(e_max=0.2, delta_e=0.05, density_circle=1):
    '''
    Functionality:
        Build a polar grid in (e, ω) space for eccentricity and argument of
        pericenter. The number of ω samples on each concentric circle increases
        with circumference to maintain roughly uniform angular density.

    Arguments:
        e_max (float): Maximum eccentricity to include (inclusive).
        delta_e (float): Radial increment in eccentricity.
        density_circle (float): Angular sampling density factor relative to delta_e.

    Returns:
        list[[float, numpy.ndarray]]:
            A list of [e_value, omega_array], where omega_array spans [0, 2π)
            with ~density_circle * (2πe / delta_e) samples for each e>0, and a
            single ω=0 sample at e=0.
    '''
    grid_e = np.linspace(0, e_max, int(e_max / delta_e + 1))
    grid_omega = [np.array([0])]
    for ii in range(1, len(grid_e)):
        circumference = 2 * np.pi * grid_e[ii]
        numPointsOnCircle = max(1, int(density_circle * circumference / delta_e))
        grid_omega.append(np.linspace(0, 2 * np.pi, numPointsOnCircle, endpoint=False))

    grid_eccANDomega = []
    for ii in range(0, len(grid_e)):
        grid_eccANDomega.append([grid_e[ii], grid_omega[ii]])
    return grid_eccANDomega


def DoPeriodogram(
    timeArray, fluxArray, duration_array, figPeriodograms,
    returnOptimalWindowLength, transitDurationPercentage, transitDurationMultiplier,
    filenameText, SystemName, DetrendingName, mission, ID, subplotCounter,
    *, base_dir=None  # added: base-dir aware file output
):
    '''
    Functionality:
        Compute a Lomb–Scargle periodogram of the (optionally sigma-clipped) light
        curve, annotate it with reference transit-duration landmarks (min/50/75/max),
        overlay false-alarm probability (FAP) levels, and optionally choose a
        cosine-filter window length for detrending based on the measured FAP and a
        user-selected duration percentile.

    Arguments:
        timeArray (array-like): Time stamps [s].
        fluxArray (array-like): Flux values aligned with `timeArray`.
        duration_array (array-like): Array of transit-duration estimates [s].
        figPeriodograms (matplotlib.figure.Figure): Figure to plot into.
        returnOptimalWindowLength (bool): If True, return window suggestion and stats.
        transitDurationPercentage (str): One of {'max','75','50'} used when
            `returnOptimalWindowLength` is True to pick a reference duration.
        transitDurationMultiplier (float): Multiplier applied to the chosen reference duration.
        filenameText (str): Title/label mode, e.g. 'progressive' or 'final'.
        SystemName (str): System identifier (unused in plotting; kept for API).
        DetrendingName (str): Label for output paths/diagnostics.
        mission (str): Mission name string for stats output.
        ID (str or int): Target identifier for stats output.
        subplotCounter (int): Index for subplot placement.
        base_dir (Path-like or None): Root directory for outputs (cluster/local/pip).

    Returns:
        If returnOptimalWindowLength is True:
            (float, float, float): (cosineFilterWindowLength [s], FAP@1%, maxPower)
        Else:
            (float, float): (FAP@1%, maxPower)
    '''
    from astropy.timeseries import LombScargle

    # Guard duration array
    if len(duration_array) == 0:
        duration_array = np.array([1.0])

    duration_min = float(np.min(duration_array))
    duration_max = float(np.max(duration_array))
    duration_50 = -27
    duration_66 = -27
    duration_75 = -27
    duration_95 = -27
    duration_99 = -27

    # Percentile-like scanning (simple)
    grid = np.linspace(duration_min, duration_max, 10000)
    n = len(duration_array)
    for duration_test in grid:
        frac = float(np.sum(duration_array < duration_test)) / n
        if (frac > 0.50 and duration_50 == -27): duration_50 = duration_test
        if (frac > 0.66 and duration_66 == -27): duration_66 = duration_test
        if (frac > 0.75 and duration_75 == -27): duration_75 = duration_test
        if (frac > 0.95 and duration_95 == -27): duration_95 = duration_test
        if (frac > 0.99 and duration_99 == -27): duration_99 = duration_test

    # Sigma-clip (3σ) for the periodogram input
    fluxMedian = np.median(fluxArray) if len(fluxArray) else 0.0
    fluxSTD = np.std(fluxArray) if len(fluxArray) else 1.0
    indexArray = np.arange(len(timeArray))
    mask = np.abs(fluxArray - fluxMedian) > 3 * fluxSTD
    indexArrayOutliers = indexArray[mask]
    timeArrayOutliers = timeArray[mask]
    fluxArrayOutliers = fluxArray[mask]
    timeArrayClipped = np.delete(timeArray, indexArrayOutliers)
    fluxArrayClipped = np.delete(fluxArray, indexArrayOutliers)

    # Raw diagnostic plot (full vs clipped)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    if len(timeArray):
        ax.scatter(timeArray / days2sec - 55000, fluxArray, color='b', s=10)
    if len(timeArrayClipped):
        ax.scatter(timeArrayClipped / days2sec - 55000, fluxArrayClipped, color='r')
    if len(timeArrayOutliers):
        ax.scatter(timeArrayOutliers / days2sec - 55000, fluxArrayOutliers, color='g', s=5)
    ax.plot([np.min(timeArray / days2sec - 55000) if len(timeArray) else 0,
             np.max(timeArray / days2sec - 55000) if len(timeArray) else 1],
            [fluxMedian, fluxMedian], color='k', linestyle='--')
    ax.plot([np.min(timeArray / days2sec - 55000) if len(timeArray) else 0,
             np.max(timeArray / days2sec - 55000) if len(timeArray) else 1],
            [fluxMedian + 3 * fluxSTD, fluxMedian + 3 * fluxSTD], color='k', linestyle='--')
    ax.plot([np.min(timeArray / days2sec - 55000) if len(timeArray) else 0,
             np.max(timeArray / days2sec - 55000) if len(timeArray) else 1],
            [fluxMedian - 3 * fluxSTD, fluxMedian - 3 * fluxSTD], color='k', linestyle='--')
    ax.set_xlabel('time')
    ax.set_ylabel('flux')

    # Lomb–Scargle (convert time to days for frequency units)
    if len(timeArrayClipped) < 3:
        # Too few points for LS
        fap_levels = np.array([1.0, 1.0, 1.0])
        max_power = 0.0
        cosineFilterWindowLength = -27
        # Still lay down an empty subplot
        if (filenameText == 'progressive'):
            axp = figPeriodograms.add_subplot(2, 5, subplotCounter)
        else:
            axp = figPeriodograms.add_subplot(1, 3, subplotCounter)
        axp.set_title(filenameText)
        if (returnOptimalWindowLength == True):
            return cosineFilterWindowLength, fap_levels[-1], max_power
        else:
            return fap_levels[-1], max_power

    print("Checking units for lombscargle: " + str(timeArrayClipped[0]))
    ls = LombScargle(timeArrayClipped / days2sec, fluxArrayClipped)
    frequency, power = ls.autopower()
    period = 1.0 / frequency
    periodLog = np.log10(period)

    # Discard strong 30-min cadence alias (~0.5 hr)
    numMaxToFind = 5
    periodTestMin = 1.1 / 24.0  # days
    periodLogTestMin = np.log10(periodTestMin)

    mask_keep = period > periodTestMin
    frequency = frequency[mask_keep]
    power = power[mask_keep]
    periodLog = periodLog[mask_keep]
    period = period[mask_keep]

    # Local maxima for labeling top peaks
    if len(power) == 0:
        powerLocalMax = np.array([])
        periodLogLocalMax = np.array([])
        powerMax = np.array([0, 0, 0, 0, 0], dtype=float)
        periodLogMax = np.array([0, 0, 0, 0, 0], dtype=float)
    else:
        indexLocalMax = argrelextrema(power, np.greater)
        powerLocalMax = power[indexLocalMax]
        periodLogLocalMax = periodLog[indexLocalMax]
        if len(powerLocalMax) == 0:
            powerMax = np.array([np.max(power)] + [0, 0, 0, 0], dtype=float)
            periodLogMax = np.array([periodLog[np.argmax(power)]] + [0, 0, 0, 0], dtype=float)
        else:
            powerLocalMaxSortedIndex = np.argsort(powerLocalMax)[::-1]
            top = min(numMaxToFind, len(powerLocalMaxSortedIndex))
            powerMax = np.zeros(5, dtype=float)
            periodLogMax = np.zeros(5, dtype=float)
            powerMax[:top] = powerLocalMax[powerLocalMaxSortedIndex[:top]]
            periodLogMax[:top] = periodLogLocalMax[powerLocalMaxSortedIndex[:top]]

    # False-alarm probabilities
    probabilities = [0.1, 0.05, 0.01]
    fap = ls.false_alarm_level(probabilities)
    max_power = float(np.max(power)) if len(power) else 0.0

    # Optional window-length selection
    cosineFilterWindowLength = -27  # sentinel
    if (returnOptimalWindowLength == True):
        if (len(powerMax) and powerMax[0] >= fap[-1]):
            if (transitDurationPercentage == 'max'):
                ref = duration_max
            elif (transitDurationPercentage == '75'):
                ref = duration_75
            elif (transitDurationPercentage == '50'):
                ref = duration_50
            else:
                ref = duration_50
            cosineFilterWindowLength = ref * transitDurationMultiplier

    # Periodogram plot (log-period axis)
    print("---- CHECKING VERTICALMAX EMPTY ARRAYS ----")
    print("I think power is empty: " + str((power)))
    print("fap[2]: " + str(fap[2]))
    print("len power: " + str(len(power)))
    print("len fap: " + str(len(fap)))
    verticalMax = 1.1 * np.max([max_power, fap[2]])

    if (filenameText == 'progressive'):
        axp = figPeriodograms.add_subplot(2, 5, subplotCounter)
    else:
        axp = figPeriodograms.add_subplot(1, 3, subplotCounter)

    if len(periodLog):
        sel = periodLog > periodLogTestMin
        axp.plot(10**periodLog[sel], power[sel], color='red', label='Lomb Scargle (in log)')
    for val, lab in [(duration_min, 'min'), (duration_50, '50%'), (duration_75, '75%'), (duration_max, 'max')]:
        if val != -27:
            axp.plot([val / days2sec, val / days2sec], [0, verticalMax], linestyle='-', linewidth=3, label=lab)
            axp.text(val / days2sec, 1.05 * verticalMax, f'{lab} = {round(val / hours2sec, 2)}hr', fontsize=10, rotation=90)
    if (returnOptimalWindowLength == True) and (cosineFilterWindowLength != -27):
        axp.plot([cosineFilterWindowLength / days2sec, cosineFilterWindowLength / days2sec], [0, verticalMax], color='black', linewidth=3, linestyle='-')
        axp.text(cosineFilterWindowLength / days2sec, 1.05 * verticalMax, 'window = ' + str(round(cosineFilterWindowLength / hours2sec, 2)) + 'hr', fontsize=10, rotation=90)

    xLimMax = (np.max([10**np.max(periodLog) if len(periodLog) else periodTestMin,
                       duration_max / days2sec,
                       (cosineFilterWindowLength / days2sec) if cosineFilterWindowLength != -27 else duration_max / days2sec])
               * 2)
    axp.set_ylabel('Power', fontsize=14)
    axp.set_xlabel('Period (days)', fontsize=14)
    axp.set_xlim([periodTestMin, xLimMax])
    axp.set_xscale('log')
    axp.tick_params(axis='both', which='major', labelsize=12)
    if len(power):
        axp.set_ylim([0, np.max(power) + 0.2 * (np.max(power) - np.min(power))])
    axp.set_title('duration % = ' + transitDurationPercentage + ', multi. = ' + str(transitDurationMultiplier) if (filenameText == 'progressive') else filenameText)

    for ii in range(0, len(fap)):
        axp.plot([periodTestMin, 10**(np.max(periodLog) if len(periodLog) else np.log10(periodTestMin))], [fap[ii], fap[ii]], color='black', linestyle='--', linewidth=3)

    # Persist detrending stats for 'final' (base-dir aware)
    if (filenameText == 'final'):
        root = _resolve_base_dir(None)
        folder_path = root / "LightCurves" / "DetrendingStats" / str(DetrendingName)
        folder_path.mkdir(parents=True, exist_ok=True)
        out_path = folder_path / f"{mission}_{ID}_detrendingStats.txt"
        with open(out_path, 'w') as f:
            f.write('Transit Duration (Min; 50; 75; Max), ' + str(duration_min) + ',' + str(duration_50) + ',' + str(duration_75) + ',' + str(duration_max) + ',' + '\n')
            # guard indexing
            pm = list(powerMax) + [0, 0, 0, 0, 0]
            plm = list(periodLogMax) + [0, 0, 0, 0, 0]
            f.write('Max Power (0;1;2;3;4;5), ' + ','.join(str(pm[i]) for i in range(5)) + '\n')
            f.write('Max Power Period (0;1;2;3;4;5), ' + ','.join(str(10**plm[i] * days2sec) for i in range(5)) + '\n')
            f.write('Fap (10pc; 5pc; 1pc), ' + ','.join(str(x) for x in fap) + '\n')

    if (returnOptimalWindowLength == True):
        return cosineFilterWindowLength, fap[2], max_power
    else:
        return fap[2], max_power


def Detrending_IterativeCosine(timeArray, fluxArray, duration_array,
                               SystemName, DetrendingName, mission, ID, factor, *,
                               base_dir=None):
    '''
    Functionality:
        Iteratively detrend a light curve using wotan’s cosine filter. 
        Each iteration computes a Lomb–Scargle periodogram via `DoPeriodogram` 
        to identify the most significant variability period. 
        If significant periodicity remains (FAP < 1%), the function applies 
        cosine detrending again with progressively smaller window lengths. 
        The process stops when no significant power remains or the maximum 
        iteration factor is reached.

    Arguments:
        timeArray (array-like): Time stamps in seconds.
        fluxArray (array-like): Normalized flux values corresponding to `timeArray`.
        duration_array (array-like): Array of predicted transit durations (seconds).
        SystemName (str): Identifier for the current target system (used in figure titles).
        DetrendingName (str): Label for figure/output naming.
        mission (str): Mission tag (e.g., 'TESS', 'Kepler') passed to `DoPeriodogram`.
        ID (str or int): Target identifier used for record-keeping.
        factor (iterable of float): List of duration multipliers to test in iterative detrending.
        base_dir (Path-like or None): Root directory for outputs (forwarded to DoPeriodogram).

    Returns:
        tuple:
            timeCosineFiltered (np.ndarray): Detrended time array (seconds).
            fluxCosineFiltered (np.ndarray): Detrended flux array.
            trendCosineFiltered (np.ndarray): Cosine trend removed from the data.
    '''
    # Make an initial copy
    timeCosineFiltered = np.copy(timeArray)
    fluxCosineFiltered = np.copy(fluxArray)
    subplotCounter = 1
    sufficientDetrendingReached = False

	# Setup the plot
    figCosine = plt.figure(figsize=(18,7))
    figCosine.suptitle(SystemName + " " + DetrendingName + " Iterative Cosine Filter Periodograms")	
    
    print('Running iterative cosine filter')
	
	#transitDurationPercentage equals 'max' or '75'. It is based on the transit duration array, which was calculated ealrier and is passed to that function. That is an array of the planet's transot duration at all times in the light curve. if transitDurationPercentage is set to 'max' then that corresponds to the maximum duration planet transit. If it is set to '75' then that corresponds to the transit duration longer than the transit duration at 75% of the times. This could also be set to 50, 25 or any arbitrary number.
	
	#transitDurationMultiplier is a multiplicative factor of transitDurationPercentage. 
    for transitDurationPercentage in ['75']:
        for transitDurationMultiplier in factor: 
            print('transitDurationPercentage = ' + str(transitDurationPercentage) + ', transitDurationMultiplier = ' + str(transitDurationMultiplier))
            if (sufficientDetrendingReached == False):
				# Now the function below will return the window length used for the cosine filter. For that it takes in the duration array and figures out the max and 75% transit durations. It also figures out if there is actually any remaining periodocity, and if there isn't it'll return -27 as an indicator that we are done
                cosineFilterWindowLength, fap_1perc, max_power = DoPeriodogram(
                    timeCosineFiltered, fluxCosineFiltered, duration_array,
                    figCosine, True, transitDurationPercentage, transitDurationMultiplier,
                    'progressive', SystemName, DetrendingName, mission, ID, subplotCounter,
                    base_dir=base_dir
                )
				#print('cosineFilterWindowLength (days) = ' + str(cosineFilterWindowLength/days2sec))
                subplotCounter += 1
                if (cosineFilterWindowLength != -27):
					# this means that a peak in the periodogram above the designated fap has been found, so we need to do some detrending
                    numSectors = 5
                    timeCosineFiltered = np.array([]) # Note that we completely re-do the cosine detrending each time with new parameters (i.e. a new window length) and not do it cumulatively. This makes sense because we want to be detrending away something which is inherently sinusoidal, not something which would look weird after a poor previous effort at cosine detrending
                    fluxCosineFiltered = np.array([])
                    trendCosineFiltered = np.array([])
                    sectorDataPoints = int(len(timeArray)/numSectors)
                    print('2')
					#print('numSectors = ' + str(numSectors))
                    for ii in range(0,numSectors):
						#print('ii = ' + str(ii))
                        timeSegment = timeArray[ii*sectorDataPoints:(ii+1)*sectorDataPoints]/days2sec - 55000
                        fluxSegment = fluxArray[ii*sectorDataPoints:(ii+1)*sectorDataPoints]
						# Suppress output text
                        text_trap = io.StringIO()
                        sys.stdout = text_trap
						#print(timeFinal)
						#print(fluxFinal)
                        fluxCosineFilteredSegment, trendCosineFilteredSegment = wotan.flatten(time=timeSegment,flux=fluxSegment,method='cosine',robust=True,break_tolerance=0.5,window_length=cosineFilterWindowLength/days2sec,return_trend=True)
						# allow printing output again
                        sys.stdout = sys.__stdout__
                        timeCosineFilteredSegment = timeSegment
                        timeCosineFiltered = np.append(timeCosineFiltered,(timeCosineFilteredSegment + 55000)*days2sec)
                        fluxCosineFiltered = np.append(fluxCosineFiltered,fluxCosineFilteredSegment)
                        trendCosineFiltered = np.append(trendCosineFiltered,trendCosineFilteredSegment)
                else:
                    sufficientDetrendingReached = True
			
				#if (transitDurationPercentage == 'max' and transitDurationMultiplier == 3):
					# Just done the first round of detrending. if we are to scale transits then we need to do it now
				
	# Save the figure
    folder_name = "../LightCurves/Figures/" + DetrendingName
	#figCosine.savefig(folder_name + '/' + SystemName + '_' + DetrendingName + '_iterativeCosine.png', bbox_inches='tight') <---- can cause a crash
    
    return timeCosineFiltered,fluxCosineFiltered,trendCosineFiltered


def Detrending_IterativeCosine2(timeOrig, fluxOrig, timeCut, fluxCut,
                                timeFinal, fluxFinal, durationArray,
                                SystemName, DetrendingName, mission, ID, *,
                                base_dir=None):
    '''
    Functionality:
        Iteratively detrend a light curve using wotan’s cosine filter, but operating
        on provided "final" arrays (timeFinal/fluxFinal) and saving intermediate
        iterations to diagnostic plots. At each iteration, the function calls
        `DoPeriodogram` to estimate an appropriate cosine window length. If a
        significant periodicity remains (FAP < 1%), it applies cosine detrending
        again; otherwise it stops. It also accumulates all intermediate detrended
        time/flux arrays in lists (listTime/listFlux) for later inspection.

    Arguments:
        timeOrig (array-like): Original time array (unused here; kept for API symmetry).
        fluxOrig (array-like): Original flux array (unused here; kept for API symmetry).
        timeCut (array-like): Time after preliminary cuts (unused here; kept for API).
        fluxCut (array-like): Flux after preliminary cuts (unused here; kept for API).
        timeFinal (array-like): Working time array (seconds) used for detrending.
        fluxFinal (array-like): Working flux array aligned with `timeFinal`.
        durationArray (array-like): Predicted transit durations (seconds).
        SystemName (str): System identifier for figure titles and filenames.
        DetrendingName (str): Label used in titles/paths.
        mission (str): Mission name (e.g., "TESS", "Kepler").
        ID (str|int): Target identifier for labeling.
    
    Returns:
        tuple:
            timeCosineFiltered (np.ndarray): Detrended time array (seconds).
            fluxCosineFiltered (np.ndarray): Detrended flux array.
            trendCosineFiltered (np.ndarray): Trend removed by the cosine filter.
            listTime (list[np.ndarray]): Time arrays from each displayed iteration.
            listFlux (list[np.ndarray]): Flux arrays from each displayed iteration.
    '''
    if wotan is None:
        raise ImportError("wotan is required for Detrending_IterativeCosine2")

    listTime = []
    listFlux = []

    timeCosineFiltered = np.copy(timeFinal)
    fluxCosineFiltered = np.copy(fluxFinal)
    subplotCounter = 1
    sufficientDetrendingReached = False

    figCosine = plt.figure(figsize=(20, 10))
    figCosine.suptitle(SystemName)

    print('Running iterative cosine filter')

    transitDurationMultiplierArray = [3]

    for transitDurationPercentage in ['max']:
        for transitDurationMultiplier in transitDurationMultiplierArray:
            print('transitDurationPercentage = ' + str(transitDurationPercentage) +
                  ', transitDurationMultiplier = ' + str(transitDurationMultiplier))

            if (sufficientDetrendingReached == False):
                cosineFilterWindowLength, fap_1perc, max_power = DoPeriodogram(
                    timeCosineFiltered, fluxCosineFiltered, durationArray, figCosine,
                    True, transitDurationPercentage, transitDurationMultiplier,
                    'progressive', SystemName, DetrendingName, mission, ID, subplotCounter,
                    base_dir=base_dir
                )
                subplotCounter += 1
                print('first')

                if (cosineFilterWindowLength != -27):
                    numSectors = 5
                    timeCosineFiltered = np.array([])   # rebuild fresh each iteration
                    fluxCosineFiltered = np.array([])
                    trendCosineFiltered = np.array([])
                    sectorDataPoints = int(len(timeFinal) / numSectors) if len(timeFinal) else 0
                    print('second')

                    for ii in range(0, numSectors):
                        seg_slice = slice(ii * sectorDataPoints, (ii + 1) * sectorDataPoints)
                        timeSegment = timeFinal[seg_slice] / days2sec - 55000
                        fluxSegment = fluxFinal[seg_slice]

                        text_trap = io.StringIO()
                        sys.stdout = text_trap
                        fluxCosineFilteredSegment, trendCosineFilteredSegment = wotan.flatten(
                            time=timeSegment, flux=fluxSegment,
                            method='cosine', robust=True, break_tolerance=0.5,
                            window_length=cosineFilterWindowLength / days2sec,
                            return_trend=True
                        )
                        sys.stdout = sys.__stdout__

                        timeCosineFiltered = np.append(timeCosineFiltered, (timeSegment + 55000) * days2sec)
                        fluxCosineFiltered = np.append(fluxCosineFiltered, fluxCosineFilteredSegment)
                        trendCosineFiltered = np.append(trendCosineFiltered, trendCosineFilteredSegment)
                        print('third')
                else:
                    sufficientDetrendingReached = True
                    trendCosineFiltered = np.copy(fluxFinal)
                    print('fourth')

            # Record iteration
            listTime.append(timeCosineFiltered)
            listFlux.append(fluxCosineFiltered)
            print(listFlux)

            # Overlay diagnostic scatter for this step
            ax = figCosine.add_subplot(3, 2, subplotCounter)
            ax.scatter(timeFinal / days2sec - 55000, fluxFinal, color='b', label='Common False Positives Cut')
            ax.scatter(timeCosineFiltered / days2sec - 55000, fluxCosineFiltered, color='r', label='Cosine Detrended')
            ax.plot()
            ax.set_xlabel('Time (days - 55000)')
            ax.set_ylabel('Flux')
            ax.legend()
            ax.set_title('dur%=' + str(transitDurationPercentage) + ' DurMult=' + str(transitDurationMultiplier))

            # Save figure (base-dir aware vs hard-coded Windows path)
            root = _resolve_base_dir(None)
            folder_name = root / "LightCurves" / "ItCos_Testing"
            folder_name.mkdir(parents=True, exist_ok=True)
            figCosine.savefig(folder_name / (f"it_cos_test{SystemName}_{DetrendingName}.png"), bbox_inches='tight')

    return timeCosineFiltered, fluxCosineFiltered, trendCosineFiltered, listTime, listFlux

def Detrending_PlugHoles(timeArray, fluxArray):
    '''
    Functionality:
        Fill temporal gaps in a light curve by fitting local polynomials on either
        side of each gap and inserting synthetic points (with added noise) across
        the gap. This can improve robustness of downstream detrending methods that
        struggle across large gaps. It also returns the indices of the synthetic
        points so they can be removed later.

    Arguments:
        timeArray (array-like): Time stamps (seconds), assumed sorted.
        fluxArray (array-like): Flux values aligned with `timeArray`.

    Returns:
        tuple:
            timeHolePlugged (np.ndarray): Original times plus synthetic in-gap times.
            fluxHolePlugged (np.ndarray): Original flux plus polynomial-filled values.
            holeIndex (np.ndarray[int]): Indices of the inserted synthetic points.
    '''
    fluxHolePlugged = []
    timeHolePlugged = []

    holeIndex = np.array([])  # record of synthetic points (to remove later if desired)
    numHoles = 0

    gapSizeThreshold = 2 * hours2sec  # seconds
    polynomialOrder = 5

    for ii in range(1, len(timeArray)):  # start at 1 (compare to previous point)
        if (np.isfinite(fluxArray[ii]) == True):

            # If the temporal gap exceeds the threshold, fill it
            if (timeArray[ii] - timeArray[ii - 1] > gapSizeThreshold):
                numPoints = (timeArray[ii] - timeArray[ii - 1]) / (29.4 * 60) + 1
                numPoints = numPoints.astype(int)
                timePlugged = np.linspace(timeArray[ii - 1], timeArray[ii], numPoints)
                timePlugged = timePlugged[1:-1]  # internal points only

                # Build polynomial using neighborhoods on each side of the gap
                polyFitSpan = (timeArray[ii] - timeArray[ii - 1]) / 5.0
                tempFlux1 = fluxArray[(timeArray > timeArray[ii - 1] - polyFitSpan) & (timeArray <= timeArray[ii - 1])]
                tempFlux2 = fluxArray[(timeArray >= timeArray[ii]) & (timeArray < timeArray[ii] + polyFitSpan)]
                tempFlux = np.append(tempFlux1, tempFlux2)
                tempTime = timeArray[(timeArray > timeArray[ii - 1] - polyFitSpan) & (timeArray < timeArray[ii] + polyFitSpan)]

                warnings.simplefilter('ignore', np.RankWarning)
                pfitGap = np.polyfit(tempTime, tempFlux, polynomialOrder)
                pfitGap = np.poly1d(pfitGap)

                filledGap_flux = pfitGap(timePlugged)
                filledGap_time = np.array(timePlugged)

                # Add noise to avoid biasing the detrend
                filledGap_std = np.mean([np.std(tempFlux1), np.std(tempFlux2)]) * 2
                filledGap_flux = filledGap_flux + np.random.normal(0, filledGap_std, len(filledGap_flux))

                # Record index range of inserted points
                newHoles = np.linspace(len(timeHolePlugged),
                                       len(timeHolePlugged) + len(filledGap_time) - 1,
                                       len(filledGap_time))
                holeIndex = np.append(holeIndex, newHoles)

                # Append synthetic gap fill
                timeHolePlugged = np.append(timeHolePlugged, filledGap_time)
                fluxHolePlugged = np.append(fluxHolePlugged, filledGap_flux)

                numHoles += 1

            # Always append the current real point
            timeHolePlugged = np.append(timeHolePlugged, timeArray[ii])
            fluxHolePlugged = np.append(fluxHolePlugged, fluxArray[ii])

    holeIndex = holeIndex.astype(int)
    return timeHolePlugged, fluxHolePlugged, holeIndex


def Detrending_RemoveHoles(timeArray, fluxArray, windowLengthFinal, holeIndex):
    '''
    Functionality:
        Remove synthetic gap-filled points (previously inserted by
        `Detrending_PlugHoles`) from time/flux arrays and companion arrays such as
        a per-point window length.

    Arguments:
        timeArray (array-like): Time stamps (seconds).
        fluxArray (array-like): Flux values.
        windowLengthFinal (array-like): Per-point window length (same length as time/flux).
        holeIndex (array-like[int]): Indices of synthetic points to be removed.

    Returns:
        tuple:
            timeArray (np.ndarray): Time with synthetic points removed.
            fluxArray (np.ndarray): Flux with synthetic points removed.
            windowLengthFinal (np.ndarray): Window lengths with synthetic points removed.
    '''
    # Compensate for possible off-by-one removal earlier in pipeline
    holeIndex = holeIndex - 1

    if (len(holeIndex) > 0):
        timeArray = np.delete(timeArray, holeIndex)
        fluxArray = np.delete(fluxArray, holeIndex)
        windowLengthFinal = np.delete(windowLengthFinal, holeIndex)

    return timeArray, fluxArray, windowLengthFinal


def FDSFSDFDS(timeFinal, fluxFinal):
    '''
    Functionality:
        Example (placeholder) wrapper for variable-window vs constant-window
        detrending calls to the (external) AC module. Demonstrates how to select
        between variable-window detrending (`DetrendLightCurveVariableWindow`) and
        a constant-window run (`DetrendLightCurve`), and then sanitize outputs by
        removing NaNs. This function references `duration_array` and `time_array`
        from outer scope (as in the original code).

    Arguments:
        timeFinal (array-like): Input time array (seconds).
        fluxFinal (array-like): Input flux array.

    Returns:
        None
            (Modifies local variables; example code for pipeline usage. In a real
            application, you would return the detrended arrays and window lengths.)
    '''
    detrending_method = 'biweight'
    detrending_windowLength = -27   # -27 → variable window mode
    detrending_minimaType = 6
    detrending_transitDurationAllowance = 1

    # Variable window parameters
    detrending_variableWindowSplits = 48  # typically 24
    detrending_variableWindowMultiplier = 3

    simCount = 0
    startTime = TIME.time()

    # DO THE DETRENDING
    if (detrending_windowLength == -27):
        # Variable window detrending
        temp1, temp2, timeFinal, fluxFinal, windowLength = AC.DetrendLightCurveVariableWindow(
            timeFinal, fluxFinal, duration_array, time_array,
            detrending_variableWindowSplits, detrending_variableWindowMultiplier,
            method=detrending_method
        )
    else:
        # Constant window detrending
        timeFinal, fluxFinal = AC.DetrendLightCurve(
            timeFinal, fluxFinal,
            window_length=detrending_windowLength,
            method=detrending_method, plot_results=True
        )
        # Companion window-length array (constant)
        windowLength = timeFinal * 0 + detrending_windowLength

    # Clean NaNs (can occur if not using variable window)
    timeFinal = timeFinal[~np.isnan(fluxFinal)]
    windowLengthFinal = windowLength[~np.isnan(fluxFinal)]
    fluxFinal = fluxFinal[~np.isnan(fluxFinal)]

def Detrending_VariableDuration(timeArray, fluxArray, durationArray, durationArrayTime,
                                method, numTransitDurationSplits, windowLengthModifier, xi):
    '''
    Functionality:
        Detrend a light curve using a **duration-adaptive** window. The predicted
        transit duration at each time is mapped to one of `numTransitDurationSplits`
        bins; for each bin we run `DetrendLightCurve` with a window length set by
        the bin’s representative duration and copy those detrended points back into
        a global output array. This protects longer events while still removing
        short-timescale variability. The factor `xi` (<= 1 typically) increases
        aggressiveness for the longest-duration bin.

    Arguments:
        timeArray (array-like): Time stamps (seconds), same length as `fluxArray`.
        fluxArray (array-like): Flux values.
        durationArray (array-like): Predicted transit duration values (seconds)
            sampled at `durationArrayTime`.
        durationArrayTime (array-like): Times (seconds) associated with `durationArray`.
        method (str): Detrending method string passed to `DetrendLightCurve`
            (e.g., "cosine", "biweight", "lowess", etc., depending on wrapper).
        numTransitDurationSplits (int): Number of duration bins/splits.
        windowLengthModifier (float): Multiplicative factor applied to the base
            duration to get the detrending window (in **days** inside the call).
        xi (float): Additional multiplier applied to the **maximum** duration end;
            allows more aggressive detrending at long durations.

    Returns:
        tuple:
            overallTimeDetrended (np.ndarray): Time array (seconds) after filtering
                out any points that yielded NaNs during detrend.
            overallFluxDetrended (np.ndarray): Detrended flux array.
            overallUsedWindowLength (np.ndarray): Window length (days) used for each
                retained point (same length as returned flux/time).
            overallTrendUsed (np.ndarray): The trend removed by the filter for each
                retained point.
    '''
    # Build reference duration bins (seconds) and the window lengths to use (days)
    windowLengthArray_ref = np.linspace(np.min(durationArray), np.max(durationArray), numTransitDurationSplits)
    windowLengthArray_set = np.linspace(
        np.min(durationArray) * windowLengthModifier,
        np.max(durationArray) * windowLengthModifier * xi,
        numTransitDurationSplits
    ) / days2sec  # convert seconds → days for the detrending call

    # Interpolate the duration array to the light-curve time grid
    durationArrayTimeTemp = np.interp(timeArray, durationArrayTime, durationArrayTime)
    durationArrayTemp = np.interp(timeArray, durationArrayTime, durationArray)

    durationArrayTime = durationArrayTimeTemp
    durationArray = durationArrayTemp

    # Initialize outputs
    overallTimeDetrended = timeArray
    overallFluxDetrended = 0 * timeArray + 1        # placeholder until filled bin-by-bin
    overallUsedWindowLength = timeArray + -27       # sentinel until filled
    overallTrendUsed = 0 * timeArray + 1            # placeholder trend

    # Apply per-bin detrending and copy results into global arrays
    for ii in range(0, numTransitDurationSplits):
        print('split ii = ' + str(ii))
        print('Window length = ' + str(windowLengthArray_set[ii]))
        print(timeArray)

        tempTimeDetrended, tempFluxDetrended, trend = DetrendLightCurve(
            timeArray, fluxArray,
            window_length=windowLengthArray_set[ii],
            method=method, plot_results=False
        )

        # Indices belonging to this bin (exclude last bin’s upper edge)
        if (ii < numTransitDurationSplits - 1):
            selectedIndicies = np.linspace(0, len(overallFluxDetrended) - 1, len(overallFluxDetrended)).astype(int)
            selectedIndicies = selectedIndicies[
                (durationArray > windowLengthArray_ref[ii]) &
                (durationArray < windowLengthArray_ref[ii + 1])
            ]

            overallFluxDetrended[selectedIndicies] = tempFluxDetrended[selectedIndicies]
            overallTrendUsed[selectedIndicies] = trend[selectedIndicies]
            overallUsedWindowLength[selectedIndicies] = windowLengthArray_set[ii]

        sys.stdout.write("Splits completed: %d   \r" % (ii + 1))
        sys.stdout.flush()

    # Remove NaN results to keep arrays aligned/sane
    overallTimeDetrended = overallTimeDetrended[~np.isnan(overallFluxDetrended)]
    overallUsedWindowLength = overallUsedWindowLength[~np.isnan(overallFluxDetrended)]
    overallTrendUsed = overallTrendUsed[~np.isnan(overallFluxDetrended)]
    overallFluxDetrended = overallFluxDetrended[~np.isnan(overallFluxDetrended)]

    return overallTimeDetrended, overallFluxDetrended, overallUsedWindowLength, overallTrendUsed


def Detrending_RemoveKinks(timeArray, fluxArray, windowLengthFinal, mission, ID, DetrendingName, base_dir=None):
    '''
    Functionality:
        Identify and remove segments around:
          (a) **gaps with "hooks"** (flux discontinuities immediately before/after a gap),
          (b) **large jumps** unassociated with gaps.
        The function returns copies of the inputs with those segments cut out, and
        also saves diagnostic plots (atlas of jumps and gaps, and summary levels).

    Arguments:
        timeArray (array-like): Time stamps (seconds), assumed sorted.
        fluxArray (array-like): Detrended (or raw) flux values.
        windowLengthFinal (array-like): Per-point window length (or any companion
            vector; trimmed in sync with time/flux).
        mission (str): Mission name (for file labels).
        ID (str|int): Target identifier (for file labels).
        DetrendingName (str): Label for output folder/file names.
        base_dir (str|pathlib.Path or None): Root of the repo/data tree. If None, uses CWD.

    Returns:
        tuple:
            timeArray_clean (np.ndarray): Time array with kinked regions removed.
            fluxArray_clean (np.ndarray): Flux array with kinked regions removed.
            windowLength_clean (np.ndarray): Companion window array with same cuts.
    '''
    # Parameters
    newGapThreshold = 2.0 / 24.0 * days2sec     # seconds
    sigmaThreshold_gap = 1.5
    gapCutWidth = 0.8 * days2sec

    jumpCheckHalfWidth = 2.1 / 24.0 * days2sec  # seconds
    jumpCutWidth = 0.8 * days2sec
    sigmaThreshold_jump = 4

    # Working copies
    temp1 = np.copy(timeArray)
    temp2 = np.copy(fluxArray)
    temp3 = np.copy(windowLengthFinal)

    newGapCount = 0
    newJumpCount = 0
    referenceMean = np.mean(fluxArray)
    referenceSTD = np.std(fluxArray)

    gapTimeList = []
    jumpTimeList = []

    gapLevelArray = []
    gapLevelTimeArray = []

    jumpLevelLeftArray = []
    jumpLevelRightArray = []
    jumpLevelTimeArray = []

    for ii in range(0, len(timeArray)):
        # Gap detection: compare neighboring means across large gaps
        if (timeArray[ii] - timeArray[ii - 1] > newGapThreshold):
            meanLeft = np.mean(fluxArray[(timeArray > timeArray[ii - 1] - newGapThreshold) &
                                         (timeArray <= timeArray[ii - 1])])
            meanRight = np.mean(fluxArray[(timeArray > timeArray[ii]) &
                                          (timeArray < timeArray[ii] + newGapThreshold)])

            gapLevelArray.append(np.abs(meanLeft - meanRight) / referenceSTD)
            gapLevelTimeArray.append(timeArray[ii])

            if (np.abs(meanLeft - meanRight) > sigmaThreshold_gap * referenceSTD):
                mask = ((temp1 < timeArray[ii - 1] - gapCutWidth) & (temp1 > timeArray[ii] + gapCutWidth))
                if (np.abs(timeArray[ii] / days2sec - 55000 - 246.452) > 1):
                    gapTimeList.append(timeArray[ii])
                    keep = np.logical_or(temp1 < timeArray[ii - 1] - gapCutWidth,
                                         temp1 > timeArray[ii] + gapCutWidth)
                    temp2 = temp2[keep]
                    temp3 = temp3[keep]
                    temp1 = temp1[keep]
                    newGapCount += 1

        else:
            # Large jump detection away from gaps
            meanLeft = np.mean(fluxArray[(timeArray > timeArray[ii - 1] - jumpCheckHalfWidth) &
                                         (timeArray <= timeArray[ii - 1])])
            meanRight = np.mean(fluxArray[(timeArray >= timeArray[ii]) &
                                          (timeArray < timeArray[ii] + jumpCheckHalfWidth)])

            jumpLevelLeftArray.append(np.abs(meanLeft - referenceMean) / referenceSTD *
                                      -1 * np.sign((meanLeft - referenceMean) / (meanRight - referenceMean)))
            jumpLevelRightArray.append(np.abs(meanRight - referenceMean) / referenceSTD *
                                       -1 * np.sign((meanLeft - referenceMean) / (meanRight - referenceMean)))
            jumpLevelTimeArray.append(timeArray[ii])

            if (np.abs(meanLeft - referenceMean) > sigmaThreshold_jump / 2. * referenceSTD and
                np.abs(meanRight - referenceMean) > sigmaThreshold_jump / 2. * referenceSTD):
                if (np.abs(meanLeft - meanRight) > sigmaThreshold_jump * referenceSTD):
                    if ((meanLeft - referenceMean) / (meanRight - referenceMean) < 0):
                        if (np.abs(timeArray[ii] / days2sec - 55000 - 246.452) > 1):
                            newJumpCount += 1
                            keep = np.logical_or(temp1 < timeArray[ii - 1] - jumpCutWidth,
                                                 temp1 > timeArray[ii] + jumpCutWidth)
                            temp2 = temp2[keep]
                            temp3 = temp3[keep]
                            temp1 = temp1[keep]
                            jumpTimeList.append(timeArray[ii])

    # Logging where things were removed
    if (len(jumpTimeList) > 0):
        jumpText = 'Jumps at time: ' + str(round(jumpTimeList[0] / days2sec - 55000, 3))
        for ii in range(1, len(jumpTimeList)):
            jumpText = jumpText + ', ' + str(round(jumpTimeList[ii] / days2sec - 55000, 3))
        print(jumpText)
    else:
        print('NO jumps')

    if (len(gapTimeList) > 0):
        gapText = 'Gaps at time: ' + str(round(gapTimeList[0] / days2sec - 55000, 3))
        for ii in range(1, len(gapTimeList)):
            gapText = gapText + ', ' + str(round(gapTimeList[ii] / days2sec - 55000, 3))
        print(gapText)
    else:
        print('NO gaps')

    # Atlas plots of the removed regions
    numJumps = len(jumpTimeList)
    figJumps = plt.figure(figsize=(17, 9))
    figJumps.suptitle(mission + ID + ' Removed Jumps In The Data')
    plot_rows = math.ceil(numJumps ** 0.5) if numJumps > 0 else 1
    plot_columns = math.ceil(numJumps ** 0.5) if numJumps > 0 else 1
    jumpDuration = 24 * hours2sec

    for ii in range(0, numJumps):
        ax = figJumps.add_subplot(plot_rows, plot_columns, ii + 1)
        timeIndividualJump = timeArray[(timeArray > jumpTimeList[ii] - jumpDuration / 2) &
                                       (timeArray < jumpTimeList[ii] + jumpDuration / 2)]
        fluxIndividualJump = fluxArray[(timeArray > jumpTimeList[ii] - jumpDuration / 2) &
                                       (timeArray < jumpTimeList[ii] + jumpDuration / 2)]
        ax.scatter(timeIndividualJump / days2sec - 55000, fluxIndividualJump)
        ax.set_ylim([np.min(fluxIndividualJump), np.max(fluxIndividualJump)])
        ax.set_xlabel('Time (BJD - 2,455,000)')
        ax.set_ylabel('Flux')

    base_root = _resolve_base_dir(None)
    folder_path = base_root / "LightCurves" / "Figures" / DetrendingName
    _ensure_parent(folder_path / "dummy.txt")
    figJumps.savefig(folder_path / f'{mission}{ID}_{DetrendingName}_hookJumps.png', bbox_inches='tight')

    numGaps = len(gapTimeList)
    figGaps = plt.figure(figsize=(17, 9))
    figGaps.suptitle(mission + ID + ' Removed Gaps With Hooks')
    plot_rows = math.ceil(numGaps ** 0.5) if numGaps > 0 else 1
    plot_columns = math.ceil(numGaps ** 0.5) if numGaps > 0 else 1
    gapDuration = 24 * hours2sec

    for ii in range(0, numGaps):
        ax = figGaps.add_subplot(plot_rows, plot_columns, ii + 1)
        timeIndividualGap = timeArray[(timeArray > gapTimeList[ii] - gapDuration / 2) &
                                      (timeArray < gapTimeList[ii] + gapDuration / 2)]
        fluxIndividualGap = fluxArray[(timeArray > gapTimeList[ii] - gapDuration / 2) &
                                      (timeArray < gapTimeList[ii] + gapDuration / 2)]
        ax.scatter(timeIndividualGap / days2sec - 55000, fluxIndividualGap)
        ax.set_ylim([np.min(fluxIndividualGap), np.max(fluxIndividualGap)])
        ax.set_xlabel('Time (BJD - 2,455,000)')
        ax.set_ylabel('Flux')

    figGaps.savefig(folder_path / f'{mission}{ID}_{DetrendingName}_hookGaps.png', bbox_inches='tight')

    # Summary levels over time
    jumpLevelTimeArray = np.array(jumpLevelTimeArray)
    jumpLevelRightArray = np.array(jumpLevelRightArray)
    jumpLevelLeftArray = np.array(jumpLevelLeftArray)
    gapLevelTimeArray = np.array(gapLevelTimeArray)
    gapLevelArray = np.array(gapLevelArray)

    fig = plt.figure(figsize=(17, 9))

    ax = fig.add_subplot(211)
    if jumpLevelTimeArray.size > 0:
        ax.scatter(jumpLevelTimeArray / days2sec - 55000, jumpLevelLeftArray, color='blue', label='left')
        ax.scatter(jumpLevelTimeArray / days2sec - 55000, jumpLevelRightArray, color='red', label='right')
        ax.plot([jumpLevelTimeArray[0] / days2sec - 55000, jumpLevelTimeArray[-1] / days2sec - 55000],
                [sigmaThreshold_jump, sigmaThreshold_jump], linestyle='--', label='sigmaThreshold_jump')
    ax.set_ylabel('Jump level')
    ax.set_xlabel('Time [BJD-2,455,000]')
    ax.legend()

    ax = fig.add_subplot(212)
    if gapLevelTimeArray.size > 0:
        ax.scatter(gapLevelTimeArray / days2sec - 55000, gapLevelArray)
        ax.plot([gapLevelTimeArray[0] / days2sec - 55000, gapLevelTimeArray[-1] / days2sec - 55000],
                [sigmaThreshold_gap / 2, sigmaThreshold_gap / 2], linestyle='--', label='sigmaThreshold_gap/2')
    ax.set_ylabel('Gap level')
    ax.set_xlabel('Time [BJD-2,455,000]')

    # Return cleaned arrays
    return temp1, temp2, temp3


def Detrending_RemoveCommonFalsePositives(timeArray, fluxArray, mission, ID, base_dir=None):
    '''
    Functionality:
        Remove time ranges known to produce common false positives across many
        targets, and apply any target-specific manual cuts if a per-target file
        exists. The ranges are loaded from CSV files and the corresponding samples
        are dropped from `timeArray` and `fluxArray`.

    Arguments:
        timeArray (array-like): Time stamps (seconds).
        fluxArray (array-like): Flux values.
        mission (str): Mission name used to locate target-specific cuts.
        ID (str|int): Target ID used to locate target-specific cuts.
        base_dir (str|pathlib.Path or None): Root of the repo/data tree. If None, uses CWD.

    Returns:
        tuple:
            timeArray_clean (np.ndarray): Time array with known-bad intervals removed.
            fluxArray_clean (np.ndarray): Flux array with those intervals removed.
    '''
    cut_fp = p_databases("common_false_positives.csv")
    cutData = np.genfromtxt(
        cut_fp,
        comments="#", delimiter=',', unpack=False, names=True, skip_header=True
    )
    cutStartArray = cutData['start']
    cutEndArray = cutData['end']

    manual_cuts_filename = p_databases("SpecificTargetCuts", f"{mission}_{ID}_manual_cuts.csv")
    if manual_cuts_filename.exists():
        print('Manual cuts found')
        cutData2 = np.genfromtxt(
            manual_cuts_filename,
            comments="#", delimiter=',', unpack=False, names=True, skip_header=True
        )
        cutStartArray = np.append(cutStartArray, cutData2['start'])
        cutEndArray = np.append(cutEndArray, cutData2['end'])

    for ii in range(0, len(cutStartArray)):
        referenceTimeArray = timeArray / days2sec - 55000
        referenceIndexArray = np.linspace(0, len(referenceTimeArray) - 1, len(referenceTimeArray)).astype(int)
        referenceIndexArray = referenceIndexArray[
            (referenceTimeArray > cutStartArray[ii]) & (referenceTimeArray < cutEndArray[ii])
        ]
        fluxArray = np.delete(fluxArray, referenceIndexArray)
        timeArray = np.delete(timeArray, referenceIndexArray)

    return timeArray, fluxArray


def Detrending_FindPotentialLedges(timeArray, fluxArray, SystemName, DetrendingName, base_dir=None):
    '''
    Functionality:
        Detect potential "ledge"-like discontinuities in the light curve by analyzing
        point-to-point flux changes (ΔF) normalized by cadence spacing and robustly
        scaled. Exclude points adjacent to large time gaps, then flag sequences where
        |ΔF| exceeds high thresholds (8σ with neighbor >5σ) to avoid isolated single
        outliers. Save overview plots and a per-ledge atlas for inspection.

    Arguments:
        timeArray (array-like): Time stamps (seconds), sorted.
        fluxArray (array-like): Flux values aligned with `timeArray`.
        SystemName (str): System identifier for plot titles.
        DetrendingName (str): Label used for output folder/filenames.
        base_dir (str|pathlib.Path or None): Root of the repo/data tree. If None, uses CWD.

    Returns:
        None
            (Saves diagnostic figures to ../LightCurves/Figures/<DetrendingName>/)
    '''
    # Diff arrays (length N-1) and mid-times
    deltaFlux = fluxArray[1:] - fluxArray[:-1]
    deltaTime = (timeArray[1:] - timeArray[:-1]) / (0.49042266845703125 * hours2sec)
    tmid = 0.5 * (timeArray[1:] + timeArray[:-1])

    # Diagnostic: cadence gap distribution
    cadenceGap = np.linspace(0, 10, 11)
    cadenceGapCount = np.zeros(11, dtype=int)
    for ii in range(len(cadenceGap)):
        cadenceGapCount[ii] = len(deltaTime[(deltaTime > cadenceGap[ii] * 0.95) & (deltaTime < cadenceGap[ii] * 1.05)])
    cadenceGapCount = np.append(cadenceGapCount, len(deltaTime) - np.sum(cadenceGapCount))

    # Indices near large gaps (3+ cadences)
    all_idx = np.arange(deltaTime.size, dtype=int)
    timeGapIndices = all_idx[deltaTime > 2.9]
    timeGapIndicesShifted = timeGapIndices + 1

    nm1 = deltaFlux.size
    valid_A = (timeGapIndices >= 0) & (timeGapIndices < nm1)
    valid_B = (timeGapIndicesShifted >= 0) & (timeGapIndicesShifted < nm1)
    idxA = timeGapIndices[valid_A]
    idxB = timeGapIndicesShifted[valid_B]

    print(len(idxA), len(idxB), len(deltaTime))

    figNewJumpDetector = plt.figure(figsize=(12, 8))

    # (1) |ΔF| vs time
    ax = figNewJumpDetector.add_subplot(311)
    ax.scatter(tmid / days2sec - 55000, np.abs(deltaFlux), color='blue')
    if idxA.size:
        ax.scatter(tmid[idxA] / days2sec - 55000, np.abs(deltaFlux[idxA]), color='red')
    if idxB.size:
        ax.scatter(tmid[idxB] / days2sec - 55000, np.abs(deltaFlux[idxB]), color='green')
    ax.set_xlabel('Time (BJD - 2,455,000)')
    ax.set_ylabel('Delta Flux (point to point)')

    # (2) Δt (in 30 min cadences) vs time
    ax = figNewJumpDetector.add_subplot(312)
    ax.scatter(tmid / days2sec - 55000, deltaTime, color='blue')
    if idxA.size:
        ax.scatter(tmid[idxA] / days2sec - 55000, deltaTime[idxA], color='red')
    if idxB.size:
        ax.scatter(tmid[idxB] / days2sec - 55000, deltaTime[idxB], color='green')
    ax.set_xlabel('Time (BJD - 2,455,000)')
    ax.set_ylabel('Delta Time (30 minute cadences)')

    # (3) Exclude points adjacent to gaps; robust-scale |ΔF|
    mask1 = np.ones(deltaFlux.size, dtype=bool)
    if idxA.size:
        mask1[idxA] = False
    if idxB.size:
        mask1[idxB] = False
    deltaFluxMasked = deltaFlux[mask1]
    timeMasked = tmid[mask1]

    deltaFluxMaskedAbsolute = np.abs(deltaFluxMasked)
    std_deltaFluxMaskedAbsolute = np.nanstd(deltaFluxMaskedAbsolute)
    if (not np.isfinite(std_deltaFluxMaskedAbsolute)) or (std_deltaFluxMaskedAbsolute == 0):
        std_deltaFluxMaskedAbsolute = 1.0
    deltaFluxScaled = deltaFluxMaskedAbsolute / std_deltaFluxMaskedAbsolute

    # Thresholds for ledge detection (avoid single-point outliers)
    deltaFluxScaledThreshold_1 = 8
    deltaFluxScaledThreshold_2 = 5

    mask2 = np.ones(deltaFluxScaled.size, dtype=bool)
    mask2[deltaFluxScaled < deltaFluxScaledThreshold_1] = False

    singleOutlierCount = 0
    for ii in range(1, len(mask2) - 1):
        if mask2[ii]:
            if (deltaFluxScaled[ii - 1] > deltaFluxScaledThreshold_2) or (deltaFluxScaled[ii + 1] > deltaFluxScaledThreshold_2):
                mask2[ii] = False
                mask2[ii - 1] = False
                mask2[ii + 1] = False
                singleOutlierCount += 1

    possibleLedgeCount = int(np.sum(mask2))
    print('Possible Ledge Count = ' + str(possibleLedgeCount))
    deltaFluxPossibleLedge = deltaFluxScaled[mask2]
    timePossibleLedge = timeMasked[mask2]

    ax = figNewJumpDetector.add_subplot(313)
    ax.scatter(timeMasked / days2sec - 55000, deltaFluxScaled, color='blue')
    if possibleLedgeCount > 0:
        ax.scatter(timePossibleLedge / days2sec - 55000, deltaFluxPossibleLedge, color='red')
    ax.set_xlabel('Time (BJD - 2,455,000)')
    ax.set_ylabel('Scaled Absolute Delta Flux')

    plt.show(block=False)

    # Atlas of potential ledges
    figPossibleLedges = plt.figure(figsize=(25, 9))
    figPossibleLedges.suptitle(SystemName + ' ' + DetrendingName + ' possible ledges')
    plot_rows = max(1, math.ceil(possibleLedgeCount ** 0.5))
    plot_columns = max(1, math.ceil(possibleLedgeCount ** 0.5))
    ledgeDuration = 24 * hours2sec

    for ii in range(possibleLedgeCount):
        ax = figPossibleLedges.add_subplot(plot_rows, plot_columns, ii + 1)
        timeIndividualLedge = timeArray[(timeArray > timePossibleLedge[ii] - ledgeDuration / 2) &
                                        (timeArray < timePossibleLedge[ii] + ledgeDuration / 2)]
        fluxIndividualLedge = fluxArray[(timeArray > timePossibleLedge[ii] - ledgeDuration / 2) &
                                        (timeArray < timePossibleLedge[ii] + ledgeDuration / 2)]
        ax.scatter(timeIndividualLedge / days2sec - 55000, fluxIndividualLedge)
        if fluxIndividualLedge.size:
            ax.set_ylim([np.min(fluxIndividualLedge), np.max(fluxIndividualLedge)])
        ax.set_xlabel('Time (BJD - 2,455,000)')
        ax.set_ylabel('Flux')

    base_root = _resolve_base_dir(None)
    folder_path = base_root / "LightCurves" / "Figures" / DetrendingName
    _ensure_parent(folder_path / "dummy.txt")
    figPossibleLedges.savefig(folder_path / f'{SystemName}_{DetrendingName}_potentialLedges.png',
                              bbox_inches='tight')


def Detrending_FindDeepestPoints(timeArray, fluxArray, SystemName, DetrendingName, base_dir=None):
    '''
    Functionality:
        Identify and visualize the N deepest flux excursions in a detrended light
        curve. For each deepest point found, plot a fixed-width window centered on
        that time, and (optionally) append those epochs to a CSV list for later
        inspection across targets that share the same detrending configuration.

    Arguments:
        timeArray (array-like): Time stamps in seconds (BJD), aligned with flux.
        fluxArray (array-like): Detrended flux array (same length as timeArray).
        SystemName (str): Identifier used in figure titles and CSV rows.
        DetrendingName (str): Secondary label used for figure/CSV output paths.
        base_dir (str|pathlib.Path or None): Root of the repo/data tree. If None, uses CWD.

    Returns:
        None
            (Saves a figure of the deepest windows and appends a CSV with the
            deepest-point epochs in days: ../LightCurves/Cuts/<DetrendingName>_deepest_point_list.csv)
    '''
    # Also make a plot of just the 9 deepest flux events in the final lightcurve.
    deepPointDuration = 24 * hours2sec
    deepPointCount = 9
    figDeepestPoints = plt.figure(figsize=(25, 9))
    figDeepestPoints.suptitle(SystemName + ' ' + DetrendingName + ' deepest points')
    plot_rows = math.ceil(deepPointCount**0.5)
    plot_columns = math.ceil(deepPointCount**0.5)
    timeTemp = np.copy(timeArray)
    fluxTemp = np.copy(fluxArray)
    timeDeepList = np.array([])

    for ii in range(0, deepPointCount):
        indexDeepest = np.argmin(fluxTemp)
        timeDeepest = timeTemp[indexDeepest]
        timeDeepList = np.append(timeDeepList, timeDeepest)
        timePlot = timeTemp[(timeTemp > timeDeepest - deepPointDuration/2) & (timeTemp < timeDeepest + deepPointDuration/2)]
        fluxPlot = fluxTemp[(timeTemp > timeDeepest - deepPointDuration/2) & (timeTemp < timeDeepest + deepPointDuration/2)]

        ax = figDeepestPoints.add_subplot(plot_rows, plot_columns, ii+1)
        ax.scatter(timePlot/days2sec-55000, fluxPlot, color='red')
        ax.set_ylim([np.min(fluxPlot), np.max(fluxPlot)])
        ax.set_xlabel('Time (BJD - 2,455,000)')
        ax.set_ylabel('Flux')

        # Prevent picking the same neighborhood again
        fluxTemp[(timeTemp > timeDeepest - deepPointDuration/2) & (timeTemp < timeDeepest + deepPointDuration/2)] = np.ones(fluxPlot.size)

    # Append deepest times (in days) to a common CSV for this detrending name
    addToFalsePositiveList = True
    base_root = _resolve_base_dir(None)
    if (addToFalsePositiveList == True):
        deepPointFilename = base_root / 'LightCurves' / 'Cuts' / f'{DetrendingName}_deepest_point_list.csv'
        _ensure_parent(deepPointFilename)
        with open(deepPointFilename, "a+") as f:
            for ii in range(0, deepPointCount):
                f.write(SystemName + "," + str(timeDeepList[ii]/days2sec-55000) + "\n")

    # Save the figure
    folder_path = base_root / "LightCurves" / "Figures" / DetrendingName
    _ensure_parent(folder_path / "dummy.txt")
    figDeepestPoints.savefig(folder_path / f'{SystemName}_{DetrendingName}_deepestPoints.png', bbox_inches='tight')


def Detrending_PlotSpecificTimes(timeArray, fluxArray, SystemName, DetrendingName, base_dir=None):
    '''
    Functionality:
        Plot fixed windows around a user-provided list of specific epochs
        (e.g., suspected transits) on the detrended light curve for quick
        visual inspection.

    Arguments:
        timeArray (array-like): Time stamps in seconds (BJD), aligned with flux.
        fluxArray (array-like): Detrended flux array.
        SystemName (str): Identifier used in figure titles.
        DetrendingName (str): Label used for output directory and file names.
        base_dir (str|pathlib.Path or None): Root of the repo/data tree. If None, uses CWD.

    Returns:
        None
            (Saves panel plots to ../LightCurves/Figures/<DetrendingName>/
             <SystemName>_<DetrendingName>_specificTimes.png)
    '''
    # Plot specific tranists (example list for Kepler-38)
    showSpecificTransitTimes = 1
    if (showSpecificTransitTimes == 1):
        TT_specific = (np.array([36,140.5,243.8,347.6,451.9,659.7,762.3,867.4,969.7,1074.9,1176.9,1282.4,1384.3]) + 55000) * days2sec
        numSpecificTransits = len(TT_specific)
        fig = plt.figure(figsize=(25, 9))
        fig.suptitle(SystemName + " " + DetrendingName + " Specific Transit Times (User Set)")
        plot_rows = math.ceil(numSpecificTransits**0.5)
        plot_columns = math.ceil(numSpecificTransits**0.5)

        plot_horizontalWindowWidth = 6 * hours2sec * 7

        for ii in range(0, numSpecificTransits):
            ax = fig.add_subplot(plot_rows, plot_columns, ii+1)
            ax.set_xlabel('Time (BJD - 2,455,000)')
            ax.set_ylabel('Flux')

            individualTransit_timeFinal = timeArray[(timeArray > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeArray < TT_specific[ii] + plot_horizontalWindowWidth/2)]
            individualTransit_fluxFinal = fluxArray[(timeArray > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeArray < TT_specific[ii] + plot_horizontalWindowWidth/2)]

            medianfluxFinal = np.median(individualTransit_fluxFinal)

            if (len(individualTransit_fluxFinal) > 0):
                ax.plot(individualTransit_timeFinal/days2sec-55000, individualTransit_fluxFinal - medianfluxFinal, color='red')

        base_root = _resolve_base_dir(None)
        folder_path = base_root / "LightCurves" / "Figures" / DetrendingName
        _ensure_parent(folder_path / "dummy.txt")
        fig.savefig(folder_path / f'{SystemName}_{DetrendingName}_specificTimes.png', bbox_inches='tight')


def DetrendLightCurve(timeOrig, fluxOrig, window_length=1, method='biweight', plot_results=False):
    '''
    Functionality:
        Wrapper around `wotan.flatten` to detrend a light curve with a chosen
        filter (e.g., 'biweight', 'lowess', 'cosine', 'gp'). Returns the flattened
        flux and the fitted trend on the original time grid.

    Arguments:
        timeOrig (array-like): Time stamps (seconds, BJD).
        fluxOrig (array-like): Flux values aligned with `timeOrig`.
        window_length (float): Window length **in days** passed to wotan.
        method (str): Detrending method (e.g., 'biweight', 'lowess', 'cosine', 'gp').
        plot_results (bool): If True, show a quick overlay of original, trend, and flattened.

    Returns:
        tuple:
            timeDetrended (np.ndarray): Same as input `timeOrig`.
            fluxDetrended (np.ndarray): Flattened (detrended) flux.
            trend (np.ndarray): Estimated trend that was removed.
    '''

    timeDetrended = np.copy(timeOrig)
    fluxDetrended = np.copy(fluxOrig)

    if (method == 'gp'):
        fluxDetrended, trend = wotan.flatten(timeOrig/days2sec-55000, fluxOrig,
                                             window_length=window_length, method=method,
                                             kernel='periodic_auto', kernel_size=5, return_trend=True)
    elif (method == 'cosine'):
        fluxDetrended, trend = wotan.flatten(timeOrig/days2sec-55000, fluxOrig,
                                             window_length=window_length, method=method,
                                             robust=True, break_tolerance=0.5, return_trend=True)
    else:
        fluxDetrended, trend = wotan.flatten(timeOrig/days2sec-55000, fluxOrig,
                                             window_length=window_length, method=method,
                                             break_tolerance=0.5, return_trend=True)

    timeDetrended = timeOrig

    if (plot_results == True):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(timeOrig/days2sec-55000, fluxOrig, linewidth=1, color='black')
        ax.plot(timeDetrended/days2sec-55000, fluxDetrended, linewidth=1, color='red')
        ax.plot(timeDetrended/days2sec-55000, trend, linewidth=2, color='green')

    return timeDetrended, fluxDetrended, trend


def Search_FitTransitMask(timeArray, fluxArray, TT_search, TD_search, meanTotalLightcurve, cadence,
                          plotting=False, mission='BLAH', ID="BLAH", SearchName='BLAH', base_dir=None):
    '''
    Functionality:
        Evaluate a set of candidate transit times/durations against a light curve
        to (a) locate local minima windows, (b) measure per-transit mean depth and
        significance, and (c) aggregate a global detection statistic and basic
        consistency metrics. Optionally produces diagnostic plots and saves summary
        figures for later inspection.

    Arguments:
        timeArray (array-like): Time stamps [s], sorted.
        fluxArray (array-like): Flux values aligned with `timeArray`.
        TT_search (array-like): Candidate mid-transit epochs [s].
        TD_search (array-like): Candidate transit durations [s] for each epoch.
        meanTotalLightcurve (float): Global reference mean flux (for plotting/baseline).
        cadence (float): Sampling cadence [s] used inside the search windowing.
        plotting (bool): If True, generate and save diagnostic figures.
        mission (str): Mission label used in filenames.
        ID (str): Target identifier used in filenames.
        SearchName (str): Output directory tag under ../PlanetSearchOutput/.
        base_dir (str|pathlib.Path or None): Root of the repo/data tree. If None, uses CWD.

    Returns:
        tuple:
            meanFlux (float), detectionSigmaOld (float), detectionSigmaNew (float),
            detectionConsistency (int), fractionDataPointsHit (float),
            TT_true (np.ndarray), stdOutOfTransit (float)
    '''

    # Coerce inputs to arrays
    timeArray = np.asarray(timeArray, dtype=float)
    fluxArray = np.asarray(fluxArray, dtype=float)
    TT_search = np.asarray(TT_search, dtype=float)
    TD_search = np.asarray(TD_search, dtype=float)

    transitDurationAllowance = 1.0
    consistencyThreshold = 3
    consistencySigmaFactor = 0.45
    fractionDataPointsHitThreshold = 0.45
    fractionIndividualTransitsDataPointsHit = 0.75
    individualDataPointSigmaCutThreshold = 3
    minimaType = 6
    cutDuringSearch = True

    # Output dir (create only if plotting AND names are meaningful)
    outdir = None
    if plotting and isinstance(SearchName, str) and SearchName.strip() not in ("", "BLAH"):
        base_root = _resolve_base_dir(None)
        outdir = (base_root / 'PlanetSearchOutput' / str(SearchName)).resolve()
        outdir.mkdir(parents=True, exist_ok=True)

    if TT_search.size == 0:
        if plotting:
            print("[WARN] No TT_search provided; skipping plots.")
        _meanFlux = meanTotalLightcurve
        return (_meanFlux, 0.0, 0.0, 0, 0.0, np.array([]), float(np.nan))

    # Mean interval estimate (for folding helpers)
    if TT_search.size >= 3:
        meanPlanetTransitInterval = float(np.mean(TT_search[1:-1] - TT_search[0:-2]))
        if not np.isfinite(meanPlanetTransitInterval) or meanPlanetTransitInterval <= 0:
            meanPlanetTransitInterval = float(np.nan)
    else:
        meanPlanetTransitInterval = float(np.nan)

    # Plot containers
    if plotting:
        fig1 = plt.figure(figsize=(30, 14))
        fig2 = plt.figure(figsize=(30, 14))
        root = int(math.ceil(TT_search.size ** 0.5))
        plot_rows = max(1, root)
        plot_columns = max(1, root)
        totalWindowTime = np.array([], dtype=float)
        scaledWindowTime = np.array([], dtype=float)
        plot_yMax1 = -np.inf
        plot_yMin1 = np.inf
        plot_yMax2 = -np.inf
        plot_yMin2 = np.inf
    else:
        totalWindowTime = np.array([], dtype=float)
        scaledWindowTime = np.array([], dtype=float)
        plot_yMax1 = plot_yMin1 = plot_yMax2 = plot_yMin2 = 0.0

    TT_true = np.zeros_like(TT_search, dtype=float)
    individualTransitMeanFluxArray = []
    individualTransitSigmaArray = []
    individualTransitDataPointCountArray = []
    hittingAGapCount = 0

    allOutOfTransitFlux = np.array(fluxArray, copy=True)
    allOutOfTransitTime = np.array(timeArray, copy=True)
    totalWindowFlux = np.array([], dtype=float)

    global_std_flux = float(np.nanstd(fluxArray)) if fluxArray.size else float("nan")

    # Per-transit loop
    for ii in range(TT_search.size):
        modifiedTD = TD_search[ii] * transitDurationAllowance
        searchWindowHalfWidth = modifiedTD / 2.0

        in9 = (timeArray < TT_search[ii] + 9.0 * searchWindowHalfWidth) & (timeArray > TT_search[ii] - 9.0 * searchWindowHalfWidth)
        in3 = (timeArray < TT_search[ii] + 3.0 * searchWindowHalfWidth) & (timeArray > TT_search[ii] - 3.0 * searchWindowHalfWidth)

        widerWindow_time = timeArray[in9]
        widerWindow_flux = fluxArray[in9]

        combinedWindows_time = timeArray[in3]
        combinedWindows_flux = fluxArray[in3]

        # No data in search window
        if combinedWindows_flux.size == 0:
            TT_true[ii] = round(TT_search[ii] / days2sec) * days2sec
            hittingAGapCount += 1
            individualTransitMeanFluxArray.append(0.0)
            individualTransitDataPointCountArray.append(0)
            individualTransitSigmaArray.append(0.0)
            if plotting:
                _ = fig1.add_subplot(plot_rows, plot_columns, ii + 1)
                _ = fig2.add_subplot(plot_rows, plot_columns, ii + 1)
            continue

        # Outlier clip
        combinedWindows_std = float(np.nanstd(combinedWindows_flux))
        combinedWindows_mean = float(np.nanmean(combinedWindows_flux))
        if not np.isfinite(combinedWindows_std) or combinedWindows_std == 0.0:
            mask_good = np.isfinite(combinedWindows_flux)
        else:
            mask_good = np.abs(combinedWindows_flux - combinedWindows_mean) < individualDataPointSigmaCutThreshold * combinedWindows_std

        combinedWindows_time = combinedWindows_time[mask_good]
        combinedWindows_flux = combinedWindows_flux[mask_good]

        if combinedWindows_flux.size == 0:
            TT_true[ii] = round(TT_search[ii] / days2sec) * days2sec
            hittingAGapCount += 1
            individualTransitMeanFluxArray.append(0.0)
            individualTransitDataPointCountArray.append(0)
            individualTransitSigmaArray.append(0.0)
            if plotting:
                _ = fig1.add_subplot(plot_rows, plot_columns, ii + 1)
                _ = fig2.add_subplot(plot_rows, plot_columns, ii + 1)
            continue

        # Find deepest window around the candidate
        tempTime, tempFlux, meanUsed, outOfTransitTime, outOfTransitFlux, ratioInOutTransitPoints = Search_IndividualTransitRelativeFlux(
            combinedWindows_time, combinedWindows_flux, TT_search[ii], modifiedTD, minimaType, -27, cadence
        )
        tempTime = np.asarray(tempTime, dtype=float)
        tempFlux = np.asarray(tempFlux, dtype=float)
        outOfTransitTime = np.asarray(outOfTransitTime, dtype=float)
        outOfTransitFlux = np.asarray(outOfTransitFlux, dtype=float)

        if tempTime.size > 0:
            TT_true[ii] = float(np.nanmean(tempTime))
            keep = np.logical_or(allOutOfTransitTime < tempTime[0], allOutOfTransitTime > tempTime[-1])
            allOutOfTransitFlux = allOutOfTransitFlux[keep]
            allOutOfTransitTime = allOutOfTransitTime[keep]
        else:
            TT_true[ii] = round(TT_search[ii] / days2sec) * days2sec

        # Inclusion test
        includeTransit = False
        if tempFlux.size > 0:
            denom = (TD_search[ii] / (29.4 * 60.0)) if TD_search[ii] > 0 else np.inf
            points_per_TD = (tempFlux.size / denom) if np.isfinite(denom) and denom > 0 else 0.0
            if (points_per_TD >= fractionIndividualTransitsDataPointsHit) and (ratioInOutTransitPoints <= 1):
                includeTransit = True

        if includeTransit:
            mean_tempFlux = float(np.nanmean(tempFlux))
            individualTransitMeanFluxArray.append(mean_tempFlux)
            totalWindowFlux = np.append(totalWindowFlux, tempFlux)
            individualTransitDataPointCountArray.append(int(tempFlux.size))

            ostd = float(np.nanstd(outOfTransitFlux)) if outOfTransitFlux.size > 1 else global_std_flux
            if not np.isfinite(ostd) or ostd == 0.0:
                ostd = global_std_flux if np.isfinite(global_std_flux) and global_std_flux > 0 else 1.0
            sigma_here = (abs(mean_tempFlux / ostd) * (tempFlux.size ** 0.5)) if ostd > 0 else 0.0
            individualTransitSigmaArray.append(float(sigma_here))

            totalWindowTime = np.append(totalWindowTime, tempTime)
            if tempTime.size > 1 and tempTime[-1] != tempTime[0]:
                scaled = ((tempTime - tempTime[0]) / (tempTime[-1] - tempTime[0]) - 0.5) * 2 * transitDurationAllowance
                scaledWindowTime = np.append(scaledWindowTime, scaled)

        else:
            hittingAGapCount += 1
            individualTransitMeanFluxArray.append(0.0)
            individualTransitDataPointCountArray.append(0)
            individualTransitSigmaArray.append(0.0)

        # Diagnostics per transit
        if plotting:
            ax1 = fig1.add_subplot(plot_rows, plot_columns, ii + 1)
            ax2 = fig2.add_subplot(plot_rows, plot_columns, ii + 1)

            if widerWindow_time.size and widerWindow_flux.size:
                ax2.scatter(widerWindow_time / days2sec - 55000, widerWindow_flux - meanUsed,
                            color=np.array([176, 239, 255]) / 255.0, s=10)

            if combinedWindows_time.size and combinedWindows_flux.size:
                ax1.scatter(combinedWindows_time / days2sec - 55000, combinedWindows_flux - meanUsed, color='b', s=20)
                ax2.scatter(combinedWindows_time / days2sec - 55000, combinedWindows_flux - meanUsed, color='b', s=20)
                try:
                    cmax = float(np.nanmax(combinedWindows_flux - meanUsed))
                    cmin = float(np.nanmin(combinedWindows_flux - meanUsed))
                    if np.isfinite(cmax): plot_yMax1 = max(plot_yMax1, cmax)
                    if np.isfinite(cmin): plot_yMin1 = min(plot_yMin1, cmin)
                except ValueError:
                    pass

            if tempTime.size and tempFlux.size:
                ax1.scatter(tempTime / days2sec - 55000, tempFlux, color='r', s=40)
                ax2.scatter(tempTime / days2sec - 55000, tempFlux, color='r', s=10)
            elif tempTime.size and tempFlux.size == 0:
                ax1.scatter(tempTime / days2sec - 55000, tempFlux, color='k', s=40)
                ax2.scatter(tempTime / days2sec - 55000, tempFlux, color='k', s=10)

            plt.xticks(fontsize=8); plt.yticks(fontsize=8)
            if np.isfinite(plot_yMin1) and np.isfinite(plot_yMax1) and plot_yMax1 > plot_yMin1:
                ax1.set_ylim([plot_yMin1, plot_yMax1])
            else:
                pad = 3.0 * (global_std_flux if np.isfinite(global_std_flux) and global_std_flux > 0 else 1e-3)
                ax1.set_ylim([meanTotalLightcurve - pad, meanTotalLightcurve + pad])

    # Aggregation
    individualTransitMeanFluxArray = np.asarray(individualTransitMeanFluxArray, dtype=float)
    individualTransitSigmaArray = np.asarray(individualTransitSigmaArray, dtype=float)
    stdOutOfTransit = float(np.nanstd(allOutOfTransitFlux)) if allOutOfTransitFlux.size else float("nan")

    has_any_transit = (individualTransitMeanFluxArray.size > 0) and (np.nanmax(np.abs(individualTransitMeanFluxArray)) > 0)

    if has_any_transit:
        total_points = int(np.sum(individualTransitDataPointCountArray))
        denom_std = stdOutOfTransit if (np.isfinite(stdOutOfTransit) and stdOutOfTransit > 0) \
                    else (global_std_flux if np.isfinite(global_std_flux) and global_std_flux > 0 else 1.0)
        mean_totalWindowFlux = float(np.nanmean(totalWindowFlux)) if totalWindowFlux.size else 0.0
        detectionSigmaOld = abs(mean_totalWindowFlux / denom_std) * (total_points ** 0.5) if total_points > 0 else 0.0
        detectionSigmaNew = float(np.sqrt(np.nansum(np.square(individualTransitSigmaArray))))

        max_sig = float(np.nanmax(individualTransitSigmaArray)) if individualTransitSigmaArray.size else 0.0
        thresholdSigma = consistencySigmaFactor * max_sig
        valid_count_mask = np.asarray(individualTransitDataPointCountArray) > 0
        denom_count = int(np.sum(valid_count_mask))
        detectionConsistency = int(np.sum(individualTransitSigmaArray[valid_count_mask] > thresholdSigma)) if denom_count > 0 else 0

        expectedMaxNumberDataPoints = 0.0
        for ii in range(TT_search.size):
            expectedMaxNumberDataPoints += (TD_search[ii] / (29.4 * 60.0)) if TD_search[ii] > 0 else 0.0
        fractionDataPointsHit = (float(totalWindowFlux.size) / expectedMaxNumberDataPoints) if expectedMaxNumberDataPoints > 0 else 0.0

        _meanFlux = float(np.nanmean(totalWindowFlux)) if totalWindowFlux.size else meanTotalLightcurve

        if cutDuringSearch:
            acceptSolution = True
            if detectionConsistency < consistencyThreshold:
                acceptSolution = False
            if fractionDataPointsHit < fractionDataPointsHitThreshold:
                acceptSolution = False
            if not acceptSolution:
                _meanFlux = meanTotalLightcurve
                detectionSigmaOld = 0.0
                detectionSigmaNew = 0.0
                detectionConsistency = 0
                fractionDataPointsHit = 0.0
    else:
        _meanFlux = meanTotalLightcurve
        detectionSigmaOld = 0.0
        detectionSigmaNew = 0.0
        detectionConsistency = 0.0
        fractionDataPointsHit = 0.0

    # Optional summary plots
    if plotting:

        def _safe_ylim(ax, yvals, default_center, default_pad):
            if yvals.size:
                ymin = float(np.nanmin(yvals))
                ymax = float(np.nanmax(yvals))
                if np.isfinite(ymin) and np.isfinite(ymax) and ymax > ymin:
                    ax.set_ylim([ymin, ymax])
                    return
            pad = 3.0 * (default_pad if np.isfinite(default_pad) and default_pad > 0 else 1e-3)
            ax.set_ylim([default_center - pad, default_center + pad])

        fig_big = plt.figure(figsize=(30, 5))

        # Left: raw windowed points
        ax = fig_big.add_subplot(131)
        ax.set_xlabel('Time (BJD - 2,455,000)')
        ax.set_ylabel('Raw phase-folded flux')
        if totalWindowTime.size and totalWindowFlux.size:
            n = min(totalWindowTime.size, totalWindowFlux.size)
            if n > 0:
                ax.scatter(totalWindowTime[:n] / days2sec - 55000, totalWindowFlux[:n] + meanTotalLightcurve, s=10)
                _safe_ylim(ax, totalWindowFlux + meanTotalLightcurve if totalWindowFlux.size else np.array([]),
                           meanTotalLightcurve, global_std_flux)

        # Middle: scaled duration vs flux
        ax = fig_big.add_subplot(132)
        ax.set_xlabel('Time (scaled transit duration)', fontsize=20)
        ax.set_ylabel('Flux', fontsize=20)
        if np.isfinite(meanPlanetTransitInterval):
            print(f'meanPlanetTransitInterval (sec): {meanPlanetTransitInterval}')
            ax.scatter((timeArray / days2sec - 55000) % (meanPlanetTransitInterval / days2sec) - 1.5, fluxArray, s=1)
        if scaledWindowTime.size and totalWindowFlux.size:
            n = min(scaledWindowTime.size, totalWindowFlux.size)
            print(f'scaledWindowTime size: {scaledWindowTime.size}, totalWindowFlux size: {totalWindowFlux.size}')
            ax.scatter(scaledWindowTime[:n], totalWindowFlux[:n] + meanTotalLightcurve, s=40)
        _safe_ylim(ax, totalWindowFlux + meanTotalLightcurve if totalWindowFlux.size else np.array([]),
                   meanTotalLightcurve, global_std_flux)
        ax.set_xlim([-1.5, 1.5])
        plt.xticks(fontsize=8); plt.yticks(fontsize=8)

        # Right: mean scaled profile
        ax = fig_big.add_subplot(133)
        ax.set_xlabel('Time (transit duration)')
        ax.set_ylabel('Mean scaled phase-folded flux')
        if scaledWindowTime.size and totalWindowFlux.size:
            meanScaledFlux_numPoints = 15
            meanScaledFlux_time = np.linspace(-1 * transitDurationAllowance, 1 * transitDurationAllowance, meanScaledFlux_numPoints)
            meanScaledFlux = np.zeros_like(meanScaledFlux_time)
            for jj in range(1, meanScaledFlux_numPoints):
                inbin = (scaledWindowTime > meanScaledFlux_time[jj - 1]) & (scaledWindowTime < meanScaledFlux_time[jj])
                meanScaledFlux[jj] = np.nan if not np.any(inbin) else float(np.nanmean(totalWindowFlux[inbin]))
            meanScaledFlux = meanScaledFlux[1:]
            meanScaledFlux_time = meanScaledFlux_time[1:] - (meanScaledFlux_time[1] - meanScaledFlux_time[0]) / 2.0
            print(f'meanScaledFlux_time size: {meanScaledFlux_time.size}, meanScaledFlux size: {meanScaledFlux.size}')
            ax.plot(meanScaledFlux_time, meanScaledFlux + meanTotalLightcurve)
            ax.plot([-1 * transitDurationAllowance, 1 * transitDurationAllowance], [1., 1.], '--')
            _safe_ylim(ax, meanScaledFlux + meanTotalLightcurve, meanTotalLightcurve, global_std_flux)
        else:
            ax.plot([-1 * transitDurationAllowance, 1 * transitDurationAllowance], [1., 1.], '--')

        plt.show(block=False)

        # Save summary figs (only if outdir is valid)
        if outdir is not None:
            fig_big.savefig((outdir / f'{mission}_{ID}_FoldedPlanetTransits.png'), bbox_inches='tight')

        # Depth/sigma per transit
        fig_depth = plt.figure(figsize=(8, 4))
        transitIndex = np.arange(individualTransitMeanFluxArray.size)

        ax = fig_depth.add_subplot(121)
        ax.set_xlabel('Transit Number')
        ax.set_ylabel('Individual transit depth (flux dip)')
        if individualTransitMeanFluxArray.size:
            ax.scatter(transitIndex, individualTransitMeanFluxArray, label='Normal data')
            if np.any(individualTransitMeanFluxArray == 0):
                ax.scatter(transitIndex[individualTransitMeanFluxArray == 0],
                           individualTransitMeanFluxArray[individualTransitMeanFluxArray == 0], label='Hit a gap')
            _safe_ylim(ax, individualTransitMeanFluxArray, 0.0, np.nanstd(individualTransitMeanFluxArray))
            ax.legend()
        plt.show(block=False)

        ax = fig_depth.add_subplot(122)
        ax.set_xlabel('Transit Number')
        ax.set_ylabel('Individual transit depth (sigma)')
        if individualTransitSigmaArray.size:
            ax.scatter(transitIndex, individualTransitSigmaArray, label='Normal data')
            if np.any(np.asarray(individualTransitDataPointCountArray) == 0):
                ax.scatter(transitIndex[np.asarray(individualTransitDataPointCountArray) == 0],
                           individualTransitSigmaArray[np.asarray(individualTransitDataPointCountArray) == 0], label='Hit a gap')
            ymin, ymax = 0.0, float(np.nanmax(individualTransitSigmaArray)) + 0.1 if np.isfinite(np.nanmax(individualTransitSigmaArray)) else 1.0
            ax.set_ylim([ymin, ymax])
            ax.legend()
        plt.show(block=False)

        if outdir is not None:
            fig_depth.savefig((outdir / f'{mission}_{ID}_IndividualTransitDepths.png'), bbox_inches='tight')
            if 'fig1' in locals():
                fig1.savefig((outdir / f'{mission}_{ID}_IndividualPlanetTransits.png'), bbox_inches='tight')
            if 'fig2' in locals():
                fig2.savefig((outdir / f'{mission}_{ID}_IndividualPlanetTransitsWiderWindow.png'), bbox_inches='tight')

        if totalWindowTime.size != totalWindowFlux.size:
            print(f"[WARN] totalWindowTime ({totalWindowTime.size}) != totalWindowFlux ({totalWindowFlux.size}); "
                  f"used min length for summary scatters.")

    return (_meanFlux, float(detectionSigmaOld), float(detectionSigmaNew),
            int(detectionConsistency), float(fractionDataPointsHit), TT_true, stdOutOfTransit)


def Search_CreateTransitMask(
    z, RA, RB, timeArray, fluxArray,
    returnTransitTimes=True, meanTotalLightcurve=-27,
    plotting=False, mission='BLAH', ID='BLAH',
    SearchName='BLAH', maxCompTime=1
):
    '''
    Functionality:
        Build an N-body (rebound) simulation of a circumbinary system from the
        packed parameter vector `z`, predict planet transit times/durations
        across the observation window, and score the match to the light curve
        using Search_FitTransitMask. Handles stability and time-limit exits.

    Arguments:
        z (sequence[float]): Packed parameters
            [mA, mB, Pbin, ebin, omegabin, thetabin, Pp, ep, omegap, thetap].
        RA (float): Primary-star radius (meters) for impact/duration model.
        RB (float): Secondary-star radius (meters) for impact/duration model.
        timeArray (array-like): Observation times [seconds].
        fluxArray (array-like): Normalized flux values aligned to timeArray.
        returnTransitTimes (bool): If True, return TT_true & TD_search too.
        meanTotalLightcurve (float): Global flux mean used as baseline.
        plotting (bool): If True, pass through to Search_FitTransitMask plots.
        mission (str): Mission tag used in filenames/labels.
        ID (str): Target identifier used in filenames/labels.
        SearchName (str): Output directory name under PlanetSearchOutput/.
        maxCompTime (float): Max allowed compute time (seconds) for the
            transit-timing routine; if exceeded, returns sentinel scores.

    Returns:
        If stable and within time budget:
            [TT_true (np.ndarray), TD_search (np.ndarray),
             sigma_solutionOld (float), meanFlux_solution (float),
             stdOutOfTransit (float)]
        If unstable:
            [np.array([]), TD_search (np.ndarray with whatever was found),
             -27.0, 27.0, -27.0]
        If exceeded time limit:
            [np.array([]), TD_search (np.ndarray with whatever was found),
             -30.0, 30.0, -30.0]
    '''
    # z will be the mean window flux, which is what we are trying to minimise
    # params will be the orbital elements
    # Get the search parameters, which are all contained in 'z'
    _mA,_mB,_Pbin,_ebin,_omegabin,_thetabin,_Pp,_ep,_omegap,_thetap = z

    # Create the rebound sim
    timeStart = timeArray[0]
    timeEnd = timeArray[-1]

    searchSim = rebound.Simulation()
    searchSim.units = ('s','m','kg')
    mass = [_mA,_mB,0.]
    period = np.array([_Pbin,_Pp])
    a = PeriodToSemiMajorAxis(mass,period)
    searchSim.add(m=_mA,r=RA)
    searchSim.add(m=_mB,r=RB,a=a[0],e=_ebin,omega=_omegabin,theta=_thetabin)
    searchSim.add(a=a[1],e=_ep,omega=_omegap,theta=_thetap)
    searchSim.t = timeStart

    timerStart = TIME.time() # used to time a single n-body simulation
    # See if the data is 2 min or 30 min cadence (TESS or Kepler)
    sorted_timeArray = np.sort(np.copy(timeArray))
    cadence = min(np.diff(sorted_timeArray)) # Cadence is in seconds
    if cadence <= 100:
        raise Exception("Data passed in appears to be in days not seconds")
    try:
        transitData_search = SSTT.TransitTiming_nbody_lite(searchSim,timeEnd,cadence,maxCompTime=maxCompTime)
    except TimeoutError:
        print('Timeout spotted')
        transitData_search = {'transitTimes':np.array([]), 'transitDurations':np.array([]), 'stable':False, 'exceedMaxCompTime':True}

    timerEnd = TIME.time() # used to time a single n-body simulation

    # July 2024: Additional output "exceedMaxCompTime" was added to the output dictionary
    TT_search = transitData_search['transitTimes']
    TD_search = transitData_search['transitDurations']
    stable = transitData_search['stable']
    exceedMaxCompTime = transitData_search['exceedMaxCompTime']

    # July 2024: Add extra condition here. The system is considered unstable if the planet never transits
    if len(TT_search) == 0:
        stable = False

    # Score the model or return sentinels
    if (stable == True) and (exceedMaxCompTime == False):
        meanFlux_solution,sigma_solutionOld,sigma_solutionNew,consistency_solution,fractionDataPointsHit_solution,TT_true,stdOutOfTransit = Search_FitTransitMask(timeArray,fluxArray,TT_search,TD_search,meanTotalLightcurve,cadence,plotting=plotting,mission=mission,ID=ID,SearchName=SearchName)

    elif (stable == False):
        meanFlux_solution = 27
        sigma_solutionOld = -27
        sigma_solutionNew = -27
        consistency_solution = 0
        fractionDataPointsHit_solution = 0
        stdOutOfTransit = -27
        TT_true = np.array([])

    elif (exceedMaxCompTime == True):
        meanFlux_solution = 30
        sigma_solutionOld = -30
        sigma_solutionNew = -30
        consistency_solution = 0
        fractionDataPointsHit_solution = 0
        stdOutOfTransit = -30
        TT_true = np.array([])

    # Output selection
    if (returnTransitTimes == True):
        return [TT_true,TD_search,sigma_solutionOld,meanFlux_solution,stdOutOfTransit]
    else:
        return [sigma_solutionOld]


def Search_Create1dSDE(sigmaResults_1d, Pp_search, SearchName, mission, ID, base_dir=None):
    '''
    Functionality:
        Compute a 1-D Signal Detection Efficiency (SDE) curve from period-scanned
        detection statistics. Detrends σ(period) with a smooth trend (wotan
        biweight if available, else robust median smoother), then normalizes the
        residuals by a guarded standard deviation to produce SDE. Saves summary
        plots and returns the peak SDE and corresponding period.

    Arguments:
        sigmaResults_1d (array-like): Detection metric vs. tested period (σ).
        Pp_search (array-like): Tested planet periods [seconds], same length.
        SearchName (str): Output subfolder under ../PlanetSearchOutput/.
        mission (str): Mission string, used in filenames.
        ID (str): Target identifier string, used in filenames.
        base_dir (str|pathlib.Path or None): Root of the repo/data tree. If None, uses CWD.

    Returns:
        tuple:
            SDE_1d_max (float): Maximum SDE value.
            period_1d_max (float): Period [seconds] at which SDE is maximal.
    '''

    # Sanitize
    sigma  = np.asarray(sigmaResults_1d, dtype=float).copy()
    period = np.asarray(Pp_search,      dtype=float).copy()
    mask = np.isfinite(sigma) & np.isfinite(period) & (period > 0.0)
    sigma  = sigma[mask]
    period = period[mask]

    if sigma.size == 0:
        print("[SDE] No valid points after masking.")
        return -27.0, -27.0

    # replace sentinels with median of non-sentinels
    valid_for_med = np.isfinite(sigma) & (sigma != -27.0) & (sigma != -29.0)
    if not np.any(valid_for_med):
        print('Unstable or no valid sigma values to compute median from.')
        return -27.0, -27.0
    med = float(np.nanmedian(sigma[valid_for_med]))
    sigma[(sigma == -27.0) | (sigma == -29.0)] = med

    # tiny jitter if perfectly flat
    if np.nanstd(sigma) == 0:
        rng = np.random.default_rng(0)
        sigma = sigma + 1e-12 * rng.normal(size=sigma.size)

    # sort and collapse duplicate periods by median (helps wotan)
    order = np.argsort(period)
    period = period[order]
    sigma  = sigma[order]

    up, idx_start = np.unique(period, return_index=True)
    if up.size != period.size:
        sigma_new = np.empty_like(up, dtype=float)
        for i in range(up.size):
            a = idx_start[i]
            b = idx_start[i+1] if i+1 < up.size else period.size
            sigma_new[i] = np.nanmedian(sigma[a:b])
        period, sigma = up, sigma_new

    x_days = period / days2sec

    # Detrend: fixed 30-day biweight
    win_days = 30.0
    trend = None
    if wotan is not None:
        try:
            _, trend = wotan.flatten(
                x_days, sigma,
                window_length=win_days,
                method='biweight',
                return_trend=True,
                edge_cutoff=0.0,
                break_tolerance=None
            )
            # patch any NaNs in trend by interpolation (edges clamp)
            if np.any(~np.isfinite(trend)):
                good = np.isfinite(trend)
                trend = np.interp(x_days, x_days[good], trend[good]) if np.sum(good) >= 2 else None
        except Exception as e:
            print(f"[SDE] wotan failed ({e}); fallback median smoother.")
            trend = None

    if trend is None:
        # NaN-safe median-binned fallback
        nbins = int(np.clip(x_days.size//30, 30, 300)) if x_days.size >= 60 else max(10, x_days.size//3)
        edges = np.linspace(x_days.min(), x_days.max(), nbins+1)
        centers = 0.5*(edges[:-1] + edges[1:])
        medvals = np.full(nbins, np.nan)
        j0 = 0
        for i in range(nbins):
            a, b = edges[i], edges[i+1]
            while j0 < x_days.size and x_days[j0] < a:
                j0 += 1
            j = j0
            vals = []
            while j < x_days.size and x_days[j] <= b:
                vals.append(sigma[j]); j += 1
            if vals:
                medvals[i] = np.median(vals)
        good = np.isfinite(medvals)
        trend = np.interp(x_days, centers[good], medvals[good]) if np.sum(good) >= 2 else np.full_like(sigma, np.nanmedian(sigma))

    # SDE math with guardrails on the denominator
    SDE = sigma - trend

    # v1: initial std on full residuals
    initialSTD = float(np.std(SDE))
    if not np.isfinite(initialSTD):
        initialSTD = 0.0

    # v1: clip to ±2*initialSTD
    if initialSTD > 0.0:
        clip_mask = (SDE <  2.0*initialSTD) & (SDE > -2.0*initialSTD)
        clipped = SDE[clip_mask]
    else:
        clipped = SDE

    clipSTD = float(np.std(clipped)) if clipped.size else 0.0

    # Use clipped std only if it's representative; else fall back to initialSTD
    MIN_FRAC   = 0.30  # at least 30% of points must remain after clipping
    FLOOR_FRAC = 0.50  # clipSTD must be >= 0.5 * initialSTD

    use_clip = (
        np.isfinite(clipSTD)
        and (clipSTD > 0.0)
        and (clipped.size >= MIN_FRAC * max(1, SDE.size))
        and (initialSTD > 0.0) and (clipSTD >= FLOOR_FRAC * initialSTD)
    )

    denom = clipSTD if use_clip else (initialSTD if initialSTD > 0.0 else 1.0)
    SDE = SDE / denom

    # optional diagnostics
    print(f"[SDE diag] N={SDE.size} kept={clipped.size} ({clipped.size/max(1,SDE.size):.2%}) "
          f"initialSTD={initialSTD:.6g} clipSTD={clipSTD:.6g} "
          f"denom={'clipSTD' if use_clip else ('initialSTD' if initialSTD>0 else '1.0')} "
          f"max={np.nanmax(SDE):.3f}")

    SDE_1d_max    = float(np.nanmax(SDE))
    period_1d_max = float(period[np.nanargmax(SDE)])

    print(f"[SDE] Max={SDE_1d_max:.3f} at {period_1d_max/days2sec:.5f} d")

    # Plots
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(2,1,1)
    ax.set_xlabel('Tested planet period (days)')
    ax.set_ylabel('sigma_1d')
    ax.set_title('all ecc and omega')
    ax.plot(period/days2sec, sigma)
    ax.plot(period/days2sec, trend, linestyle='--', color='red')

    ax = fig.add_subplot(2,1,2)
    ax.set_xlabel('Tested planet period (days)')
    ax.set_ylabel('SDE_1d')
    ax.set_title('all ecc and omega')
    ax.text(0.8, 0.9, f"Max SDE = {SDE_1d_max:.3f}",
            horizontalalignment='center', transform=ax.transAxes,
            fontstyle='italic', fontsize=10)
    ax.plot(period/days2sec, SDE)

    base_root = _resolve_base_dir(None)
    outdir = base_root / 'PlanetSearchOutput' / str(SearchName)
    _ensure_parent(outdir / 'dummy.txt')
    fig.savefig(outdir / f'{ID}_{mission}SDE.png', bbox_inches='tight')

    figPaper = plt.figure(figsize=(18,6))
    axPaper = figPaper.add_subplot(111)
    axPaper.plot(period/days2sec, SDE, color='blue')
    axPaper.set_xlabel('Planet Period (days)', fontsize=20)
    axPaper.set_ylabel('Signal Detection Efficiency (SDE)', fontsize=20)
    axPaper.tick_params(axis="x", labelsize=16)
    axPaper.tick_params(axis="y", labelsize=16)
    figPaper.savefig(outdir / f'{ID}_{mission}SDEpaper.png', bbox_inches='tight')

    return SDE_1d_max, period_1d_max


def Search_CheckIfFinished(SearchName, ID, mission, TotalSectors, base_dir=None):
    '''
    Functionality:
        Verify whether all sector result arrays for a given search run have been
        written to disk. This checks for files named:
        ../PlanetSearchOutput/<SearchName>/<mission>_<ID>_searchResults_array_<TotalSectors>_<ii>.npy
        for ii = 1..TotalSectors.

    Arguments:
        SearchName (str): Output subfolder under ../PlanetSearchOutput/.
        ID (str): Target identifier used in filenames.
        mission (str): Mission tag used in filenames.
        TotalSectors (int): Total number of sectors expected.
        base_dir (str|pathlib.Path or None): Root of the repo/data tree. If None, uses CWD.

    Returns:
        bool:
            True if all sector files exist, False otherwise. Prints progress for
            existing sectors.
    '''
    # Look through the output folder to see if all sectors have been outputted
    base_root = _resolve_base_dir(None)
    searchFinished = True
    for ii in range(1,TotalSectors+1):
        filename = base_root / 'PlanetSearchOutput' / SearchName / f"{mission}_{ID}_searchResults_array_{TotalSectors}_{ii}.npy"
        if (os.path.exists(filename) == False):
            searchFinished = False
            break
        else:
            print('Sector #' + str(ii) + '/' + str(TotalSectors) + ' finished')
    return searchFinished


def Detrending_IterativeCosine_Test(
    timeOrig, fluxOrig, timeCut, fluxCut,
    timeCommonFalsePositivesRemoved, fluxCommonFalsePositivesRemoved,
    durationArray, SystemName, DetrendingName, mission, ID, base_dir=None
):
    '''
    Functionality:
        Diagnostic routine that sweeps cosine filter window settings around an
        example list of specific transit epochs. For each epoch, performs a
        Lomb–Scargle-based window-length suggestion (DoPeriodogram), applies a
        cosine detrend in segments, and saves comparison plots showing original,
        eclipse-cut, CFPR-cut, and cosine-detrended snippets.

    Arguments:
        timeOrig, fluxOrig (array-like): Original light curve [s], [flux].
        timeCut, fluxCut (array-like): After eclipse-removal light curve.
        timeCommonFalsePositivesRemoved, fluxCommonFalsePositivesRemoved (array-like):
            Light curve after removing common false positives.
        durationArray (array-like): Predicted transit-duration timeline [s].
        SystemName (str): Label used in figure titles.
        DetrendingName (str): Label used for output directory/filenames.
        mission (str): Mission label (passed into DoPeriodogram title).
        ID (str): Target identifier (passed into DoPeriodogram title).
        base_dir (str|pathlib.Path or None): Root of the repo/data tree. If None, uses CWD.

    Returns:
        tuple:
            timeCosineFiltered (np.ndarray): Concatenated detrended time array [s].
            fluxCosineFiltered (np.ndarray): Concatenated detrended flux.
            trendCosineFiltered (np.ndarray): Concatenated fitted trend.
            listTime (list): (NOTE: not defined inside; legacy return).
            listFlux (list): (NOTE: not defined inside; legacy return).
    '''
    base_root = _resolve_base_dir(None)
    folder_path = base_root / "LightCurves" / "ItCos_Testing"
    _ensure_parent(folder_path / "dummy.txt")

    TT_specific = (np.array([36,140.5,243.8,347.6,451.9,659.7,762.3,867.4,969.7,1074.9,1176.9,1282.4,1384.3]) + 55000) * days2sec # Kepler-38
    numSpecificTransits = len(TT_specific)
    plot_horizontalWindowWidth = 6 * hours2sec * 7 # Just a rough transit duration

    # Make an initial copy
    timeCosineFiltered = np.copy(timeCommonFalsePositivesRemoved)
    fluxCosineFiltered = np.copy(fluxCommonFalsePositivesRemoved)
    subplotCounter = 1
    sufficientDetrendingReached = False

    # Setup the plot
    figCosine = plt.figure(figsize=(20,10))
    figCosine.suptitle(SystemName)

    print('Running iterative cosine filter test')

    # sweep parameters
    multiMin=2.5
    multiMax=3
    transitDurationMultiplierArray =np.linspace(multiMin,multiMax,int((multiMax-multiMin) / (.125)) + 1)

    for ii in range(0,numSpecificTransits):
        subplotCounter = 1

        OrigIndividualTransit_timeFinal = timeOrig[(timeOrig > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeOrig < TT_specific[ii] + plot_horizontalWindowWidth/2)]
        OrigIndividualTransit_fluxFinal = fluxOrig[(timeOrig > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeOrig < TT_specific[ii] + plot_horizontalWindowWidth/2)]
        OrigIndividualTransit_meanFlux = np.mean(OrigIndividualTransit_fluxFinal)

        CutIndividualTransit_timeFinal = timeCut[(timeCut > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeCut < TT_specific[ii] + plot_horizontalWindowWidth/2)]
        CutIndividualTransit_fluxFinal = fluxCut[(timeCut > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeCut < TT_specific[ii] + plot_horizontalWindowWidth/2)]

        CommonFalsePositivesRemovedIndividualTransit_timeFinal = timeCommonFalsePositivesRemoved[(timeCommonFalsePositivesRemoved > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeCommonFalsePositivesRemoved < TT_specific[ii] + plot_horizontalWindowWidth/2)]
        CommonFalsePositivesRemovedIndividualTransit_fluxFinal = fluxCommonFalsePositivesRemoved[(timeCommonFalsePositivesRemoved > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeCommonFalsePositivesRemoved < TT_specific[ii] + plot_horizontalWindowWidth/2)]

        fig = plt.figure(figsize=(35,15))
        fig.suptitle(SystemName + " " + DetrendingName + " "+ str(TT_specific[ii]))
        ax = fig.add_subplot(351)
        ax.scatter(OrigIndividualTransit_timeFinal/days2sec-55000,OrigIndividualTransit_fluxFinal,color='b',label='Orig')
        ax.scatter(CutIndividualTransit_timeFinal/days2sec-55000,CutIndividualTransit_fluxFinal,color='g',label='Eclipses Cut')
        ax.scatter(CommonFalsePositivesRemovedIndividualTransit_timeFinal/days2sec-55000,CommonFalsePositivesRemovedIndividualTransit_fluxFinal,color='r',label='Common False Positives Cut')
        ax.set_xlabel('Time (days - 55000)')
        ax.set_ylabel('Flux')
        ax.legend()
        for transitDurationPercentage in ['max','75']:
            for transitDurationMultiplier in transitDurationMultiplierArray:
                print('transitDurationPercentage = ' + str(transitDurationPercentage) + ', transitDurationMultiplier = ' + str(transitDurationMultiplier))

                if (sufficientDetrendingReached == False):
                    cosineFilterWindowLength,fap_1perc,max_power = DoPeriodogram(timeCosineFiltered,fluxCosineFiltered,durationArray,figCosine,True,transitDurationPercentage,transitDurationMultiplier,'progressive',SystemName,DetrendingName,ID, mission,subplotCounter)
                    subplotCounter += 1
                    print('first')
                    # build cosine-detrended in segments
                    numSectors = 5
                    timeCosineFiltered = np.array([])
                    fluxCosineFiltered = np.array([])
                    trendCosineFiltered = np.array([])
                    sectorDataPoints = int(len(timeOrig)/numSectors)
                    print('second')

                    timeSegment = timeCommonFalsePositivesRemoved[ii*sectorDataPoints:(ii+1)*sectorDataPoints]/days2sec - 55000
                    fluxSegment = fluxCommonFalsePositivesRemoved[ii*sectorDataPoints:(ii+1)*sectorDataPoints]
                    text_trap = io.StringIO()
                    sys.stdout = text_trap
                    fluxCosineFilteredSegment, trendCosineFilteredSegment = wotan.flatten(time=timeSegment,flux=fluxSegment,method='cosine',robust=True,break_tolerance=0.5,window_length=cosineFilterWindowLength/days2sec,return_trend=True)
                    sys.stdout = sys.__stdout__
                    timeCosineFilteredSegment = timeSegment
                    timeCosineFiltered = np.append(timeCosineFiltered,(timeCosineFilteredSegment + 55000)*days2sec)
                    fluxCosineFiltered = np.append(fluxCosineFiltered,fluxCosineFilteredSegment)
                    trendCosineFiltered = np.append(trendCosineFiltered,trendCosineFilteredSegment)

                    CosIndividualTransit_time=timeCosineFiltered[(timeCosineFiltered > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeCosineFiltered < TT_specific[ii] + plot_horizontalWindowWidth/2)]
                    CosIndividualTransit_flux=fluxCosineFiltered[(timeCosineFiltered > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeCosineFiltered < TT_specific[ii] + plot_horizontalWindowWidth/2)]

                    ax=fig.add_subplot(3,5,subplotCounter)
                    ax.scatter(CommonFalsePositivesRemovedIndividualTransit_timeFinal/days2sec-55000,CommonFalsePositivesRemovedIndividualTransit_fluxFinal,color='b',label='Common False Positives Cut')
                    ax.scatter(CosIndividualTransit_time/days2sec-55000,CosIndividualTransit_flux,color='r',label='Cosine Detrended')
                    ax.set_xlabel('Time (days - 55000)')
                    ax.set_ylabel('Flux')
                    ax.set_title('%='+str(transitDurationPercentage)+"Mult="+str(transitDurationMultiplier))
                    ax.legend()
                    print('third')
                else:
                    #sufficientDetrendingReached = True
                    print('fourth')
                fig.savefig(folder_path / f"{SystemName}_{DetrendingName}TT={str(TT_specific[ii]/days2sec-55000)}.png", bbox_inches='tight')

    return timeCosineFiltered,fluxCosineFiltered,trendCosineFiltered,listTime,listFlux


def Detrending_TestCosine(
    timeOrig, fluxOrig, timeCut, fluxCut,
    timeCommonFalsePositivesRemoved, fluxCommonFalsePositivesRemoved,
    durationArray, SystemName, DetrendingName, K, base_dir=None
):
    '''
    Functionality:
        Evaluate iterative cosine detrending around a set of specific transit
        times and compare against pre-cut versions of the light curve. Produces
        multi-panel diagnostics per transit and saves figures for inspection.

    Arguments:
        timeOrig (array-like): Original time array [s].
        fluxOrig (array-like): Original flux array aligned with `timeOrig`.
        timeCut (array-like): Time array after eclipse/false-positive cuts [s].
        fluxCut (array-like): Flux array aligned with `timeCut`.
        timeCommonFalsePositivesRemoved (array-like): Time after common FP cuts [s].
        fluxCommonFalsePositivesRemoved (array-like): Flux aligned with previous.
        durationArray (array-like): Transit-duration estimates [s].
        SystemName (str): System identifier for figure titling.
        DetrendingName (str): Detrending run label for outputs.
        K (unused): Kept for API compatibility.
        base_dir (str|pathlib.Path or None): Root of the repo/data tree. If None, uses CWD.

    Returns:
        None
            Creates and saves diagnostic figures to the configured output path.
    '''
    base_root = _resolve_base_dir(None)
    folder_path = base_root / "LightCurves" / "ItCos_Testing"
    _ensure_parent(folder_path / "dummy.txt")

    TT_specific = (np.array([36,140.5,243.8,347.6,451.9,659.7,762.3,867.4,969.7,1074.9,1176.9,1282.4,1384.3]) + 55000) * days2sec
    numSpecificTransits = len(TT_specific)
    plot_horizontalWindowWidth = 6 * hours2sec * 7
    CosIndividualTransit_timeList, CosIndividualTransit_fluxList = [], []
    listTime, listFlux = [], []

    time, flux, trend, timeList, fluxList = Detrending_IterativeCosine_Test(
        timeOrig, fluxOrig, timeCut, fluxCut,
        timeCommonFalsePositivesRemoved, fluxCommonFalsePositivesRemoved,
        durationArray, SystemName, DetrendingName, ID, mission, base_dir=base_dir
    )

    for jj in range(len(timeList)):
        for ii in range(numSpecificTransits):
            OrigIndividualTransit_timeFinal = timeOrig[(timeOrig > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeOrig < TT_specific[ii] + plot_horizontalWindowWidth/2)]
            OrigIndividualTransit_fluxFinal = fluxOrig[(timeOrig > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeOrig < TT_specific[ii] + plot_horizontalWindowWidth/2)]
            CutIndividualTransit_timeFinal = timeCut[(timeCut > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeCut < TT_specific[ii] + plot_horizontalWindowWidth/2)]
            CutIndividualTransit_fluxFinal = fluxCut[(timeCut > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeCut < TT_specific[ii] + plot_horizontalWindowWidth/2)]
            CommonFalsePositivesRemovedIndividualTransit_timeFinal = timeCommonFalsePositivesRemoved[(timeCommonFalsePositivesRemoved > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeCommonFalsePositivesRemoved < TT_specific[ii] + plot_horizontalWindowWidth/2)]
            CommonFalsePositivesRemovedIndividualTransit_fluxFinal = fluxCommonFalsePositivesRemoved[(timeCommonFalsePositivesRemoved > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeCommonFalsePositivesRemoved < TT_specific[ii] + plot_horizontalWindowWidth/2)]
            CosIndividualTransit_timeList.append(timeList[jj][(timeList[jj] > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeList[jj] < TT_specific[ii] + plot_horizontalWindowWidth/2)])
            CosIndividualTransit_fluxList.append(fluxList[jj][(timeList[jj] > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeList[jj] < TT_specific[ii] + plot_horizontalWindowWidth/2)])

        fig = plt.figure(figsize=(35,15))
        fig.suptitle(SystemName + " " + DetrendingName + " " + str(TT_specific[ii]))

        if len(OrigIndividualTransit_timeFinal) > 0:
            ax = fig.add_subplot(351)
            ax.scatter(OrigIndividualTransit_timeFinal/days2sec-55000, OrigIndividualTransit_fluxFinal, color='b', label='Orig')
            ax.scatter(CutIndividualTransit_timeFinal/days2sec-55000, CutIndividualTransit_fluxFinal, color='g', label='Eclipses Cut')
            ax.scatter(CommonFalsePositivesRemovedIndividualTransit_timeFinal/days2sec-55000, CommonFalsePositivesRemovedIndividualTransit_fluxFinal, color='r', label='Common FP Cut')
            ax.set_xlabel('Time (days - 55000)')
            ax.set_ylabel('Flux')
            ax.legend()

            for ll in range(len(timeList)):
                ax = fig.add_subplot(3,5,ll)
                ax.scatter(CommonFalsePositivesRemovedIndividualTransit_timeFinal/days2sec-55000, CommonFalsePositivesRemovedIndividualTransit_fluxFinal, color='b', label='Common FP Cut')
                ax.scatter(CosIndividualTransit_timeList[ll]/days2sec-55000, CosIndividualTransit_fluxList[ll], color='r', label='Cosine Detrended')
                ax.set_xlabel('Time (days - 55000)')
                ax.set_ylabel('Flux')
                ax.legend()

        fig.savefig(folder_path / f"{SystemName}_{DetrendingName}TT={str(TT_specific[ii]/days2sec-55000)}.png", bbox_inches='tight')


def Detrending_VariableBiweight_Test(
    timeOrig, fluxOrig, timeCut, fluxCut,
    timeCommonFalsePositivesRemoved, fluxCommonFalsePositivesRemoved,
    timeCosineDetrended, fluxCosineDetrended,
    durationArray, durationArrayTime,
    SystemName, DetrendingName, base_dir=None
):
    '''
    Functionality:
        Sweep a range of xi scaling factors for variable-window biweight
        detrending, generate detrended series for each xi, and plot targeted
        transit windows comparing original/cut/cosine-detrended against each
        variable-biweight result. Saves a per-transit figure grid.

    Arguments:
        timeOrig (array-like): Original time array [s].
        fluxOrig (array-like): Original flux array aligned with `timeOrig`.
        timeCut (array-like): Time array after cuts [s].
        fluxCut (array-like): Flux array aligned with `timeCut`.
        timeCommonFalsePositivesRemoved (array-like): Time after common FP cuts [s].
        fluxCommonFalsePositivesRemoved (array-like): Flux aligned with previous.
        timeCosineDetrended (array-like): Time after cosine detrending [s].
        fluxCosineDetrended (array-like): Flux after cosine detrending.
        durationArray (array-like): Transit-duration estimates [s].
        durationArrayTime (array-like): Times corresponding to `durationArray` [s].
        SystemName (str): System identifier used in figure titles.
        DetrendingName (str): Secondary label for outputs.
        base_dir (str|pathlib.Path or None): Root of the repo/data tree. If None, uses CWD.

    Returns:
        None
            Produces and saves diagnostic figures to the VarBiweight_testing folder.
    '''
    variableDetrending_splits = 2
    variableDetrending_modifier = 4
    fig = plt.figure(figsize=(35,15))
    timeVariableDetrended, fluxVariableDetrended = [], []
    windowLengthTest, trendVariableDetrended, xilist = [], [], []
    VariableDetrendedIndividualTransit_timeFinal, VariableDetrendedIndividualTransit_fluxFinal = [], []

    for jj in range(10):
        xi = .75 + .75 * jj
        xilist.append(xi)
        AtimeVariableDetrended, AfluxVariableDetrended, AwindowLengthTest, AtrendVariableDetrended = Detrending_VariableDuration(
            timeCosineDetrended, fluxCosineDetrended,
            durationArray, durationArrayTime,
            'biweight', variableDetrending_splits, variableDetrending_modifier, xi
        )
        timeVariableDetrended.append(AtimeVariableDetrended)
        fluxVariableDetrended.append(AfluxVariableDetrended)
        windowLengthTest.append(AwindowLengthTest)
        trendVariableDetrended.append(AtrendVariableDetrended)

    TT_specific = (np.array([36,140.5,243.8,347.6,451.9,659.7,762.3,867.4,969.7,1074.9,1176.9,1282.4,1384.3]) + 55000) * days2sec
    numSpecificTransits = len(TT_specific)
    plot_horizontalWindowWidth = 6 * hours2sec * 7

    for ii in range(numSpecificTransits):
        VariableDetrendedIndividualTransit_fluxFinal = []
        VariableDetrendedIndividualTransit_timeFinal = []
        OrigIndividualTransit_timeFinal = timeOrig[(timeOrig > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeOrig < TT_specific[ii] + plot_horizontalWindowWidth/2)]
        OrigIndividualTransit_fluxFinal = fluxOrig[(timeOrig > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeOrig < TT_specific[ii] + plot_horizontalWindowWidth/2)]
        CutIndividualTransit_timeFinal = timeCut[(timeCut > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeCut < TT_specific[ii] + plot_horizontalWindowWidth/2)]
        CutIndividualTransit_fluxFinal = fluxCut[(timeCut > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeCut < TT_specific[ii] + plot_horizontalWindowWidth/2)]
        CommonFalsePositivesRemovedIndividualTransit_timeFinal = timeCommonFalsePositivesRemoved[(timeCommonFalsePositivesRemoved > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeCommonFalsePositivesRemoved < TT_specific[ii] + plot_horizontalWindowWidth/2)]
        CommonFalsePositivesRemovedIndividualTransit_fluxFinal = fluxCommonFalsePositivesRemoved[(timeCommonFalsePositivesRemoved > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeCommonFalsePositivesRemoved < TT_specific[ii] + plot_horizontalWindowWidth/2)]
        CosineDetrendedIndividualTransit_timeFinal = timeCosineDetrended[(timeCosineDetrended > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeCosineDetrended < TT_specific[ii] + plot_horizontalWindowWidth/2)]
        CosineDetrendedIndividualTransit_fluxFinal = fluxCosineDetrended[(timeCosineDetrended > TT_specific[ii] - plot_horizontalWindowWidth/2) & (timeCosineDetrended < TT_specific[ii] + plot_horizontalWindowWidth/2)]

        fig.suptitle(SystemName + " " + DetrendingName + " " + str(TT_specific[ii]))
        if len(OrigIndividualTransit_timeFinal) > 0:
            ax = fig.add_subplot(341)
            ax.scatter(OrigIndividualTransit_timeFinal/days2sec-55000, OrigIndividualTransit_fluxFinal, color='b', label='Orig')
            ax.scatter(CutIndividualTransit_timeFinal/days2sec-55000, CutIndividualTransit_fluxFinal, color='blue', label='Eclipses Cut')
            ax.scatter(CommonFalsePositivesRemovedIndividualTransit_timeFinal/days2sec-55000, CommonFalsePositivesRemovedIndividualTransit_fluxFinal, color='r', label='Common FP Cut')
            ax.set_xlabel('Time (days - 55000)')
            ax.set_ylabel('Flux')
            ax.legend()

            ax = fig.add_subplot(342)
            ax.scatter(CommonFalsePositivesRemovedIndividualTransit_timeFinal/days2sec-55000, CommonFalsePositivesRemovedIndividualTransit_fluxFinal, color='green', label='Common FP Cut')
            ax.scatter(CosineDetrendedIndividualTransit_timeFinal/days2sec-55000, CosineDetrendedIndividualTransit_fluxFinal, color='r', label='Cosine Detrended')
            ax.set_xlabel('Time (days - 55000)')
            ax.set_ylabel('Flux')
            ax.legend()

            for zz in range(10):
                VariableDetrendedIndividualTransit_timeFinal.append(
                    timeVariableDetrended[zz][(timeVariableDetrended[zz] > TT_specific[ii] - plot_horizontalWindowWidth/2) &
                                              (timeVariableDetrended[zz] < TT_specific[ii] + plot_horizontalWindowWidth/2)]
                )
                VariableDetrendedIndividualTransit_fluxFinal.append(
                    fluxVariableDetrended[zz][(timeVariableDetrended[zz] > TT_specific[ii] - plot_horizontalWindowWidth/2) &
                                              (timeVariableDetrended[zz] < TT_specific[ii] + plot_horizontalWindowWidth/2)]
                )
                az = fig.add_subplot(3,4,zz+3)
                az.scatter(CosineDetrendedIndividualTransit_timeFinal/days2sec-55000, CosineDetrendedIndividualTransit_fluxFinal, label='Cosine Detrended')
                az.scatter(VariableDetrendedIndividualTransit_timeFinal[zz]/days2sec-55000, VariableDetrendedIndividualTransit_fluxFinal[zz], color='r', label=f'VarBi xi={xilist[zz]:.2f}')
                az.set_xlabel('Time (BJD - 2,455,000)')
                az.set_ylabel('Flux')
                az.set_ylim(-0.0006, 0.0008)

        folder_path = _resolve_base_dir(None) / "LightCurves" / "VarBiweight_testing"
        _ensure_parent(folder_path / "dummy.txt")
        fig.savefig(folder_path / f"{SystemName}_{'WHY'}TT={str(TT_specific[ii]/days2sec-55000)}.png", bbox_inches='tight')


def Detrending_CheckKnownTransits(timeArray, fluxArray, ID, mission, base_dir=None):
    '''
    Functionality:
        Compute the mean in-transit depth and out-of-transit scatter using a
        list of known transit intervals for a target, and generate a quick
        diagnostic plot of in-transit points.

    Arguments:
        timeArray (array-like): Time array [s].
        fluxArray (array-like): Flux array aligned with `timeArray`.
        ID (str): Target identifier used to locate the known-transit list.
        mission (str): Mission label used to locate the known-transit list.
        base_dir (str|pathlib.Path or None): Root of the repo/data tree. If None, uses CWD.

    Returns:
        tuple:
            meanInTransitFlux (float): Mean transit depth (1 - mean flux) for the
                concatenated in-transit data.
            outOfTransitSTD (float): Standard deviation of out-of-transit flux.
    '''
    base_root = _resolve_base_dir(None)
    kt_path = base_root / 'LightCurves' / 'KnownTransits' / f"{mission}_{ID}_knownPrimaryTransits.txt"
    knownTransitList = np.genfromtxt(kt_path)
    indexArray = np.linspace(0, len(timeArray)-1, len(timeArray)).astype(int)
    inTransitFlux = np.array([])
    inTransitIndices = np.array([]).astype(int)
    numTransits = 0

    for ii in range(len(knownTransitList)):
        singleTransitFlux = fluxArray[np.logical_and(timeArray/days2sec-55000 > knownTransitList[ii][0], timeArray/days2sec-55000 < knownTransitList[ii][1])]
        singleTransitIndicies = indexArray[np.logical_and(timeArray/days2sec-55000 > knownTransitList[ii][0], timeArray/days2sec-55000 < knownTransitList[ii][1])].astype(int)
        if len(singleTransitFlux) > 0:
            inTransitFlux = np.append(inTransitFlux, singleTransitFlux)
            inTransitIndices = np.append(inTransitIndices, singleTransitIndicies)
            numTransits += 1

    meanInTransitFlux = 1 - np.mean(inTransitFlux)
    outOfTransitIndices = np.delete(indexArray, inTransitIndices)
    outOfTransitSTD = np.std(fluxArray[outOfTransitIndices])

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(timeArray[inTransitIndices]/days2sec-55000, fluxArray[inTransitIndices])
    ax.plot(np.array([timeArray[0], timeArray[-1]])/days2sec-55000, [meanInTransitFlux, meanInTransitFlux], linestyle='--', color='k')
    ax.set_xlabel('Time')
    ax.set_ylabel('Flux (in transit only)')
    plt.show(block=False)

    return meanInTransitFlux, outOfTransitSTD


def Detrending_TestCosine2(timeArray, fluxArray, duration_array, ID, mission, DetrendingName, base_dir=None):
    '''
    Functionality:
        Run an iterative cosine detrending using window lengths chosen from a
        Lomb–Scargle periodogram of the current residuals. Re-detrend in equal
        segments after each window-length update until stopping criteria are met.
        Saves a periodogram figure.

    Arguments:
        timeArray (array-like): Time array [s] to detrend.
        fluxArray (array-like): Flux array aligned with `timeArray`.
        duration_array (array-like): Transit-duration estimates [s].
        ID (str): Target ID used in output filenames.
        mission (str): Mission label used in output filenames.
        DetrendingName (str): Secondary label used in output filenames.
        base_dir (str|pathlib.Path or None): Root of the repo/data tree. If None, uses CWD.

    Returns:
        tuple:
            timeCosineFiltered (np.ndarray): Time after final cosine detrending [s].
            fluxCosineFiltered (np.ndarray): Flux after final cosine detrending.
            trendCosineFiltered (np.ndarray): Last-pass cosine trend concatenated.
    '''
    timeCosineFiltered = np.copy(timeArray)
    fluxCosineFiltered = np.copy(fluxArray)
    subplotCounter = 1
    sufficientDetrendingReached = False

    figCosine = plt.figure(figsize=(18,7))
    figCosine.suptitle(SystemName + " " + DetrendingName + " Iterative Cosine Filter Periodograms")

    for transitDurationPercentage in ['max','75']:
        for transitDurationMultiplier in factor:
            if not sufficientDetrendingReached:
                cosineFilterWindowLength, fap_1perc, max_power = DoPeriodogram(
                    timeCosineFiltered, fluxCosineFiltered, duration_array, figCosine, True,
                    transitDurationPercentage, transitDurationMultiplier, 'progressive',
                    SystemName, DetrendingName, ID, mission, subplotCounter
                )
                subplotCounter += 1
                if cosineFilterWindowLength != -27:
                    numSectors = 5
                    timeCosineFiltered = np.array([])
                    fluxCosineFiltered = np.array([])
                    trendCosineFiltered = np.array([])
                    sectorDataPoints = int(len(timeArray)/numSectors)
                    for ii in range(numSectors):
                        timeSegment = timeArray[ii*sectorDataPoints:(ii+1)*sectorDataPoints]/days2sec - 55000
                        fluxSegment = fluxArray[ii*sectorDataPoints:(ii+1)*sectorDataPoints]
                        text_trap = io.StringIO()
                        sys.stdout = text_trap
                        fluxCosineFilteredSegment, trendCosineFilteredSegment = wotan.flatten(
                            time=timeSegment, flux=fluxSegment, method='cosine',
                            robust=True, break_tolerance=0.5,
                            window_length=cosineFilterWindowLength/days2sec, return_trend=True
                        )
                        sys.stdout = sys.__stdout__
                        timeCosineFilteredSegment = timeSegment
                        timeCosineFiltered = np.append(timeCosineFiltered, (timeCosineFilteredSegment + 55000)*days2sec)
                        fluxCosineFiltered = np.append(fluxCosineFiltered, fluxCosineFilteredSegment)
                        trendCosineFiltered = np.append(trendCosineFiltered, trendCosineFilteredSegment)
                else:
                    sufficientDetrendingReached = True

    folder_name = "../LightCurves/Figures/" + DetrendingName
    return timeCosineFiltered, fluxCosineFiltered, trendCosineFiltered


def Detrending_IterativeCosine2(
    timeOrig, fluxOrig, timeCut, fluxCut,
    timeFinal, fluxFinal, durationArray,
    SystemName, DetrendingName, ID, mission, base_dir=None
):
    '''
    Functionality:
        Iteratively detrend a light curve with a cosine filter whose window
        length is set from the current Lomb–Scargle periodogram. Each pass
        re-applies wotan cosine detrending in fixed segments and records
        snapshots. Saves a composite figure of the evolution.

    Arguments:
        timeOrig (array-like): Original time [s] (retained for API compatibility).
        fluxOrig (array-like): Original flux aligned with `timeOrig`.
        timeCut (array-like): Time after preliminary cuts [s].
        fluxCut (array-like): Flux after preliminary cuts.
        timeFinal (array-like): Working time array to detrend [s].
        fluxFinal (array-like): Working flux array aligned with `timeFinal`.
        durationArray (array-like): Transit-duration estimates [s] for window sizing.
        SystemName (str): System label for figure titles.
        DetrendingName (str): Detrending run label for output paths.
        ID (str): Target identifier for DoPeriodogram/filenames.
        mission (str): Mission label for DoPeriodogram/filenames.
        base_dir (str|pathlib.Path or None): Root of the repo/data tree. If None, uses CWD.

    Returns:
        tuple:
            timeCosineFiltered (np.ndarray): Time array after final pass [s].
            fluxCosineFiltered (np.ndarray): Flux array after final pass.
            trendCosineFiltered (np.ndarray): Concatenated cosine trend from final pass.
            listTime (list[np.ndarray]): Snapshot times across iterations.
            listFlux (list[np.ndarray]): Snapshot fluxes across iterations.
    '''
    listTime, listFlux = [], []
    timeCosineFiltered = np.copy(timeFinal)
    fluxCosineFiltered = np.copy(fluxFinal)
    subplotCounter = 1
    sufficientDetrendingReached = False

    figCosine = plt.figure(figsize=(20,10))
    figCosine.suptitle(SystemName)

    multiMin, multiMax = 2.5, 3
    transitDurationMultiplierArray = [3]

    for transitDurationPercentage in ['max']:
        for transitDurationMultiplier in transitDurationMultiplierArray:
            if not sufficientDetrendingReached:
                cosineFilterWindowLength, fap_1perc, max_power = DoPeriodogram(
                    timeCosineFiltered, fluxCosineFiltered, durationArray, figCosine, True,
                    transitDurationPercentage, transitDurationMultiplier,
                    'progressive', SystemName, DetrendingName, ID, mission, subplotCounter
                )
                subplotCounter += 1
                if cosineFilterWindowLength != -27:
                    numSectors = 5
                    timeCosineFiltered = np.array([])
                    fluxCosineFiltered = np.array([])
                    trendCosineFiltered = np.array([])
                    sectorDataPoints = int(len(timeFinal)/numSectors)
                    for ii in range(numSectors):
                        timeSegment = timeFinal[ii*sectorDataPoints:(ii+1)*sectorDataPoints]/days2sec - 55000
                        fluxSegment = fluxFinal[ii*sectorDataPoints:(ii+1)*sectorDataPoints]
                        text_trap = io.StringIO()
                        sys.stdout = text_trap
                        fluxCosineFilteredSegment, trendCosineFilteredSegment = wotan.flatten(
                            time=timeSegment, flux=fluxSegment, method='cosine',
                            robust=True, break_tolerance=0.5,
                            window_length=cosineFilterWindowLength/days2sec, return_trend=True
                        )
                        sys.stdout = sys.__stdout__
                        timeCosineFilteredSegment = timeSegment
                        timeCosineFiltered = np.append(timeCosineFiltered, (timeCosineFilteredSegment + 55000)*days2sec)
                        fluxCosineFiltered = np.append(fluxCosineFiltered, fluxCosineFilteredSegment)
                        trendCosineFiltered = np.append(trendCosineFiltered, trendCosineFilteredSegment)
                else:
                    pass

            listTime.append(timeCosineFiltered)
            listFlux.append(fluxCosineFiltered)

            ax = figCosine.add_subplot(3,2,subplotCounter)
            ax.scatter(timeFinal/days2sec-55000, fluxFinal, color='b', label='Common False Positives Cut')
            ax.scatter(timeCosineFiltered/days2sec-55000, fluxCosineFiltered, color='r', label='Cosine Detrended')
            ax.set_xlabel('Time (days - 55000)')
            ax.set_ylabel('Flux')
            ax.legend()
            ax.set_title('dur%=' + str(transitDurationPercentage) + ' DurMult=' + str(transitDurationMultiplier))

            folder_path = _resolve_base_dir(None) / "LightCurves" / "ItCos_Testing"
            _ensure_parent(folder_path / "dummy.txt")
            figCosine.savefig(folder_path / f"it_cos_test{SystemName}_{DetrendingName}.png", bbox_inches='tight')

    return timeCosineFiltered, fluxCosineFiltered, trendCosineFiltered, listTime, listFlux

def InjectTransits(
    timeArray, fluxArray, KIC, DetrendingName,
    orbit_params, stellar_params, injection_type,
    injection_param_file=None, base_dir=None
):
    '''
    Functionality:
        Inject synthetic circumbinary planet transits into a light curve.
        Transit mid-times/durations are derived via N-body timing
        (Search_CreateTransitMask). The photometric profile is generated
        with BATMAN and scaled by the flux ratio. Parameters can be
        randomized, manual, or drawn from archive-based CSVs. Outputs include
        figures and parameter logs.

    Arguments:
        timeArray (array-like): Observation times [s].
        fluxArray (array-like): Flux values aligned with `timeArray`.
        KIC (str or int): Target ID (KIC or TIC).
        DetrendingName (str): Label for output directories.
        orbit_params (dict): Binary/planet context with keys:
            Pbin (s), e (–), omega (rad), sep (rad, used as θ).
        stellar_params (dict): Stellar/system properties with keys:
            mA, mB (kg), rA, rB (m), met (dex), frat (fB/fA).
        injection_type (str): One of {"random","manual","manual_wata","manual_tess",
                                      "archive_full_pileup","archive_sculpted","archive_raw"}.
        injection_param_file (str, optional): CSV filename under ../stanley_cbp/Databases/
            for manual_wata/manual_tess parameter sourcing.
        base_dir (str|pathlib.Path or None): Root of the repo/data tree. If None, uses CWD.

    Returns:
        tuple:
            timeInjected (np.ndarray): Time array (copy of input) [s].
            fluxInjected (np.ndarray): Flux with injected transit signatures.
        Side effects:
            - Saves parameter CSV, plot, and injected transit list under
              ../LightCurves/Injections/{DetrendingName}/
    '''

    base_root = _resolve_base_dir(None)
    _ = p_user_data()

    if (injection_type in {"archive_sculpted", "archive_full_pileup", "archive_raw"}):
        exo_path = base_root / '../stanley_cbp/Databases' / 'exoplanet_archive.csv'
        exoplanet_archive = Table.read(exo_path, delimiter=',', comment='#')

    if (injection_type == "manual_wata"):
        p = base_root / '../stanley_cbp/Databases' / str(injection_param_file)
        if os.path.isfile(p):
            inj_params = Table.read(p)
            if int(KIC) not in inj_params['KIC']:
                injection_type = 'manual'
        else:
            injection_type = 'manual'

    if (injection_type == "manual_tess"):
        p = base_root / '../stanley_cbp/Databases' / str(injection_param_file)
        if os.path.isfile(p):
            inj_params = Table.read(p)
            if 'TIC' not in inj_params.colnames or int(KIC) not in inj_params['TIC']:
                injection_type = 'manual'
        else:
            injection_type = 'manual'

    remove_random_transits = False
    timeInjected = np.copy(timeArray)
    fluxInjected = np.copy(fluxArray)

    params = batman.TransitParams()
    params.limb_dark = "quadratic"

    logg_sun = 4.4374
    loggValue = np.log10(stellar_params['mA']/mSun_kg) - 2*np.log10(stellar_params['rA']/rSun_m) + logg_sun
    temperature = MassRadiusTemperatureRelation(stellar_params['mA'], stellar_params['rA'])
    
    print('----- BATMAN TRANSIT INJECTION PARAMETERS -----')
    print('mA = ' + str(round(stellar_params['mA']/mSun_kg,3)))
    print('mB = ' + str(round(stellar_params['mB']/mSun_kg,3)))
    print('RA = ' + str(round(stellar_params['rA']/rSun_m,3)))
    print('RB = ' + str(round(stellar_params['rB']/rSun_m,3)))
    print('logg = ' + str(loggValue))
    print('temperature (K) = ' + str(temperature))
    print('metallicity = ' + str(stellar_params['met']))
    print('flux ratio (fB/fA) = ' + str(stellar_params['frat']))
    print('limb darkening model = ' + params.limb_dark)

    sc = LDPSetCreator(teff=(temperature, 0.00001), logg=(loggValue, 0.00001), z=(stellar_params['met'], 0.00001), filters=[kepler])
    ps = sc.create_profiles(nsamples=2000)
    qc, qe = ps.coeffs_qd()
    linParam = qc[0][0]
    quadParam = qc[0][1]

    numDataPoints = 10000
    abin = PeriodToSemiMajorAxis(np.array([stellar_params['mA'], stellar_params['mB']]), np.array([orbit_params['Pbin']]))
    ebin = orbit_params['e']
    random_archive_index = -27

    if (injection_type == "random"):
        a_min = 2.5 * abin * (1 + ebin)
        a_max = 4.0 * abin * (1 + ebin)
        _ap = np.random.uniform(a_min, a_max)
        _ep = np.random.uniform(0, 0.15)
        _omegap = np.random.uniform(0, 2*np.pi)
        _thetap = np.random.uniform(0, 2*np.pi)
        _Pp = SemiMajorAxisToPeriod(np.array([stellar_params['mA']+stellar_params['mB'], 0]), np.array([_ap]))
        _Rp = 2 * rEarth_m

    elif (injection_type == "manual_wata"):
        _ep = inj_params[inj_params['KIC'] == int(KIC)]['ep'][0]
        _omegap = inj_params[inj_params['KIC'] == int(KIC)]['omegap'][0]
        _thetap = inj_params[inj_params['KIC'] == int(KIC)]['thetap'][0]
        _Pp = inj_params[inj_params['KIC'] == int(KIC)]['Pp_days'][0] * days2sec
        _Rp = inj_params[inj_params['KIC'] == int(KIC)]['Rp_rEarth'][0] * rEarth_m
        _ap = PeriodToSemiMajorAxis(np.array([stellar_params['mA']+stellar_params['mB'], 0]), np.array([_Pp]))

    elif (injection_type == "manual_tess"):
        _ep = inj_params[inj_params['TIC'] == int(TIC)]['ep'][0]
        _omegap = inj_params[inj_params['TIC'] == int(TIC)]['omegap'][0]
        _thetap = inj_params[inj_params['TIC'] == int(TIC)]['thetap'][0]
        _Pp = inj_params[inj_params['TIC'] == int(TIC)]['Pp_days'][0] * days2sec
        _Rp = inj_params[inj_params['TIC'] == int(TIC)]['Rp_rEarth'][0] * rEarth_m
        _ap = PeriodToSemiMajorAxis(np.array([stellar_params['mA']+stellar_params['mB'], 0]), np.array([_Pp]))

    elif (injection_type == "manual"):
        _ep = 0.01
        _omegap = 0.0
        _thetap = 0.0
        _Pp = 7.5 * (1 + ebin)**1.5 * orbit_params['Pbin']
        _ap = PeriodToSemiMajorAxis(np.array([stellar_params['mA']+stellar_params['mB'], 0]), np.array([_Pp]))
        _Rp = 5 * rEarth_m

    elif (injection_type == "archive_full_pileup"):
        random_archive_index = int(np.floor(np.random.uniform(0, len(exoplanet_archive))))
        _ep = np.random.uniform(0, 0.15)
        a_min = 2.5 * abin * (1 + ebin)
        a_max = 4.0 * abin * (1 + ebin)
        _ap = np.random.uniform(a_min, a_max)
        _Pp = SemiMajorAxisToPeriod(np.array([stellar_params['mA']+stellar_params['mB'], 0]), np.array([_ap]))
        _ap = np.random.uniform(a_min, a_max)
        _omegap = np.random.uniform(0, 2*np.pi)
        _thetap = np.random.uniform(0, 2*np.pi)
        _Rp = exoplanet_archive['pl_rade'][random_archive_index] * rEarth_m

    elif (injection_type == "archive_sculpted"):
        stablePlanetFound = False
        while not stablePlanetFound:
            random_archive_index = int(np.floor(np.random.uniform(0, len(exoplanet_archive))))
            _Pp = exoplanet_archive['pl_orbper'][random_archive_index] * days2sec
            _ap = PeriodToSemiMajorAxis(np.array([stellar_params['mA']+stellar_params['mB'], 0]), np.array([_Pp]))
            if _ap > 2.5 * abin * (1 + ebin):
                stablePlanetFound = True
        _ep = np.random.uniform(0, 0.15)
        _omegap = np.random.uniform(0, 2*np.pi)
        _thetap = np.random.uniform(0, 2*np.pi)
        _Rp = exoplanet_archive['pl_rade'][random_archive_index] * rEarth_m

    z = (
        stellar_params['mA'], stellar_params['mB'],
        orbit_params['Pbin'], orbit_params['e'],
        orbit_params['omega'], orbit_params['sep'],
        _Pp, _ep, _omegap, _thetap
    )
    TT, TD, sigma_solutionOld, meanFlux_solution, stdOutOfTransit = Search_CreateTransitMask(
        z, stellar_params['rA'], stellar_params['rB'], timeArray, fluxArray,
        returnTransitTimes=True, meanTotalLightcurve=-27, plotting=False,
        mission='BLAH', ID='BLAH', SearchName='BLAH'
    )

    inj_dir = base_root / 'LightCurves' / 'Injections' / DetrendingName
    _ensure_parent(inj_dir / "dummy.txt")

    params_filename = inj_dir / f"{KIC}_planetParameters.csv"
    np.savetxt(params_filename, np.transpose([
        stellar_params['mA']/mSun_kg, stellar_params['mB']/mSun_kg,
        stellar_params['rA']/rSun_m, stellar_params['rB']/rSun_m,
        orbit_params['Pbin']/days2sec, orbit_params['e'], orbit_params['omega'],
        _Rp/rEarth_m, _Pp/days2sec, _ep, _omegap, _thetap, random_archive_index
    ]))

    flux_ratio = stellar_params['frat']
    numTransits = len(TT)
    depth = []
    output_time, output_duration, output_impactparameter = [], [], []
    Tb = np.zeros(len(TT))

    #may need to add removal of random transits here from Wata's version of the code

    for ii in range(numTransits):
        params.per = _Pp/years2sec
        params.t0 = 0.0
        params.inc = 90
        params.ecc = 0.0
        params.w = 0.0
        params.u = [linParam, quadParam]
        params.rp = _Rp/stellar_params['rA']
        params.a = _ap/stellar_params['rA']

        duration_rough = _Pp*stellar_params['rA']/(np.pi*_ap) * (1+_Rp/stellar_params['rA']) / years2sec
        timeTransit_rough = np.linspace(-0.6*duration_rough, 0.6*duration_rough, numDataPoints)
        m = batman.TransitModel(params, timeTransit_rough)
        fluxTransit_rough = m.light_curve(params)

        timeTransit_precise = timeTransit_rough[fluxTransit_rough < fluxTransit_rough[0]]
        fluxTransit_precise = fluxTransit_rough[fluxTransit_rough < fluxTransit_rough[0]]
        timeTransit_scaled = np.linspace(-0.5*TD[ii]/years2sec, 0.5*TD[ii]/years2sec, len(timeTransit_precise))
        fluxTransit_scaled = fluxTransit_precise

        depth_old = ( _Rp/stellar_params['rA'] )**2
        depth_new = depth_old * 1.0/(1.0 + flux_ratio)
        temp = 1.0 - fluxTransit_scaled
        temp = temp * depth_new/depth_old
        fluxTransit_scaled = 1.0 - temp

        if len(fluxTransit_scaled) == 0:
            depth.append(0)
        else:
            depth.append(1 - np.min(fluxTransit_scaled))

        if len(timeTransit_precise) > 0:
            timeTransit_orig = timeInjected[(timeInjected > TT[ii] - 0.5*TD[ii]) & (timeInjected < TT[ii] + 0.5*TD[ii])]
            fluxTransit_injected = np.interp(timeTransit_orig - TT[ii], timeTransit_scaled*years2sec, fluxTransit_scaled)
            timeTransit_injected = timeTransit_orig
            fluxInjected[(timeInjected > TT[ii] - 0.5*TD[ii]) & (timeInjected < TT[ii] + 0.5*TD[ii])] -= (1 - fluxTransit_injected)

            if len(timeTransit_orig) > 0:
                output_time.append(TT[ii])
                output_duration.append(TD[ii])
                output_impactparameter.append(Tb[ii])

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(timeInjected/days2sec-55000, fluxInjected)
    fig.savefig(inj_dir / f"{KIC}_injectedTransit.png", bbox_inches='tight')
    plt.show(block=False)

    np.savetxt(
        inj_dir / f"{KIC}_injectedTransitList.txt",
        np.transpose([np.array(output_time)/days2sec-55000, np.array(output_duration)/hours2sec, np.array(output_impactparameter)])
    )

    return timeInjected, fluxInjected


def InjectTransits2(timeArray, fluxArray, ID, mission, DetrendingName, orbit_params, stellar_params, base_dir=None):
    '''
    Functionality:
        Inject synthetic planet transits into a light curve using BATMAN.
        Planet orbital elements are randomly sampled near the circumbinary
        stability boundary; transit mid-times/durations come from
        Search_CreateTransitMask. Transit profiles are scaled by the stellar
        flux ratio and written into the light curve by interpolation. Outputs
        include a plot and a text file listing injected transits.

    Arguments:
        timeArray (array-like): Observation times [s].
        fluxArray (array-like): Flux values aligned with `timeArray`.
        ID (str): Target identifier used in filenames.
        mission (str): Mission identifier used in filenames.
        DetrendingName (str): Output subfolder/label for artifacts.
        orbit_params (dict): Binary orbital context with keys:
            Pbin (s), e (–), omega (rad), sep (rad; used as θ).
        stellar_params (dict): Stellar/system properties with keys:
            mA, mB (kg), rA, rB (m), met (dex), frat (fB/fA).
        base_dir (str|pathlib.Path or None): Root of the repo/data tree. If None, uses CWD.

    Returns:
        tuple:
            timeInjected (np.ndarray): Copy of input times [s].
            fluxInjected (np.ndarray): Flux with injected transit signatures.
        Side effects:
            - Saves parameter CSV and injected-transit diagnostics under
              ../LightCurves/Injections/{DetrendingName}/
    '''

    base_root = _resolve_base_dir(None)
    timeInjected = np.copy(timeArray)
    fluxInjected = np.copy(fluxArray)

    params = batman.TransitParams()
    params.limb_dark = "quadratic"

    loggValue = np.log10(stellar_params['mA']/mSun_kg) - 2*np.log10(stellar_params['rA']/rSun_m) + 4.437
    temperature = MassRadiusTemperatureRelation(stellar_params['mA'], stellar_params['rA'])

    print('----- BATMAN TRANSIT INJECTION PARAMETERS -----')
    print('mA = ' + str(round(stellar_params['mA']/mSun_kg,3)))
    print('mB = ' + str(round(stellar_params['mB']/mSun_kg,3)))
    print('RA = ' + str(round(stellar_params['rA']/rSun_m,3)))
    print('RB = ' + str(round(stellar_params['rB']/rSun_m,3)))
    print('logg = ' + str(loggValue))
    print('temperature (K) = ' + str(temperature))
    print('metallicity = ' + str(stellar_params['met']))
    print('flux ratio (fB/fA) = ' + str(stellar_params['frat']))
    print('limb darkening model = ' + params.limb_dark)

    sc = LDPSetCreator(teff=(temperature,0.00001), logg=(loggValue,0.00001), z=(stellar_params['met'],0.00001), filters=[kepler])
    ps = sc.create_profiles(nsamples=2000)
    qc, qe = ps.coeffs_qd()
    linParam = qc[0][0]
    quadParam = qc[0][1]

    numDataPoints = 10000
    abin = PeriodToSemiMajorAxis(np.array([stellar_params['mA'], stellar_params['mB']]), np.array([orbit_params['Pbin']]))
    ebin = orbit_params['e']

    # Sample circumbinary-stable like orbits near apoapse scaling.
    a_min = 2.2 * abin * (1 + ebin)
    a_max = 4.1 * abin * (1 + ebin)
    _ap = np.random.uniform(a_min, a_max)
    _ep = np.random.uniform(0, 0.15)
    _omegap = np.random.uniform(0, 2*np.pi)
    _thetap = np.random.uniform(0, 2*np.pi)
    _Pp = SemiMajorAxisToPeriod(np.array([stellar_params['mA']+stellar_params['mB'], 0]), np.array([_ap]))

    z = (stellar_params['mA'], stellar_params['mB'], orbit_params['Pbin'], orbit_params['e'],
         orbit_params['omega'], orbit_params['sep'], _Pp, _ep, _omegap, _thetap)

    TT, TD, sigma_solutionOld, meanFlux_solution, stdOutOfTransit = Search_CreateTransitMask(
        z, stellar_params['rA'], stellar_params['rB'],
        timeArray, fluxArray, returnTransitTimes=True,
        meanTotalLightcurve=-27, plotting=False, mission=mission, ID=ID, SearchName='BLAH'
    )

    inj_dir = base_root / 'LightCurves' / 'Injections' / DetrendingName
    _ensure_parent(inj_dir / "dummy.txt")

    params_filename = inj_dir / f"{mission}_{ID}_planetParameters.csv"
    np.savetxt(params_filename, np.transpose([_Pp/days2sec, _ep, _omegap, _thetap]))

    flux_ratio = stellar_params['frat']
    depth = []
    output_time, output_duration, output_impactparameter = [], [], []
    Tb = np.zeros(len(TT))
    R_p = 2 * rEarth_m

    for ii in range(len(TT)):
        params.per = orbit_params['Pbin']/years2sec
        params.t0 = 0.0
        params.inc = 90
        params.ecc = 0.0
        params.w = 0.0
        params.u = [linParam, quadParam]
        params.rp = R_p/stellar_params['rA']
        params.a  = abin/stellar_params['rA']

        duration_rough = orbit_params['Pbin']*stellar_params['rA']/(np.pi*abin) * (1 + R_p/stellar_params['rA']) / years2sec
        timeTransit_rough = np.linspace(-0.6*duration_rough, 0.6*duration_rough, numDataPoints)

        m = batman.TransitModel(params, timeTransit_rough)
        fluxTransit_rough = m.light_curve(params)

        timeTransit_precise = timeTransit_rough[fluxTransit_rough < fluxTransit_rough[0]]
        fluxTransit_precise = fluxTransit_rough[fluxTransit_rough < fluxTransit_rough[0]]

        timeTransit_scaled = np.linspace(-0.5*TD[ii]/years2sec, 0.5*TD[ii]/years2sec, len(timeTransit_precise))
        fluxTransit_scaled = fluxTransit_precise

        depth_old = (R_p/stellar_params['rA'])**2
        depth_new = depth_old / (1.0 + flux_ratio)
        temp = (1.0 - fluxTransit_scaled) * (depth_new/depth_old)
        fluxTransit_scaled = 1.0 - temp

        depth.append(0 if len(fluxTransit_scaled) == 0 else 1 - np.min(fluxTransit_scaled))
        print('Transit #' + str(ii) + ', time = ' + str(round(TT[ii]/days2sec - 55000,3)) +
              ', duration = ' + str(round(TD[ii]/hours2sec,3)) +
              ', depth = ' + str(round(depth[ii],8)) + ', b = ' + str(round(Tb[ii],3)))

        if len(timeTransit_precise) > 0:
            timeTransit_orig = timeInjected[(timeInjected > TT[ii] - 0.5*TD[ii]) & (timeInjected < TT[ii] + 0.5*TD[ii])]
            fluxTransit_injected = np.interp(timeTransit_orig - TT[ii], timeTransit_scaled*years2sec, fluxTransit_scaled)
            fluxInjected[(timeInjected > TT[ii] - 0.5*TD[ii]) & (timeInjected < TT[ii] + 0.5*TD[ii])] -= (1 - fluxTransit_injected)

            if len(timeTransit_orig) > 0:
                output_time.append(TT[ii])
                output_duration.append(TD[ii])
                output_impactparameter.append(Tb[ii])

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(timeInjected/days2sec-55000, fluxInjected)
    fig.savefig(inj_dir / f"{mission}_{ID}_injectedTransit.png", bbox_inches='tight')
    plt.show(block=False)

    np.savetxt(inj_dir / f"{mission}_{ID}_injectedTransitList.txt",
               np.transpose([np.array(output_time)/days2sec-55000, np.array(output_duration)/hours2sec, np.array(output_impactparameter)]))

    return timeInjected, fluxInjected

def InjectTransits_Batman(systemName, secondaryName, TT, TD, Tb, reboundSim, timeOrig, fluxOrig,
                          flux_ratio=0, metallicity=0, temperature=-27, base_dir=None):
    '''
    Functionality:
        Inject Mandel & Agol transit models (via BATMAN) into a light curve
        for a provided sequence of transit mid-times and durations. The
        underlying system geometry is read from a REBOUND simulation to set
        radii, semi-major axis, and limb-darkening through ldtk. Transit
        profiles are scaled by a flux ratio and injected via interpolation.
        Outputs a list of injected transits.

    Arguments:
        systemName (str): Primary system identifier used in output filenames.
        secondaryName (str): Secondary label used in output filenames.
        TT (array-like): Transit mid-times [s].
        TD (array-like): Transit durations [s].
        Tb (array-like): Impact parameters (dimensionless, same length as TT).
        reboundSim (rebound.Simulation): System simulation with star, companion, planet.
        timeOrig (array-like): Original time array [s].
        fluxOrig (array-like): Original flux array aligned with `timeOrig`.
        flux_ratio (float, optional): fB/fA dilution factor. Default 0.
        metallicity (float, optional): [Fe/H] used for limb darkening. Default 0.
        temperature (float, optional): Stellar Teff (K). If -27, it is estimated
            via MassRadiusTemperatureRelation. Default -27.
        base_dir (str, optional): Root directory for outputs. If None, uses the
            environment variable STANLEY_BASE_DIR; if unset, resolves to the
            package root (.. relative to this file) when available, else '..'.

    Returns:
        tuple:
            timeInjected (np.ndarray): Copy of original times [s].
            fluxInjected (np.ndarray): Flux with injected transits.
        Side effects:
            - Saves injected-transit list to <base_dir>/LightCurves/
    '''
    import os

    # Resolve base directory for outputs (cluster/local/pip-safe)
    if base_dir is None:
        base_dir = os.environ.get('STANLEY_BASE_DIR')
    if base_dir is None:
        if '__file__' in globals():
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        else:
            base_dir = '..'

    out_lightcurves_dir = os.path.join(base_dir, 'LightCurves')
    os.makedirs(out_lightcurves_dir, exist_ok=True)

    timeInjected = np.copy(timeOrig)
    fluxInjected = np.copy(fluxOrig)

    params = batman.TransitParams()
    params.limb_dark = "quadratic"

    p = reboundSim.particles
    loggValue = np.log10(p[0].m/mSun_kg) - 2*np.log10(p[0].r/rSun_m) + 4.437
    if temperature == -27:
        temperature = MassRadiusTemperatureRelation(p[0].m, p[0].r)

    print('----- BATMAN TRANSIT INJECTION PARAMETERS -----')
    print('mA = ' + str(round(p[0].m/mSun_kg,3)))
    print('mB = ' + str(round(p[1].m/mSun_kg,3)))
    print('RA = ' + str(round(p[0].r/rSun_m,3)))
    print('RB = ' + str(round(p[1].r/rSun_m,3)))
    print('logg = ' + str(loggValue))
    print('temperature (K) = ' + str(temperature))
    print('metallicity = ' + str(metallicity))
    print('flux ratio (fB/fA) = ' + str(flux_ratio))
    print('limb darkening model = ' + params.limb_dark)

    sc = LDPSetCreator(teff=(temperature,0.00001), logg=(loggValue,0.00001), z=(metallicity,0.00001), filters=[kepler])
    ps = sc.create_profiles(nsamples=2000)
    qc, qe = ps.coeffs_qd()
    linParam = qc[0][0]
    quadParam = qc[0][1]

    numDataPoints = 10000
    orbits = reboundSim.orbits()

    depth = []
    output_time, output_duration, output_impactparameter = [], [], []

    for ii in range(len(TT)):
        params.per = orbits[1].P/years2sec
        params.t0 = 0.0
        params.inc = 90
        params.ecc = 0.0
        params.w = 0.0
        params.u = [linParam, quadParam]
        params.rp = p[2].r/p[0].r
        params.a  = orbits[1].a/p[0].r

        duration_rough = orbits[1].P * p[0].r/(np.pi*orbits[1].a) * (1 + p[2].r/p[0].r) / years2sec
        timeTransit_rough = np.linspace(-0.6*duration_rough, 0.6*duration_rough, numDataPoints)

        m = batman.TransitModel(params, timeTransit_rough)
        fluxTransit_rough = m.light_curve(params)

        timeTransit_precise = timeTransit_rough[fluxTransit_rough < fluxTransit_rough[0]]
        fluxTransit_precise = fluxTransit_rough[fluxTransit_rough < fluxTransit_rough[0]]

        timeTransit_scaled = np.linspace(-0.5*TD[ii]/years2sec, 0.5*TD[ii]/years2sec, len(timeTransit_precise))
        fluxTransit_scaled = fluxTransit_precise

        depth_old = (p[2].r/p[0].r)**2
        depth_new = depth_old / (1.0 + flux_ratio)
        temp = (1.0 - fluxTransit_scaled) * (depth_new/depth_old)
        fluxTransit_scaled = 1.0 - temp

        depth.append(0 if len(fluxTransit_scaled) == 0 else 1 - np.min(fluxTransit_scaled))
        print('Transit #' + str(ii) + ', time = ' + str(round(TT[ii]/days2sec - 55000,3)) +
              ', duration = ' + str(round(TD[ii]/hours2sec,3)) +
              ', depth = ' + str(round(depth[ii],8)) + ', b = ' + str(round(Tb[ii],3)))

        if len(timeTransit_precise) > 0:
            timeTransit_orig = timeInjected[(timeInjected > TT[ii] - 0.5*TD[ii]) & (timeInjected < TT[ii] + 0.5*TD[ii])]
            fluxTransit_injected = np.interp(timeTransit_orig - TT[ii], timeTransit_scaled*years2sec, fluxTransit_scaled)
            fluxInjected[(timeInjected > TT[ii] - 0.5*TD[ii]) & (timeInjected < TT[ii] + 0.5*TD[ii])] -= (1 - fluxTransit_injected)

            if len(timeTransit_orig) > 0:
                output_time.append(TT[ii])
                output_duration.append(TD[ii])
                output_impactparameter.append(Tb[ii])

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(timeInjected/days2sec-55000, fluxInjected)
    plt.show(block=False)

    np.savetxt(
        os.path.join(out_lightcurves_dir, f'{systemName}_{secondaryName}_injectedTransitList.txt'),
        np.transpose([
            np.array(output_time)/days2sec-55000,
            np.array(output_duration)/hours2sec,
            np.array(output_impactparameter)
        ])
    )

    return timeInjected, fluxInjected


def Do_Interpolation(last_transit_times, last_transit_durations,
                     current_transit_times, current_transit_durations,
                     timeArray, fluxArray):
    '''
    Functionality:
        Interpolate between two transit-solution epochs to propose a new set
        of mid-times and durations, then evaluate that proposal with
        Search_FitTransitMask to obtain a predicted detection significance.

    Arguments:
        last_transit_times (array-like): Previous-epoch transit mid-times [s].
        last_transit_durations (array-like): Previous-epoch durations [s].
        current_transit_times (array-like): Current-epoch transit mid-times [s].
        current_transit_durations (array-like): Current-epoch durations [s].
        timeArray (array-like): Light-curve times [s].
        fluxArray (array-like): Light-curve fluxes (same length as timeArray).

    Returns:
        list:
            [predicted_sigma_solution] where predicted_sigma_solution is the
            scalar significance returned by Search_FitTransitMask. Returns -27
            if either solution has zero transits.
    '''
    # Safe/degenerate case: no transits to interpolate
    if (len(last_transit_times) == 0) or (len(current_transit_times) == 0):
        return -27

    def interp(val1, val2):
        '''
        Functionality:
            Return the midpoint between two values.
    
        Arguments:
            val1 (float): First value.
            val2 (float): Second value.
    
        Returns:
            float:
                (val1 + val2) / 2
        '''
        return (val1 + val2) / 2

    # Align and interpolate times/durations depending on count mismatch
    if len(last_transit_times) == len(current_transit_times):
        new_transit_times = [interp(current_transit_times[ii], last_transit_times[ii])
                             for ii in range(len(last_transit_times))]
        new_transit_durations = [interp(current_transit_durations[ii], last_transit_durations[ii])
                                 for ii in range(len(last_transit_durations))]
    elif len(last_transit_times) > len(current_transit_times):
        if abs(current_transit_times[0] - last_transit_times[0]) > abs(current_transit_times[0] - last_transit_times[1]):
            new_transit_times = [interp(current_transit_times[ii], last_transit_times[ii])
                                 for ii in range(len(current_transit_times))]
            new_transit_durations = [interp(current_transit_durations[ii], last_transit_durations[ii])
                                     for ii in range(len(current_transit_durations))]
        else:
            new_transit_times = [interp(current_transit_times[ii], last_transit_times[ii+1])
                                 for ii in range(len(current_transit_times))]
            new_transit_durations = [interp(current_transit_durations[ii], last_transit_durations[ii+1])
                                     for ii in range(len(current_transit_durations))]
    else:
        if abs(current_transit_times[0] - last_transit_times[0]) > abs(current_transit_times[0] - last_transit_times[1]):
            new_transit_times = [interp(current_transit_times[ii], last_transit_times[ii])
                                 for ii in range(len(last_transit_times))]
            new_transit_durations = [interp(current_transit_durations[ii], last_transit_durations[ii])
                                     for ii in range(len(last_transit_durations))]
        else:
            new_transit_times = [interp(current_transit_times[ii+1], last_transit_times[ii])
                                 for ii in range(len(last_transit_times))]
            new_transit_durations = [interp(current_transit_durations[ii+1], last_transit_durations[ii])
                                     for ii in range(len(last_transit_durations))]

    # Cadence sanity check and evaluation
    sorted_timeArray = np.sort(np.copy(timeArray))
    cadence = min(np.diff(sorted_timeArray))
    if cadence <= 100:
        raise Exception("Data passed in appears to be in days not seconds")
    meanTotalLightcurve = -27
    (meanFlux_solution, predicted_sigma_solution, sigma_solutionNew,
     consistency_solution, fractionDataPointsHit_solution,
     TT_true, stdOutOfTransit) = Search_FitTransitMask(
        timeArray, fluxArray,
        np.array(new_transit_times), np.array(new_transit_durations),
        meanTotalLightcurve, cadence, plotting=False
    )
    return [predicted_sigma_solution]

def Do_Interpolation_N(last_transit_times, last_transit_durations,
                       current_transit_times, current_transit_durations,
                       timeArray, fluxArray, interpolation_distance):
    '''
    Functionality:
        Like Do_Interpolation, but interpolates a fractional distance between
        the two solutions. Distance 0 uses previous solution; 1 uses current.

    Arguments:
        last_transit_times (array-like): Previous-epoch mid-times [s].
        last_transit_durations (array-like): Previous-epoch durations [s].
        current_transit_times (array-like): Current-epoch mid-times [s].
        current_transit_durations (array-like): Current-epoch durations [s].
        timeArray (array-like): Light-curve times [s].
        fluxArray (array-like): Light-curve fluxes.
        interpolation_distance (float): Fraction in [0, 1] from previous to
            current solution.

    Returns:
        list:
            [predicted_sigma_solution] as returned by Search_FitTransitMask.
            Returns -27 if either solution has zero transits.
    '''
    if (interpolation_distance < 0) or (interpolation_distance > 1):
        raise Exception("Interpolation Distance must be [0, 1] not:", interpolation_distance)
    if (len(last_transit_times) == 0) or (len(current_transit_times) == 0):
        return -27

    def interp(val1, val2, d):
        '''
        Functionality:
            Interpolate using (val1 + val2) * d.
            (Note: this is *not* a standard linear interpolation.)
    
        Arguments:
            val1 (float): First value.
            val2 (float): Second value.
            d (float): Scaling factor.
    
        Returns:
            float:
                (val1 + val2) * d
        '''
        return (val1 + val2) * d

    if len(last_transit_times) == len(current_transit_times):
        new_transit_times = [interp(current_transit_times[ii], last_transit_times[ii], interpolation_distance)
                             for ii in range(len(last_transit_times))]
        new_transit_durations = [interp(current_transit_durations[ii], last_transit_durations[ii], interpolation_distance)
                                 for ii in range(len(last_transit_durations))]
    elif len(last_transit_times) > len(current_transit_times):
        if abs(current_transit_times[0] - last_transit_times[0]) > abs(current_transit_times[0] - last_transit_times[1]):
            new_transit_times = [interp(current_transit_times[ii], last_transit_times[ii], interpolation_distance)
                                 for ii in range(len(current_transit_times))]
            new_transit_durations = [interp(current_transit_durations[ii], last_transit_durations[ii], interpolation_distance)
                                     for ii in range(len(current_transit_durations))]
        else:
            new_transit_times = [interp(current_transit_times[ii], last_transit_times[ii+1], interpolation_distance)
                                 for ii in range(len(current_transit_times))]
            new_transit_durations = [interp(current_transit_durations[ii], last_transit_durations[ii+1], interpolation_distance)
                                     for ii in range(len(current_transit_durations))]
    else:
        if abs(current_transit_times[0] - last_transit_times[0]) > abs(current_transit_times[0] - last_transit_times[1]):
            new_transit_times = [interp(current_transit_times[ii], last_transit_times[ii], interpolation_distance)
                                 for ii in range(len(last_transit_times))]
            new_transit_durations = [interp(current_transit_durations[ii], last_transit_durations[ii], interpolation_distance)
                                     for ii in range(len(last_transit_durations))]
        else:
            new_transit_times = [interp(current_transit_times[ii+1], last_transit_times[ii], interpolation_distance)
                                 for ii in range(len(last_transit_times))]
            new_transit_durations = [interp(current_transit_durations[ii+1], last_transit_durations[ii], interpolation_distance)
                                     for ii in range(len(last_transit_durations))]

    sorted_timeArray = np.sort(np.copy(timeArray))
    cadence = min(np.diff(sorted_timeArray))
    if cadence <= 100:
        raise Exception("Data passed in appears to be in days not seconds")
    meanTotalLightcurve = -27
    (meanFlux_solution, predicted_sigma_solution, sigma_solutionNew,
     consistency_solution, fractionDataPointsHit_solution,
     TT_true, stdOutOfTransit) = Search_FitTransitMask(
        timeArray, fluxArray,
        np.array(new_transit_times), np.array(new_transit_durations),
        meanTotalLightcurve, cadence, plotting=False
    )
    return [predicted_sigma_solution]

 
def Progress_Bar(simCount, totalParams, simStartTime, onCluster):
    '''
    Functionality:
        Print a compact ETA/progress readout for long simulations when running
        locally. Returns elapsed wall time regardless of environment.

    Arguments:
        simCount (int): Zero-based index of current simulation.
        totalParams (int): Total number of simulations/tasks.
        simStartTime (float): Epoch timestamp from TIME.time() at start.
        onCluster (bool): If True, suppresses console output.

    Returns:
        float:
            simElapsedTime (seconds) since simStartTime.
    '''
    simPercentageComplete = 100.*(simCount+1)/(totalParams)
    simElapsedTime = TIME.time() - simStartTime
    simTotalTime = simElapsedTime/(simPercentageComplete/100.)
    remainingTime = simTotalTime - simElapsedTime
    if (onCluster == False):
        if (remainingTime < 60):
            sys.stdout.write("Remaining time (sec): %.2f, %d%% completed   \r" % (remainingTime,simPercentageComplete))
        elif (remainingTime > 60 and remainingTime < 3600):
            sys.stdout.write("Remaining time (min): %.2f, %d%% completed   \r" % (remainingTime/60.,simPercentageComplete))
        elif (remainingTime > 3600 and remainingTime < 86400):
            sys.stdout.write("Remaining time (hrs): %.2f, %d%% completed   \r" % (remainingTime/3600.,simPercentageComplete))
        elif (remainingTime > 86400):
            sys.stdout.write("Remaining time (days): %.2f, %d%% completed   \r" % (remainingTime/86400.,simPercentageComplete))
        sys.stdout.flush()
    return simElapsedTime

def log_info(filename, info, do_logging=False):
    '''
    Functionality:
        Append a line or list of lines to a text file if logging is enabled.

    Arguments:
        filename (str): Target file path.
        info (str | list[str]): Single string or list of strings to write.
        do_logging (bool): If True, writes to file; otherwise no-op.

    Returns:
        None
    '''
    if do_logging:
        with open(filename, "a") as f:
            if type(info) == list:
                f.writelines(info)
            else:
                f.write(info)

def Get_transit_times(z, RA, RB, timeArray, fluxArray, returnTransitTimes=True,
                      meanTotalLightcurve=-27, plotting=False,
                      mission='BLAH', ID='BLAH', SearchName='BLAH', maxCompTime=1):
    '''
    Functionality:
        Build a REBOUND simulation from parameter vector `z`, then compute
        predicted transit times/durations using SSTT.TransitTiming_nbody_lite
        across the provided light-curve time span.

    Arguments:
        z (tuple): (mA, mB, Pbin, ebin, omegabin, thetabin, Pp, ep, omegap, thetap)
            masses [kg], periods [s], angles [rad].
        RA, RB (float): Stellar radii [m] for primary and secondary (used in sim).
        timeArray (array-like): Light-curve times [s]; defines start/end times.
        fluxArray (array-like): Unused here; kept for API symmetry.
        returnTransitTimes (bool): Unused here; kept for API symmetry.
        meanTotalLightcurve (float): Unused here; kept for API symmetry.
        plotting (bool): Unused here; kept for API symmetry.
        mission, ID, SearchName (str): Unused here; kept for API symmetry.
        maxCompTime (float): Per-call computation time limit passed downstream.

    Returns:
        dict:
            Output of SSTT.TransitTiming_nbody_lite, including fields such as
            'transitTimes', 'transitDurations', 'stable', and 'exceedMaxCompTime'.

    Raises:
        Exception: If the cadence inferred from timeArray suggests days instead
            of seconds (cadence <= 100).
    '''
    _mA,_mB,_Pbin,_ebin,_omegabin,_thetabin,_Pp,_ep,_omegap,_thetap = z

    timeStart = timeArray[0]
    timeEnd = timeArray[-1]

    searchSim = rebound.Simulation()
    searchSim.units = ('s','m','kg')
    mass = [_mA,_mB,0.]
    period = np.array([_Pbin,_Pp])
    a = AC.PeriodToSemiMajorAxis(mass,period)
    searchSim.add(m=_mA, r=RA)
    searchSim.add(m=_mB, r=RB, a=a[0], e=_ebin, omega=_omegabin, theta=_thetabin)
    searchSim.add(a=a[1], e=_ep, omega=_omegap, theta=_thetap)
    searchSim.t = timeStart

    sortedTime = np.sort(timeArray)
    cadence = min(np.diff(sortedTime))
    if cadence <= 100:
        raise Exception(f"Data passed in appears to be in days not seconds{cadence}")

    transitData_search = SSTT.TransitTiming_nbody_lite(searchSim, timeEnd, cadence, maxCompTime=maxCompTime)
    return transitData_search


def bin_and_plot_lightcurve(
    lc: Optional[lk.LightCurve] = None,
    time: Optional[np.ndarray] = None,
    flux: Optional[u.Quantity] = None,
    flux_err: Optional[u.Quantity] = None,
    bin_minutes=30,
    gap_threshold_minutes=30,
    plot=False,
    xlb=None,
    xub=None,
    ylb=0,
    yub=10
):
    '''
    Functionality:
        Segment a light curve on large time gaps and bin each contiguous
        segment by a fixed time interval. Optionally plot the binned result.

    Arguments:
        lc (lightkurve.LightCurve, optional): Input LightCurve object. If given,
            `time`, `flux`, and `flux_err` are ignored.
        time (np.ndarray, optional): Time stamps as BTJD (BJD - 2457000) [days].
        flux (astropy.units.Quantity, optional): Flux values.
        flux_err (astropy.units.Quantity, optional): Flux uncertainties.
        bin_minutes (float): Bin size [minutes].
        gap_threshold_minutes (float): Gap threshold separating segments [min].
        plot (bool): If True, generates an errorbar plot.
        xlb, xub (float): X-axis limits for plotting (BTJD). If None, auto-determined.
        ylb, yub (float): Y-axis limits for plotting.

    Returns:
        tuple:
            (binned_btjd, binned_flux, binned_flux_err)
    '''

    # --- Input Handling ---
    if lc is not None:
        btjd = lc.time.btjd
        flux = lc.flux
        flux_err = lc.flux_err
    elif time is not None and flux is not None and flux_err is not None:
        btjd = time
    else:
        raise ValueError("Provide either a LightCurve object or time, flux, and flux_err arrays.")

    bin_seconds = bin_minutes * 60
    gap_threshold = gap_threshold_minutes / (24 * 60)  # minutes → days

    # --- Sort by time ---
    sort_idx = np.argsort(btjd)
    btjd = np.array(btjd)[sort_idx]
    flux = flux[sort_idx]
    flux_err = flux_err[sort_idx]

    # Auto-determine x-axis bounds if not supplied
    if xlb is None:
        xlb = np.min(btjd)
    if xub is None:
        xub = np.max(btjd)

    # --- Identify segments separated by gaps ---
    gaps = np.diff(btjd) > gap_threshold
    segment_edges = np.concatenate(([0], np.where(gaps)[0] + 1, [len(btjd)]))

    binned_btjd = []
    binned_flux = []
    binned_flux_err = []

    # --- Bin each segment ---
    for i in range(len(segment_edges) - 1):
        start, end = segment_edges[i], segment_edges[i + 1]
        btjd_seg = btjd[start:end]
        flux_seg = flux[start:end]
        flux_err_seg = flux_err[start:end]

        if len(btjd_seg) == 0:
            continue

        time_sec = btjd_seg * 86400.0
        bin_edges = np.arange(time_sec[0], time_sec[-1] + bin_seconds, bin_seconds)
        bin_indices = np.digitize(time_sec, bin_edges)

        for j in range(1, len(bin_edges)):
            in_bin = bin_indices == j
            if not np.any(in_bin):
                continue

            fluxes_bin = flux_seg[in_bin]
            errors_bin = flux_err_seg[in_bin]
            times_bin = btjd_seg[in_bin]

            # Skip masked/unusable bins
            if np.all(np.ma.getmaskarray(fluxes_bin)) or np.all(np.isnan(fluxes_bin)):
                continue

            n_points = len(fluxes_bin)
            mean_flux = np.mean(fluxes_bin)
            mean_error = np.mean(errors_bin) / np.sqrt(n_points)

            if np.isnan(mean_flux) or np.isnan(mean_error):
                continue

            binned_btjd.append(np.mean(times_bin))
            binned_flux.append(mean_flux)
            binned_flux_err.append(np.abs(mean_error))

    # Convert time to astropy Time if plotting
    binned_time = Time(np.array(binned_btjd) + 2457000, format='jd')
    binned_flux = u.Quantity(binned_flux)
    binned_flux_err = u.Quantity(binned_flux_err)

    # --- Plotting ---
    if plot:
        plt.figure(figsize=(10, 4))
        plt.errorbar(binned_time.btjd, binned_flux, yerr=binned_flux_err,
                     fmt='.', alpha=0.8, label="Binned Light Curve")
        plt.xlabel("Time [BJD - 2457000]")
        plt.ylabel(f"Flux [{binned_flux.unit}]")
        plt.title(f"Binned Light Curve (Bin Size = {bin_minutes} min)")
        plt.xlim(xlb, xub)
        plt.ylim(ylb, yub)
        plt.legend()
        plt.tight_layout()
        plt.show()

    return np.array(binned_btjd), binned_flux, binned_flux_err

