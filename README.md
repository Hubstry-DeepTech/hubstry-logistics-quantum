# Hubstry Quantum-Ready Sustainable Logistics Platform

> **Quantum-inspired** route optimization for sustainable fleet logistics.
> Integrates IoT telemetry, QUBO-VRP solving, CO2 analytics, and post-quantum
> cryptography in a single demonstrator for the VW / BMW use case.

---

## About Hubstry DeepTech

**Hubstry DeepTech** is an original proprietary creation of
**Guilherme Gonçalves Machado** — Technical Founder, Full Stack, sole owner.

The GitHub organization `Hubstry-DeepTech` and the account `guilherme-machado-ceo`
are also original proprietary creations of Guilherme Gonçalves Machado.

**What is Hubstry?**

Hubstry is a **deep tech P&D hub** dedicated to accelerating innovation with
scientific rigor and strategic resilience. Our purpose is to mitigate risk, cost,
and time in the development of proprietary technologies, enabling companies
and partners to access cutting-edge solutions without bearing the full weight of
internal R&D investment alone.

Our model creates **significant technological moats** in strategic sectors, offering
early competitive advantage and temporary exclusivity in emerging technologies —
before they become market standards. Additionally, Hubstry operates in anticipating
disruption routes on **3-to-5-year horizons**, helping organizations prepare against
unexpected disruptions and ensuring greater strategic predictability.

In summary: **we are the partner that transforms technological uncertainty
into long-term competitive advantage.**

---

## Important — Read Before Using

### Quantum Expectations Management

This is a **"Quantum-Ready"** platform — not a quantum-speedup demo.

**What we ARE:**
- A production-ready pipeline architecture designed to plug into quantum hardware (D-Wave, IBM Qiskit, Google Cirq)
- A QUBO formulation that maps Vehicle Routing Problems to a form solvable on quantum annealers
- A working demonstration using Simulated Annealing (D-Wave `neal`-style) as the classical solver

**What we are NOT (yet):**
- A claim of quantum advantage. The current solver is classical SA — it produces correct, optimized results, but without quantum speedup
- A benchmark against quantum hardware. Hardware integration is the planned next step
- A production fleet management system. This is a validated MVP demonstrating the integration architecture

The value proposition is the **pipeline** — not the solver. When quantum hardware matures beyond NISQ-era limitations, this same QUBO formulation runs on real qubits with zero architecture changes.

### Intellectual Property Notice

This repository contains **original proprietary work** by Guilherme Gonçalves Machado
/ Hubstry DeepTech. All source code, architectural designs, optimization formulations,
integration patterns, and documentation are proprietary.

The platform draws concepts from three proprietary Hubstry DeepTech projects:
- **IoT Protocol Hubstry** — sensor telemetry architecture
- **Gurudev Core** — quantum optimization framework
- **Hubstry Security** — post-quantum cryptography layer

All foundational IP belongs to Guilherme Gonçalves Machado. This repository
represents a novel integration of these domains into a unified logistics pipeline.

**License:** CC BY-NC-SA 4.0 — Non-commercial use only. See [LICENSE](LICENSE).

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    run_mvp.py (Entry Point)             │
├──────────┬──────────────────┬────────────────────────────┤
│ IoT Layer │    Core Layer    │     Security Layer         │
│          │                  │                            │
│ iot_     │ quantum_         │ pqc_wrapper.py             │
│ bridge.py│ optimizer.py     │   (Kyber768 / Dilithium3   │
│          │                  │    simulated via AES+SHA3)  │
│ GPS,      │ QUBO-VRP        │                            │
│ speed,    │ Simulated        │ security_bridge.py         │
│ payload   │ Annealing        │   (encrypt routes,         │
│           │                  │    sign reports)           │
├──────────┴──────────────────┼────────────────────────────┤
│ config/settings.py           │ sustainability_calc.py    │
│   (fleet, solver, env         │   (CO2 KPIs, EU 2030      │
│    parameters)                 │    target tracking)       │
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

  Pipeline completed in ~1-3 seconds
  Steps: iot_telemetry → qubo_optimize → sustainability_calc → security_sign

  QUBO Solver (Simulated Annealing):
    Total distance:   ~69 km
    Vehicles used:     2

  Sustainability Metrics:
    CO2 saved:         ~12 kg
    Reduction:         ~35%
    EU 2030 progress:  ~65% (target: 55%)
```

## Integrated Repositories

| Repository | Role in MVP | Status |
|---|---|---|
| **iot-protocol-hubstry** | Fleet telemetry simulation — GPS, speed, payload, fuel | Concepts integrated |
| **gurudev-core** | Quantum-inspired QUBO formulation & SA solver for VRP | Concepts integrated |
| **hubstry-security** | Post-quantum crypto (Kyber768/Dilithium3) with AES fallback | Concepts integrated |

> Note: The three original repositories are independent proprietary projects.
> This MVP re-implements their core concepts in a unified, zero-dependency pipeline.

## Key Technologies

- **QUBO (Quadratic Unconstrained Binary Optimization)** — maps VRP to a form solvable on quantum annealers (D-Wave) and classical SA fallbacks
- **Simulated Annealing** — classical solver from D-Wave `neal` package, reimplemented in pure Python for zero-dependency MVP
- **Haversine distance** — GPS-aware routing in the Munich metropolitan area
- **Kyber768 / Dilithium3** — NIST PQC standards simulated via AES-256+SHA3
- **EU 2030 CO2 targets** — 55% reduction vs 1990 baseline tracking

## Configuration

Edit `config/settings.py` to adjust:
- Fleet size & vehicle capacity
- SA solver parameters (sweeps, temperature range, reads)
- CO2 emission factors
- PQC algorithm selection & key rotation

## File Structure

```
hubstry-logistics-quantum/
├── run_mvp.py              # Entry point — run this
├── README.md               # This file
├── LICENSE                  # CC BY-NC-SA 4.0
├── .gitignore              # Python exclusions
├── config/
│   ├── settings.py         # All configurable parameters
│   └── __init__.py
├── iot_layer/
│   ├── iot_bridge.py       # Fleet telemetry simulation
│   └── __init__.py
├── core_layer/
│   ├── quantum_optimizer.py    # QUBO-VRP solver (SA)
│   ├── sustainability_calc.py  # CO2 emission KPIs
│   └── __init__.py
├── security_layer/
│   ├── pqc_wrapper.py      # Kyber768/Dilithium3 simulation
│   ├── security_bridge.py  # Encrypt routes, sign reports
│   └── __init__.py
└── simulation/
    ├── simulate_fleet.py   # Full pipeline orchestrator
    └── __init__.py
```

## Roadmap

- [x] MVP: IoT → QUBO → CO2 → PQC pipeline
- [ ] D-Wave real hardware integration (QPU sampler)
- [ ] Streamlit dashboard with live route visualization
- [ ] Real fleet data ingestion (MQTT / REST API)
- [ ] Multi-depot VRP formulation
- [ ] Hybrid QAOA + heuristic solver
- [ ] Production deployment with monitoring

---

**Founder & Owner:** Guilherme Gonçalves Machado
**License:** CC BY-NC-SA 4.0 — Hubstry DeepTech
