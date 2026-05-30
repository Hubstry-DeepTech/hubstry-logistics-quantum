"""
Hubstry Quantum-Ready Sustainable Logistics Platform
====================================================
IoT Bridge — Fleet telemetry data from delivery vehicles.

Integrates with: IoT Protocol Hubstry architecture.
Supports two data modes:
  - Real GPS data from Porto Taxi Trajectory Dataset (CSV)
  - Simulated data with random GPS coordinates (fallback)

The real dataset provides validated GPS coordinates from 442 taxis
operating in the Porto metropolitan area, Portugal.
"""

import csv
import math
import os
import random
import time
from typing import List, Dict, Any, Optional

from config.settings import (
    FLEET_SIZE,
    DEPOT_LAT,
    DEPOT_LON,
    NUM_DELIVERIES,
    SPEED_KMH,
    SENSOR_INTERVAL_SEC,
    ZONE_LAT_MIN,
    ZONE_LAT_MAX,
    ZONE_LON_MIN,
    ZONE_LON_MAX,
    VEHICLE_CAPACITY,
    USE_REAL_DATA,
    DATA_FILE,
)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two GPS coordinates
    using the Haversine formula.

    Args:
        lat1, lon1: Coordinates of point 1 (decimal degrees).
        lat2, lon2: Coordinates of point 2 (decimal degrees).

    Returns:
        Distance in kilometers.
    """
    R = 6371.0  # Earth radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class TelemetryReading:
    """Single telemetry snapshot from one vehicle."""

    __slots__ = (
        "vehicle_id", "timestamp", "latitude", "longitude",
        "speed_kmh", "heading_deg", "payload_pct", "fuel_liters",
        "engine_temp_c", "odometer_km",
    )

    def __init__(self, vehicle_id: str, latitude: float, longitude: float,
                 **kwargs):
        self.vehicle_id = vehicle_id
        self.timestamp = kwargs.get("timestamp", time.time())
        self.latitude = latitude
        self.longitude = longitude
        self.speed_kmh = kwargs.get("speed_kmh", round(random.uniform(5, 60), 1))
        self.heading_deg = kwargs.get("heading_deg", round(random.uniform(0, 359)))
        self.payload_pct = kwargs.get("payload_pct", round(random.uniform(20, 95), 1))
        self.fuel_liters = kwargs.get("fuel_liters", round(random.uniform(10, 55), 1))
        self.engine_temp_c = kwargs.get("engine_temp_c", round(random.uniform(75, 105), 1))
        self.odometer_km = kwargs.get("odometer_km", round(random.uniform(1000, 80000)))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dictionary."""
        return {k: getattr(self, k) for k in self.__slots__}

    def __repr__(self) -> str:
        return (f"Telemetry(vehicle={self.vehicle_id}, "
                f"lat={self.latitude:.4f}, lon={self.longitude:.4f}, "
                f"speed={self.speed_kmh} km/h, payload={self.payload_pct}%)")


