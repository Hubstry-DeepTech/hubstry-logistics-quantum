"""
Hubstry Quantum-Ready Sustainable Logistics Platform
====================================================
Configuration settings for the MVP demonstration.

Integrates:
  - IoT Protocol Hubstry (sensor telemetry)
  - Gurudev Core (quantum-inspired optimization)
  - Hubstry Security (post-quantum cryptography)

Use case: Fleet route optimization with carbon footprint reduction.
Data source: Porto Taxi Trajectory Dataset (real GPS coordinates).
"""

# ---------------------------------------------------------------------------
# General
# ---------------------------------------------------------------------------
APP_NAME = "Hubstry Quantum Logistics MVP"
APP_VERSION = "0.3.0"
ENVIRONMENT = "development"          # development | staging | production

# ---------------------------------------------------------------------------
# IoT Layer — fleet sensor parameters
# ---------------------------------------------------------------------------
FLEET_SIZE = 8                       # number of delivery vehicles
DEPOT_LAT = 41.2050                  # Porto logistics hub latitude (Leixões)
DEPOT_LON = -8.6900                  # Porto logistics hub longitude
NUM_DELIVERIES = 6                   # delivery points per route cycle
SPEED_KMH = 40                       # average urban delivery speed km/h
SENSOR_INTERVAL_SEC = 300             # telemetry polling interval (5 min)

# Data source configuration
USE_REAL_DATA = True                  # True = Porto Taxi CSV, False = simulated
DATA_FILE = "data/porto_taxi_sample.csv"  # real GPS dataset sample

# Delivery zone bounding box (Porto metropolitan area)
ZONE_LAT_MIN = 41.10
ZONE_LAT_MAX = 41.25
ZONE_LON_MIN = -8.70
ZONE_LON_MAX = -8.57

# ---------------------------------------------------------------------------
# Core / Quantum Layer — QUBO VRP solver parameters
# ---------------------------------------------------------------------------
ALPHA_DISTANCE = 1.0                # weight: minimize total distance
ALPHA_CAPACITY = 0.8                # weight: respect vehicle capacity
ALPHA_TIMEWINDOW = 0.5              # weight: respect time windows
NUM_READS = 100                      # number of simulated-annealing samples
SA_NUM_SWEEPS = 1000                 # simulated-annealing sweeps per sample
SA_BETA_RANGE = (0.1, 50.0)         # inverse-temperature schedule range
VEHICLE_CAPACITY = 20                # max parcels per vehicle per cycle

# ---------------------------------------------------------------------------
# Sustainability Layer — CO2 emission factors
# ---------------------------------------------------------------------------
DIESEL_EMISSION_FACTOR = 2.68        # kg CO2 per liter of diesel
FUEL_CONSUMPTION_L_PER_KM = 0.12    # liters per km (medium delivery van)
EU_CO2_TARGET_2030 = 55             # % reduction target vs 1990 baseline
EU_BASELINE_CO2_PER_TKM = 0.124     # kg CO2 per tonne-km (EU 1990 avg)

# ---------------------------------------------------------------------------
# Security Layer — Post-Quantum Cryptography simulation
# ---------------------------------------------------------------------------
PQC_ALGORITHM_KEM = "Kyber768"       # Key Encapsulation Mechanism
PQC_ALGORITHM_SIG = "Dilithium3"     # Digital Signature
PQC_FALLBACK_CIPHER = "SHA3-256 keystream (XOR, nao-AEAD / non-AEAD)" # didactic fallback
PQC_FALLBACK_HASH = "SHA3-256"       # classical fallback hash
HSM_SIMULATED = True                 # use software-based HSM simulation
KEY_ROTATION_HOURS = 24              # automatic key rotation interval
TLS_MIN_VERSION = "1.3"             # minimum TLS version for fleet comms
DATA_CLASSIFICATION = "RESTRICTED"   # GDPR compliance level

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(name)-28s | %(levelname)-8s | %(message)s"
LOG_FILE = "hubstry_mvp.log"
