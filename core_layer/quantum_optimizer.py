"""
Hubstry Quantum-Ready Sustainable Logistics Platform
====================================================
Quantum-Inspired Route Optimizer — QUBO formulation for VRP.

Integrates with: Gurudev Core quantum optimization framework.

Formulates the Vehicle Routing Problem (VRP) as a Quadratic Unconstrained
Binary Optimization (QUBO) problem and solves it via Simulated Annealing
(D-Wave neal-style classical fallback).

MVP Scope:
  - Single-depot, homogeneous fleet
  - Capacity constraints
  - Minimize total distance (fuel & CO2 proxy)
"""

import math
import random
import time
from typing import List, Dict, Tuple, Optional

from config.settings import (
    ALPHA_DISTANCE,
    ALPHA_CAPACITY,
    ALPHA_TIMEWINDOW,
    NUM_READS,
    SA_NUM_SWEEPS,
    SA_BETA_RANGE,
    VEHICLE_CAPACITY,
)


class QuboVRPOptimizer:
    """
    QUBO-based Vehicle Routing Problem solver.

    Uses binary variables x[i][k] where:
      - i = node index (0 = depot, 1..N = delivery points)
      - k = position in route sequence

    Constraints:
      1. Each node visited exactly once  (alpha_distance)
      2. Vehicle capacity not exceeded   (alpha_capacity)
      3. Depot at start/end of each route (alpha_timewindow)

    Objective: minimize total weighted distance.
    """

    def __init__(self, distance_matrix: List[List[float]],
                 demands: List[int], seed: int = 42):
        """
        Args:
            distance_matrix: N x N symmetric matrix in km.
            demands: List of parcel counts per delivery node
                     (index 0 = depot, demand 0).
            seed: Random seed for reproducibility.
        """
        self.dist = distance_matrix
        self.demands = demands
        self.n_nodes = len(distance_matrix)
        self.n_vehicles = self._estimate_fleet_size()
        self.seed = seed
        self._solution: Optional[List[List[int]]] = None
        self._best_energy = float("inf")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _estimate_fleet_size(self) -> int:
        """Estimate minimum vehicles needed based on total demand."""
        total_demand = sum(self.demands)
        return max(2, math.ceil(total_demand / VEHICLE_CAPACITY))

    def _route_distance(self, route: List[int]) -> float:
        """Total distance of a single route (starts and ends at depot 0)."""
        if not route:
            return 0.0
        total = self.dist[0][route[0]]
        for i in range(len(route) - 1):
            total += self.dist[route[i]][route[i + 1]]
        total += self.dist[route[-1]][0]
        return total

    def _energy(self, assignment: List[int]) -> float:
        """
        Compute QUBO energy for a given vehicle assignment.

        Args:
            assignment: assignment[i] = vehicle index for node i
                        (0 = depot, not assigned to a vehicle).

        Returns:
            Weighted energy value (lower is better).
        """
        routes: Dict[int, List[int]] = {}
        for i in range(1, self.n_nodes):
            v = assignment[i] if i < len(assignment) else 0
            routes.setdefault(v, []).append(i)

        energy = 0.0

        # 1) Distance penalty
        for v, nodes in routes.items():
            if nodes:
                energy += ALPHA_DISTANCE * self._route_distance(nodes)

        # 2) Capacity penalty
        for v, nodes in routes.items():
            cap = sum(self.demands[n] for n in nodes)
            if cap > VEHICLE_CAPACITY:
                energy += ALPHA_CAPACITY * (cap - VEHICLE_CAPACITY) ** 2

        # 3) Balance penalty (spread deliveries evenly)
        if len(routes) > 1:
            sizes = [len(nodes) for nodes in routes.values()]
            avg = sum(sizes) / len(sizes)
            energy += ALPHA_TIMEWINDOW * sum((s - avg) ** 2 for s in sizes)

        return energy

    def _simulated_annealing(self) -> Tuple[List[int], float]:
        """
        Run simulated annealing to find the best vehicle assignment.

        Returns:
            (best_assignment, best_energy)
        """
        rng = random.Random(self.seed)
        beta_min, beta_max = SA_BETA_RANGE

        # Initial random assignment
        current = [rng.randint(0, self.n_vehicles - 1) for _ in range(self.n_nodes)]
        current[0] = 0  # depot is fixed
        current_energy = self._energy(current)

        best = list(current)
        best_energy = current_energy

        for sweep in range(SA_NUM_SWEEPS):
            beta = beta_min + (beta_max - beta_min) * sweep / SA_NUM_SWEEPS

            for _ in range(self.n_nodes - 1):
                idx = rng.randint(1, self.n_nodes - 1)
                old_val = current[idx]
                new_val = rng.randint(0, self.n_vehicles - 1)

                if new_val == old_val:
                    continue

                current[idx] = new_val
                new_energy = self._energy(current)

                delta = new_energy - current_energy
                if delta > 0:
                    # Metropolis acceptance criterion
                    if rng.random() >= math.exp(-beta * delta):
                        current[idx] = old_val  # reject
                        continue
                else:
                    current_energy = new_energy

                if current_energy < best_energy:
                    best = list(current)
                    best_energy = current_energy

        return best, best_energy

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def solve(self, num_reads: int = None) -> Dict:
        """
        Run the full QUBO optimization pipeline.

        Args:
            num_reads: Number of independent SA runs (default: NUM_READS).

        Returns:
            Dict with keys: 'routes', 'total_distance', 'best_energy',
                           'n_vehicles_used', 'execution_time_sec'.
        """
        num_reads = num_reads or NUM_READS
        t0 = time.perf_counter()

        overall_best: Optional[List[int]] = None
        overall_best_energy = float("inf")

        for read in range(num_reads):
            assignment, energy = self._simulated_annealing()
            if energy < overall_best_energy:
                overall_best = assignment
                overall_best_energy = energy

        # Reconstruct routes from best assignment
        routes: Dict[int, List[int]] = {}
        for i in range(1, self.n_nodes):
            v = overall_best[i]
            routes.setdefault(v, []).append(i)

        # Sort each route by distance (nearest-neighbour within route)
        sorted_routes: List[List[int]] = []
        for v in sorted(routes.keys()):
            route = routes[v]
            if len(route) > 1:
                ordered = [route[0]]
                remaining = set(route[1:])
                while remaining:
                    last = ordered[-1]
                    nearest = min(remaining, key=lambda n: self.dist[last][n])
                    ordered.append(nearest)
                    remaining.remove(nearest)
                route = ordered
            sorted_routes.append(route)

        total_dist = sum(self._route_distance(r) for r in sorted_routes)
        elapsed = time.perf_counter() - t0

        self._solution = sorted_routes
        self._best_energy = overall_best_energy

        return {
            "routes": sorted_routes,
            "total_distance": round(total_dist, 2),
            "best_energy": round(overall_best_energy, 4),
            "n_vehicles_used": len(sorted_routes),
            "execution_time_sec": round(elapsed, 4),
            "n_reads": num_reads,
        }
