"""
Hubstry Quantum-Ready Sustainable Logistics Platform
====================================================
OR-Tools VRP Solver — Industry-standard benchmark.

Google OR-Tools is the most widely used open-source solver for Vehicle
Routing Problems. This module wraps OR-Tools as a reference benchmark
to compare against our QUBO formulation.

OR-Tools uses:
  - Constraint Programming (CP) with local search
  - Google's proprietary routing algorithms
  - PathCheapestArcFirst heuristic for initial solution

This allows direct comparison:
  Hubstry QUBO (D-Wave neal / builtin SA)  vs  Google OR-Tools VRP
"""

import time
from typing import Dict, List, Optional, Tuple

# Optional OR-Tools import
_ORTOOLS_AVAILABLE = False
try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    _ORTOOLS_AVAILABLE = True
except ImportError:
    pass


class ORToolsVRPSolver:
    """
    Vehicle Routing Problem solver using Google OR-Tools.

    Uses the CVRP (Capacitated VRP) formulation with:
      - Distance matrix from Haversine calculations
      - Capacity constraints per vehicle
      - Automatic vehicle fleet sizing

    Reference:
      https://developers.google.com/optimization/routing/vrp
    """

    def __init__(self, distance_matrix: List[List[float]],
                 demands: List[int], seed: int = 42):
        self.dist = distance_matrix
        self.demands = demands
        self.n_nodes = len(distance_matrix)
        self.n_vehicles = max(2, self.n_nodes - 1)  # max vehicles = n-1
        self.seed = seed
        self._available = _ORTOOLS_AVAILABLE

    @property
    def available(self) -> bool:
        return self._available

    def solve(self, time_limit_sec: float = 5.0,
              num_vehicles: int = None) -> Dict:
        """
        Solve the CVRP using OR-Tools.

        Args:
            time_limit_sec: Maximum solver time in seconds.
            num_vehicles: Override vehicle count (default: auto).

        Returns:
            Dict with routes, total distance, and metadata.
        """
        if not self._available:
            raise RuntimeError(
                "OR-Tools not installed. Run: python -m pip install ortools"
            )

        num_vehicles = num_vehicles or self.n_vehicles
        n = self.n_nodes
        t0 = time.perf_counter()

        # Create routing index manager
        manager = pywrapcp.RoutingIndexManager(
            n, num_vehicles, 0  # depot = node 0
        )

        # Create routing model
        routing = pywrapcp.RoutingModel(manager)

        # Distance callback
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(self.dist[from_node][to_node] * 1000)  # meters

        transit_callback_index = routing.RegisterTransitCallback(
            distance_callback
        )
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Demand callback (capacity constraint)
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return self.demands[from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(
            demand_callback
        )
        vehicle_capacity = 20  # same as config VEHICLE_CAPACITY
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # slack
            [vehicle_capacity] * num_vehicles,  # capacity per vehicle
            True,  # start cumul to zero
            "Capacity"
        )

        # Search parameters
        search_params = pywrapcp.DefaultRoutingSearchParameters()
        search_params.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_params.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_params.time_limit.seconds = int(time_limit_sec)

        # Solve
        solution = routing.Solve()
        elapsed = time.perf_counter() - t0

        if not solution:
            # Fallback: return empty result
            return {
                "routes": [],
                "total_distance": 0.0,
                "n_vehicles_used": 0,
                "execution_time_sec": round(elapsed, 4),
                "solver": "OR-Tools (no solution found)",
                "ortools_available": True,
            }

        # Extract routes
        routes = []
        for vehicle_id in range(num_vehicles):
            index = routing.Start(vehicle_id)
            route = []
            route_distance = 0
            while routing.IsEnd(index) == 0:
                node = manager.IndexToNode(index)
                if node != 0:  # skip depot
                    route.append(node)
                prev_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    prev_index, index, vehicle_id
                )
            if route:  # only add non-empty routes
                routes.append(route)

        # Count used vehicles and compute actual distance
        actual_dist = 0.0
        for route in routes:
            if route:
                actual_dist += self.dist[0][route[0]]
                for i in range(len(route) - 1):
                    actual_dist += self.dist[route[i]][route[i + 1]]
                actual_dist += self.dist[route[-1]][0]

        return {
            "routes": routes,
            "total_distance": round(actual_dist, 2),
            "n_vehicles_used": len(routes),
            "execution_time_sec": round(elapsed, 4),
            "solver": "Google OR-Tools (Guided Local Search)",
            "ortools_available": True,
            "search_strategy": "PATH_CHEAPEST_ARC + GUIDED_LOCAL_SEARCH",
            "time_limit_sec": time_limit_sec,
        }
