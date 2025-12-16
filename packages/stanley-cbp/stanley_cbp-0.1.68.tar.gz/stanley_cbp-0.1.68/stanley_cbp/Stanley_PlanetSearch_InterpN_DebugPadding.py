# -*- coding: utf-8 -*-

"""
Functionality:
    Runs the Stanley circumbinary planet **search** by forward-modeling an N-body grid
    over (e_p, ω_p, P_p, θ_p), building transit masks, and recording the per-grid
    significance (σ). The period–theta grid is adaptive; the (e, ω) grid samples full
    0–360° at each eccentricity level. This script writes all sector outputs needed
    for downstream aggregation/analysis.

Command-line Arguments:
    --searchName (str): Identifier for this run (folder under PlanetSearchOutput).
    --systemName (str): Target identifier (e.g., 'Kepler 16' or a resolvable TIC/KIC).
    --detrendingName (str): Label matching the detrended LC & binary params artifacts.
    --totalSectors (int): Total θ_p sectors used to split the workload.
    --currentSector (int): Which sector index to compute (1-indexed).
    --onCluster (int): 0/1 flag to format progress output for HPC logs.
    --parallel (int): 0/1 to dispatch all sectors via multiprocessing.
    --interpolationValue (int): Skip N theta samples and interpolate between sims.

Inputs (Required pipeline artifacts):
    LightCurves/Processed/<DetrendingName>/<MISSION>_<ID>_<DetrendingName>_detrended.csv
    LightCurves/Processed/<DetrendingName>/<MISSION>_<ID>_<DetrendingName>_binaryStartingParams.csv

Outputs (Written by this script):
    PlanetSearchOutput/<searchName>/<MISSION>_<ID>_searchParameters_array
        - Human-readable Python literal with the grids used (mA/mB/P_bin/e_bin/ω_bin/θ_bin,
          plus the (P_p, θ_p) and (e_p, ω_p) grids).
    PlanetSearchOutput/<searchName>/<MISSION>_<ID>_simInfo.npy
        - Tuple: (searchName, systemName, detrendingName, totalSectors, mission, ID).
        - Written by sector 1 (for analysis to discover the context and detrending label).
    PlanetSearchOutput/<searchName>/<MISSION>_<ID>_searchResults_array_<totalSectors>_<currentSector>.npy
        - High-dimensional tensor packing σ over the grid for this sector only.
    PlanetSearchOutput/<searchName>/<MISSION>_<ID>_minutesTimeTaken.txt
        - Wall-clock runtime in minutes for this sector.

Runtime Behavior / Notes:
    - Uses path helpers from Stanley_Functions (AC.base_dir / AC.p_outputs / AC.p_processed)
      so working directory does not matter. You may override the base via the STANLEY_BASE env var.
    - Time is handled internally in SI seconds; detrended CSV stores times in days and is converted.
    - The θ_p dimension can be sparsely simulated with --interpolationValue > 1; skipped thetas are
      filled via AC.Do_Interpolation_N between consecutive simulated masks.
    - σ sentinel values:
        * -27 indicates dynamically unstable cells (or pruned regions).
        * -29 pads unused θ/ω slots to a consistent rectangular tensor.
    - This script must complete sector 1 to produce simInfo and searchParameters_array for analysis.
"""

import os
import sys
import io
import time
import importlib
import rebound
import math
import timeit
import datetime
import matplotlib
matplotlib.use("Agg")  # headless-safe everywhere
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection
from collections import OrderedDict
from mpl_toolkits.mplot3d import Axes3D
from scipy import optimize
import pylab, argparse, warnings
import multiprocessing
from functools import partial
from pathlib import Path

# Package-relative import fallback
try:
    # package mode
    from . import Stanley_Functions as AC
    from . import Stanley_TransitTiming as SSTT
    from .Stanley_Constants import *
except Exception:
    # repo (flat) mode
    import Stanley_Functions as AC
    import Stanley_TransitTiming as SSTT
    from Stanley_Constants import *

# 2A: Use AC base + path helpers
BASE = AC.base_dir()
_p_outputs     = AC.p_outputs
_p_processed   = AC.p_processed
_p_lightcurves = AC.p_lightcurves

