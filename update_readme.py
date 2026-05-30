"""
README Updater — Dashboard Sprint
Executar na raiz do repositorio:
  python update_readme.py

Faz 4 edicoes cirurgicas sem destruir conteudo existente.
"""

import sys
from pathlib import Path

README_PATH = Path(__file__).parent / "README.md"

def main():
    print("Atualizando README.md — 4 edicoes cirurgicas...")

    content = README_PATH.read_text(encoding="utf-8")
    changes = 0

    # === EDIT 1: Badge TRL 4 -> 4 to 5 ===
    old1 = '<img src="https://img.shields.io/badge/TRL-4-yellow" alt="TRL 4">'
    new1 = '<img src="https://img.shields.io/badge/TRL-4_to_5-yellow" alt="TRL 4 to 5">'
    if old1 in content:
        content = content.replace(old1, new1)
        changes += 1
        print("  [1/4] Badge TRL atualizado")
    else:
        print("  [1/4] Badge TRL ja atualizado ou nao encontrado")

    # === EDIT 2: Add Dashboard section before Architecture ===
    dashboard_section = """## Dashboard Interativo / Interactive Dashboard

Dashboard Streamlit com visualizacao de rotas em mapa interativo, graficos comparativos
e metricas auditaveis — evidencia visual de TRL 4->5.

Streamlit dashboard with interactive route map, comparative charts, and auditable
metrics — visual evidence of TRL 4->5 progression.

**4 modos de visualizacao / 4 viewing modes** (isomorfos ao artigo Zenodo):

| Modo / Mode | Publico-alvo / Audience | Conteudo / Content |
|---|---|---|
| Operacional | Operacoes / Operations | CO2, veiculos, conformidade EU 2030 |
| Tecnico | Engenharia / Engineering | BQM variables, tempo de execucao, gap analysis |
| Investidor | C-level / Investors | TRL progress, competitive moat, projecao de escala |
| Governo | Governo / Government | Metricas auditaveis, reprodutibilidade, export |

**Instalacao / Installation:**
```bash
python -m pip install -r dashboard/requirements.txt
```

**Execucao / Run:**
```powershell
# Windows
.\\run_dashboard.ps1

# Linux / macOS
streamlit run dashboard/dashboard.py
```

O dashboard abre automaticamente no navegador em `http://localhost:8501`.

---

"""

    arch_marker = "## Arquitetura / Architecture"
    if "## Dashboard Interativo" not in content and arch_marker in content:
        content = content.replace(arch_marker, dashboard_section + arch_marker)
        changes += 1
        print("  [2/4] Secao Dashboard adicionada")
    else:
        print("  [2/4] Secao Dashboard ja existe ou marcador nao encontrado")

    # === EDIT 3: Add dashboard to File Structure ===
    old_tree_line = "    simulation/"
    new_tree_block = """    dashboard/
    |   dashboard.py           # Streamlit dashboard v1.0
    |   requirements.txt       # Dependencias com version pinning
    |   README.md              # Documentacao do dashboard
    |   data/
    |       benchmark_results.json  # Dados do benchmark v0.3.0
    run_dashboard.ps1          # Launcher PowerShell
    simulation/"""

    if "dashboard.py" not in content and old_tree_line in content:
        content = content.replace(old_tree_line, new_tree_block)
        changes += 1
        print("  [3/4] Dashboard adicionado a estrutura de arquivos")
    else:
        print("  [3/4] Dashboard ja esta na estrutura de arquivos")

    # === EDIT 4: Roadmap — check off Dashboard ===
    old4 = "- [ ] Dashboard Streamlit com visualizacao de rotas / Route visualization dashboard"
    new4 = "- [x] Dashboard Streamlit com visualizacao de rotas / Route visualization dashboard (TRL 4->5)"
    if old4 in content:
        content = content.replace(old4, new4)
        changes += 1
        print("  [4/4] Roadmap atualizado — Dashboard marcado como concluido")
    else:
        print("  [4/4] Roadmap ja atualizado ou item nao encontrado")

    # Write back
    README_PATH.write_text(content, encoding="utf-8")

    print()
    print(f"README.md atualizado — {changes} edicoes aplicadas.")
    print("Conteudo pre-existente preservado integralmente.")

if __name__ == "__main__":
    main()
