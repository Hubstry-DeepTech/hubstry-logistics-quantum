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
- Uma demonstração funcional usando Simulated Annealing (estilo D-Wave `neal`) como solver clássico

**O que NÃO somos (ainda):**
- Uma alegação de vantagem quântica. O solver atual é SA clássico — produz resultados corretos e otimizados, mas sem speedup quântico
- Um benchmark contra hardware quântico. A integração com hardware é o próximo passo planejado
- Um sistema de gestão de frotas em produção. Este é um MVP validado que demonstra a arquitetura de integração

A proposta de valor é o **pipeline** — não o solver. Quando o hardware quântico amadurecer além das limitações da era NISQ, esta mesma formulação QUBO roda em qubits reais com zero alterações arquiteturais.

### Aviso de Propriedade Intelectual

Este repositório contém **trabalho original proprietário** de Guilherme Gonçalves
Machado / Hubstry DeepTech. Todo o código-fonte, projetos arquiteturais,
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

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    run_mvp.py (Entry Point)             │
├──────────┬──────────────────┬────────────────────────────┤
│ IoT Layer │    Core Layer    │     Security Layer         │
│          │                  │                            │
│ iot_     │ quantum_         │ pqc_wrapper.py             │
│ bridge.py│ optimizer.py     │   (Kyber768 / Dilithium3   │
│          │                  │    simulado via AES+SHA3)  │
│ GPS,      │ QUBO-VRP        │                            │
│ velocid., │ Simulated        │ security_bridge.py         │
│ carga     │ Annealing        │   (criptografa rotas,      │
│           │                  │    assina relatórios)      │
├──────────┴──────────────────┼────────────────────────────┤
│ config/settings.py           │ sustainability_calc.py    │
│   (frota, solver, amb.       │   (KPIs de CO₂, meta EU  │
│    parâmetros)                │    2030)                   │
└─────────────────────────────────────────────────────────┘
```

## Início Rápido

```bash
# Sem dependências externas — apenas Python 3.8+ (stdlib)
python run_mvp.py
```

**Resultado esperado:**
```
  Hubstry Quantum Logistics MVP v0.1.0

  Pipeline concluído em ~1-3 segundos
  Etapas: iot_telemetry → qubo_optimize → sustainability_calc → security_sign

  Solver QUBO (Simulated Annealing):
    Distância total:  ~69 km
    Veículos usados:    2

  Métricas de Sustentabilidade:
    CO₂ economizado:    ~12 kg
    Redução:            ~35%
    Progresso EU 2030:  ~65% (meta: 55%)
```

## Repositórios Integrados

| Repositório | Papel no MVP | Status |
|---|---|---|
| **iot-protocol-hubstry** | Simulação de telemetria — GPS, velocidade, carga, combustível | Conceitos integrados |
| **gurudev-core** | Formulação QUBO e solver SA para VRP | Conceitos integrados |
| **hubstry-security** | Criptografia PQC (Kyber768/Dilithium3) com fallback AES | Conceitos integrados |

> Nota: Os três repositórios originais são projetos proprietários independentes.
> Este MVP reimplementa seus conceitos centrais em um pipeline unificado sem dependências.

## Tecnologias Principais

- **QUBO (Otimização Binária Quadrática Irrestrita)** — mapeia VRP para forma
  resolvível em quantum annealers (D-Wave) e fallbacks clássicos
- **Simulated Annealing** — solver clássico do pacote D-Wave `neal`,
  reimplementado em Python puro para MVP sem dependências
- **Distância Haversine** — roteamento geolocalizado na região metropolitana de Munique
- **Kyber768 / Dilithium3** — padrões NIST de PQC simulados via AES-256+SHA3
- **Metas CO₂ da UE 2030** — rastreamento de redução de 55% vs linha de base de 1990

## Configuração

Edite `config/settings.py` para ajustar:
- Tamanho da frota e capacidade dos veículos
- Parâmetros do solver SA (varreduras, faixa de temperatura, amostras)
- Fatores de emissão de CO₂
- Algoritmo PQC e rotação de chaves

## Estrutura de Arquivos

```
hubstry-logistics-quantum/
├── run_mvp.py              # Ponto de entrada — execute este
├── README.md               # Este arquivo
├── LICENSE                  # CC BY-NC-SA 4.0
├── .gitignore              # Exclusões Python
├── config/
│   ├── settings.py         # Todos os parâmetros configuráveis
│   └── __init__.py
├── iot_layer/
│   ├── iot_bridge.py       # Simulação de telemetria de frota
│   └── __init__.py
├── core_layer/
│   ├── quantum_optimizer.py    # Solver QUBO-VRP (SA)
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
- [ ] Integração com hardware real D-Wave (QPU sampler)
- [ ] Dashboard Streamlit com visualização de rotas em tempo real
- [ ] Ingestão de dados reais de frota (MQTT / REST API)
- [ ] Formulação VRP multi-depósito
- [ ] Solver híbrido QAOA + heurísticas
- [ ] Deploy em produção com monitoramento

---

**Founder & Owner:** Guilherme Gonçalves Machado
**Licença:** CC BY-NC-SA 4.0 — Hubstry DeepTech