# Main search function
def Stanley_FindPlanets(
    SearchName='BLAH',
    SystemName='Kepler-64',
    DetrendingName='BLAH',
    totalSectors=1,
    onCluster=False,
    currentSector=1,
    N_interp=1,
    BoundsType=None,
    MinValue=None,
    MaxValue=None,
    e_max_planet = 0.2,
):
    '''
    Functionality:
        Perform a planetary search using an N-body forward model over a grid of orbital parameters.
        Each grid cell defines a combination of binary and planetary parameters (e, ω, P, θ) to evaluate
        the light curve’s transit consistency. Results are stored per-sector for later aggregation.

    Arguments:
        SearchName (str): Name of the search output directory.
        SystemName (str): Identifier of the binary system (e.g. 'Kepler-64' or 'TIC 123456').
        DetrendingName (str): Label of the detrending used to produce the LC CSVs.
        totalSectors (int): Total number of sector partitions for parallelized searches.
        onCluster (bool): Cluster/HPC flag for progress output format.
        currentSector (int): Current sector being processed (1-indexed).
        N_interp (int): Skip this many θ points between direct sims and fill via interpolation.
        e_max_planet (float): Maximum planetary eccentricity to sample. Set to 0.0 for circular only orbits in the local tutorial run.

    Returns:
        None. Saves outputs to PlanetSearchOutput/<SearchName>/ (legacy filenames).
    '''

    # small debug helper
    def _ts():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    def _dbg(msg):
        print(f"[{_ts()}] {msg}", flush=True)

    _dbg("=== BEGIN Stanley_FindPlanets ===")
    _dbg(f"currentSector = {currentSector}, totalSectors = {totalSectors}, N_interp = {N_interp}")
    _dbg(f"SearchName = {SearchName}")
    _dbg(f"SystemName = {SystemName}")
    _dbg(f"DetrendingName = {DetrendingName}")
    _dbg(f"BASE = {BASE}")

    warnings.filterwarnings("ignore")

    t_reload0 = time.time()
    _dbg("Reloading modules AC and SSTT...")
    importlib.reload(AC)
    importlib.reload(SSTT)
    _dbg(f"Modules reloaded in {round(time.time() - t_reload0, 2)} s")

    plt.close("all")
    plt.ion
    pylab.ion

    # Threshold parameters (kept for parity)
    consistencyThreshold = 3
    consistencySigmaFactor = 0.45
    fractionDataPointsHitThreshold = 0.45
    individualDataPointSigmaCutThreshold = 3

    # STEP 1. LOAD DETRENDED LIGHT CURVE
    _dbg("Calling AC.GetID to resolve mission/ID...")
    ID, mission = AC.GetID(SystemName)
    _dbg(f"Resolved: mission = {mission}, ID = {ID}")
    if mission not in ("TIC", "KIC"):
        raise Exception("Mission should be TIC or KIC not:", mission)

    # Input paths (repo-root aware via AC helpers)
    detrended_csv = _p_processed(DetrendingName, f"{mission}_{ID}_{DetrendingName}_detrended.csv")
    binary_csv    = _p_processed(DetrendingName, f"{mission}_{ID}_{DetrendingName}_binaryStartingParams.csv")

    # 2B: Preflight checks before reads
    _dbg(f"Reading detrended data: {detrended_csv}")
    _dbg(f"Reading binary parameters: {binary_csv}")
    _dbg(f"Exists? detrended_csv={detrended_csv.exists()}  binary_csv={binary_csv.exists()}")

    if not detrended_csv.exists():
        raise FileNotFoundError(
            f"Missing detrended CSV. Rerun detrending with --detrendingName {DetrendingName}\nExpected: {detrended_csv}"
        )
    if not binary_csv.exists():
        raise FileNotFoundError(
            "Missing binaryStartingParams CSV (usually written during detrending/period validation).\n"
            f"Expected: {binary_csv}\n"
            "Ensure detrending finished and wrote binary params under the SAME DetrendingName."
        )

    t_io0 = time.time()
    detrendedData = np.transpose(np.genfromtxt(str(detrended_csv)))
    _dbg(f"Loaded detrended data in {round(time.time() - t_io0, 2)} s; N={len(detrendedData[0])}")

    timeArray = detrendedData[0] * days2sec
    fluxArray = detrendedData[1]

    t_io1 = time.time()
    binaryParamsFile = np.genfromtxt(str(binary_csv), delimiter=',')
    _dbg(f"Loaded binary params in {round(time.time() - t_io1, 2)} s")

    mA_set = binaryParamsFile[0][1] * mSun_kg
    mB_set = binaryParamsFile[1][1] * mSun_kg
    RA_set = binaryParamsFile[2][1] * rSun_m
    RB_set = binaryParamsFile[3][1] * rSun_m
    if mission == "KIC":
        bjd0bin_set = (binaryParamsFile[4][1] + 55000) * days2sec
    elif mission == "TIC":
        bjd0bin_set = binaryParamsFile[4][1] * days2sec
    thetabin_set = np.radians(binaryParamsFile[5][1])
    Pbin_set = binaryParamsFile[6][1] * days2sec
    ebin_set = binaryParamsFile[7][1]
    omegabin_set = np.radians(binaryParamsFile[8][1])

    _dbg(f"Binary params summary: mA={mA_set/mSun_kg:.3f} Msun, mB={mB_set/mSun_kg:.3f} Msun, Pbin={Pbin_set/days2sec:.3f} d, e={ebin_set:.4f}")

    # LC stats (used in mask-making)
    meanTotalLightcurve = np.mean(fluxArray)
    maxTotalLightcurve = np.max(fluxArray)
    _dbg(f"Lightcurve stats: mean={meanTotalLightcurve:.6f}, max={maxTotalLightcurve:.6f}")

    # STEP 2. DEFINE THE SEARCH GRID
    t_grid0 = time.time()
    _dbg("Defining base (fixed) binary grids (1-point each)...")
    # legacy 1-point arrays to preserve array shapes
    mA_search = np.linspace(1.0 * mA_set, 1.0 * mA_set, 1)
    mB_search = np.linspace(1.0 * mB_set, 1.0 * mB_set, 1)
    Pbin_search = np.linspace(1.0 * Pbin_set, 1.0 * Pbin_set, 1)
    ebin_search = np.linspace(1.0 * ebin_set, 1.0 * ebin_set, 1)
    omegabin_search = np.linspace(1.0 * omegabin_set, 1.0 * omegabin_set, 1)
    thetabin_search = np.linspace(1.0 * thetabin_set, 1.0 * thetabin_set, 1)
    _dbg("Base grids defined.")

    # Eccentricity and omega grid
    density_circle = 1
    numEccSteps = 4

    if e_max_planet > 0:
        delta_e = e_max_planet / (numEccSteps - 1)
        _dbg(
            f"Building ecc/omega grid with e_max_planet={e_max_planet}, "
            f"delta_e={delta_e}, density_circle={density_circle}..."
        )
        eccANDomega_search = AC.CalculateEccentricityOmegaSearchGrid(
            e_max=e_max_planet,
            delta_e=delta_e,
            density_circle=density_circle,
        )
    else:
        # Circular only planetary grid: ep = 0, omegap = 0
        eccANDomega_search = [[0.0, np.array([0.0])]]
        _dbg("Using circular only planetary grid (ep = 0, omegap = 0).")

    _dbg(
        f"eccANDomega_search built: {len(eccANDomega_search)} eccentricity levels; "
        f"omegas at first level: {len(eccANDomega_search[0][1])}"
    )

    # Period/Theta adaptive grid
    min_time = float(np.min(timeArray))
    max_time = float(np.max(timeArray))
    total_length_of_data = max_time - min_time
    _dbg(f"Time span: {total_length_of_data/days2sec:.2f} days")

    _dbg("Building period/theta adaptive grid...")
    t_grid1 = time.time()
    
    # Make the bounds type, minValue, and maxValue optional arguments
    if (BoundsType == None) and (MinValue == None) and (MaxValue == None):
        BoundsType = 'stability limit ratio to stability limit ratio'
        MinValue = 2.2
        MaxValue = 4.1

    periodANDtheta_search = AC.CalculatePeriodThetaSearchGrid(
        mA_set, mB_set, RA_set, RB_set, Pbin_set, ebin_set, 'adaptive period theta',
        durationFactor_thetap=3., durationFactor_P=3., minValue=MinValue, maxValue=MaxValue,
        boundsType=BoundsType, length_of_data=total_length_of_data
    )
    _dbg(f"periodANDtheta_search built in {round(time.time() - t_grid1, 2)} s; periods={len(periodANDtheta_search)}")
    if len(periodANDtheta_search) > 0:
        _dbg(f"Example: first period has {len(periodANDtheta_search[0][1])} thetas")

    # Preserve original full list for metadata and shape info
    periodANDtheta_search_orig = periodANDtheta_search.copy()

    # OUTPUT FOLDER + SECTOR SLICING
    out_dir = _p_outputs(SearchName)
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)
        _dbg(f"Created output folder: {out_dir}")
    else:
        _dbg(f"Using existing output folder: {out_dir}")

    if totalSectors > 1:
        startIndex = int(round((currentSector - 1.) / totalSectors * len(periodANDtheta_search)))
        endIndex = int(round((currentSector) / totalSectors * len(periodANDtheta_search)))
        _dbg(f"Slicing periods for sector {currentSector}/{totalSectors}: startIndex={startIndex}, endIndex={endIndex}")
        periodANDtheta_search = periodANDtheta_search[startIndex:endIndex]
        _dbg(f"Sliced period count for this sector: {len(periodANDtheta_search)}")

    # METADATA OUTPUTS (LEGACY NAMES) ON SECTOR 1
    periodANDtheta_search_orig_list = [[pt[0], list(pt[1])] for pt in periodANDtheta_search_orig]
    eccANDomega_search_list = [[eo[0], list(eo[1])] for eo in eccANDomega_search]
    z = (
        list(mA_search), list(mB_search), list(Pbin_search), list(ebin_search),
        list(omegabin_search), list(thetabin_search),
        periodANDtheta_search_orig_list, eccANDomega_search_list
    )

    if currentSector == 1:
        params_txt = out_dir / f"{mission}_{ID}_searchParameters_array"
        _dbg(f"Saving search parameter array (sector 1) to {params_txt}")
        with open(params_txt, "w") as outfile:
            outfile.write(str(z))

        siminfo_base = out_dir / f"{mission}_{ID}_simInfo"
        simInfo = (SearchName, SystemName, DetrendingName, totalSectors, mission, ID)
        np.save(str(siminfo_base), simInfo)
        _dbg(f"Saved simInfo to {siminfo_base}.npy")

    # PARAMETER-SPACE SUMMARY (LEGACY PRINTS)
    numParams = 1
    for ii in range(0, 6):
        numParams *= len(z[ii])

    numThetaValues = sum(len(pt[1]) for pt in periodANDtheta_search)
    numParams *= numThetaValues

    numOmegaValues = sum(len(eo[1]) for eo in eccANDomega_search)
    numParams *= numOmegaValues

    _dbg("----- SEARCH SUMMARY -----")
    print("Search for planets around " + SystemName + " (" + mission + "_" + ID + ") DetrendingName =  " + DetrendingName + " and SearchName =  " + SearchName, flush=True)
    print("Total parameter space size: {}".format(numParams), flush=True)
    print("mA between [{},{}] with step size {}".format(np.min(mA_search) / mSun_kg, np.max(mA_search) / mSun_kg, (mA_search[np.mod(1, len(mA_search))] - mA_search[0]) / mSun_kg), flush=True)
    print("mB between [{},{}] with step size {}".format(np.min(mB_search) / mSun_kg, np.max(mB_search) / mSun_kg, (mB_search[np.mod(1, len(mB_search))] - mB_search[0]) / mSun_kg), flush=True)
    print("--", flush=True)
    print("Pbin between [{},{}] with step size {}".format(np.min(Pbin_search) / days2sec, np.max(Pbin_search) / days2sec, (Pbin_search[np.mod(1, len(Pbin_search))] - Pbin_search[0]) / days2sec), flush=True)
    print("ebin between [{},{}] with step size {}".format(np.min(ebin_search), np.max(ebin_search), ebin_search[np.mod(1, len(ebin_search))] - ebin_search[0]), flush=True)
    print("omegabin between [{},{}] with step size {}".format(np.min(omegabin_search) / (np.pi / 180.), np.max(omegabin_search) / (np.pi / 180.), np.degrees(omegabin_search[np.mod(1, len(omegabin_search))] - omegabin_search[0])) , flush=True)
    print("thetabin between [{},{}] with step size {}".format(np.min(thetabin_search) / (np.pi / 180.), np.max(thetabin_search) / (np.pi / 180.), np.degrees(thetabin_search[np.mod(1, len(thetabin_search))] - thetabin_search[0])) , flush=True)
    print("--", flush=True)
    if len(periodANDtheta_search) > 0:
        print("Pp between [{},{}] ({} steps total)".format(periodANDtheta_search[-1][0] / days2sec, periodANDtheta_search[0][0] / days2sec, len(periodANDtheta_search)), flush=True)
        print("thetap between [{},{}] with step size between {} deg ({} steps) and {} deg ({} steps)".format(
            np.min(periodANDtheta_search[0][1]) / (np.pi / 180.), np.max(periodANDtheta_search[0][1]) / (np.pi / 180.),
            np.degrees(periodANDtheta_search[-1][1][1] - periodANDtheta_search[-1][1][0]) if len(periodANDtheta_search[-1][1]) > 1 else np.nan,
            len(periodANDtheta_search[-1][1]),
            np.degrees(periodANDtheta_search[0][1][1] - periodANDtheta_search[0][1][0]) if len(periodANDtheta_search[0][1]) > 1 else np.nan,
            len(periodANDtheta_search[0][1])
        ), flush=True)
    print("Circular eccentricity and omega grid", flush=True)
    print("ep between [{},{}] with step size {}".format(eccANDomega_search[0][0], eccANDomega_search[-1][0], eccANDomega_search[np.mod(1, len(eccANDomega_search))][0] - eccANDomega_search[0][0]), flush=True)
    print("omegap full 360 deg with density = {}x delta_e and average step size = {} deg ({} steps total over all eccentricity)".format(
        density_circle, 360. / numOmegaValues * len(eccANDomega_search), numOmegaValues
    ), flush=True)
    _dbg(f"Search setup done in {round(time.time() - t_grid0, 2)} s total since grid start")

    # SEARCH
    # (legacy) predeclare logging flag/filename (kept false by default)
    do_logging = False
    log_filename = _p_outputs(SearchName, f"{mission}_{ID}_log_of_searchResults_sector_{currentSector}")

    # Allocate results with legacy dimension logic
    num_periods_to_search = len(periodANDtheta_search)
    num_eccentricities_to_search = len(eccANDomega_search)
    length_longest_omega_grid = len(eccANDomega_search[-1][1]) if num_eccentricities_to_search > 0 else 0
    length_longest_theta_grid = len(periodANDtheta_search_orig[-1][1]) if len(periodANDtheta_search_orig) > 0 else 0
    size_of_individual_result = 1

    _dbg("Allocating searchResults array...")
    searchResults = np.ndarray(
        shape=[
            len(mA_search), len(mB_search), len(Pbin_search), len(ebin_search),
            len(omegabin_search), len(thetabin_search),
            num_periods_to_search, num_eccentricities_to_search,
            length_longest_omega_grid, length_longest_theta_grid, size_of_individual_result
        ],
        dtype=float
    )
    _dbg(f"searchResults shape = {searchResults.shape}")

    # Index iterator (exclude final 2 dims)
    _dbg("Generating index_search iterator...")
    index_search = np.ndindex(np.shape(searchResults)[0:-2])
    _dbg("index_search ready.")

    totalParams = np.product(np.shape(searchResults)[0:-1])
    simCount = 0
    simStartTime = time.time()
    simExpectedTimeOutputted = False
    simExpectedTime = -27

    maxCompTime = np.inf  # adaptive cap via compTime
    compTime = np.zeros(1000)
    _dbg("Starting main search loop...")

    for index in index_search:
        # breadcrumb across the grid
        if index[6] % 10 == 0 and index[7] == 0 and index[8] == 0:
            _dbg(f"Loop progress marker: period idx {index[6]}/{num_periods_to_search}, ecc idx {index[7]}, omega idx {index[8]}")

        this_omega_index = index[8]
        if index[7] < len(eccANDomega_search):
            num_of_omegas_at_eccentricity = len(eccANDomega_search[index[7]][1])
        else:
            num_of_omegas_at_eccentricity = 0

        # inside circular grid?
        if this_omega_index < num_of_omegas_at_eccentricity and index[6] < len(periodANDtheta_search):
            thetas = periodANDtheta_search[index[6]][1]
            period = periodANDtheta_search[index[6]][0]
            eccentricity = eccANDomega_search[index[7]][0]
            this_omega = eccANDomega_search[index[7]][1][this_omega_index]
            is_this_first = True
            last_transit_times = []
            last_transit_durations = []

            # Walk thetas with interpolation gaps
            for ii in range(0, len(thetas), N_interp):
                theta = thetas[ii]
                specificSimStartTime = time.time()
                this_z = (mA_search[index[0]], mB_search[index[1]], Pbin_search[index[2]], ebin_search[index[3]],
                          omegabin_search[index[4]], thetabin_search[index[5]], period, eccentricity, this_omega, theta)

                if is_this_first:
                    last_transit_times, last_transit_durations, sigma_solutionOld, _, _ = AC.Search_CreateTransitMask(
                        this_z, RA_set, RB_set, timeArray, fluxArray,
                        meanTotalLightcurve=meanTotalLightcurve, plotting=False, mission=mission, ID=ID, SearchName=SearchName, maxCompTime=maxCompTime
                    )
                    searchResults[index][ii] = [sigma_solutionOld]
                    specificSimEndTime = time.time()
                    is_this_first = False
                    AC.log_info(str(log_filename), [f"First transit times: {last_transit_times}\n",
                                                    f"First transit durations: {last_transit_durations}\n",
                                                    f"First: {sigma_solutionOld}\n"], do_logging=do_logging)
                else:
                    current_transit_times, current_transit_durations, sigma_solutionOld, _, _ = AC.Search_CreateTransitMask(
                        this_z, RA_set, RB_set, timeArray, fluxArray,
                        returnTransitTimes=True, meanTotalLightcurve=meanTotalLightcurve, plotting=False, mission=mission, ID=ID, SearchName=SearchName, maxCompTime=maxCompTime
                    )
                    searchResults[index][ii] = [sigma_solutionOld]
                    AC.log_info(str(log_filename), [f"Current transit times: {current_transit_times}\n",
                                                    f"Current transit durations: {current_transit_durations}\n",
                                                    f"Current: {sigma_solutionOld}\n"], do_logging=do_logging)
                    specificSimEndTime = time.time()

                    # Interpolate skipped thetas
                    previous_ii = ii - N_interp
                    for jj in range(previous_ii + 1, ii, 1):
                        interpolation_distance = (jj - previous_ii) / N_interp
                        sigma_interp = AC.Do_Interpolation_N(
                            last_transit_times, last_transit_durations,
                            current_transit_times, current_transit_durations,
                            timeArray, fluxArray, interpolation_distance
                        )
                        searchResults[index][jj] = sigma_interp
                        AC.log_info(str(log_filename), f"Interp: {sigma_interp}\n", do_logging=do_logging)

                    last_transit_times = current_transit_times
                    last_transit_durations = current_transit_durations

                # adaptive runtime cap
                if (specificSimEndTime - specificSimStartTime < maxCompTime) and (np.sum(compTime > 0) < len(compTime)):
                    compTime[np.sum(compTime > 0)] = specificSimEndTime - specificSimStartTime
                    maxCompTime = np.mean(compTime[compTime > 0]) * 100

                # progress (simulate + interpolate counted as 2)
                simCount += 2
                simElapsedTime = AC.Progress_Bar(simCount, totalParams, simStartTime, onCluster)
                if simCount % 50 == 0:
                    _dbg(f"Progress: simCount={simCount}/{totalParams}, elapsed={round((time.time()-simStartTime)/60,2)} min")

            # If loop ended before final theta due to step > 1, fill remainder by direct sims
            if len(thetas) > 0 and 'ii' in locals() and ii < len(thetas) - 1:
                for kk in range(ii, len(thetas)):
                    theta = thetas[kk]
                    specificSimStartTime = time.time()
                    this_z = (mA_search[index[0]], mB_search[index[1]], Pbin_search[index[2]], ebin_search[index[3]],
                              omegabin_search[index[4]], thetabin_search[index[5]], period, eccentricity, this_omega, theta)
                    last_transit_times, last_transit_durations, sigma_solutionOld, _, _ = AC.Search_CreateTransitMask(
                        this_z, RA_set, RB_set, timeArray, fluxArray,
                        returnTransitTimes=True, meanTotalLightcurve=meanTotalLightcurve, plotting=False, mission=mission, ID=ID, SearchName=SearchName, maxCompTime=maxCompTime
                    )
                    searchResults[index][kk] = [sigma_solutionOld]
                    AC.log_info(str(log_filename), [f"Final if even transit times: {last_transit_times}\n",
                                                    f"Final if even transit durations: {last_transit_durations}\n",
                                                    f"Final if even: {sigma_solutionOld}\n"], do_logging=do_logging)
                    specificSimEndTime = time.time()

                    if (specificSimEndTime - specificSimStartTime < maxCompTime) and (np.sum(compTime > 0) < len(compTime)):
                        compTime[np.sum(compTime > 0)] = specificSimEndTime - specificSimStartTime
                        maxCompTime = np.mean(compTime[compTime > 0]) * 100

                    simCount += 1
                    simElapsedTime = AC.Progress_Bar(simCount, totalParams, simStartTime, onCluster)
                    if simCount % 50 == 0:
                        _dbg(f"Progress: simCount={simCount}/{totalParams}, elapsed={round((time.time()-simStartTime)/60,2)} min")

            # Fill remaining theta slots with sentinel -29 (outside grid length)
            for ii2 in range(len(thetas), length_longest_theta_grid):
                searchResults[index][ii2] = -29
                simCount += 1
                simElapsedTime = AC.Progress_Bar(simCount, totalParams, simStartTime, onCluster)
                if simCount % 50 == 0:
                    _dbg(f"Progress: simCount={simCount}/{totalParams}, elapsed={round((time.time()-simStartTime)/60,2)} min")

        # Outside omega grid, fill with -29
        else:
            searchResults[index] = -29

    # SAVE OUTPUTS (LEGACY FILENAMES)
    _dbg("Main loop complete, saving outputs...")

    out_arr_base = _p_outputs(SearchName, f"{mission}_{ID}_searchResults_array_{totalSectors}_{currentSector}")
    np.save(str(out_arr_base), searchResults)
    _dbg(f"searchResults saved to: {out_arr_base}.npy")

    # Legacy minutesTimeTaken "txt" → write plain text minutes (not .npy)
    runtime_txt = _p_outputs(SearchName, f"{mission}_{ID}_minutesTimeTaken.txt")
    # simElapsedTime is in seconds; store minutes as in the original behavior
    minutes_taken = np.array([simElapsedTime / 60.0], dtype=float)
    np.savetxt(str(runtime_txt), minutes_taken)
    _dbg(f"Runtime (minutes) saved to: {runtime_txt}")

    now = datetime.datetime.now()
    _dbg(f"Sector {currentSector} finished at {now}")
    _dbg("=== END Stanley_FindPlanets ===")
    