class IoTBridge:
    """
    Fleet telemetry bridge supporting real and simulated data modes.

    Real mode: loads GPS coordinates from Porto Taxi Trajectory Dataset CSV.
    Simulated mode: generates random coordinates within the delivery zone.
    """

    def __init__(self, seed: int = 42, use_real_data: bool = None):
        self._rng = random.Random(seed)
        self._use_real = use_real_data if use_real_data is not None else USE_REAL_DATA
        self._csv_points: List[Dict[str, Any]] = []
        self._csv_demands: List[int] = []
        self._data_source: str = "unknown"
        self._load_data()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_data(self) -> None:
        """Load delivery points from the configured data source."""
        if self._use_real:
            loaded = self._load_csv()
            if loaded:
                return
            # Fallback to simulated if CSV not found
            print("  [IoT] CSV not found, falling back to simulated data")

        # Simulated mode
        self._data_source = "simulated"
        self._generate_simulated_network()

    def _load_csv(self) -> bool:
        """
        Load real delivery points from Porto Taxi sample CSV.

        Returns:
            True if loaded successfully, False otherwise.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(base_dir, DATA_FILE)

        if not os.path.isfile(csv_path):
            return False

        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            self._csv_points = [
                {"lat": float(row["latitude"]), "lon": float(row["longitude"])}
                for row in rows
            ]
            self._csv_demands = [int(row["parcels"]) for row in rows]

            # Use seed to select a reproducible subset
            indices = list(range(len(self._csv_points)))
            self._rng.shuffle(indices)
            selected = indices[:NUM_DELIVERIES]
            selected.sort()

            self._csv_points = [self._csv_points[i] for i in selected]
            self._csv_demands = [self._csv_demands[i] for i in selected]

            self._data_source = "Porto Taxi Trajectory Dataset (real GPS)"
            print(f"  [IoT] Loaded {len(self._csv_points)} real delivery "
                  f"points from: {self._data_source}")
            return True

        except (ValueError, KeyError, IOError) as e:
            print(f"  [IoT] CSV load error: {e}")
            return False

    def _generate_simulated_network(self) -> None:
        """Generate random delivery waypoints within the zone."""
        self._csv_points = [
            {
                "lat": self._rng.uniform(ZONE_LAT_MIN, ZONE_LAT_MAX),
                "lon": self._rng.uniform(ZONE_LON_MIN, ZONE_LON_MAX),
            }
            for _ in range(NUM_DELIVERIES)
        ]
        self._csv_demands = [
            self._rng.randint(2, 8) for _ in range(NUM_DELIVERIES)
        ]

    def _jitter(self, value: float, magnitude: float = 0.0005) -> float:
        """Add small random GPS jitter to simulate sensor imprecision."""
        return value + self._rng.uniform(-magnitude, magnitude)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def data_source(self) -> str:
        """Return a description of the current data source."""
        return self._data_source

    def get_delivery_points(self) -> List[Dict[str, float]]:
        """
        Return the list of delivery waypoints.

        Each point is a dict with 'lat' and 'lon' keys.
        Index 0 is the depot.
        """
        depot = {"lat": DEPOT_LAT, "lon": DEPOT_LON}
        return [depot] + self._csv_points

    def get_demands(self) -> List[int]:
        """
        Return parcel demand per delivery point.

        Index 0 is depot (demand 0), followed by each delivery point.
        """
        return [0] + self._csv_demands

    def get_fleet_snapshot(self) -> List[TelemetryReading]:
        """
        Capture a telemetry snapshot of the entire fleet.

        Returns a list of TelemetryReading objects, one per vehicle.
        """
        readings: List[TelemetryReading] = []
        points = self.get_delivery_points()

        for i in range(FLEET_SIZE):
            target = points[i % len(points)]
            vid = f"VH-{i + 1:03d}"

            readings.append(TelemetryReading(
                vehicle_id=vid,
                latitude=self._jitter(target["lat"]),
                longitude=self._jitter(target["lon"]),
                speed_kmh=round(self._rng.uniform(0, SPEED_KMH), 1),
                heading_deg=round(self._rng.uniform(0, 359)),
                payload_pct=round(
                    max(5, VEHICLE_CAPACITY - i * 2 + self._rng.uniform(-5, 5)),
                    1
                ),
                fuel_liters=round(self._rng.uniform(8, 58), 1),
                engine_temp_c=round(self._rng.uniform(78, 102), 1),
                odometer_km=round(self._rng.uniform(5000, 75000)),
            ))
        return readings

    def compute_distance_matrix(self) -> List[List[float]]:
        """
        Build a symmetric distance matrix (km) between all delivery points
        including the depot.

        Returns:
            N x N list of lists where N = 1 depot + NUM_DELIVERIES.
        """
        points = self.get_delivery_points()
        n = len(points)
        matrix: List[List[float]] = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                d = haversine_km(
                    points[i]["lat"], points[i]["lon"],
                    points[j]["lat"], points[j]["lon"],
                )
                matrix[i][j] = round(d, 3)
                matrix[j][i] = matrix[i][j]  # symmetric
        return matrix
