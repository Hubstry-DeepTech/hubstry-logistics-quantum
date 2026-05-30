"""
Hubstry Quantum-Ready Sustainable Logistics Platform
====================================================
Sustainability Calculator — CO2 emission modelling and reporting.

Computes carbon footprint metrics for delivery fleet routes,
tracks reductions against EU 2030 targets, and generates
sustainability KPIs for the VW / BMW use case.
"""

import math
from typing import Dict, List, Tuple

from config.settings import (
    DIESEL_EMISSION_FACTOR,
    FUEL_CONSUMPTION_L_PER_KM,
    EU_CO2_TARGET_2030,
    EU_BASELINE_CO2_PER_TKM,
    VEHICLE_CAPACITY,
)


class SustainabilityCalculator:
    """
    Calculate carbon-emission metrics for vehicle routing solutions.

    Metrics include:
      - Total CO2 emitted (kg) per route and per fleet
      - CO2 per delivery (kg/delivery)
      - Improvement percentage vs unoptimized baseline
      - Progress toward EU 2030 reduction target
    """

    def __init__(self, distance_matrix, demands: List[int]):
        """
        Args:
            distance_matrix: N x N distance matrix (km).
            demands: Parcel count per delivery node.
        """
        self.dist = distance_matrix
        self.demands = demands

    # ------------------------------------------------------------------
    # Core calculations
    # ------------------------------------------------------------------

    def route_co2(self, route: List[int]) -> float:
        """
        Calculate CO2 emissions for a single route.

        Formula:  distance_km * FUEL_CONSUMPTION_L_PER_KM * DIESEL_EMISSION_FACTOR

        Args:
            route: List of node indices (excluding depot start/end).

        Returns:
            CO2 in kg.
        """
        if not route:
            return 0.0

        distance = self.dist[0][route[0]]
        for i in range(len(route) - 1):
            distance += self.dist[route[i]][route[i + 1]]
        distance += self.dist[route[-1]][0]

        co2 = distance * FUEL_CONSUMPTION_L_PER_KM * DIESEL_EMISSION_FACTOR
        return round(co2, 3)

    def fleet_co2(self, routes: List[List[int]]) -> float:
        """
        Total CO2 for all fleet routes.

        Args:
            routes: List of route lists.

        Returns:
            Total CO2 in kg.
        """
        return round(sum(self.route_co2(r) for r in routes), 3)

    def baseline_co2(self, n_deliveries: int) -> float:
        """
        Estimate CO2 for an unoptimized baseline route.

        Models unoptimized dispatch: each delivery is a SEPARATE
        round-trip from depot (no route consolidation). This is the
        typical "before optimization" scenario in real fleets where
        each order triggers an individual vehicle dispatch.

        Total distance = sum of 2 * dist[depot][i] for all deliveries.

        Args:
            n_deliveries: Total number of delivery points.

        Returns:
            Baseline CO2 in kg.
        """
        baseline_distance_km = self._unoptimized_fleet_distance(n_deliveries)
        co2 = baseline_distance_km * FUEL_CONSUMPTION_L_PER_KM * DIESEL_EMISSION_FACTOR
        return round(co2, 3)

    def _unoptimized_fleet_distance(self, n: int) -> float:
        """
        Total distance for unoptimized individual round-trips.
        Each delivery = separate Depot → point → Depot trip (×2).
        """
        if n <= 0:
            return 0.0
        total = 0.0
        for i in range(1, min(n + 1, len(self.dist))):
            total += 2.0 * self.dist[0][i]
        return total

    # ------------------------------------------------------------------
    # KPI computation
    # ------------------------------------------------------------------

    def compute_kpis(self, routes: List[List[int]]) -> Dict:
        """
        Generate a comprehensive sustainability report.

        Args:
            routes: Optimized route assignment from the QUBO solver.

        Returns:
            Dict with sustainability KPIs.
        """
        optimized_co2 = self.fleet_co2(routes)
        n_deliveries = sum(len(r) for r in routes)
        baseline = self.baseline_co2(n_deliveries)

        total_distance = 0.0
        for r in routes:
            if r:
                total_distance += self.dist[0][r[0]]
                for i in range(len(r) - 1):
                    total_distance += self.dist[r[i]][r[i + 1]]
                total_distance += self.dist[r[-1]][0]

        total_parcels = sum(self.demands[n] for r in routes for n in r)
        total_tkm = total_distance * (total_parcels / max(len(routes), 1))

        reduction_pct = 0.0
        if baseline > 0:
            reduction_pct = ((baseline - optimized_co2) / baseline) * 100

        eu_progress = min(100.0, reduction_pct / EU_CO2_TARGET_2030 * 100)

        return {
            "optimized_co2_kg": optimized_co2,
            "baseline_co2_kg": round(baseline, 3),
            "co2_saved_kg": round(max(0, baseline - optimized_co2), 3),
            "reduction_pct": round(reduction_pct, 1),
            "total_distance_km": round(total_distance, 2),
            "total_deliveries": n_deliveries,
            "total_parcels": total_parcels,
            "co2_per_delivery_kg": round(optimized_co2 / max(n_deliveries, 1), 3),
            "co2_per_parcel_kg": round(optimized_co2 / max(total_parcels, 1), 4),
            "eu_2030_progress_pct": round(eu_progress, 1),
            "eu_2030_target_pct": EU_CO2_TARGET_2030,
            "vehicles_used": len(routes),
            "fuel_consumed_liters": round(
                total_distance * FUEL_CONSUMPTION_L_PER_KM, 2
            ),
        }