# Parallel wrappers (cluster)
def parallel(args):
    '''
    Execute Stanley_FindPlanets in parallel across multiple sectors using multiprocessing.
    '''
    print(f"[{datetime.datetime.now()}] Entering parallel(args)", flush=True)
    pool = multiprocessing.Pool()
    SearchName = args.searchName
    SystemName = args.systemName
    DetrendingName = args.detrendingName
    totalSectors = args.totalSectors
    onCluster = bool(args.onCluster)
    interpValue = args.interpolationValue
    boundsType = args.boundsType if hasattr(args, 'boundsType') else 'stability limit ratio to stability limit ratio'
    MinValue = args.minValue if hasattr(args, 'minValue') else 2.2
    MaxValue = args.maxValue if hasattr(args, 'maxValue') else 4.1
    e_max_planet = args.e_max_planet if hasattr(args, 'e_max_planet') else 0.2
    currentSector = range(1, totalSectors + 1)
    func = partial(Stanley_FindPlanets, SearchName, SystemName, DetrendingName, totalSectors, onCluster, N_interp=interpValue, BoundsType=boundsType, MinValue=MinValue, MaxValue=MaxValue, e_max_planet=e_max_planet)
    print(f"[{datetime.datetime.now()}] Launching pool.map over sectors 1..{totalSectors}", flush=True)
    pool.map(func, currentSector)
    pool.close()
    pool.join()
    print(f"[{datetime.datetime.now()}] parallel(args) complete", flush=True)

