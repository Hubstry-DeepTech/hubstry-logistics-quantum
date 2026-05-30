#!/usr/bin/env python3
"""
Hubstry Quantum-Ready Sustainable Logistics Platform
====================================================
MVP Entry Point — run this to execute the full pipeline.

Integrates three GitHub repositories:
  1. IoT Protocol Hubstry   — fleet telemetry simulation
  2. Gurudev Core           — quantum-inspired QUBO optimization
  3. Hubstry Security       — post-quantum cryptography

Demonstrates:
  - IoT sensor data generation (Munich delivery network)
  - QUBO-VRP route optimization via Simulated Annealing
  - CO2 emission reduction vs unoptimized baseline
  - Post-quantum encryption & digital signatures

Usage:
    python run_mvp.py

Requirements:
    Python 3.8+ (no external dependencies — uses only stdlib)
"""

import sys
import os
import json

# Ensure project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation.simulate_fleet import FleetSimulator
from config.settings import APP_NAME, APP_VERSION


def main():
    """Run the complete Hubstry Quantum Logistics MVP pipeline."""
    print(f"\n  {APP_NAME} v{APP_VERSION}")
    print(f"  Python {sys.version.split()[0]}")
    print()

    # Create simulator and run full pipeline
    sim = FleetSimulator(seed=42)
    results = sim.run(num_reads=100)

    # Print formatted report
    sim.print_report(results)

    # Save detailed JSON results
    output_path = os.path.join(os.path.dirname(__file__), "mvp_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Detailed results saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
