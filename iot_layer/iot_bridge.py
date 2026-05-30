"""
Hubstry Quantum-Ready Sustainable Logistics Platform
====================================================
IoT Bridge — Simulates fleet telemetry data from delivery vehicles.

Integrates with: IoT Protocol Hubstry architecture.
Provides realistic GPS positions, speed, payload, and fuel readings
for the Munich metropolitan delivery network.
"""

import math
import random
import time
from typing import List, Dict, Any

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
        return {
            k: getattr(self, k) for k in self.__slots__
        }

    def __repr__(self) -> str:
        return (f"Telemetry(vehicle={self.vehicle_id}, "
                f"lat={self.latitude:.4f}, lon={self.longitude:.4f}, "
                f"speed={self.speed_kmh} km/h, payload={self.payload_pct}%)")


class IoTBridge:
    """
    Simulates the IoT Protocol Hubstry telemetry stream.

    Generates realistic delivery-vehicle data for the Munich area,
    including GPS jitter, payload decay, and fuel consumption modelling.
    """

    def __init__(self, seed: int = 42):
        self._rng = random.Random(seed)
        self._delivery_points: List[Dict[str, float]] = []
        self._generate_delivery_network()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _generate_delivery_network(self) -> None:
        """Pre-generate random delivery waypoints within the zone."""
        self._delivery_points = [
            {
                "lat": self._rng.uniform(ZONE_LAT_MIN, ZONE_LAT_MAX),
                "lon": self._rng.uniform(ZONE_LON_MIN, ZONE_LON_MAX),
            }
            for _ in range(NUM_DELIVERIES)
        ]

    def _jitter(self, value: float, magnitude: float = 0.0005) -> float:
        """Add small random GPS jitter to simulate sensor imprecision."""
        return value + self._rng.uniform(-magnitude, magnitude)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_delivery_points(self) -> List[Dict[str, float]]:
        """
        Return the list of delivery waypoints.

        Each point is a dict with 'lat' and 'lon' keys.
        Index 0 is the depot (Munich HQ).
        """
        depot = {"lat": DEPOT_LAT, "lon": DEPOT_LON}
        return [depot] + self._delivery_points

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
