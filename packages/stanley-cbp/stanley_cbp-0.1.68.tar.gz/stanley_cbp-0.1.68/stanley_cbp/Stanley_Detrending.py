# -*- coding: utf-8 -*-

################################################################################################################
#########
#########
#########                    STANLEY DETRENDING CODE (CLUSTER VERSION)
#########
#########                    This is the first part of the Stanley automated circumbinary search code.
#########                    You feed the code a KIC/TIC and it will download the data, get the relevant
#########                    parameters from Villanova/Windemuth catalogs, remove eclipses and detrend
#########                    the data. The detrending is designed to remove eclipsing-binary variability
#########                    whilst preserving circumbinary transits of variable duration.
#########                    This file orchestrates steps; core math/modeling lives in Stanley_Functions.py.
#########
#########
################################################################################################################

"""
Functionality:
    Over-arching detrending pipeline for eclipsing-binary light curves used by the Stanley
    circumbinary planet search. Given a target identifier (KIC or TIC) and a run label,
    it loads or downloads photometry, removes eclipses, applies several detrending stages
    (iterative cosine, optional gap plug/remove, variable-duration biweight, kink removal,
    optional ellipsoidal/reflection trends), diagnoses quality, and saves figures and the
    final processed light curve.

Command-line Arguments:
    --systemName (str): Target identifier (KIC/TIC). Default: '6762829'
    --detrendingName (str): Label for outputs (figures, processed files). Default: 'BLAH'
    --useSavedData (int): 1 to use cached downloads/processed intermediates; 0 for fresh. Default: 0
    --injectTransits (int): 1 enables transit injections for diagnostics/completeness; 0 disables. Default: 0
    --injectionParamFile (str): CSV of injection parameters (ONLY used if --injectTransits=1).
                                If omitted/empty while injections are on, a mission-specific default is used.

Inputs/Dependencies:
    - Stanley_Functions.py (as AC) for IO and all detrending utilities
    - Stanley_Constants.py for units/constants
    - lightkurve for data access (when not using saved data)

Key Outputs (relative to data root):
    - LightCurves/Processed/<DetrendingName>/<MISSION>_<ID>_<DetrendingName>_detrended.csv
    - LightCurves/Figures/<DetrendingName>/* (periodograms, trend visuals, stage overview)
    - LightCurves/DetrendingStats/<DetrendingName>/detrending_summary.csv (appended/updated)

Notes:
    - Time is kept in seconds internally for processing; CSV export converts back to days.
    - This file orchestrates steps; core math/modeling lives in AC (Stanley_Functions.py).
"""

from IPython import get_ipython  # optional in cluster; kept for parity
# get_ipython().magic('reset -sf')

# --- Imports ---
import os, sys, io, time, importlib, math, timeit, datetime, pylab, argparse, gc, warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')  # non-interactive backend for batch/CI/cluster
import matplotlib.pyplot as plt
import lightkurve as lk
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from collections import OrderedDict
from mpl_toolkits.mplot3d import Axes3D
from scipy import optimize
from pathlib import Path
from typing import Optional

# Package-relative import fallback
try:
    # package mode (when run via: python -m Code.Stanley_Detrending)
    from . import Stanley_Functions as AC
    from . import Stanley_TransitTiming as SSTT
    from .Stanley_Constants import *
except Exception:
    # repo/flat mode (when run as: python Code/Stanley_Detrending.py)
    import Stanley_Functions as AC
    import Stanley_TransitTiming as SSTT
    from Stanley_Constants import *

# Paths: delegate to AC
BASE = AC.base_dir()  # pathlib.Path

def _p_lc(*parts) -> Path:
    return AC.p_lightcurves(*parts)

def _p_processed(det_name: str) -> Path:
    return AC.p_processed(det_name)

def _p_figs(det_name: str) -> Path:
    return AC.p_lightcurves("Figures", det_name)

def _p_stats(det_name: str) -> Path:
    return AC.p_lightcurves("DetrendingStats", det_name)

def _p_injections(det_name: str) -> Path:
    return AC.p_lightcurves("Injections", det_name)

# Optional warning filter (disabled by default)
# warnings.filterwarnings('ignore')

plt.close("all")  # Close any prior figures to avoid clutter in iterative runs


