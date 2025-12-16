# -*- coding: utf-8 -*-

"""
Functionality:
    Aggregates Stanley circumbinary search results, constructs a 1D SDE over planet period
    (marginalized over e, ω, and θ_p), selects the best-fit model, reconstructs transit times
    and durations, makes TTV/TDV plots, and writes a concise summary plus helper files.

Command-line Arguments:
    --searchName (str): Identifier for this run (folder name in PlanetSearchOutput).
    --systemName (str): Target identifier (e.g., 'Kepler 16' or a resolvable name).
    --totalSectors (int): Total θ_p sectors used in the search split.
    --currentSector (int): Current sector index (not needed for aggregation).
    --onCluster (bool): Flag for cluster context.

Inputs (From saved pipeline artifacts):
    PlanetSearchOutput/<searchName>/<MISSION>_<ID>_simInfo.npy
    PlanetSearchOutput/<searchName>/<MISSION>_<ID>_searchParameters_array
    PlanetSearchOutput/<searchName>/<MISSION>_<ID>_searchResults_array_<total>_<sector>.npy
    LightCurves/Processed/<DetrendingName>/<MISSION>_<ID>_<DetrendingName>_detrended.csv
    LightCurves/Processed/<DetrendingName>/<MISSION>_<ID>_<DetrendingName>_binaryStartingParams.csv

Outputs (Written by this script):
    PlanetSearchOutput/<searchName>/<MISSION>_<ID>_TTVs.png
    PlanetSearchOutput/<searchName>/<MISSION>_<ID>_TDVs.png
    PlanetSearchOutput/<searchName>/<MISSION>_<ID>_SearchResults.txt
    PlanetSearchOutput/<searchName>/<MISSION>_<ID>_planetTransitCuts.npy
    PlanetSearchOutput/<searchName>/<MISSION>_<ID>_discoveredTransitList.txt

Notes:
    Times are handled in SI seconds internally; human-readable outputs convert to days/hours.
    The (e, ω) grid is circular in e–ω space and is not collapsed.
"""

import os, sys, io, time, importlib, rebound, math, timeit, datetime, matplotlib
import numpy as np
matplotlib.use('Agg')  # Use non-interactive backend for batch/CI
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection
from collections import OrderedDict
from mpl_toolkits.mplot3d import Axes3D
from scipy import optimize
import time, pylab, argparse, warnings
from pathlib import Path
warnings.filterwarnings("ignore")  # Suppress expected numerical warnings

# Package-relative import fallback
try:
    # When installed as a package
    from . import Stanley_Functions as AC 
    from . import Stanley_TransitTiming as SSTT
    from .Stanley_Constants import *
except Exception:
    # Original local imports (cluster/local repo)
    import Stanley_Functions as AC
    import Stanley_TransitTiming as SSTT
    from Stanley_Constants import *

importlib.reload(AC)    # Ensure latest project helpers during iterative runs
importlib.reload(SSTT)

plt.close("all")
plt.ion
pylab.ion

# Use AC base + path helpers
BASE = AC.base_dir()
_p_outputs     = AC.p_outputs
_p_lightcurves = AC.p_lightcurves
_p_processed   = AC.p_processed

