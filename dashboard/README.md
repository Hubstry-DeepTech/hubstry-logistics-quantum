# Hubstry DeepTech — Dashboard

Dashboard interativo para o Quantum-Ready Sustainable Logistics MVP (TRL 4 -> 5).

## Arquivos

| Arquivo | Descricao |
|---------|-----------|
| `dashboard.py` | Aplicacao Streamlit principal |
| `requirements.txt` | Dependencias com version pinning |
| `data/benchmark_results.json` | Dados do benchmark v0.3.0 (hardcoded demo) |
| `README.md` | Este arquivo |

## Requisitos

- Python 3.9+
- Windows / macOS / Linux
- Navegador moderno (Chrome, Firefox, Edge)

## Instalacao e Execucao

### Windows (PowerShell)

```powershell
# A partir da raiz do repositorio
python -m pip install -r dashboard\requirements.txt --quiet
python -m streamlit run dashboard\dashboard.py
```

### Linux / macOS

```bash
# A partir da raiz do repositorio
python -m pip install -r dashboard/requirements.txt --quiet
streamlit run dashboard/dashboard.py
```

Ou execute o script:
```powershell
.\run_dashboard.ps1
```

## Funcionalidades

- **4 modos de visualizacao** isomorfos ao artigo Zenodo:
  - **Operacional**: CO2, veiculos, conformidade EU 2030
  - **Tecnico**: BQM variables, tempo de execucao, gap analysis
  - **Investidor**: TRL progress, competitive moat, projecao de escala
  - **Governo**: Metricas auditaveis, reprodutibilidade, export
- **Mapa interativo** (folium) com rotas coloridas por solver
- **Graficos interativos** (plotly) — distancia, tempo, gap, CO2
- **Projecao de escala** com disclaimer metodologico
- **Export** JSON e CSV auditaveis
- **Re-execucao** do benchmark via botao (condicional)
- **Badges** TRL 4->5 e PQC (Kyber768/Dilithium3)
- **Timestamp** visivel para reprodutibilidade cientifica

## Dados

O dashboard carrega dados de `data/benchmark_results.json`. Se o arquivo nao existir
ou estiver corrompido, utiliza dados de fallback embutidos (benchmark v0.3.0).

Para gerar dados frescos, execute `benchmark.py` na raiz do repositorio e copie
o `benchmark_results.json` gerado para `dashboard/data/`.

## Licenca

CC BY-NC-SA 4.0 — Hubstry DeepTech
