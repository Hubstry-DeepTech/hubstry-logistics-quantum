#!/usr/bin/env python3
"""
Hubstry Quantum-Ready Sustainable Logistics Platform
====================================================
Benchmark — Compare QUBO solvers vs Google OR-Tools industry standard.

Runs the same VRP problem with multiple solvers and produces a
side-by-side comparison table showing distance, time, and CO2 metrics.

Usage:
    python benchmark.py
    python benchmark.py --dwave       # include D-Wave neal
    python benchmark.py --no-ortools   # skip OR-Tools
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
from config.settings import APP_NAME, APP_VERSION, NUM_READS


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


def run_benchmark(use_dwave=None, skip_ortools=False):
    """Run full benchmark comparing all available solvers."""
    print(f"\n{'='*70}")
    print(f"  {APP_NAME} — SOLVER BENCHMARK")
    print(f"  {APP_VERSION}")
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

    # 2) D-Wave neal (if available or requested)
    try:
        import neal
        import dimod
        if use_dwave is not False:
            solvers.append({
                "name": "Hubstry D-Wave neal",
                "key": "dwave",
                "optimizer": QuboVRPOptimizer(distance_matrix, demands, seed=42),
                "use_dwave": True,
            })
    except ImportError:
        print("  [INFO] D-Wave neal not installed, skipping")

    # 3) OR-Tools (if available and not skipped)
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
            print(f"✗ {e}")
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
        print(f"✓ {kpis['total_distance_km']} km, {kpis['execution_time_sec']}s")

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

    # Find best
    if len(results) > 1:
        best_dist = min(r["total_distance_km"] for r in results)
        best = next(r for r in results if r["total_distance_km"] == best_dist)
        print(f"\n  Best distance: {best['solver']} ({best_dist} km)")

        hubstry = next((r for r in results if r["key"] != "ortools"), None)
        ortools = next((r for r in results if r["key"] == "ortools"), None)

        if hubstry and ortools:
            diff_pct = ((hubstry["total_distance_km"] - ortools["total_distance_km"])
                         / ortools["total_distance_km"] * 100)
            print(f"  Hubstry vs OR-Tools: {diff_pct:+.1f}% distance")
            if diff_pct <= 5:
                print(f"  ✓ Hubstry is WITHIN 5% of industry standard")
            elif diff_pct <= 10:
                print(f"  ~ Hubstry is WITHIN 10% of industry standard")
            else:
                print(f"  ⚠ Gap detected — QUBO formulation tuning needed")

    print(f"\n{'='*70}")

    # Save results
    output_path = os.path.join(os.path.dirname(__file__), "benchmark_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to: {output_path}")

    return results


def main():
    args = set(sys.argv[1:])
    use_dwave = "--dwave" in args
    skip_ortools = "--no-ortools" in args

    if "--help" in args or "-h" in args:
        print(__doc__)
        return

    run_benchmark(use_dwave=use_dwave, skip_ortools=skip_ortools)


if __name__ == "__main__":
    main()