# Public programmatic entry point
def runAnalysisModule(
    searchName: str,
    systemName: str,
    totalSectors: int = 1,
    currentSector: int = 1,
    onCluster: bool = False
):
    """
    Functionality:
        Aggregates Stanley circumbinary search results, constructs a 1D SDE over planet period
        (marginalized over e, ω, and θ_p), selects the best-fit model, reconstructs transit times
        and durations, makes TTV/TDV plots, and writes a concise summary plus helper files.

    Arguments:
        searchName (str): Folder name under PlanetSearchOutput containing this run's artifacts.
        systemName (str): Target identifier (e.g., 'Kepler 16' or 'TIC 123456789').
        totalSectors (int): Total number of θ_p sector splits used by the search.
        currentSector (int): Unused by aggregation (kept for interface parity).
        onCluster (bool): If True, assume non-interactive plotting/logging context.

    Returns:
        dict with key results/paths for downstream use (also writes files to disk).
    """
    # Thresholds (for parity; used by upstream too)
    consistencyThreshold = 3
    consistencySigmaFactor = 0.45
    fractionDataPointsHitThreshold = 0.45
    individualDataPointSigmaCutThreshold = 3

    # Step 1: Load detrended light curve and run context
    ID, mission = AC.GetID(systemName)  # Resolve target to TIC/KIC and numeric ID
    if (mission != "TIC") and (mission != "KIC"):
        raise Exception("Mission should be TIC or KIC not:", mission)

    # Load simInfo produced by PlanetSearch sector 1
    input_folder   = _p_outputs(searchName)
    input_filename = input_folder / f"{mission}_{ID}_simInfo.npy"
    print(f"[{datetime.datetime.now()}] Analysis expecting simInfo at: {input_filename}", flush=True)

    # 3B: Guard if PlanetSearch did not finish sector 1
    if not input_filename.exists():
        raise FileNotFoundError(
            "simInfo.npy not found.\n"
            f"Expected: {input_filename}\n\n"
            "This usually means PlanetSearch did not complete sector 1, or wrote to a different base.\n"
            "Make sure Stanley_PlanetSearch_InterpN_DebugPadding.py ran successfully with the SAME searchName "
            "and that it used AC path helpers (p_outputs, etc.)."
        )

    simInfo = np.load(str(input_filename))  # [SearchName, SystemName, DetrendingName, totalSectors, mission, ID]
    DetrendingName = simInfo[2]
    totalSectors   = int(simInfo[3])

    # Detrended LC (file stores days; convert to seconds)
    detrended_csv = _p_lightcurves("Processed", DetrendingName, f"{mission}_{ID}_{DetrendingName}_detrended.csv")
    detrendedData = np.transpose(np.genfromtxt(str(detrended_csv)))
    timeArray = detrendedData[0] * days2sec
    fluxArray = detrendedData[1]

    # Stellar radii for transit chord modeling
    binary_params_csv = _p_lightcurves("Processed", DetrendingName, f"{mission}_{ID}_{DetrendingName}_binaryStartingParams.csv")
    binaryParamsFile = np.genfromtxt(str(binary_params_csv), delimiter=',')
    RA_set = binaryParamsFile[2][1] * rSun_m
    RB_set = binaryParamsFile[3][1] * rSun_m

    # Basic LC statistics for normalization and guards
    meanTotalLightcurve = np.mean(fluxArray)
    maxTotalLightcurve  = np.max(fluxArray)

    # Step 2: Load hyperparameter grids and sector outputs
    params_txt = input_folder / f"{mission}_{ID}_searchParameters_array"
    with open(params_txt, "r") as infile:
        z = eval(infile.read())  # Trusted internal artifact (kept as-is for identical behavior)

    mA_search             = z[0]
    mB_search             = z[1]
    Pbin_search           = z[2]
    ebin_search           = z[3]
    omegabin_search       = z[4]
    thetabin_search       = z[5]
    periodANDtheta_search = z[6]
    eccANDomega_search    = z[7]
    Pp_search = np.array([pt[0] for pt in periodANDtheta_search])  # Periods in seconds

    # Derive parameter count for reporting
    numParams = 1
    for ii in range(0, 6):
        numParams *= len(z[ii])

    numThetaValues = sum(len(pt[1]) for pt in periodANDtheta_search)  # θ_p samples
    numParams *= numThetaValues

    numOmegaValues = sum(len(eo[1]) for eo in eccANDomega_search)     # ω samples across e levels
    numParams *= numOmegaValues

    print('Loading results for searchName = ' + searchName + ', systemName = ' + systemName + ', detrendingName = ' + DetrendingName)

    searchResults = []
    numSectorsComplete = 0
    allSectorsComplete = True

    # Concatenate sector tensors along θ_p axis (axis=6)
    for ii in range(1, totalSectors + 1):
        sector_npy = input_folder / f"{mission}_{ID}_searchResults_array_{totalSectors}_{ii}.npy"
        if not sector_npy.exists():
            print('Sector ' + str(ii) + "/" + str(totalSectors) + ' not finished')
            allSectorsComplete = False
        else:
            numSectorsComplete += 1
            temp = np.load(str(sector_npy))
            if (len(searchResults) == 0):
                searchResults = temp
            else:
                searchResults = np.concatenate((searchResults, temp), axis=6)

    if (allSectorsComplete == False):
        msg = f'Only {numSectorsComplete}/{totalSectors} sector(s) completed. Cannot get results yet'
        print(msg)
        return {
            "status": "incomplete",
            "message": msg,
            "sectors_done": numSectorsComplete,
            "sectors_total": totalSectors
        }

    print(str(totalSectors) + ' sector(s) loaded')

    # Rebuild θ_p sampling over 0–360° for plotting/indices
    thetap_search = np.linspace(np.radians(0), np.radians(360), np.shape(searchResults)[9])

    # Sigma field view; last axis packs multiple outputs, index 0 is sigma
    sigmaResults = searchResults[:, :, :, :, :, :, :, :, :, :, 0]

    # Collapse to 1D series over P_p with instability guard
    sigmaResults_1d = np.zeros(len(periodANDtheta_search))
    unstableFraction = []
    unstableFractionThreshold = 1  # Mark fully unstable wedges

    for ii in range(0, len(Pp_search)):
        dataSlice = sigmaResults[:, :, :, :, :, :, ii, :, :, :]  # Fix Period index, scan over e/ω/θ
        if (len(dataSlice[dataSlice >= -27]) == 0):
            unstableFraction.append(1)
        else:
            unstableFraction.append(len(dataSlice[dataSlice == -27]) / len(dataSlice[dataSlice >= -27]))
        if (unstableFraction[ii] < unstableFractionThreshold):
            sigmaResults_1d[ii] = np.max(dataSlice)
        else:
            sigmaResults_1d[ii] = -27

    # Compute 1D SDE and locate max-significance period
    print('Create 1D SDE')
    SDE_1d_max, period_sdeMax = AC.Search_Create1dSDE(sigmaResults_1d, Pp_search, searchName, mission, ID)
    print('1D SDE created')

    # Identify best-fit hypercube indices at period_sdeMax
    shape = [
        sigmaResults.shape[0], sigmaResults.shape[1], sigmaResults.shape[2],
        sigmaResults.shape[3], sigmaResults.shape[4], sigmaResults.shape[5],
        sigmaResults.shape[7], sigmaResults.shape[8], sigmaResults.shape[9]
    ]
    bestPeriodIndex = np.argmin(np.abs(Pp_search - period_sdeMax))
    temp_idx = sigmaResults[:, :, :, :, :, :, bestPeriodIndex, :, :, :].argmax()
    temp = np.unravel_index(temp_idx, tuple(shape))

    # Extract best-fit parameters
    mA_bestFit       = mA_search[temp[0]]
    mB_bestFit       = mB_search[temp[1]]
    Pbin_bestFit     = Pbin_search[temp[2]]
    ebin_bestFit     = ebin_search[temp[3]]
    omegabin_bestFit = omegabin_search[temp[4]]
    thetabin_bestFit = thetabin_search[temp[5]]
    Pp_bestFit       = periodANDtheta_search[bestPeriodIndex][0]
    ep_bestFit       = eccANDomega_search[temp[6]][0]
    omegap_bestFit   = eccANDomega_search[temp[6]][1][temp[7]]
    thetap_bestFit   = periodANDtheta_search[bestPeriodIndex][1][temp[8]]

    # Reconstruct transit times/durations for the winning model
    print('Getting best fitting transit times')
    zbest = (mA_bestFit, mB_bestFit, Pbin_bestFit, ebin_bestFit, omegabin_bestFit, thetabin_bestFit, Pp_bestFit, ep_bestFit, omegap_bestFit, thetap_bestFit)
    TT_bestFit, TD_bestFit, sigma_solutionOld, meanFlux_solution, stdOutOfTransit = AC.Search_CreateTransitMask(
        zbest, RA_set, RB_set, timeArray, fluxArray, returnTransitTimes=True,
        meanTotalLightcurve=meanTotalLightcurve, plotting=True, SearchName=searchName, mission=mission, ID=ID
    )

    print('sigma_solutionOld = ' + str(sigma_solutionOld))
    print('meanFlux_solution = ' + str(meanFlux_solution))

    # Optional comparison against known/injected transits (Kepler only)
    fractionRealTransitsFound = -27
    numRealTransits = -27
    numFoundRealTransits = -27

    if mission == "KIC":
        KIC = ID
        injectedTransits = ('Inject' in searchName)
        if injectedTransits:
            knownTransitsFilename = BASE / 'LightCurves' / 'Injections' / searchName / (KIC + '1026032_injectedTransitList.txt')
        else:
            knownTransitsFilename = BASE / 'LightCurves' / 'KnownTransits' / (KIC + '_knownPrimaryTransits.txt')

        if os.path.exists(knownTransitsFilename):
            print('Known transits exist, checking for a match')
            realPlanetData = np.genfromtxt(knownTransitsFilename)
            realPlanetData = np.array(realPlanetData)
            if injectedTransits:
                realTransitStartTime = (realPlanetData[:, 0] + 55000 - realPlanetData[:, 1] / 2 / 24) * days2sec
                realTransitEndTime   = (realPlanetData[:, 0] + 55000 + realPlanetData[:, 1] / 2 / 24) * days2sec
            else:
                realTransitStartTime = (realPlanetData[:, 0] + 55000) * days2sec
                realTransitEndTime   = (realPlanetData[:, 1] + 55000) * days2sec

            realTransit_duration = realTransitEndTime - realTransitStartTime
            realTransit_time = 0.5 * (realTransitEndTime + realTransitStartTime)

            print("Checking for transit match")
            numRealTransits = len(realTransit_time)
            numFoundRealTransits = 0

            for jj in range(0, len(realTransit_time)):
                if (realTransit_duration[jj] > 0):
                    has_data = timeArray[(timeArray > realTransit_time[jj] - realTransit_duration[jj] / 2) &
                                         (timeArray < realTransit_time[jj] + realTransit_duration[jj] / 2)]
                    if len(has_data) > 0:
                        for kk in range(0, len(TT_bestFit)):
                            if (np.abs(TT_bestFit[kk] - realTransit_time[jj]) < realTransit_duration[jj] / 2):
                                inTransitTimes = timeArray[(timeArray > realTransit_time[jj] - realTransit_duration[jj] / 2) &
                                                           (timeArray < realTransit_time[jj] + realTransit_duration[jj] / 2)]
                                if len(inTransitTimes) > 0:
                                    numFoundRealTransits += 1
            fractionRealTransitsFound = (numFoundRealTransits / numRealTransits) if (numRealTransits > 0) else -27
        else:
            print('No known transits file found')

    os.makedirs(_p_outputs(searchName), exist_ok=True)  # Ensure output folder exists

    # TTVs: Robustly handle too-few finite TTs
    TT_bestFit = np.asarray(TT_bestFit, float)
    if np.sum(np.isfinite(TT_bestFit)) < 2:
        print("[TTV] Fewer than 2 finite transit times; skipping fit")
        TTV_search_bestFit, m, c = np.array([]), np.nan, np.nan
    else:
        TTV_search_bestFit, m, c = SSTT.TT_to_TTV(TT_bestFit[np.isfinite(TT_bestFit)])

    transitIndex = np.linspace(1, len(TTV_search_bestFit), len(TTV_search_bestFit))

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    ax.scatter(transitIndex, TTV_search_bestFit / days2sec, s=150, edgecolor='r', facecolor=np.array([255, 153, 145]) / 255)
    ax.set_ylabel('Transit Timing Variation (days)', fontsize=22)
    ax.set_xlabel('Transit Number', fontsize=22)
    plt.xticks(fontsize=18); plt.yticks(fontsize=18)
    fig.savefig(str(_p_outputs(searchName) / f"{mission}_{ID}_TTVs.png"), bbox_inches='tight')

    # TDVs
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    ax.scatter(transitIndex, TD_bestFit / hours2sec, s=150, edgecolor='b', facecolor=np.array([166, 233, 255]) / 255)
    ax.set_ylabel('Transit Duration (hours)', fontsize=22)
    ax.set_xlabel('Transit Number', fontsize=22)
    plt.xticks(fontsize=18); plt.yticks(fontsize=18)
    fig.savefig(str(_p_outputs(searchName) / f"{mission}_{ID}_TDVs.png"), bbox_inches='tight')

    # Human-readable summary
    output_txt_path = _p_outputs(searchName) / f"{mission}_{ID}_SearchResults.txt"
    outputFile = open(output_txt_path, 'w')
    outputFile.write('System name = ' + systemName + "\n")
    outputFile.write('mission + ID = ' + mission + "_" + ID + "\n")
    outputFile.write('Search name = ' + searchName + "\n")
    outputFile.write('Detrending name = ' + DetrendingName + "\n")
    outputFile.write('Total sectors = ' + str(totalSectors) + "\n")
    outputFile.write('Num Theta_p steps = ' + str(len(thetap_search)) + "\n")
    outputFile.write('Search parameter count = ' + str(numParams) + "\n")
    outputFile.write('SDE_1d (max value) = ' + str(SDE_1d_max) + "\n")
    outputFile.write('SDE_1d (period) = ' + str(period_sdeMax / days2sec) + "\n")
    outputFile.write('meanFlux_solution = ' + str(meanFlux_solution) + "\n")
    outputFile.write('stdOutOfTransit = ' + str(stdOutOfTransit) + "\n")
    outputFile.write('mA (Msun) = ' + str(round(mA_bestFit / mSun_kg, 4)) + ' Msun' + "\n")
    outputFile.write('mB (Msun) = ' + str(round(mB_bestFit / mSun_kg, 4)) + ' Msun' + "\n")
    outputFile.write('Pbin (days) = ' + str(round(Pbin_bestFit / days2sec, 4)) + ' days' + "\n")
    outputFile.write('ebin = ' + str(round(ebin_bestFit, 4)) + "\n")
    outputFile.write('omegabin (deg) = ' + str(round(omegabin_bestFit * 180. / np.pi, 4)) + ' deg' + "\n")
    outputFile.write('thetabin (deg) = ' + str(round(thetabin_bestFit * 180. / np.pi, 4)) + ' deg' + "\n")
    outputFile.write('Pp (days) = ' + str(round(Pp_bestFit / days2sec, 4)) + ' days' + "\n")
    outputFile.write('ep = ' + str(round(ep_bestFit, 4)) + "\n")
    outputFile.write('omegap (deg) = ' + str(round(omegap_bestFit * 180. / np.pi, 4)) + ' deg' + "\n")
    outputFile.write('thetap (deg) = ' + str(round(thetap_bestFit * 180. / np.pi, 4)) + ' deg' + "\n")

    # Transit mid-time list (days, BJD-2,450,000 convention)
    finite_TT = TT_bestFit[np.isfinite(TT_bestFit)]
    if finite_TT.size > 0:
        transit_times_days = finite_TT / days2sec - 55000
        transitTimingString_bestFit = ", ".join(str(round(x, 3)) for x in transit_times_days)
    else:
        transitTimingString_bestFit = "None"
    outputFile.write('Transit timing (best fit) = ' + transitTimingString_bestFit + "\n")

    outputFile.write('Real planet transits discovered fraction = ' + str(fractionRealTransitsFound) + "\n")
    outputFile.write('Number real transits = ' + str(numRealTransits) + "\n")
    outputFile.write('Number real transits found = ' + str(numFoundRealTransits) + "\n")
    outputFile.close()

    # Transit-window cuts for optional re-detrending masks
    cutRecord = np.array([
        (TT_bestFit - 0.55 * TD_bestFit) / days2sec - 55000,
        (TT_bestFit + 0.55 * TD_bestFit) / days2sec - 55000
    ])
    np.save(str(_p_outputs(searchName) / f"{mission}_{ID}_planetTransitCuts.npy"), cutRecord)

    # Mid-times (days) and durations (hours) for downstream vetting
    disc_list_path = _p_outputs(searchName) / f"{mission}_{ID}_discoveredTransitList.txt"
    np.savetxt(
        str(disc_list_path),
        np.transpose([TT_bestFit / days2sec - 55000, TD_bestFit / hours2sec])
    )
    
    # Return a compact summary for programmatic use
    return {
        "status": "ok",
        "mission": mission,
        "ID": ID,
        "DetrendingName": DetrendingName,
        "SDE_1d_max": float(SDE_1d_max),
        "period_sdeMax_days": float(period_sdeMax / days2sec),
        "TTV_png": str(_p_outputs(searchName) / f"{mission}_{ID}_TTVs.png"),
        "TDV_png": str(_p_outputs(searchName) / f"{mission}_{ID}_TDVs.png"),
        "summary_txt": str(output_txt_path),
        "discovered_list_txt": str(disc_list_path)
    }