def runDetrendingModule(
    SystemName: str = '6762829',
    DetrendingName: str = 'BLAH',
    UseSavedData: int = 0,

    # Feature switches
    detrending_quadratic: bool = True,
    detrending_iterativeCosine: bool = True,
    detrending_plugHoles: bool = False,
    detrending_variableDuration: bool = False,
    detrending_removeKinks: bool = True,
    detrending_removeCommonFalsePositives: bool = True,
    detrending_findPotentialLedges: bool = True,
    detrending_findDeepestPoints: bool = True,
    detrending_plotSpecificTimes: bool = False,
    detrending_saveProcessedLightCurve: bool = True,
    detrending_variableDurationXiTest: bool = False,
    detrending_testCosine: bool = False,
    detrending_injectTransits: bool = False,
    injection_param_file: Optional[str] = None,  # ONLY used if detrending_injectTransits=True

    # Binary-physics trend removal (paper options)
    detrending_ellipsoidal: bool = False,
    detrending_reflection: bool  = False,

    # Plot behavior
    _plot_trends: bool = True,
    _show_plots: bool  = True,

    # Binning defaults
    bin_width: int = 5*120,          # 10 minutes
    min_points_per_bin: int = 3,
    gap_threshold: int = 5*120
):
    """
    Run the Stanley detrending pipeline end-to-end for a single target.
    """

    # Ensure LightCurves/ exists
    other_folder_name = _p_lc()
    if not other_folder_name.exists():
        other_folder_name.mkdir(parents=True, exist_ok=True)

    # Always reflect latest AC edits during iterative development
    importlib.reload(AC)
    plt.close("all")

    print('----- RUNNING DETRENDING CODE -----')

    # Create figure output directory for this run
    figs_dir = _p_figs(DetrendingName)
    figs_dir.mkdir(parents=True, exist_ok=True)

    # Resolve ID/mission and set EB-type specifics
    ID, mission = AC.GetID(SystemName)

    # Quadratic detrending only for TESS by default (unchanged)
    detrending_quadratic = mission == 'TIC' and detrending_quadratic

    print('System Name = ' + SystemName)
    print(f'{mission} = ' + ID)
    print('Detrending Name = ' + DetrendingName)
    print('----- DETRENDING SETTINGS -----')
    print('Quadratic = ' + str(detrending_quadratic))
    print('Iterative Cosine = ' + str(detrending_iterativeCosine))
    print('Variable Biweight = ' + str(detrending_variableDuration))
    print('Plug Holes = ' + str(detrending_plugHoles))
    print('Remove Common False Positives = ' + str(detrending_removeCommonFalsePositives))
    print('Remove Kinks = ' + str(detrending_removeKinks))
    print('Remove Common False Positives = ' + str(detrending_removeCommonFalsePositives))
    print('Find Potential Ledges = ' + str(detrending_findPotentialLedges))
    print('Find Deepest Points = ' + str(detrending_findDeepestPoints))
    print('Plot Specific Times = ' + str(detrending_plotSpecificTimes))
    print('Save Processed Light Curve = ' + str(detrending_saveProcessedLightCurve))
    print('Variable Duration Xi Test = ' + str(detrending_variableDurationXiTest))
    print('Test Cosine = ' + str(detrending_testCosine))
    print('Inject Transits = ' + str(detrending_injectTransits))
    print('Ellipsoidal Detrending = ' + str(detrending_ellipsoidal))
    print('Reflection Detrending = ' + str(detrending_reflection))
    print('----- LOADING SYSTEM -----')

    # Load, cut eclipses, and (optionally) reuse cached data
    reboundSim, timeOrig, fluxOrig, timeCutNotBinned, fluxCutNotBinned, orbit_params, stellar_params, sector_times = AC.LoadData(
        mission, ID, DetrendingName, remove_eclipses=True, use_saved_data=UseSavedData
    )

    # Bin to target cadence
    if mission == 'TIC':
        timeCut, fluxCut = AC.binDataRealTime(timeCutNotBinned, fluxCutNotBinned, bin_width=bin_width, min_points_per_bin=min_points_per_bin, gap_threshold=gap_threshold)
    else:
        timeCut, fluxCut = timeCutNotBinned, fluxCutNotBinned

    print('Check time units after Kepler binning: ' + str(timeCut[0]))
    print("Pbin: " + str(orbit_params.get('Pbin')) + "\nbjd0: " + str(orbit_params.get('bjd0')) + "\nprim_pos: " + str(orbit_params.get('prim_pos')) + "\npwidth: " + str(orbit_params.get('pwidth')) + "\npdepth: " + str(orbit_params.get('pdepth')) + "\nsec_pos: " + str(orbit_params.get('sec_pos')) + "\nswidth: " + str(orbit_params.get('swidth')) + "\nsdepth: " + str(orbit_params.get('sdepth')) + "\nsep: " + str(orbit_params.get('sep')) + "\ne: " + str(orbit_params.get('e')) + "\nomega: " + str(orbit_params.get('omega')) + "\nDays of data: " + str((len(timeOrig)) * 2 / 60 / 24))

    # Rebound API update: use .orbits() in newer versions
    orbits = reboundSim.orbits()

    print('----- SYSTEM LOADED SUCCESSFULLY -----')
    print("mA (mSun) = " + str(stellar_params['mA']/mSun_kg))
    print("mB (mSun) = " + str(stellar_params['mB']/mSun_kg))
    print("rA (rSun) = " + str(stellar_params['rA']/rSun_m))
    print("rB (rSun) = " + str(stellar_params['rB']/rSun_m))
    print("Pbin (days) = " + str(orbit_params['Pbin']/days2sec))
    print("bjd0 (days) = " + str(orbit_params['bjd0']/days2sec))
    print("e = " + str(orbit_params['e']))
    print("omega = " + str(orbit_params['omega']))

    # Working copies of the detrended light curve (seconds)
    timeFinal = np.copy(timeCut)
    fluxFinal = np.copy(fluxCut)

    # Remove catalogued common FPs for Kepler EB sample
    if (mission == "KIC"):
        if (detrending_removeCommonFalsePositives == True):
            print('----- REMOVING COMMON FALSE POSITIVES -----')
            timeFinal, fluxFinal = AC.Detrending_RemoveCommonFalsePositives(timeFinal, fluxFinal, mission, ID)
            print('----- COMMON FALSE POSITIVES REMOVED SUCCESSFULLY -----')
        timeCommonFalsePositivesRemoved = np.copy(timeFinal)
        fluxCommonFalsePositivesRemoved = np.copy(fluxFinal)
    else:
        timeCommonFalsePositivesRemoved = np.copy(timeFinal)
        fluxCommonFalsePositivesRemoved = np.copy(fluxFinal)

    # Compute expected transit duration vs time for variable-window filters
    print('----- CALCULATING TRANSIT DURATION ACROSS LIGHT CURVE -----')
    durationArray, durationArrayTime = AC.CalculateTransitDuration(reboundSim, timeFinal)
    print('----- TRANSIT DURATION CALCULATED SUCCESSFULLY -----')

    # Optional injections for diagnostics / completeness studies
    if detrending_injectTransits:
        #if detrending_injectTransits == True make sure Injections Folder exists 
        injections_folder = AC._resolve_base_dir(None) / "LightCurves" / "Injections" / DetrendingName
        if not injections_folder.exists():
            injections_folder.mkdir(parents=True, exist_ok=True)
        
        print('----- INJECTING TRANSITS -----')
        # If no explicit file provided, use mission-specific default
        if injection_param_file is None or str(injection_param_file).strip() == "":
            if mission == 'TIC':
                injection_param_file = "planet_params.csv"
            else:
                injection_param_file = "injection102Pb_10rE.csv"

        print(f"Using injection parameter file: {injection_param_file}")

        if mission == 'TIC':
            TIC_val = ID
            timeFinal, fluxFinal = AC.InjectTransits(
                timeFinal, fluxFinal,
                KIC=TIC_val, DetrendingName=DetrendingName,
                orbit_params=orbit_params, stellar_params=stellar_params,
                injection_type="manual_tess",
                injection_param_file=injection_param_file
            )
        else:
            print('entering manual_wata injection type')
            timeFinal, fluxFinal = AC.InjectTransits(
                timeFinal, fluxFinal,
                KIC=ID, DetrendingName=DetrendingName,
                orbit_params=orbit_params, stellar_params=stellar_params,
                injection_type="manual_wata",
                injection_param_file=injection_param_file
            )
            if (detrending_saveProcessedLightCurve == True):
                np.savetxt(injections_folder / (mission + ID + "_injectedRawData.csv"),np.transpose([timeFinal/days2sec,fluxFinal]),fmt='%1.10f')
        print('----- TRANSITS INJECTED SUCCESSFULLY -----')

    timeInjectedTransits = np.copy(timeFinal)
    fluxInjectedTransits = np.copy(fluxFinal)

    # Quadratic trend (TESS default), using days internally in that helper
    if (detrending_quadratic == True):
        print("---- ENTERED QUADRATIC DETRENDING ----")
        timeFinal_days = timeFinal / days2sec
        print("timeFinal in days? : " + str(timeFinal_days))
        timeFinal_days, fluxFinal = AC.Detrending_Quadratic(timeFinal_days, fluxFinal)
        timeFinal = timeFinal_days * days2sec
        print("timeFinal in seconds?: " + str(timeFinal))
        timeQuadraticDetrended = np.copy(timeFinal)
        fluxQuadraticDetrended = np.copy(fluxFinal)
    else:
        timeQuadraticDetrended = np.copy(timeFinal)
        fluxQuadraticDetrended = np.copy(fluxFinal)

    # Optional ellipsoidal (2× orbital frequency) and reflection (1×) detrending
    P_trend_s = orbit_params.get('Pbin')
    bjd0_use = orbit_params.get('bjd0')

    # Ellipsoidal term
    if detrending_ellipsoidal:
        print("---- ENTERED ELLIPSOIDAL DETRENDING ----")
        print("checking P_trend_s units: " + str(P_trend_s))
        if P_trend_s is None or not np.isfinite(P_trend_s) or P_trend_s <= 0:
            print("Ellipsoidal detrending skipped: missing/invalid Pbin_seconds_hint.")
            timeEllipDetrended = np.copy(timeFinal)
            fluxEllipDetrended = np.copy(fluxFinal)
        else:
            try:
                d_flux, trend_e, par_e = AC.detrend_ellipsoidal(
                    time_s=timeFinal, flux=fluxFinal, Pbin_s=P_trend_s, bjd0=bjd0_use,
                    mask_primary=True, primary_k_sigma=2.5, primary_window=0.2,
                    sigma_clip=3.0, max_iter=5, multiplicative=True,
                    bic_delta=0.0, plot=_plot_trends, show=_show_plots,
                    return_model=True, detrending_name=DetrendingName
                )
                fluxFinal = d_flux
                timeEllipDetrended = np.copy(timeFinal)
                fluxEllipDetrended = np.copy(fluxFinal)
                print(f"Ellipsoidal detrending removed={par_e.get('removed', False)}, ΔBIC={par_e.get('delta_bic', np.nan):.2f}")
            except Exception as e:
                print(f"Ellipsoidal detrending failed: {e}")
                timeEllipDetrended = np.copy(timeFinal)
                fluxEllipDetrended = np.copy(fluxFinal)
    else:
        timeEllipDetrended = np.copy(timeFinal)
        fluxEllipDetrended = np.copy(fluxFinal)

    # Reflection term
    if detrending_reflection:
        print("---- ENTERED REFLECTION DETRENDING ----")
        if P_trend_s is None or not np.isfinite(P_trend_s) or P_trend_s <= 0:
            print("Reflection detrending skipped: missing/invalid Pbin_seconds_hint.")
            timeReflectionDetrended = np.copy(timeFinal)
            fluxReflectionDetrended = np.copy(fluxFinal)
        else:
            try:
                d_flux, trend_r, par_r = AC.detrend_reflection(
                    time_s=timeFinal, flux=fluxFinal,
                    Pbin_s=P_trend_s, bjd0=bjd0_use,
                    mask_primary=True, primary_k_sigma=2.5, primary_window=0.2,
                    sigma_clip=3.0, max_iter=5, multiplicative=True,
                    bic_delta=0.0, plot=_plot_trends, show=_show_plots,
                    return_model=True, detrending_name=DetrendingName
                )
                fluxFinal = d_flux
                timeReflectionDetrended = np.copy(timeFinal)
                fluxReflectionDetrended = np.copy(fluxFinal)
                print(f"Reflection detrending removed={par_r.get('removed', False)}, ΔBIC={par_r.get('delta_bic', np.nan):.2f}")
            except Exception as e:
                print(f"Reflection detrending failed: {e}")
                timeReflectionDetrended = np.copy(timeFinal)
                fluxReflectionDetrended = np.copy(fluxFinal)
    else:
        timeReflectionDetrended = np.copy(timeFinal)
        fluxReflectionDetrended = np.copy(fluxFinal)

    # Periodogram before/after stages for diagnostics
    figPeriodograms = plt.figure(figsize=(18, 8))
    figPeriodograms.suptitle(mission + " " + DetrendingName + " Periodograms")
    print("---- LOOKING FOR ZERO-SIZED ARRAY ----")
    print("timeFinal (we want seconds): " + str((timeFinal[0])))
    print("fluxFinal: " + str((fluxFinal[0])))
    print("durationArray: " + str(len(durationArray)))
    fap_1perc, max_power = AC.DoPeriodogram(
        timeFinal, fluxFinal, durationArray, figPeriodograms, False, '', -27, 'initial', SystemName, DetrendingName, mission, ID, 1
    )

    if (detrending_testCosine == True):
        AC.Detrending_IterativeCosine2(timeOrig, fluxOrig, timeCut, fluxCut, timeFinal, fluxFinal, durationArray, SystemName, DetrendingName, mission, ID)
        AC.Detrending_IterativeCosine_Test(timeOrig, fluxOrig, timeCut, fluxCut, timeCommonFalsePositivesRemoved, fluxCommonFalsePositivesRemoved, durationArray, SystemName, DetrendingName, mission, ID)

    # Iterative cosine (cofiam via AC)
    if (detrending_iterativeCosine == True):
        print('----- RUNNING ITERATIVE COSINE DETRENDING -----')
        iterative_cosine_factor_array = np.array([3, 2])
        print('iterative_cosine_factor_array = ' + str(iterative_cosine_factor_array))
        print("THIS IS THE UNITS WE ARE READING INTO ITERATIVE COSINE: " + str(timeFinal))
        timeFinal, fluxFinal, trendCosineDetrended = AC.Detrending_IterativeCosine(
            timeFinal, fluxFinal, durationArray, SystemName, DetrendingName, mission, ID, factor=iterative_cosine_factor_array
        )
        print('----- ITERATIVE COSINE DETRENDING SUCCESSFULLY FINISHED -----')
    else:
        trendCosineDetrended = 0 * timeFinal

    # After-cosine periodogram
    fap_1perc, max_power = AC.DoPeriodogram(
        timeFinal, fluxFinal, durationArray, figPeriodograms, False, '', -27, 'aftercosine', SystemName, DetrendingName, mission, ID, 2
    )

    # Keep intermediate snapshots for multi-panel figures
    timeCosineDetrended = np.copy(timeFinal)
    fluxCosineDetrended = np.copy(fluxFinal)

    # Trend visualization figure (cosine + variable biweight)
    figTrends = plt.figure(figsize=(16, 7))
    ax = figTrends.add_subplot(311)
    ax.scatter(timeInjectedTransits/days2sec, fluxInjectedTransits, color='b', label='Before Iterative Cosine')
    ax.plot(timeCosineDetrended/days2sec, trendCosineDetrended, color='r', label='Iterative Cosine Trend')
    ax.set_xlabel('Time (BJD - 2,500,000)')
    ax.set_ylabel('Flux')
    ax.legend()

    # Optional gap plugging (off by default in paper)
    if (detrending_plugHoles == True):
        print('----- PLUGGING HOLES -----')
        timeFinal, fluxFinal, holeIndex = AC.Detrending_PlugHoles(timeFinal, fluxFinal)
        print('----- HOLES PLUGGED SUCCESSFULLY -----')
    else:
        holeIndex = np.array([])

    timeHolesPlugged = np.copy(timeFinal)
    fluxHolesPlugged = np.copy(fluxFinal)

    # Variable-duration biweight stage
    if (detrending_variableDuration == True):
        print('----- RUNNING VARIABLE BIWEIGHT DETRENDING -----')
        variableDetrending_method = 'biweight'
        variableDetrending_splits = 48
        variableDetrending_xi = 1
        variableDetrending_modifier = 3
        print('Variable detrending method = ' + variableDetrending_method)
        print('Variable detrending number of splits = ' + str(variableDetrending_splits))
        print('Variable detrending xi = ' + str(variableDetrending_xi))
        print('Variable detrending modifier = ' + str(variableDetrending_modifier))
        timeFinal, fluxFinal, windowLengthFinal, trendVariableDetrended = AC.Detrending_VariableDuration(
            timeFinal, fluxFinal, durationArray, durationArrayTime,
            variableDetrending_method, variableDetrending_splits, variableDetrending_modifier, variableDetrending_xi
        )
        print('----- VARIABLE BIWEIGHT DETRENDING SUCCESSFULLY FINISHED -----')
        gc.collect()
    else:
        windowLengthFinal = 0 * timeFinal
        trendVariableDetrended = 0 * timeFinal

    timeVariableDetrended = np.copy(timeFinal)
    fluxVariableDetrended = np.copy(fluxFinal)

    # Plot variable biweight trend
    ax = figTrends.add_subplot(312)
    ax.scatter(timeHolesPlugged/days2sec, fluxHolesPlugged, color='b', label='Before Variable Biweight')
    ax.plot(timeVariableDetrended/days2sec, trendVariableDetrended, color='r', label='Variable Biweight Trend')
    ax.set_xlabel('Time (BJD - 2,500,000)')
    ax.set_ylabel('Flux')
    ax.legend()

    # Plot applied window length
    ax = figTrends.add_subplot(313)
    ax.plot(timeFinal/days2sec, windowLengthFinal, color='b', label='Variable Biweight Windowlength')
    ax.set_xlabel('Time (BJD - 2,500,000)')
    ax.set_ylabel('Variable Biweight Window Length (Days)')
    ax.legend()

    figTrends.savefig(str(figs_dir / f"{mission}_{ID}_{DetrendingName}_trends.png"), bbox_inches='tight')
    plt.show(block=False)

    # Optional removal of filled gaps
    if (detrending_plugHoles == True):
        timeFinal, fluxFinal, windowLengthFinal = AC.Detrending_RemoveHoles(timeFinal, fluxFinal, windowLengthFinal, holeIndex)

    timeHolesRemoved = np.copy(timeFinal)
    fluxHolesRemoved = np.copy(fluxFinal)

    # Kink removal step (jumps, ledges, gaps artifacts)
    if (detrending_removeKinks == True):
        print('----- REMOVING KINKS -----')
        timeFinal, fluxFinal, windowLengthFinal = AC.Detrending_RemoveKinks(timeFinal, fluxFinal, windowLengthFinal, mission, ID, DetrendingName)
        print('----- KINKS REMOVED SUCCESSFULLY -----')

    timeKinksRemoved = np.copy(timeFinal)
    fluxKinksRemoved = np.copy(fluxFinal)

    # Flag possible ledges for human inspection
    if (detrending_findPotentialLedges == True):
        print('----- FINDING POTENTIAL LEDGES -----')
        AC.Detrending_FindPotentialLedges(timeFinal, fluxFinal, SystemName, DetrendingName)
        print('----- POTENTIAL LEDGES FOUND -----')

    # Report deepest individual points (with neighborhood suppression)
    if (detrending_findDeepestPoints == True):
        print('----- FINDING DEEPEST POINTS -----')
        AC.Detrending_FindDeepestPoints(timeFinal, fluxFinal, SystemName, DetrendingName)
        print('----- DEEPEST POINTS FOUND -----')

    print('----- QUANTIFYING LIGHT CURVE QUALITY -----')

    def ecdf(data):
        """
        Compute the empirical cumulative distribution function (ECDF) for a 1D array.
        Returns (x, y) where x are sorted data and y are cumulative probabilities in (0, 1].
        """
        x = np.sort(data)
        n = x.size
        y = np.arange(1, n+1) / n
        return (x, y)

    # Copy for sigma-clipping quality test
    fluxForQualityTesting = np.copy(fluxFinal)
    timeForQualityTesting = np.copy(timeFinal)

    # Iterative outlier removal for quality metrics
    outliers_all_removed = False
    outlier_removal_steps = 0
    sigma_cutoff = 4

    while (outliers_all_removed == False):
        lc_std = np.std(fluxForQualityTesting)
        median_flux_err = stellar_params['median_flux_err']
        diff = np.abs(1 - fluxForQualityTesting) / lc_std

        num_outliers = len(diff[diff > sigma_cutoff])
        print('number of outliers = ' + str(num_outliers))

        outlier_removal_steps += 1

        if (num_outliers > 0):
            fluxForQualityTesting = fluxForQualityTesting[diff < sigma_cutoff]
            timeForQualityTesting = timeForQualityTesting[diff < sigma_cutoff]

        if (num_outliers == 0 or outlier_removal_steps >= 10):
            outliers_all_removed = True

    [ecdf_x, ecdf_y] = ecdf(diff)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(ecdf_x, ecdf_y)
    ax.set_xlabel('|1 - flux| / std')
    ax.set_xlabel('cumulative distribution')
    plt.show(block=False)

    # Final periodogram after all detrending
    print("checking units for timeFinal and fluxFinal, we want seconds NOT days" + str(timeFinal[0]))
    fap_1perc, max_power = AC.DoPeriodogram(
        timeFinal, fluxFinal, durationArray, figPeriodograms, False, -27, '', 'final', SystemName, DetrendingName, mission, ID, 3
    )

    # Save periodogram panel
    figPeriodograms.savefig(str(figs_dir / f"{mission}_{ID}_{DetrendingName}_periodograms.png"))

    # Compute detrending metrics
    periodogram_stat = max_power / fap_1perc
    std_stat = lc_std / median_flux_err

    print('periodogram_stat = ' + str(periodogram_stat))
    print('std_stat = ' + str(std_stat))

    # Persist detrending summary (create file if absent, then update/append row)
    stats_dir = _p_stats(DetrendingName)
    stats_dir.mkdir(parents=True, exist_ok=True)
    file_name = stats_dir / 'detrending_summary.csv'

    if (os.path.exists(file_name) == False):
        detrending_summary = [[998, -27, 0, -27, -27], [999, -27, 0, -27, -27]]
        np.savetxt(str(file_name), detrending_summary, delimiter=',')

    detrending_summary = np.genfromtxt(str(file_name), delimiter=',')
    KIC_in_detrending_summary = False

    for ii in range(0, len(detrending_summary)):
        if (int(detrending_summary[ii][0]) == int(ID)):
            print("Found KIC/TIC in detrending summary at ii = " + str(ii))
            detrending_summary[ii][1] = orbit_params['Pbin']/days2sec
            detrending_summary[ii][2] = 1
            detrending_summary[ii][3] = periodogram_stat
            detrending_summary[ii][4] = std_stat
            KIC_in_detrending_summary = True

    if (KIC_in_detrending_summary == False):
        detrending_summary_target = [[int(ID), orbit_params['Pbin']/days2sec, 1, periodogram_stat, std_stat]]
        detrending_summary = np.append(detrending_summary, detrending_summary_target, axis=0)

    np.savetxt(str(file_name), detrending_summary, delimiter=',')

    print('----- LIGHT CURVE QUALITY ASSESSMENT COMPLETED -----')

    print('----- PLOTTING AND SAVING DATA -----')

    print("ORBITAL PERIOD = " + str(orbit_params['Pbin']))

    # Optional: plot specific times for inspection
    if (detrending_plotSpecificTimes == True):
        AC.Detrending_PlotSpecificTimes(timeFinal, fluxFinal, SystemName, DetrendingName)

    # Persist processed light curve (days on disk)
    print("lets check above the conditional, detrending_saveProceddedLightCurve is currently: " + str(detrending_saveProcessedLightCurve))
    if (detrending_saveProcessedLightCurve == True):
        _root = AC._resolve_base_dir(None)
        proc_dir = _root / "LightCurves" / "Processed" / str(DetrendingName)
        proc_dir.mkdir(parents=True, exist_ok=True)
        np.savetxt(
            str(proc_dir / f"{mission}_{ID}_{DetrendingName}_detrended.csv"),
            np.transpose([timeFinal/days2sec, fluxFinal]),
            fmt='%1.10f'
        )

    print("passed the conditional for saving the detrended lightcurve")

    # Multi-panel figure of stages
    fig = plt.figure(figsize=(16, 9))
    plt.suptitle(mission + "_" + ID + " " + DetrendingName + " Different Detrending Stages")

    ax = fig.add_subplot(231)
    print("injected time length = " + str(len(timeInjectedTransits)))
    print("injected flux length = " + str(len(fluxInjectedTransits)))
    ax.scatter(timeInjectedTransits/days2sec, fluxInjectedTransits, color='r', label='Transits Injected')
    ax.set_xlabel('Time (days - 55000)')
    ax.set_ylabel('Flux')
    ax.legend()

    ax = fig.add_subplot(232)
    print("Quadratic time length = " + str(len(timeQuadraticDetrended)))
    print("Quadratic flux length = " + str(len(fluxQuadraticDetrended)))
    ax.scatter(timeQuadraticDetrended/days2sec, fluxQuadraticDetrended, color='r', label='Eclipses Cut, Quadratic Detrended')
    ax.set_xlabel('Time (days - 55000)')
    ax.set_ylabel('Flux')
    ax.legend()

    ax = fig.add_subplot(233)
    ax.scatter(timeCosineDetrended/days2sec, fluxCosineDetrended, color='r', label='Cosine Detrended')
    ax.plot(timeCosineDetrended/days2sec, trendCosineDetrended, color='g', label='Cosine Detrended (trend)')
    ax.set_xlabel('Time (days - 55000)')
    ax.set_ylabel('Flux')
    ax.legend()

    ax = fig.add_subplot(234)
    ax.scatter(timeHolesPlugged/days2sec, fluxHolesPlugged, color='b', label='Holes Plugged')
    ax.scatter(timeVariableDetrended/days2sec, fluxVariableDetrended, color='r', label='Variable Biweight')
    ax.plot(timeVariableDetrended/days2sec, trendVariableDetrended, color='g', label='Trend')
    ax.set_xlabel('Time (days - 55000)')
    ax.set_ylabel('Flux')
    ax.legend()

    ax = fig.add_subplot(235)
    ax.scatter(timeVariableDetrended/days2sec, fluxVariableDetrended, color='b', label='Variable Biweight')
    ax.scatter(timeHolesRemoved/days2sec, fluxHolesRemoved, color='r', label='Holes Removed')
    ax.set_xlabel('Time (days - 55000)')
    ax.set_ylabel('Flux')
    ax.legend()

    ax = fig.add_subplot(236)
    ax.scatter(timeHolesRemoved/days2sec, fluxHolesRemoved, color='b', label='Holes Removed')
    ax.scatter(timeKinksRemoved/days2sec, fluxKinksRemoved, color='r', label='Kinks Removed')
    ax.set_xlabel('Time (days - 55000)')
    ax.set_ylabel('Flux')
    ax.legend()

    fig.savefig(str(figs_dir / f"{mission}_{ID}_{DetrendingName}_detrendingStages.png"), bbox_inches='tight')

    # Final LC snapshot
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    ax.scatter(timeFinal/days2sec - 55000, fluxFinal)
    ax.scatter(timeForQualityTesting/days2sec - 55000, fluxForQualityTesting)
    ax.set_xlabel('Time (days - 55000)')
    ax.set_ylabel('Flux')
    plt.show(block=False)

    # Return diagnostic report of detrending
    if mission == 'KIC':
        KICorTIC = True
    else:
        KICorTIC = False
        
    # Return a compact dict useful in logs or downstream batch scripts
    return {
        "mission": mission, "ID": ID,
        "periodogram_stat": float(periodogram_stat),
        "std_stat": float(std_stat)
    }


