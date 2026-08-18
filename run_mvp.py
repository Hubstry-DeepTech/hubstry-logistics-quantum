#!/usr/bin/env python3
"""
Hubstry Quantum-Ready Sustainable Logistics Platform
====================================================
MVP Entry Point — run this to execute the full pipeline.

Integrates three GitHub repositories:
  1. IoT Protocol Hubstry   — fleet telemetry simulation
  2. Gurudev Core           — quantum-inspired QUBO optimization
  3. Hubstry Security       — post-quantum cryptography

Usage:
    python run_mvp.py                  # auto-detect solver
    python run_mvp.py --builtin        # force pure Python SA
    python run_mvp.py --dwave          # force D-Wave neal (requires dwave-neal)

Requirements:
    Python 3.8+ stdlib (zero dependencies for builtin solver)
    Optional: pip install -r requirements-dwave.txt
"""

import sys
import os
import json

# Windows/cp1252: quando stdout e um pipe ou redirecionamento, o Python usa a
# codificacao local (cp1252 no Brasil), que nao cobre os caracteres do relatorio
# (setas, subscritos). Forcamos UTF-8 para o pipeline funcionar em qualquer
# console, redirecionamento, CI ou container.
# On Windows, piped/redirected stdout falls back to the locale encoding, which
# cannot encode the report characters. Force UTF-8 for portability.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass

# Ensure project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation.simulate_fleet import FleetSimulator
from config.settings import APP_NAME, APP_VERSION


def parse_args():
    """Parse command-line arguments."""
    args = set(sys.argv[1:])
    return {
        "use_dwave": "--dwave" in args,
        "force_builtin": "--builtin" in args,
    }


def main():
    """Run the complete Hubstry Quantum Logistics MVP pipeline."""
    args = parse_args()

    use_dwave = None
    if args["use_dwave"]:
        use_dwave = True
    elif args["force_builtin"]:
        use_dwave = False

    print(f"\n  {APP_NAME} v{APP_VERSION}")
    print(f"  Python {sys.version.split()[0]}")

    # Check D-Wave availability
    try:
        import dimod
        import neal
        print(f"  D-Wave Ocean:       neal v{neal.__version__}, dimod v{dimod.__version__}")
        if use_dwave is None:
            print("  Solver:             D-Wave neal (auto-detected)")
    except ImportError:
        print("  D-Wave Ocean:       not installed (using builtin SA)")
        if use_dwave is True:
            print("  [WARNING] --dwave requested but dwave-neal not found")
            use_dwave = None

    if use_dwave is False:
        print("  Solver:             Built-in SA (forced via --builtin)")

    print()

    # Create simulator and run full pipeline
    sim = FleetSimulator(seed=42)
    results = sim.run(num_reads=100, use_dwave=use_dwave)

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
