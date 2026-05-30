# -*- coding: utf-8 -*-
"""
Add Dashboard screenshots to README.md
Executar na raiz do repositorio: python add_screenshots.py

Creates docs/screenshots/ folder and adds image references in the Dashboard section.
"""

import shutil
from pathlib import Path

README_PATH = Path(__file__).parent / "README.md"
SCREENSHOTS_DIR = Path(__file__).parent / "docs" / "screenshots"

def main():
    # Create screenshots directory
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Pasta criada: {SCREENSHOTS_DIR}")

    # Copy screenshots (they should be in the same folder as this script)
    script_dir = Path(__file__).parent
    screenshots = [
        ("dashboard-operacional.png", "Dashboard - Modo Operacional"),
        ("dashboard-tecnico.png", "Dashboard - Modo Tecnico"),
        ("dashboard-investidor.png", "Dashboard - Modo Investidor"),
        ("dashboard-governo.png", "Dashboard - Modo Governo"),
    ]

    for filename, description in screenshots:
        src = script_dir / filename
        if src.exists():
            shutil.copy2(src, SCREENSHOTS_DIR / filename)
            print(f"  Copied: {filename}")
        else:
            print(f"  NOT FOUND: {filename} (coloque os prints na raiz do repo)")

    # Add screenshots to README
    content = README_PATH.read_text(encoding="utf-8")

    screenshots_md = """

<p align="center">
  <img src="docs/screenshots/dashboard-operacional.png" alt="Dashboard - Modo Operacional" width="800">
</p>
<p align="center">
  <em>Modo Operacional: Impacto ambiental e conformidade EU 2030</em>
</p>

<p align="center">
  <img src="docs/screenshots/dashboard-tecnico.png" alt="Dashboard - Modo Tecnico" width="800">
</p>
<p align="center">
  <em>Modo Tecnico: Metricas de execucao e analise de gap</em>
</p>

<p align="center">
  <img src="docs/screenshots/dashboard-investidor.png" alt="Dashboard - Modo Investidor" width="800">
</p>
<p align="center">
  <em>Modo Investidor: TRL progress, moat competitivo e projecao de escala</em>
</p>

<p align="center">
  <img src="docs/screenshots/dashboard-governo.png" alt="Dashboard - Modo Governo" width="800">
</p>
<p align="center">
  <em>Modo Governo: Metricas auditaveis e reprodutibilidade cientifica</em>
</p>

"""

    # Insert after "O dashboard abre automaticamente no navegador em" line
    marker = "O dashboard abre automaticamente no navegador em `http://localhost:8501`."
    if marker in content and "docs/screenshots/dashboard-operacional.png" not in content:
        content = content.replace(marker, marker + screenshots_md)
        README_PATH.write_text(content, encoding="utf-8")
        print("\nScreenshots adicionados ao README.md!")
    elif "docs/screenshots/dashboard-operacional.png" in content:
        print("\nScreenshots ja existem no README.md.")
    else:
        print("\nMarcador nao encontrado no README.")


if __name__ == "__main__":
    main()
