# -*- coding: utf-8 -*-
"""
Fix accents in Dashboard section of README.md
Executar na raiz do repositorio: python fix_readme_accents.py
"""

import re
from pathlib import Path

README_PATH = Path(__file__).parent / "README.md"

def main():
    content = README_PATH.read_text(encoding="utf-8")

    # Map of unaccented -> accented replacements (targeted for Dashboard section only)
    replacements = {
        "visualizacao de rotas em mapa interativo, graficos comparativos": 
        "visualiza\u00e7\u00e3o de rotas em mapa interativo, gr\u00e1ficos comparativos",
        "e metricas auditaveis": "e m\u00e9tricas audit\u00e1veis",
        "evidencia visual": "evid\u00eancia visual",
        "4 modos de visualizacao": "4 modos de visualiza\u00e7\u00e3o",
        "Publico-alvo": "P\u00fablico-alvo",
        "Conteudo / Content": "Conte\u00fado / Content",
        "Operacoes / Operations": "Opera\u00e7\u00f5es / Operations",
        "veiculos, conformidade": "ve\u00edculos, conformidade",
        "tempo de execucao, gap": "tempo de execu\u00e7\u00e3o, gap",
        "projecao de escala": "proje\u00e7\u00e3o de escala",
        "Metricas auditaveis": "M\u00e9tricas audit\u00e1veis",
        "Instalacao / Installation": "Instala\u00e7\u00e3o / Installation",
        "Execucao / Run": "Execu\u00e7\u00e3o / Run",
    }

    # Find Dashboard section boundaries
    dash_start = content.find("## Dashboard Interativo")
    if dash_start == -1:
        print("Secao Dashboard nao encontrada.")
        return

    # Find next ## heading after dashboard section
    next_heading = content.find("\n## ", dash_start + 10)
    if next_heading == -1:
        next_heading = len(content)

    dash_section = content[dash_start:next_heading]

    # Apply replacements only within dashboard section
    new_dash_section = dash_section
    changes = 0
    for old, new in replacements.items():
        if old in new_dash_section:
            new_dash_section = new_dash_section.replace(old, new)
            changes += 1

    # Reconstruct full content
    content = content[:dash_start] + new_dash_section + content[next_heading:]
    README_PATH.write_text(content, encoding="utf-8")

    print(f"Acentos corrigidos: {changes} substituicoes aplicadas.")


if __name__ == "__main__":
    main()
