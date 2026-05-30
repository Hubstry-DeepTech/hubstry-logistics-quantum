"""
Hubstry Quantum-Ready Sustainable Logistics Platform
====================================================
Fleet Simulation — End-to-end orchestration of the logistics pipeline.

Coordinates the full data flow:
  1. IoT Bridge  → generates fleet telemetry & delivery points
  2. QUBO Solver → optimizes vehicle routes
  3. Sustainability → computes CO2 KPIs
  4. Security    → encrypts & signs results

Provides a single run() method for the complete MVP demonstration.
"""

import time
from typing import Dict, Any

from iot_layer.iot_bridge import IoTBridge
from core_layer.quantum_optimizer import QuboVRPOptimizer
from core_layer.sustainability_calc import SustainabilityCalculator
from security_layer.security_bridge import SecurityBridge


class FleetSimulator:
    """
    Orchestrates the complete quantum-ready logistics pipeline.

    Usage:
        sim = FleetSimulator(seed=42)
        results = sim.run()
        sim.print_report(results)
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.iot = IoTBridge(seed=seed)
        self.security = SecurityBridge(seed=seed)

    def run(self, num_reads: int = 100, use_dwave: bool = None) -> Dict[str, Any]:
        """
        Execute the full pipeline and return all results.

        Args:
            num_reads: Number of SA samples for the QUBO solver.
            use_dwave: Force D-Wave (True), force builtin (False), or auto (None).

        Returns:
            Comprehensive results dictionary.
        """
        t_start = time.perf_counter()

        # ---- 1. IoT: generate delivery network ----
        points = self.iot.get_delivery_points()
        distance_matrix = self.iot.compute_distance_matrix()
        demands = self.iot.get_demands()

        # ---- 2. Quantum: optimize routes ----
        optimizer = QuboVRPOptimizer(
            distance_matrix=distance_matrix,
            demands=demands,
            seed=self.seed,
        )
        solver_result = optimizer.solve(num_reads=num_reads, use_dwave=use_dwave)

        # ---- 3. Sustainability: compute CO2 KPIs ----
        calc = SustainabilityCalculator(distance_matrix, demands)
        kpis = calc.compute_kpis(solver_result["routes"])

        # ---- 4. Security: encrypt route plan & sign report ----
        encrypted_routes = self.security.encrypt_route_plan(
            routes=solver_result["routes"],
            metadata={"n_reads": num_reads, "solver": "SA-QUBO"},
        )
        signed_report = self.security.sign_sustainability_report(kpis)

        t_end = time.perf_counter()

        return {
            "pipeline": {
                "total_time_sec": round(t_end - t_start, 4),
                "steps": ["iot_telemetry", "qubo_optimize",
                          "sustainability_calc", "security_sign"],
            },
            "iot": {
                "delivery_points": len(points),
                "depot": points[0],
                "fleet_size": 8,
                "data_source": self.iot.data_source,
            },
            "optimizer": solver_result,
            "sustainability": kpis,
            "security": self.security.status(),
            "encrypted_routes": encrypted_routes,
            "signed_report": signed_report,
        }

    # ------------------------------------------------------------------
    # Reporting helpers
    # ------------------------------------------------------------------

    @staticmethod
    def print_report(results: Dict) -> None:
        """Print a human-readable summary to stdout."""
        print("\n" + "=" * 65)
        print("  HUBSTRY QUANTUM-READY SUSTAINABLE LOGISTICS — MVP RESULTS")
        print("=" * 65)

        pipe = results["pipeline"]
        iot = results["iot"]
        print(f"\n  Data Source:       {iot['data_source']}")
        print(f"  Pipeline:           {pipe['total_time_sec']:.4f} seconds")
        print(f"  Steps:             {' → '.join(pipe['steps'])}")

        opt = results["optimizer"]
        print(f"\n  QUBO Solver ({opt.get('solver', 'SA')})")
        if opt.get("bqm_variables", 0) > 0:
            print(f"    BQM variables:    {opt['bqm_variables']}")
        print(f"    Reads:            {opt['n_reads']}")
        print(f"    Best energy:      {opt['best_energy']}")
        print(f"    Vehicles used:    {opt['n_vehicles_used']}")
        print(f"    Total distance:   {opt['total_distance']} km")

        for i, route in enumerate(opt["routes"]):
            stops = " → ".join(f"N{n}" for n in route)
            print(f"    Route {i + 1}: Depot → {stops} → Depot")

        sus = results["sustainability"]
        print(f"\n  Sustainability Metrics:")
        print(f"    Optimized CO2:    {sus['optimized_co2_kg']} kg")
        print(f"    Baseline CO2:     {sus['baseline_co2_kg']} kg")
        print(f"    CO2 saved:        {sus['co2_saved_kg']} kg")
        print(f"    Reduction:        {sus['reduction_pct']}%")
        print(f"    Fuel consumed:     {sus['fuel_consumed_liters']} L")
        print(f"    EU 2030 progress: {sus['eu_2030_progress_pct']}% "
              f"(target: {sus['eu_2030_target_pct']}%)")

        sec = results["security"]
        print(f"\n  Security Layer:")
        print(f"    PQC Algorithm:    {sec['pqc']['kem_algorithm']} + "
              f"{sec['pqc']['sig_algorithm']}")
        print(f"    Fallback:         {sec['pqc']['fallback_cipher']}")
        print(f"    Encryption ops:  {sec['encrypt_operations']}")
        print(f"    Signature ops:   {sec['sign_operations']}")

        print("\n" + "=" * 65)
