# -*- coding: utf-8 -*-

"""
Lightweight N-body transit timing utilities for Stanley.
- TransitTiming_nbody_lite: find mid-transit times/durations from a REBOUND Simulation.
- TT_to_TTV: convert transit times to TTVs by fitting and removing a linear ephemeris.

Timeout policy:
- No OS signal timeouts are used here. We rely solely on an internal wall-clock guard
  via `maxCompTime`, which exits the loop gracefully and returns a flagged result.
"""

from __future__ import annotations
import time
import numpy as np
import matplotlib.pyplot as plt
import rebound

__all__ = ["TransitTiming_nbody_lite", "TT_to_TTV"]


def TransitTiming_nbody_lite(sim: rebound.Simulation,timeEnd: float,cadence: float,maxCompTime: float = np.inf) -> dict:
    """
    Integrate a REBOUND Simulation forward and record transits of body 2 across body 0.

    Parameters:
    sim: rebound.Simulation
        Pre-configured simulation (units consistent with seconds/meters).
    timeEnd: float
        Absolute simulation time to integrate to (same units as sim.t).
    cadence: float
        Photometric cadence [seconds]. Transit time bisection precision is 3*cadr.
    maxCompTime: float, optional
        Hard wall-clock limit in seconds; if exceeded, the function exits early
        and sets 'exceedMaxCompTime' in the return dict.

    Returns:
    dict
        {
          'transitTimes': np.ndarray (seconds, absolute sim time),
          'transitDurations': np.ndarray (seconds),
          'stable': bool (eccentricity change below threshold),
          'exceedMaxCompTime': bool (True if wall clock limit hit)
        }

    Notes:
    - Coplanar geometry assumption for crossing test:
      crossing when x changes sign and (y_transiter - y_star) > 0 with observer on -z.
    - Stability heuristic: max |e(t) - e(t0)| < 0.1 across the integration.
    - Timeout handling is graceful: the loop checks the real wall clock against
      `maxCompTime` and returns early with 'exceedMaxCompTime'=True instead of raising.
    """
    timerStart = time.time()
    timerCurrent = timerStart
    exceedMaxCompTime = False

    stable = True  # becomes False if eccentricity varies too much

    transittimes = []
    transitdurations = []
    transitimpactparameters = [] 

    # Particle and orbit handles
    p = sim.particles
    orbits = sim.orbits()

    # Integration step reference from the transiter's orbital period
    P_transiter = orbits[1].P

    # Stability check scaffolding
    deltaEccentricityThreshold = 0.1
    numEccentricityChecks = 20
    base = 1.5
    currentEccentricityCheck = 1
    e_transiter = [orbits[1].e]

    transitingBody = 2
    baseBody = 0

    # Kepler 30 min -> 90 min precision; TESS 2 min -> 6 min precision
    tPrecision = 3.0 * cadence  # seconds

    # Only body 0 and 2 are active during integration step checks
    sim.N_active = 2

    timeStart = sim.t

    # Main integration loop with wall-clock guard
    while (sim.t < timeEnd) and ((timerCurrent - timerStart) < maxCompTime):
        timerCurrent = time.time()

        # Previous x position (transiter relative to base body) and time
        x_old = p[transitingBody].x - p[baseBody].x
        t_old = sim.t

        # Integrate by an eighth of the planet's period
        sim.integrate(sim.t + P_transiter / 8.0)

        # New x position/time
        x_new = p[transitingBody].x - p[baseBody].x
        t_new = sim.t

        # Crossings only count if transiter is in front of the star: (y_transiter - y_star) > 0
        if x_old * x_new < 0.0 and (p[transitingBody].y - p[baseBody].y) > 0.0:
            # Bisection to timing precision
            while (t_new - t_old) > tPrecision:
                if x_old * x_new < 0.0:
                    t_new = sim.t
                else:
                    t_old = sim.t
                sim.integrate((t_new + t_old) / 2.0)
                x_new = p[transitingBody].x - p[baseBody].x

            # Record mid-transit and an approximate duration from relative speed
            transittimes.append(sim.t)
            transitdurations.append(
                2.0 * (p[baseBody].r + p[transitingBody].r) /
                ((p[transitingBody].vx - p[baseBody].vx) ** 2.0 +
                 (p[transitingBody].vz - p[baseBody].vz) ** 2.0) ** 0.5
            )

            # Push beyond the transit
            sim.integrate(sim.t + P_transiter / 10.0)

        # Log-spaced eccentricity checks (more frequent early)
        fractionSimCompleted = (sim.t - timeStart) / max(1e-12, (timeEnd - timeStart))
        if fractionSimCompleted > base ** (currentEccentricityCheck - numEccentricityChecks):
            orbits = sim.orbits()
            e_transiter.append(orbits[1].e)
            delta_e_step = abs(e_transiter[currentEccentricityCheck] - e_transiter[0])

            if delta_e_step > deltaEccentricityThreshold:
                break  # early exit on instability

            currentEccentricityCheck += 1

    # Exceeded wall clock?
    if (timerCurrent - timerStart) >= maxCompTime:
        exceedMaxCompTime = True

    transittimes = np.array(transittimes)
    transitdurations = np.array(transitdurations)

    # Final stability check
    orbits = sim.orbits()
    e_transiter = np.array(e_transiter)
    delta_e = np.max(np.abs(e_transiter - e_transiter[0]))
    if delta_e > deltaEccentricityThreshold:
        stable = False

    transitData = {
        "transitTimes": transittimes,
        "transitDurations": transitdurations,
        "stable": stable,
        "exceedMaxCompTime": exceedMaxCompTime,
    }
    return transitData


def TT_to_TTV(TT: np.ndarray):
    """
    Convert transit times to TTVs by removing a best-fit linear ephemeris.

    Parameters:
    TT: array-like
        Transit mid-times (float). NaNs/inf are ignored.

    Returns:
    (ttv, m, c)
        ttv: np.ndarray
            Residuals after subtracting m * n + c (n = 0..N-1).
        m: float
            Best-fit slope (period).
        c: float
            Best-fit intercept (epoch).

    Notes:
    - Uses a simple closed-form least-squares fit on (0, 1, ..., N-1).
    - Returns empty TTVs and (nan, nan) if fewer than 2 finite transits.
    """
    TT = np.asarray(TT, dtype=float)
    mask = np.isfinite(TT)
    y = TT[mask]
    if y.size < 2:
        return np.array([]), np.nan, np.nan

    x = np.arange(y.size, dtype=float)

    # Center to improve conditioning
    x0 = x - x.mean()
    y0 = y - y.mean()

    Sxx = float(np.dot(x0, x0))
    if Sxx == 0.0:
        m = 0.0
        c = float(y.mean())
    else:
        m = float(np.dot(x0, y0) / Sxx)
        c = float(y.mean() - m * x.mean())

    ttv = y - (m * x + c)
    return ttv, m, c

