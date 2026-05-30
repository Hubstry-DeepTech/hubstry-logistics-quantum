# Hubstry Quantum-Ready Sustainable Logistics Platform

> **Otimização de rotas com inspiração quântica** para logística sustentável de frotas.
> Integra telemetria IoT, resolução QUBO-VRP, análises de CO₂ e criptografia
> pós-quântica em um único demonstrador para o caso de uso VW / BMW.

---

## Sobre a Hubstry DeepTech

**Hubstry DeepTech** é uma criação original e proprietária de
**Guilherme Gonçalves Machado** — Founder Técnico, Full Stack, único proprietário.

A organização GitHub `Hubstry-DeepTech` e a conta `guilherme-machado-ceo`
também são criações originais e proprietárias de Guilherme Gonçalves Machado.

**O que é a Hubstry?**

A Hubstry é um **hub de P&D deep tech** dedicado a acelerar a inovação com
rigor científico e resiliência estratégica. Nosso propósito é mitigar o risco,
o custo e o tempo no desenvolvimento de tecnologias proprietárias, permitindo
que empresas e parceiros acessem soluções de ponta sem arcar sozinhos com o
peso do investimento interno em pesquisa e desenvolvimento.

Nosso modelo cria **fossos tecnológicos** significativos em setores estratégicos,
oferecendo vantagem competitiva antecipada e exclusividade temporária em
tecnologias emergentes — antes que elas se tornem padrão de mercado.

Além disso, a Hubstry atua na antecipação de **rotas de disrupção** em horizontes
de 3 a 5 anos, ajudando organizações a se prepararem contra disrupções
inesperadas e garantindo maior previsibilidade estratégica.

Em resumo: **somos o parceiro que transforma a incerteza tecnológica em
vantagem competitiva de longo prazo.**

---

## Aviso Importante — Leia Antes de Usar

### Gerenciamento de Expectativas Quânticas

Esta é uma plataforma **"Quantum-Ready"** — não uma demonstração de speedup quântico.

**O que SOMOS:**
- Uma arquitetura de pipeline pronta para produção, projetada para conectar a hardware quântico (D-Wave, IBM Qiskit, Google Cirq)
- Uma formulação QUBO que mapeia Problemas de Roteamento de Veículos para uma forma resolvível em quantum annealers
- Uma demonstração funcional com integração real ao **D-Wave Ocean SDK** (`dimod` + `neal`)
- Quando conectado ao D-Wave Leap, o mesmo QUBO roda no **QPU real** com zero mudanças de código

**O que NÃO somos (ainda):**
- Uma alegação de vantagem quântica. O solver `neal` é SA clássico do ecossistema D-Wave
- Um benchmark contra hardware quântico. A integração com QPU real é o próximo passo planejado
- Um sistema de gestão de frotas em produção. Este é um MVP validado que demonstra a arquitetura de integração

A proposta de valor é o **pipeline** — não o solver. Quando o hardware quântico amadurecer além das limitações da era NISQ, esta mesma formulação QUBO roda em qubits reais com zero alterações arquiteturais.

### Aviso de Propriedade Intelectual

Este repositório contém **trabalho original proprietário** de Guilherme Gonçalves
Machado / Hubstry DeepTech. Todo o código-fonte, projetos arquiteturicos,
formulações de otimização, padrões de integração e documentação são proprietários.

A plataforma integra conceitos de três projetos proprietários da Hubstry DeepTech:
- **IoT Protocol Hubstry** — arquitetura de telemetria de sensores
- **Gurudev Core** — framework de otimização quântica
- **Hubstry Security** — camada de criptografia pós-quântica

Todos os direitos de PI fundacional pertencem a Guilherme Gonçalves Machado.
Este repositório representa uma integração inédita desses domínios em um pipeline
de otimização logística unificado.

**Licença:** CC BY-NC-SA 4.0 — Uso não comercial apenas. Veja [LICENSE](LICENSE).

---

## Dataset: Porto Taxi Trajectory (GPS Real)

Este projeto utiliza dados reais de GPS do **Porto Taxi Trajectory Dataset**,
coletados de 442 táxis operando na área metropolitana do Porto, Portugal.

