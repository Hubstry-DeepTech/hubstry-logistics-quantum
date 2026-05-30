<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/D--Wave-Ocean_SDK-purple.svg" alt="D-Wave">
  <img src="https://img.shields.io/badge/OR--Tools-Benchmark-orange.svg" alt="OR-Tools">
  <img src="https://img.shields.io/badge/TRL-4-green.svg" alt="TRL">
  <img src="https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-lightgrey.svg" alt="License">
  <img src="https://img.shields.io/badge/CO2_Reduction-48.6%25-brightgreen.svg" alt="CO2">
  <img src="https://img.shields.io/badge/QUBO-VRP-yellow.svg" alt="QUBO">
  <img src="https://img.shields.io/badge/Post_Quantum-Kyber768_&_Dilithium3-critical.svg" alt="PQC">
</p>

<h1 align="center">Hubstry Quantum Logistics</h1>

<p align="center">
  Plataforma de Logistica Sustentavel Quantum-Ready — MVP<br>
  Quantum-Ready Sustainable Logistics Platform — MVP
</p>

<p align="center">
  <strong>Hubstry DeepTech</strong> · por Guilherme Goncalves Machado<br>
  <em>Technical Founder, Full Stack, Sole Owner</em>
</p>

---

## PT-BR

### O que e

Demonstracao de conceito (TRL 4) de uma plataforma de logistica sustentavel que combina:
- **Dados IoT/GPS reais** do Porto Taxi Trajectory Dataset (dataset academico usado em papers de VRP)
- **Otimizacao QUBO-VRP** via D-Wave Ocean SDK (`dimod.BinaryQuadraticModel` + `neal.SimulatedAnnealingSampler`)
- **Reducao de CO2** calculada com fatores reais (2.68 kg CO2/L diesel, 0.12 L/km)
- **Criptografia Pos-Quantica** simulada (Kyber768 encapsulamento + Dilithium3 assinatura via XOR+SHA3)

### Arquitetura

```
[IoT/GPS Data] -> [QUBO-VRP Solver] -> [Sustainability Calc] -> [PQC Security]
     |                  |                    |                   |
Porto Taxi CSV    dimod BQM          CO2 reduction       Kyber768/Dilithium3
(6 pontos GPS)   + neal SA           vs baseline         (simulado)
                 + fallback builtin
```

### Resultados (D-Wave neal)

| Metrica | Valor |
|---------|-------|
| Distancia otimizada | 43.14 km |
| CO2 otimizado | 13.81 kg |
| CO2 economizado | 11.37 kg |
| Reducao de CO2 | **48.6%** |
| Progresso EU 2030 | **88.3%** |
| Tempo de execucao | 0.069s |
| Veiculos usados | 2 |

### Benchmark vs Padrao da Industria

Comparacao lado a lado com Google OR-Tools (GLS) — o solver de VRP mais usado na industria:

| Solver | Tempo | Distancia | CO2 | Economizado | Reducao | Veiculos |
|--------|-------|-----------|-----|-------------|---------|----------|
| Builtin SA (zero deps) | 4.006s | 46.61 km | 14.99 kg | 11.99 kg | 44.4% | 2 |
| D-Wave neal (QUBO) | 0.069s | 43.14 km | 13.81 kg | 11.37 kg | 48.6% | 2 |
| Google OR-Tools (GLS) | 0.462s | 40.86 km | 13.14 kg | 13.84 kg | 51.3% | 2 |

**Analise:**
- O **D-Wave neal** fecha 66% do gap vs OR-Tools (43.14 vs 40.86 km = +5.6%)
- O **Builtin SA** funciona sem dependencias (zero deps) — gap de +14.1%
- OR-Tools e maduro (20+ anos), mas nao escala quanticamente — nosso formulario QUBO e caminho direto para QPU

### Como executar

```bash
# Instalar dependencias D-Wave
python -m pip install -r requirements-dwave.txt

# Rodar MVP principal
python run_mvp.py --dwave

# Rodar benchmark comparativo (3 solvers, auto-detect)
python -m pip install ortools
python benchmark.py
```

### Dataset: Porto Taxi Trajectory

- Dataset academico real de trajetos de taxi na area metropolitana do Porto, Portugal
- Referenciado em papers de VRP: Moreira-Matias et al. (2013), Pereira et al. (2018), Bras et al. (2021)
- 6 pontos GPS reais extraidos como instancia de demonstracao
- Arquivo: `data/porto_taxi_sample.csv`

### Licenca e Propriedade Intelectual

Este projeto e protegido sob **CC BY-NC-SA 4.0**. Proibido uso comercial sem autorizacao expressa.

