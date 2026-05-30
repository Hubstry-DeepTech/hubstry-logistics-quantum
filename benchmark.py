#!/usr/bin/env python3
"""
Hubstry Quantum-Ready Sustainable Logistics Platform
====================================================
Benchmark v0.3.0 — Compare QUBO solvers vs Google OR-Tools industry standard.

3-solver auto-detection:
  1. Hubstry Builtin SA  (zero deps, always available)
  2. D-Wave neal QUBO    (auto-detected if dimod+neal installed)
  3. Google OR-Tools GLS  (auto-detected if ortools installed)

Usage:
    python benchmark.py              # run all detected solvers
    python benchmark.py --no-dwave   # skip D-Wave neal
    python benchmark.py --no-ortools # skip OR-Tools
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from iot_layer.iot_bridge import IoTBridge
from core_layer.quantum_optimizer import QuboVRPOptimizer
from core_layer.sustainability_calc import SustainabilityCalculator
from core_layer.ortools_solver import ORToolsVRPSolver
from config.settings import APP_NAME, NUM_READS


def run_solver(name, optimizer, num_reads=NUM_READS, use_dwave=None):
    """Run a single solver and return results with timing."""
    t0 = time.perf_counter()
    try:
        result = optimizer.solve(num_reads=num_reads, use_dwave=use_dwave)
        elapsed = time.perf_counter() - t0
        result["total_time_with_overhead"] = round(elapsed, 4)
        return result
    except Exception as e:
        return {"error": str(e), "solver": name, "routes": [], "total_distance": 0}


def run_benchmark(skip_dwave=False, skip_ortools=False):
    """Run full benchmark comparing all available solvers."""
    VERSION = "0.3.0"
    print(f"\n{'='*70}")
    print(f"  {APP_NAME} — SOLVER BENCHMARK  v{VERSION}")
    print(f"{'='*70}")

    # Load data
    print("\n  Loading data...")
    iot = IoTBridge(seed=42)
    points = iot.get_delivery_points()
    distance_matrix = iot.compute_distance_matrix()
    demands = iot.get_demands()
    n_deliveries = len(points) - 1

    print(f"  Data source:  {iot.data_source}")
    print(f"  Deliveries:   {n_deliveries}")
    print(f"  Fleet size:   8 vehicles (max capacity 20 parcels)")

    # Define solvers to run
    solvers = []

    # 1) Built-in SA (always available)
    solvers.append({
        "name": "Hubstry Builtin SA",
        "key": "builtin",
        "optimizer": QuboVRPOptimizer(distance_matrix, demands, seed=42),
        "use_dwave": False,
    })

    # 2) D-Wave neal (auto-detected if installed)
    if not skip_dwave:
        try:
            import neal
            import dimod
            solvers.append({
                "name": "D-Wave neal (QUBO)",
                "key": "dwave",
                "optimizer": QuboVRPOptimizer(distance_matrix, demands, seed=42),
                "use_dwave": True,
            })
        except ImportError:
            print("  [INFO] D-Wave neal not installed, skipping")

    # 3) OR-Tools (auto-detected if installed)
    if not skip_ortools:
        try:
            from ortools.constraint_solver import routing_enums_pb2
            solvers.append({
                "name": "Google OR-Tools GLS",
                "key": "ortools",
                "optimizer": ORToolsVRPSolver(distance_matrix, demands, seed=42),
                "use_dwave": None,
            })
        except ImportError:
            print("  [INFO] OR-Tools not installed, skipping")

    # Run all solvers
    print(f"\n  Running {len(solvers)} solver(s)...\n")
    calc = SustainabilityCalculator(distance_matrix, demands)
    results = []
    errors = []

    for s in solvers:
        name = s["name"]
        print(f"  Solving with {name}...", end=" ", flush=True)

        try:
            if s["key"] == "ortools":
                solver_result = s["optimizer"].solve(time_limit_sec=5.0)
            else:
                solver_result = run_solver(
                    name, s["optimizer"],
                    num_reads=NUM_READS,
                    use_dwave=s["use_dwave"]
                )
        except Exception as e:
            print(f"x {e}")
            errors.append({"solver": name, "error": str(e)})
            continue

        kpis = calc.compute_kpis(solver_result.get("routes", []))
        kpis["solver"] = solver_result.get("solver", name)
        kpis["key"] = s["key"]
        kpis["execution_time_sec"] = solver_result.get(
            "execution_time_sec", solver_result.get("total_time_with_overhead", 0)
        )
        kpis["n_vehicles_used"] = solver_result.get("n_vehicles_used", 0)
        kpis["bqm_variables"] = solver_result.get("bqm_variables", 0)

        results.append(kpis)
        print(f"OK {kpis['total_distance_km']} km, {kpis['execution_time_sec']}s")

    # Print comparison table
    print(f"\n{'='*70}")
    print(f"  BENCHMARK RESULTS — {n_deliveries} deliveries, Porto Taxi GPS")
    print(f"{'='*70}")

    header = f"  {'Solver':<28} {'Time':>7} {'Dist':>8} {'CO2':>8} {'Saved':>8} {'Reduc.':>8} {'Veh.':>4}"
    print(header)
    print(f"  {'-'*66}")

    for r in results:
        print(f"  {r['solver']:<28} {r['execution_time_sec']:>6.3f}s "
              f"{r['total_distance_km']:>7.1f}km "
              f"{r['optimized_co2_kg']:>7.2f}kg "
              f"{r['co2_saved_kg']:>7.2f}kg "
              f"{r['reduction_pct']:>7.1f}% "
              f"{r['n_vehicles_used']:>3}")

    # Analysis section
    if len(results) > 1:
        best_dist = min(r["total_distance_km"] for r in results)
        best = next(r for r in results if r["total_distance_km"] == best_dist)
        print(f"\n  Best distance: {best['solver']} ({best_dist} km)")

        ortools = next((r for r in results if r["key"] == "ortools"), None)
        dwave = next((r for r in results if r["key"] == "dwave"), None)
        builtin = next((r for r in results if r["key"] == "builtin"), None)

        if ortools:
            for r in results:
                if r["key"] != "ortools":
                    diff_pct = ((r["total_distance_km"] - ortools["total_distance_km"])
                                / ortools["total_distance_km"] * 100)
                    print(f"  {r['solver']} vs OR-Tools: {diff_pct:+.1f}% distance")

        if dwave and builtin:
            speedup = builtin["execution_time_sec"] / max(dwave["execution_time_sec"], 0.0001)
            gap_bi = ((dwave["total_distance_km"] - builtin["total_distance_km"])
                      / builtin["total_distance_km"] * 100)
            print(f"\n  D-Wave neal vs Builtin: {speedup:.1f}x faster, {gap_bi:+.1f}% distance")

        if dwave and ortools:
            gap = ((dwave["total_distance_km"] - ortools["total_distance_km"])
                   / ortools["total_distance_km"] * 100)
            if gap > 5:
                print("  Gap - QUBO tuning needed")
            elif gap > 0:
                print("  Small gap - competitive")
            else:
                print("  Outperforms industry standard!")

    print(f"\n{'='*70}")

    # Save results
    output_path = os.path.join(os.path.dirname(__file__), "benchmark_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"version": VERSION, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "dataset": iot.data_source, "deliveries": n_deliveries,
                   "results": results}, f, indent=2, default=str)
    print(f"\n  Results saved to: {output_path}")

    return results


def main():
    args = set(sys.argv[1:])
    skip_dwave = "--no-dwave" in args
    skip_ortools = "--no-ortools" in args

    if "--help" in args or "-h" in args:
        print(__doc__)
        return

    run_benchmark(skip_dwave=skip_dwave, skip_ortools=skip_ortools)


if __name__ == "__main__":
    main()
