# Hubstry Quantum-Ready Sustainable Logistics Platform

> **Quantum-inspired** route optimization for sustainable fleet logistics.
> Integrates IoT telemetry, QUBO-VRP solving, CO2 analytics, and post-quantum
> cryptography in a single demonstrator for the VW / BMW use case.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    run_mvp.py (Entry Point)             │
├──────────┬──────────────────┬────────────────────────────┤
│ IoT Layer │    Core Layer    │     Security Layer         │
│          │                  │                            │
│ iot_     │ quantum_         │ pqc_wrapper.py             │
│ bridge.py│ optimizer.py     │   (Kyber768 / Dilithium3   │
│          │                  │    simulated)               │
│ GPS,      │ QUBO-VRP        │                            │
│ speed,    │ Simulated        │ security_bridge.py         │
│ payload   │ Annealing        │   (encrypt routes,         │
│           │                  │    sign reports)           │
├──────────┴──────────────────┼────────────────────────────┤
│ config/settings.py           │ sustainability_calc.py    │
│   (fleet, solver, env       │   (CO2 KPIs, EU 2030      │
│    parameters)               │    tracking)               │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# No external dependencies — Python 3.8+ stdlib only
python run_mvp.py
```

**Expected output:**
```
  Hubstry Quantum Logistics MVP v0.1.0

  Pipeline completed in 0.XX seconds
  Steps: iot_telemetry → qubo_optimize → sustainability_calc → security_sign

  QUBO Solver (Simulated Annealing):
    Total distance:   XX.XX km
    Vehicles used:    X

  Sustainability Metrics:
    CO2 saved:        X.X kg
    Reduction:        XX.X%
```

## Integrated Repositories

| Repository | Role in MVP |
|---|---|
| **iot-protocol-hubstry** | Fleet telemetry simulation — GPS, speed, payload, fuel |
| **gurudev-core** | Quantum-inspired QUBO formulation & SA solver for VRP |
| **hubstry-security** | Post-quantum crypto (Kyber768/Dilithium3) with AES fallback |

## Key Technologies

- **QUBO (Quadratic Unconstrained Binary Optimization)** — maps VRP to a form
  solvable on quantum annealers (D-Wave) and classical SA fallbacks
- **Simulated Annealing** — classical solver from D-Wave `neal` package,
  reimplemented in pure Python for zero-dependency MVP
- **Haversine distance** — GPS-aware routing in the Munich metropolitan area
- **Kyber768 / Dilithium3** — NIST PQC standards simulated via AES-256+SHA3
- **EU 2030 CO2 targets** — 55% reduction vs 1990 baseline tracking

## Configuration

Edit `config/settings.py` to adjust:
- Fleet size & vehicle capacity
- SA solver parameters (sweeps, temperature range, reads)
- CO2 emission factors
- PQC algorithm selection & key rotation

## License

MIT — Hubstry DeepTech