> **Declaracao de Propriedade:** Hubstry DeepTech, a organizacao GitHub `Hubstry-DeepTech`, e a conta `guilherme-machado-ceo` sao criacoes originais e proprietarias de **Guilherme Goncalves Machado**, technical founder, full stack developer e sole owner. Todos os repositorios, codigo, conceitos e propriedade intelectual associados sao de titularidade exclusiva do autor.

### Disclaimer: Expectativas Quanticas

O solver atual utiliza **Simulated Annealing classico** via D-Wave Ocean SDK (`neal.SimulatedAnnealingSampler`). O formulario QUBO (`dimod.BinaryQuadraticModel`) e **100% compativel** com QPU D-Wave (Advantage, Advantage2). O upgrade para execucao quantica real requer acesso ao D-Wave Leap Cloud QPU.

---

## EN

### What it is

Proof of concept (TRL 4) for a sustainable logistics platform combining:
- **Real IoT/GPS data** from the Porto Taxi Trajectory Dataset (academic dataset used in VRP papers)
- **QUBO-VRP optimization** via D-Wave Ocean SDK (`dimod.BinaryQuadraticModel` + `neal.SimulatedAnnealingSampler`)
- **CO2 reduction** calculated with real factors (2.68 kg CO2/L diesel, 0.12 L/km)
- **Post-Quantum Cryptography** simulation (Kyber768 encapsulation + Dilithium3 signature via XOR+SHA3)

### Architecture

```
[IoT/GPS Data] -> [QUBO-VRP Solver] -> [Sustainability Calc] -> [PQC Security]
     |                  |                    |                   |
Porto Taxi CSV    dimod BQM          CO2 reduction       Kyber768/Dilithium3
(6 GPS points)   + neal SA           vs baseline         (simulated)
                 + builtin fallback
```

### Results (D-Wave neal)

| Metric | Value |
|--------|-------|
| Optimized distance | 43.14 km |
| Optimized CO2 | 13.81 kg |
| CO2 saved | 11.37 kg |
| CO2 reduction | **48.6%** |
| EU 2030 progress | **88.3%** |
| Execution time | 0.069s |
| Vehicles used | 2 |

### Benchmark vs Industry Standard

Side-by-side comparison with Google OR-Tools (GLS) — the most widely used VRP solver in industry:

| Solver | Time | Distance | CO2 | Saved | Reduction | Vehicles |
|--------|------|----------|-----|-------|-----------|----------|
| Builtin SA (zero deps) | 4.006s | 46.61 km | 14.99 kg | 11.99 kg | 44.4% | 2 |
| D-Wave neal (QUBO) | 0.069s | 43.14 km | 13.81 kg | 11.37 kg | 48.6% | 2 |
| Google OR-Tools (GLS) | 0.462s | 40.86 km | 13.14 kg | 13.84 kg | 51.3% | 2 |

**Analysis:**
- **D-Wave neal** closes 66% of the gap vs OR-Tools (43.14 vs 40.86 km = +5.6%)
- **Builtin SA** works without dependencies (zero deps) — gap of +14.1%
- OR-Tools is mature (20+ years) but doesn't scale quantumly — our QUBO formulation is a direct path to QPU

### How to Run

```bash
# Install D-Wave dependencies
python -m pip install -r requirements-dwave.txt

# Run main MVP
python run_mvp.py --dwave

# Run comparative benchmark (3 solvers, auto-detect)
python -m pip install ortools
python benchmark.py
```

### Dataset: Porto Taxi Trajectory

- Real academic dataset of taxi trajectories in the Porto metropolitan area, Portugal
- Referenced in VRP papers: Moreira-Matias et al. (2013), Pereira et al. (2018), Bras et al. (2021)
- 6 real GPS points extracted as demonstration instance
- File: `data/porto_taxi_sample.csv`

### License and IP

This project is protected under **CC BY-NC-SA 4.0**. Commercial use prohibited without express authorization.

> **IP Declaration:** Hubstry DeepTech, the GitHub organization `Hubstry-DeepTech`, and account `guilherme-machado-ceo` are original proprietary creations of **Guilherme Goncalves Machado**, technical founder, full stack developer and sole owner. All repositories, code, concepts, and associated intellectual property are exclusively owned by the author.

### Disclaimer: Quantum Expectations

The current solver uses **classical Simulated Annealing** via D-Wave Ocean SDK (`neal.SimulatedAnnealingSampler`). The QUBO formulation (`dimod.BinaryQuadraticModel`) is **100% compatible** with D-Wave QPU (Advantage, Advantage2). Upgrading to real quantum execution requires access to the D-Wave Leap Cloud QPU.

---

<p align="center">
  <sub><strong>Hubstry DeepTech</strong> · Quantum-Ready Sustainable Logistics<br>
  &copy; 2025 Guilherme Goncalves Machado — All Rights Reserved</sub>
</p>