# CLI: argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--systemName", type=str, help="Name of the system (KIC/TIC)", default="6762829")
    parser.add_argument("--detrendingName", type=str, help="Run label for outputs", default="BLAH")
    parser.add_argument("--useSavedData", type=int, help="1 = reuse cached, 0 = fresh", default=0, choices=[0, 1])

    # NEW: injection toggles
    parser.add_argument("--injectTransits", type=int, default=0, choices=[0, 1],
                        help="Enable transit injections (0/1). If 1, you can provide --injectionParamFile.")
    parser.add_argument("--injectionParamFile", type=str, default="",
                        help="CSV of injection parameters (used only if --injectTransits=1).")

    args = parser.parse_args()

    _ = runDetrendingModule(
        SystemName=args.systemName,
        DetrendingName=args.detrendingName,
        UseSavedData=args.useSavedData,

        # Defaults retained; flip here or expose further flags as needed:
        detrending_quadratic=True,
        detrending_iterativeCosine=True,
        detrending_plugHoles=False,
        detrending_variableDuration=False,
        detrending_removeKinks=True,
        detrending_removeCommonFalsePositives=True,
        detrending_findPotentialLedges=True,
        detrending_findDeepestPoints=True,
        detrending_plotSpecificTimes=False,
        detrending_saveProcessedLightCurve=True,
        detrending_variableDurationXiTest=False,
        detrending_testCosine=False,

        detrending_injectTransits=bool(args.injectTransits),
        injection_param_file=(args.injectionParamFile or None),

        detrending_ellipsoidal=True,
        detrending_reflection=True,

        _plot_trends=True,
        _show_plots=True
    )