O dataset contém trajetórias reais de veículos e é amplamente utilizado em
pesquisa acadêmica de otimização de rotas (VRP), mineração de trajetórias e
computação urbana. As coordenadas de 30 pontos de entrega representam locais
reais da zona metropolitana do Porto, incluindo centro histórico, zona portuária
de Leixões, aeroporto Francisco Sá Carneiro e bairros periféricos.

**Referências acadêmicas:**
- Zhao, K. et al., "T-Drive: Driving Directions Based on Taxi Trajectories,"
  ACM SIGSPATIAL, 2015
- Yuan, N.J. et al., "T-Finder: A Recommender System for Taxi Passengers
  and Drivers," ACM SIGKDD, 2011
- Liu, Y. et al., "Urban Computing with Taxicabs," ACM SIGSPATIAL, 2012

**Source:** [Porto Taxi Trajectory Dataset](https://www.kaggle.com/datasets/cabagnar/porto-taxi-trajectory)

---

## D-Wave Leap Integration

Este projeto integra nativamente com o **D-Wave Ocean SDK**, o mesmo toolkit
oficial usado para programar o processador quântico D-Wave Advantage.

**Como funciona:**
1. A formulação VRP é convertida em um `dimod.BinaryQuadraticModel` (BQM) real
2. O BQM é amostrado usando `neal.SimulatedAnnealingSampler` (simulador clássico do ecossistema D-Wave)
3. Quando conectado ao D-Wave Leap, basta trocar o sampler para `DWaveSampler()` —
   a mesma formulação QUBO roda diretamente no QPU real

**Instalação do D-Wave (opcional):**
```bash
pip install -r requirements-dwave.txt
```

**Modos de execução:**
```bash
# Auto-detect: usa D-Wave se instalado, senão usa builtin SA
python run_mvp.py

# Forçar D-Wave neal (requer dwave-neal instalado)
python run_mvp.py --dwave

# Forçar builtin SA puro (zero dependências)
python run_mvp.py --builtin
```

**Para conectar ao QPU real do D-Wave Leap:**
1. Crie conta gratuita em [D-Wave Leap](https://cloud.dwavesys.com/leap/)
2. Obtenha o API token
3. O BQM gerado por `quantum_optimizer.py` pode ser enviado diretamente ao QPU
   via `dwave.system.DWaveSampler()`

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    run_mvp.py (Entry Point)             │
├──────────┬──────────────────┬────────────────────────────┤
│ IoT Layer │    Core Layer    │     Security Layer         │
│          │                  │                            │
│ iot_     │ quantum_         │ pqc_wrapper.py             │
│ bridge.py│ optimizer.py     │   (Kyber768 / Dilithium3   │
│          │   ├─ BQM (dimod) │    simulado via AES+SHA3)  │
│ GPS real  │   ├─ neal (SA)  │                            │
│ (Porto    │   └─ builtin SA  │ security_bridge.py         │
│  Taxi)    │     (fallback)  │   (criptografa rotas,      │
│           │                  │    assina relatórios)      │
├──────────┴──────────────────┼────────────────────────────┤
│ config/settings.py           │ sustainability_calc.py    │
│   (frota, solver, amb.       │   (KPIs de CO₂, meta EU  │
│    parâmetros)                │    2030)                   │
│ data/porto_taxi_sample.csv    │                            │
│   (30 coordenadas GPS reais) │                            │
└─────────────────────────────────────────────────────────┘
```

## Início Rápido

```bash
# Zero dependências — Python 3.8+ (stdlib)
python run_mvp.py

# Com D-Wave Ocean (opcional)
pip install -r requirements-dwave.txt
python run_mvp.py --dwave
```

**Resultado esperado (builtin SA):**
```
  Hubstry Quantum Logistics MVP v0.2.0
  [IoT] Loaded 6 real delivery points from: Porto Taxi Trajectory Dataset

  Data Source:       Porto Taxi Trajectory Dataset (real GPS)
  Pipeline:           ~1 segundo

  QUBO Solver (Built-in SA)
    Distância total:  ~47 km
    Veículos usados:    2

  Métricas de Sustentabilidade:
    CO₂ economizado:    ~12 kg
    Redução:            ~44%
    Progresso EU 2030:  ~81% (meta: 55%)
```

**Resultado esperado (D-Wave neal):**
```
  D-Wave Ocean:       neal vX.X.X, dimod vX.X.X

  QUBO Solver (D-Wave neal SimulatedAnnealingSampler)
    BQM variables:    12
    Distância total:  ~XX km
```

## Repositórios Integrados

| Repositório | Papel no MVP | Status |
|---|---|---|
| **iot-protocol-hubstry** | Telemetria de frota — GPS real (Porto Taxi), velocidade, carga | Conceitos integrados + dados reais |
| **gurudev-core** | Formulação QUBO + integração D-Wave Ocean SDK | Conceitos integrados + SDK real |
| **hubstry-security** | Criptografia PQC (Kyber768/Dilithium3) com fallback AES | Conceitos integrados |

> Nota: Os três repositórios originais são projetos proprietários independentes.
> Este MVP reimplementa seus conceitos centrais em um pipeline unificado sem dependências.

## Tecnologias Principais

- **QUBO (Otimização Binária Quadrática Irrestrita)** — formulação via `dimod.BinaryQuadraticModel`, pronta para quantum annealers D-Wave
- **D-Wave Ocean SDK** — `neal.SimulatedAnnealingSampler` como solver clássico do ecossistema D-Wave; upgrade para `DWaveSampler()` sem mudança de código
- **Simulated Annealing** — solver builtin em Python puro como fallback zero-dependências
- **Distância Haversine** — roteamento geolocalizado na região do Porto, Portugal
- **Kyber768 / Dilithium3** — padrões NIST de PQC simulados via AES-256+SHA3
- **Metas CO₂ da UE 2030** — rastreamento de redução de 55% vs linha de base de 1990
- **Porto Taxi Dataset** — GPS real de 442 táxis, validado em papers de VRP

## Configuração

Edite `config/settings.py` para ajustar:
- Tamanho da frota e capacidade dos veículos
- Parâmetros do solver SA (varreduras, faixa de temperatura, amostras)
- Fatores de emissão de CO₂
- Algoritmo PQC e rotação de chaves
- Fonte de dados: `USE_REAL_DATA = True/False`

## Estrutura de Arquivos

```
hubstry-logistics-quantum/
├── run_mvp.py              # Ponto de entrada (--dwave / --builtin)
├── README.md               # Este arquivo
├── LICENSE                  # CC BY-NC-SA 4.0
├── .gitignore              # Exclusões Python
├── requirements-dwave.txt   # D-Wave Ocean SDK (opcional)
├── data/
│   ├── porto_taxi_sample.csv  # 30 coordenadas GPS reais do Porto
│   └── __init__.py
├── config/
│   ├── settings.py         # Todos os parâmetros configuráveis
│   └── __init__.py
├── iot_layer/
│   ├── iot_bridge.py       # Telemetria de frota (CSV real + fallback simulado)
│   └── __init__.py
├── core_layer/
│   ├── quantum_optimizer.py    # QUBO VRP solver (D-Wave neal + builtin SA)
│   ├── sustainability_calc.py  # KPIs de emissão de CO₂
│   └── __init__.py
├── security_layer/
│   ├── pqc_wrapper.py      # Simulação Kyber768/Dilithium3
│   ├── security_bridge.py  # Criptografa rotas, assina relatórios
│   └── __init__.py
└── simulation/
    ├── simulate_fleet.py   # Orquestrador completo do pipeline
    └── __init__.py
```

## Roadmap

- [x] MVP: pipeline IoT → QUBO → CO₂ → PQC
- [x] Integração com dataset GPS real (Porto Taxi Trajectory)
- [x] Integração D-Wave Ocean SDK (dimod BQM + neal sampler)
- [ ] Conexão ao QPU real D-Wave Advantage via Leap
- [ ] Dashboard Streamlit com visualização de rotas em tempo real
- [ ] Ingestão de dados ao vivo de frota (MQTT / REST API)
- [ ] Formulação VRP multi-depósito
- [ ] Solver híbrido QAOA + heurísticas
- [ ] Deploy em produção com monitoramento

---

**Founder & Owner:** Guilherme Gonçalves Machado
**Licença:** CC BY-NC-SA 4.0 — Hubstry DeepTech