def array(args):
    '''
    Run Stanley_FindPlanets sequentially for a single sector.
    '''
    print(f"[{datetime.datetime.now()}] Entering array(args)", flush=True)
    SearchName = args.searchName
    SystemName = args.systemName
    DetrendingName = args.detrendingName
    totalSectors = args.totalSectors
    onCluster = bool(args.onCluster)
    currentSector = args.currentSector
    interpValue = args.interpolationValue
    boundsType = args.boundsType if hasattr(args, 'boundsType') else 'stability limit ratio to stability limit ratio'
    MinValue = args.minValue if hasattr(args, 'minValue') else 2.2
    MaxValue = args.maxValue if hasattr(args, 'maxValue') else 4.1
    e_max_planet = args.e_max_planet if hasattr(args, 'e_max_planet') else 0.2
    print(f"[{datetime.datetime.now()}] Calling Stanley_FindPlanets for sector={currentSector}", flush=True)
    Stanley_FindPlanets(SearchName, SystemName, DetrendingName, totalSectors, onCluster, currentSector, N_interp=interpValue, BoundsType=boundsType, MinValue=MinValue, MaxValue=MaxValue, e_max_planet=e_max_planet)
    print(f"[{datetime.datetime.now()}] array(args) complete", flush=True)

# CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--searchName", type=str, help="A unique identifier for the simulation", default='DefaultSearch')
    parser.add_argument("--systemName", type=str, help="Name of the system (e.g. Kepler 16)", default='Kepler 64')
    parser.add_argument("--detrendingName", type=str, help="Name of the detrending label", default='BLAH')
    parser.add_argument("--totalSectors", type=int, help="Number of sectors over which the search is split", default=1)
    parser.add_argument("--currentSector", type=int, help="Current sector (1-indexed)", default=1)
    parser.add_argument("--onCluster", type=int, help="Are we on a cluster? (0/1)", default=0)
    parser.add_argument("--parallel", type=int, help="Run all sectors in parallel? (0/1)", default=0)
    parser.add_argument("--interpolationValue", type=int, help="Skip N thetas and interpolate", default=1)
    parser.add_argument("--boundsType", type=str, help="Type of bounds for period grid", default=None)
    parser.add_argument("--minValue", type=float, help="Minimum value for period grid", default=None)
    parser.add_argument("--maxValue", type=float, help="Maximum value for period grid", default=None)
    parser.add_argument("--e_max_planet", type=float, help="Maximum planetary eccentricity to sample", default=0.2)
    args = parser.parse_args()

    print(f"[{datetime.datetime.now()}] BASE resolved to: {BASE}", flush=True)
    print(f"[{datetime.datetime.now()}] Script start with args: {args}", flush=True)
    if (args.parallel == 0):
        array(args)
    else:
        parallel(args)
    print(f"[{datetime.datetime.now()}] Script end.", flush=True)
