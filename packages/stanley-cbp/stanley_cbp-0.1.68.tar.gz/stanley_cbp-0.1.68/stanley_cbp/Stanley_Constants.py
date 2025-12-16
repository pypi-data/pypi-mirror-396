# Physical and astronomical constants used throughout Stanley
# (Units remain exactly the same as the original version.)

speedOfLight = 299792458.0      # m/s
au2m = 1.49598e11               # m
hours2sec = 3600.0              # s
days2sec = 86400.0              # s
years2sec = 31557600.0          # s

mSun_kg = 1.98892e30            # kg
mEarth_kg = 5.9742e24           # kg
mMoon_kg = 7.34767309e22        # kg
mJupiter_kg = 1.8987e27         # kg

rSun_m = 6.9634e8               # m
rJupiter_m = 6.9911e7           # m
rEarth_m = 6.371e6              # m

G_Nm2pkg2 = 6.67384e-11         # N·m²/kg²

# ---- Backward-compatibility aliases (legacy UPPERCASE names) ----
# Keep these AFTER the lowercase names are defined.
try:
    YEARS2SEC
except NameError:
    YEARS2SEC = years2sec

try:
    DAYS2SEC
except NameError:
    DAYS2SEC = days2sec

try:
    HOURS2SEC
except NameError:
    HOURS2SEC = hours2sec

try:
    MSUN_KG
except NameError:
    MSUN_KG = mSun_kg

try:
    RSUN_M
except NameError:
    RSUN_M = rSun_m

# Optional extras
try:
    MJUPITER_KG
except NameError:
    MJUPITER_KG = mJupiter_kg
try:
    REARTH_M
except NameError:
    REARTH_M = rEarth_m
try:
    RJUPITER_M
except NameError:
    RJUPITER_M = rJupiter_m
