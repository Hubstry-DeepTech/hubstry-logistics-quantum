"""
Hubstry Quantum-Ready Sustainable Logistics Platform
====================================================
Quantum-Inspired Route Optimizer — QUBO formulation for VRP.

Integrates with: Gurudev Core quantum optimization framework.

Formulates the Vehicle Routing Problem (VRP) as a Quadratic Unconstrained
Binary Optimization (QUBO) problem and solves it via:

  1. D-Wave Ocean neal (SimulatedAnnealingSampler) — preferred
  2. Built-in pure-Python SA — fallback when dwave-neal not installed

MVP Scope:
  - Single-depot, homogeneous fleet
  - Capacity constraints
  - Minimize total distance (fuel & CO2 proxy)

D-Wave Leap Integration:
  - Builds a proper dimod.BinaryQuadraticModel from VRP constraints
  - Samples with neal.SimulatedAnnealingSampler (classical)
  - Ready for DWaveSampler() on real QPU (set DWAVE_API_TOKEN env var)
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

# Optional D-Wave Ocean SDK import
_DWAVE_AVAILABLE = False
try:
    import dimod
    import neal
    _DWAVE_AVAILABLE = True
except ImportError:
    pass


class QuboVRPOptimizer:
    """
    QUBO-based Vehicle Routing Problem solver with D-Wave Ocean integration.

    Solvers (auto-selected by availability):
      - D-Wave neal.SimulatedAnnealingSampler (requires: dwave-neal)
      - Built-in pure-Python SA (zero dependencies fallback)

    Binary variables x[v][i]: vehicle v visits node i (v=0..K-1, i=1..N-1).
    """

    def __init__(self, distance_matrix: List[List[float]],
                 demands: List[int], seed: int = 42):
        self.dist = distance_matrix
        self.demands = demands
        self.n_nodes = len(distance_matrix)
        self.n_vehicles = self._estimate_fleet_size()
        self.seed = seed
        self._solution: Optional[List[List[int]]] = None
        self._best_energy = float("inf")
        self._dwave_available = _DWAVE_AVAILABLE

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

    def _order_route_nn(self, nodes: List[int]) -> List[int]:
        """Order route nodes by nearest-neighbour heuristic."""
        if len(nodes) <= 1:
            return list(nodes)
        ordered = [nodes[0]]
        remaining = set(nodes[1:])
        while remaining:
            last = ordered[-1]
            nearest = min(remaining, key=lambda n: self.dist[last][n])
            ordered.append(nearest)
            remaining.remove(nearest)
        return ordered

    # ------------------------------------------------------------------
    # Built-in SA Solver (pure Python, zero deps)
    # ------------------------------------------------------------------

    def _energy(self, assignment: List[int]) -> float:
        """Compute energy for a vehicle assignment."""
        routes: Dict[int, List[int]] = {}
        for i in range(1, self.n_nodes):
            v = assignment[i] if i < len(assignment) else 0
            routes.setdefault(v, []).append(i)

        energy = 0.0
        for v, nodes in routes.items():
            if nodes:
                energy += ALPHA_DISTANCE * self._route_distance(nodes)
            cap = sum(self.demands[n] for n in nodes)
            if cap > VEHICLE_CAPACITY:
                energy += ALPHA_CAPACITY * (cap - VEHICLE_CAPACITY) ** 2

        if len(routes) > 1:
            sizes = [len(nodes) for nodes in routes.values()]
            avg = sum(sizes) / len(sizes)
            energy += ALPHA_TIMEWINDOW * sum((s - avg) ** 2 for s in sizes)
        return energy

    def _simulated_annealing_builtin(self) -> Tuple[List[int], float]:
        """Pure-Python SA with Metropolis acceptance."""
        rng = random.Random(self.seed)
        beta_min, beta_max = SA_BETA_RANGE

        current = [rng.randint(0, self.n_vehicles - 1) for _ in range(self.n_nodes)]
        current[0] = 0
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
                    if rng.random() >= math.exp(-beta * delta):
                        current[idx] = old_val
                        continue
                else:
                    current_energy = new_energy
                if current_energy < best_energy:
                    best = list(current)
                    best_energy = current_energy

        return best, best_energy

    # ------------------------------------------------------------------
    # D-Wave Ocean Solver (dimod BQM + neal)
    # ------------------------------------------------------------------

    def _build_bqm(self) -> "dimod.BinaryQuadraticModel":
        """
        Build a proper BinaryQuadraticModel for the VRP.

        Variables: x_{v,i} in {0,1} — vehicle v visits delivery node i.
        Objective: minimize weighted distance + constraint penalties.

        QUBO = A * distance_terms + B * capacity_penalty
               + C * assignment_penalty + D * balance_penalty
        """
        import dimod

        N = self.n_nodes
        K = self.n_vehicles
        P_ASSIGN = 10.0   # penalty: each node visited exactly once
        P_CAP = 8.0       # penalty: vehicle capacity

        bqm = dimod.BinaryQuadraticModel({}, {}, 0.0, dimod.BINARY)

        for v in range(K):
            for i in range(1, N):
                var = f"x_{v}_{i}"

                # Linear: round-trip distance contribution (depot → i → depot)
                bqm.add_variable(var, ALPHA_DISTANCE * 2.0 * self.dist[0][i])

                # Linear: assignment constraint (part of: sum_v x_{v,i} = 1)
                bqm.add_variable(var, P_ASSIGN)

                # Linear: capacity (penalty for loading)
                demand_i = self.demands[i]
                bqm.add_variable(var, P_CAP * demand_i * demand_i)

            # Quadratic: pairwise distance between co-assigned nodes
            for i in range(1, N):
                for j in range(i + 1, N):
                    vi, vj = f"x_{v}_{i}", f"x_{v}_{j}"
                    # If both in same vehicle, route connects them
                    bqm.add_interaction(vi, vj, ALPHA_DISTANCE * self.dist[i][j])
                    # Capacity interaction
                    bqm.add_interaction(
                        vi, vj,
                        -2.0 * P_CAP * self.demands[i] * self.demands[j]
                    )

            # Linear: capacity target (subtract target squared)
            cap_linear = -2.0 * P_CAP * VEHICLE_CAPACITY
            for i in range(1, N):
                bqm.add_variable(f"x_{v}_{i}", cap_linear)

        # Cross-vehicle: node assigned to at most one vehicle
        for i in range(1, N):
            for v1 in range(K):
                for v2 in range(v1 + 1, K):
                    bqm.add_interaction(
                        f"x_{v1}_{i}", f"x_{v2}_{i}",
                        2.0 * P_ASSIGN
                    )

        # Balance penalty: distribute nodes evenly across vehicles
        target_per_v = (N - 1) / K
        for v in range(K):
            for i in range(1, N):
                bqm.add_variable(f"x_{v}_{i}", ALPHA_TIMEWINDOW)
            for i in range(1, N):
                for j in range(i + 1, N):
                    bqm.add_interaction(
                        f"x_{v}_{i}", f"x_{v}_{j}",
                        2.0 * ALPHA_TIMEWINDOW
                    )

        return bqm

    def _solve_dwave(self, num_reads: int) -> Tuple[List[int], float]:
        """
        Solve using D-Wave Ocean neal.SimulatedAnnealingSampler.

        Builds a dimod BQM, samples with neal, decodes into assignment.

        Returns:
            (assignment, energy)
        """
        import neal

        bqm = self._build_bqm()
        sampler = neal.SimulatedAnnealingSampler()
        num_vars = self.n_vehicles * (self.n_nodes - 1)

        response = sampler.sample(
            bqm,
            num_reads=num_reads,
            num_sweeps=SA_NUM_SWEEPS,
            seed=self.seed,
        )

        best_sample = response.first.sample
        best_energy = response.first.energy

        # Decode: x_{v,i} = 1 means vehicle v visits node i
        assignment = [0] * self.n_nodes
        for v in range(self.n_vehicles):
            for i in range(1, self.n_nodes):
                var = f"x_{v}_{i}"
                if var in best_sample and best_sample[var] == 1:
                    assignment[i] = v

        return assignment, best_energy

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def solve(self, num_reads: int = None, use_dwave: bool = None) -> Dict:
        """
        Run the QUBO optimization pipeline.

        Auto-selects solver:
          - If dwave-neal installed AND use_dwave != False → D-Wave neal
          - Otherwise → built-in pure-Python SA

        Args:
            num_reads: Number of independent samples (default: NUM_READS).
            use_dwave: Force D-Wave (True), force builtin (False),
                       or auto-detect (None).

        Returns:
            Dict with solver results and metadata.
        """
        num_reads = num_reads or NUM_READS
        t0 = time.perf_counter()

        # Select solver
        use_dwave_solver = False
        if use_dwave is True:
            if not self._dwave_available:
                print("  [Solver] dwave-neal not installed, falling back to builtin SA")
            else:
                use_dwave_solver = True
        elif use_dwave is None and self._dwave_available:
            use_dwave_solver = True

        # Run selected solver
        if use_dwave_solver:
            overall_best, overall_best_energy = self._solve_dwave(num_reads)
            solver_name = "D-Wave neal (SimulatedAnnealingSampler)"
            n_bqm_vars = self.n_vehicles * (self.n_nodes - 1)
        else:
            overall_best = None
            overall_best_energy = float("inf")
            for _ in range(num_reads):
                assignment, energy = self._simulated_annealing_builtin()
                if energy < overall_best_energy:
                    overall_best = assignment
                    overall_best_energy = energy
            solver_name = "Built-in SA (pure Python, zero deps)"
            n_bqm_vars = 0

        # Reconstruct routes
        routes: Dict[int, List[int]] = {}
        for i in range(1, self.n_nodes):
            v = overall_best[i]
            routes.setdefault(v, []).append(i)

        sorted_routes: List[List[int]] = []
        for v in sorted(routes.keys()):
            route = self._order_route_nn(routes[v])
            sorted_routes.append(route)

        total_dist = sum(self._route_distance(r) for r in sorted_routes)
        elapsed = time.perf_counter() - t0

        self._solution = sorted_routes
        self._best_energy = overall_best_energy

        result = {
            "routes": sorted_routes,
            "total_distance": round(total_dist, 2),
            "best_energy": round(overall_best_energy, 4),
            "n_vehicles_used": len(sorted_routes),
            "execution_time_sec": round(elapsed, 4),
            "n_reads": num_reads,
            "solver": solver_name,
            "dwave_available": self._dwave_available,
            "bqm_variables": n_bqm_vars,
        }

        return result