# CLI entry point (cluster usage)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run STANLEY analysis module on completed search output."
    )
    parser.add_argument(
        "--searchName",
        type=str,
        help="Unique identifier for the simulation / search run.",
        default="Needs a name",
    )
    parser.add_argument(
        "--systemName",
        type=str,
        help="Name of the system (e.g. Kepler-16, TIC123...).",
        default="Kepler 16",
    )
    parser.add_argument(
        "--totalSectors",
        type=int,
        help="Total sectors used to split the search.",
        default=1,
    )
    parser.add_argument(
        "--currentSector",
        type=int,
        help="Current search sector (if relevant to your analysis; otherwise ignored).",
        default=1,
    )
    parser.add_argument(
        "--onCluster",
        type=int,
        choices=[0, 1],
        help="Are we on a cluster? (0/1)",
        default=0,
    )

    args = parser.parse_args()

    print(f"[{datetime.datetime.now()}] Analysis start with args: {args}", flush=True)

    out = runAnalysisModule(
        searchName=args.searchName,
        systemName=args.systemName,
        totalSectors=args.totalSectors,
        currentSector=args.currentSector,
        onCluster=bool(args.onCluster),
    )

    print(
        f"[{datetime.datetime.now()}] Analysis end. Result: {out.get('status', 'unknown')}",
        flush=True,
    )
