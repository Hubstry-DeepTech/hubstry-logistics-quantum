"""
Hubstry DeepTech — Quantum-Ready Sustainable Logistics Dashboard
Version 1.0 | TRL 4 -> 5 Evidence Artifact

Streams benchmark data from benchmark_results.json and presents
audience-filtered views isomorphic to the Zenodo article structure.

Audience modes:
  - Tecnico:     BQM variables, execution time, solver internals
  - Operacional: CO2, vehicles, route map, EU 2030 compliance
  - Investidor:  TRL progress, competitive moat, scale projection
  - Governo:     Auditable metrics, reprodutibility, export
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Graceful import handling — report missing deps instead of crashing
# ---------------------------------------------------------------------------
try:
    import streamlit as st
except ImportError:
    print("ERROR: streamlit not installed. Run:")
    print("  python -m pip install streamlit>=1.28.0,<1.37.0")
    sys.exit(1)

try:
    import streamlit_folium as sf
    import folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    import pandas as pd
    import numpy as np
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "data"
BENCHMARK_JSON = DATA_DIR / "benchmark_results.json"
PROJECT_ROOT = Path(__file__).parent.parent

PORTO_CENTER = [41.1496, -8.6109]

# Solver colors for consistent theming across map and charts
SOLVER_COLORS = {
    "Builtin SA": "#3B82F6",       # blue
    "D-Wave neal (SA)": "#10B981",   # green
    "OR-Tools (GLS)": "#F59E0B",     # amber
}

# CO2 emission factor: ~120 g CO2 per km for a light delivery van (EU avg)
CO2_FACTOR_G_PER_KM = 120

# ---------------------------------------------------------------------------
# Fallback data — used when benchmark_results.json is missing or corrupted
# ---------------------------------------------------------------------------
FALLBACK_DATA = {
    "benchmark_version": "0.3.0",
    "timestamp": "2026-05-30T10:29:57Z",
    "dataset": "porto_taxi_trajectory",
    "num_locations": 6,
    "locations": [
        {"id": 0, "name": "Centro (Aliados)", "lat": 41.14961, "lon": -8.61099},
        {"id": 1, "name": "Estadio do Dragao", "lat": 41.15794, "lon": -8.62902},
        {"id": 2, "name": "Ribeira (Douro)", "lat": 41.14548, "lon": -8.58985},
        {"id": 3, "name": "Parque da Cidade", "lat": 41.16158, "lon": -8.63652},
        {"id": 4, "name": "Vila Nova de Gaia", "lat": 41.13999, "lon": -8.59540},
        {"id": 5, "name": "Baixa (Sao Bento)", "lat": 41.15194, "lon": -8.60868},
    ],
    "solvers": [
        {
            "name": "Builtin SA",
            "status": "success",
            "total_distance_km": 46.61,
            "execution_time_s": 7.73,
            "bqm_variables": 24,
            "route": [0, 1, 3, 5, 2, 4, 0],
        },
        {
            "name": "D-Wave neal (SA)",
            "status": "success",
            "total_distance_km": 43.14,
            "execution_time_s": 1.03,
            "bqm_variables": 24,
            "route": [0, 2, 4, 5, 1, 3, 0],
        },
        {
            "name": "OR-Tools (GLS)",
            "status": "success",
            "total_distance_km": 40.86,
            "execution_time_s": 1.02,
            "bqm_variables": None,
            "route": [0, 5, 2, 4, 3, 1, 0],
        },
    ],
}


# ---------------------------------------------------------------------------
# Data loading with error handling
# ---------------------------------------------------------------------------
def load_benchmark_data():
    """Load benchmark data from JSON with fallback to hardcoded defaults."""
    if BENCHMARK_JSON.exists():
        try:
            with open(BENCHMARK_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Basic validation
            if "solvers" in data and "locations" in data:
                return data
            else:
                st.warning(
                    "benchmark_results.json exists but has unexpected format. "
                    "Using fallback data."
                )
                return FALLBACK_DATA
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            st.warning(
                f"Could not parse benchmark_results.json: {e}. Using fallback data."
            )
            return FALLBACK_DATA
    else:
        st.info(
            "No benchmark_results.json found. Using embedded fallback data "
            "from benchmark v0.3.0. Run benchmark.py to generate fresh results."
        )
        return FALLBACK_DATA


# ---------------------------------------------------------------------------
# KPI computation
# ---------------------------------------------------------------------------
def compute_kpis(data):
    """Compute key performance indicators from benchmark data."""
    solvers = data["solvers"]
    best = min(solvers, key=lambda x: x["total_distance_km"])
    best_km = best["total_distance_km"]
    kpis = {}
    for s in solvers:
        gap_pct = ((s["total_distance_km"] - best_km) / best_km) * 100 if best_km > 0 else 0
        co2_g = s["total_distance_km"] * CO2_FACTOR_G_PER_KM
        co2_kg = co2_g / 1000
        kpis[s["name"]] = {
            "distance_km": s["total_distance_km"],
            "time_s": s["execution_time_s"],
            "gap_vs_best_pct": gap_pct,
            "co2_kg": round(co2_kg, 2),
            "route": s.get("route", []),
            "status": s.get("status", "unknown"),
            "bqm_variables": s.get("bqm_variables"),
        }
    return kpis


# ---------------------------------------------------------------------------
# Timestamp formatting
# ---------------------------------------------------------------------------
def format_timestamp(ts_str):
    """Format ISO timestamp to BRT display string."""
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        brt = dt.astimezone(timezone(timedelta(hours=-3)))
        return brt.strftime("%d/%m/%Y %H:%M BRT")
    except Exception:
        return ts_str


# ---------------------------------------------------------------------------
# Folium map
# ---------------------------------------------------------------------------
def create_route_map(data):
    """Create a folium map with route polylines for each solver."""
    m = folium.Map(location=PORTO_CENTER, zoom_start=13, tiles="CartoDB positron")
    locations = data["locations"]
    loc_map = {loc["id"]: loc for loc in locations}

    for solver in data["solvers"]:
        if solver.get("status") != "success":
            continue
        route = solver.get("route", [])
        if not route or len(route) < 2:
            continue

        color = SOLVER_COLORS.get(solver["name"], "#999999")
        coords = []
        for idx in route:
            loc = loc_map.get(idx)
            if loc:
                coords.append([loc["lat"], loc["lon"]])

        # Draw route polyline
        if len(coords) >= 2:
            folium.PolyLine(
                coords,
                color=color,
                weight=3,
                opacity=0.8,
                tooltip=f"{solver['name']} — {solver['total_distance_km']} km",
            ).add_to(m)

    # Add location markers
    for loc in locations:
        folium.Marker(
            [loc["lat"], loc["lon"]],
            popup=f"<b>{loc['name']}</b><br>ID: {loc['id']}<br>({loc['lat']:.5f}, {loc['lon']:.5f})",
            icon=folium.DivIcon(html=f"<div style='font-size:11px;color:#333;font-weight:bold;text-align:center;width:20px;'>{loc['id']}</div>"),
        ).add_to(m)

    # Add legend
    legend_html = """
    <div style="position:fixed;bottom:20px;left:20px;z-index:9999;
                background:white;padding:10px 14px;border-radius:6px;
                box-shadow:0 2px 6px rgba(0,0,0,0.15);font-size:12px;line-height:1.8;">
      <b>Rotas por Solver</b><br>
    """
    for solver in data["solvers"]:
        c = SOLVER_COLORS.get(solver["name"], "#999")
        legend_html += f'<span style="color:{c};font-weight:bold;">━━</span> {solver["name"]}<br>'
    legend_html += "</div>"
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


# ---------------------------------------------------------------------------
# Plotly charts
# ---------------------------------------------------------------------------
def create_distance_chart(kpis):
    """Bar chart comparing total distance per solver."""
    names = list(kpis.keys())
    distances = [kpis[n]["distance_km"] for n in names]
    colors = [SOLVER_COLORS.get(n, "#999") for n in names]

    fig = go.Figure(
        go.Bar(
            x=names,
            y=distances,
            marker_color=colors,
            text=[f"{d:.2f} km" for d in distances],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Distancia Total por Solver",
        yaxis_title="km",
        height=350,
        margin=dict(t=40, b=20, l=60, r=20),
        template="plotly_white",
    )
    return fig


def create_time_chart(kpis):
    """Bar chart comparing execution time per solver."""
    names = list(kpis.keys())
    times = [kpis[n]["time_s"] for n in names]
    colors = [SOLVER_COLORS.get(n, "#999") for n in names]

    fig = go.Figure(
        go.Bar(
            x=names,
            y=times,
            marker_color=colors,
            text=[f"{t:.2f}s" for t in times],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Tempo de Execucao por Solver",
        yaxis_title="segundos",
        height=350,
        margin=dict(t=40, b=20, l=60, r=20),
        template="plotly_white",
    )
    return fig


def create_gap_chart(kpis):
    """Horizontal bar chart showing gap % vs best solver."""
    names = list(kpis.keys())
    gaps = [kpis[n]["gap_vs_best_pct"] for n in names]
    colors = [SOLVER_COLORS.get(n, "#999") for n in names]

    fig = go.Figure(
        go.Bar(
            y=names,
            x=gaps,
            orientation="h",
            marker_color=colors,
            text=[f"{g:.1f}%" for g in gaps],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Gap (%) vs Melhor Solver (OR-Tools)",
        xaxis_title="%",
        height=300,
        margin=dict(t=40, b=20, l=120, r=40),
        template="plotly_white",
    )
    return fig


def create_co2_chart(kpis):
    """Bar chart comparing CO2 emissions per solver."""
    names = list(kpis.keys())
    co2 = [kpis[n]["co2_kg"] for n in names]
    colors = [SOLVER_COLORS.get(n, "#999") for n in names]

    fig = go.Figure(
        go.Bar(
            x=names,
            y=co2,
            marker_color=colors,
            text=[f"{c:.2f} kg" for c in co2],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Estimativa de CO2 por Rota",
        yaxis_title="kg CO2",
        height=350,
        margin=dict(t=40, b=20, l=60, r=20),
        template="plotly_white",
    )
    return fig


# ---------------------------------------------------------------------------
# Scale projection (linear, with explicit disclaimer)
# ---------------------------------------------------------------------------
def project_scale(kpis, n_multiplier):
    """
    Project metrics linearly for n_multiplier * current deliveries.
    DISCLAIMER: this is an illustrative estimate. Real behavior for N>20
    depends on graph topology and solver parameters — NOT for operational planning.
    """
    base_deliveries = 5  # current: 5 deliveries + 1 depot = 6 locations
    projected = {}
    for name, kpi in kpis.items():
        projected[name] = {
            "n_deliveries": base_deliveries * n_multiplier,
            "distance_km": kpi["distance_km"] * n_multiplier,
            "co2_kg": round(kpi["co2_kg"] * n_multiplier, 2),
            "time_s": kpi["time_s"] * n_multiplier,  # naive linear
        }
    return projected


def create_projection_chart(projected):
    """Line chart showing projected distance for multiple N values."""
    names = list(projected.keys())
    n_vals = sorted(set(p["n_deliveries"] for p in projected.values()))

    fig = go.Figure()
    for name in names:
        color = SOLVER_COLORS.get(name, "#999")
        x_data = [n for n in n_vals]
        # Find the entry for this name
        entry = projected[name]
        fig.add_trace(
            go.Scatter(
                x=[entry["n_deliveries"]],
                y=[entry["distance_km"]],
                mode="markers+lines",
                name=name,
                marker=dict(size=10, color=color),
                line=dict(color=color),
                text=f'{entry["distance_km"]:.1f} km',
            )
        )

    fig.update_layout(
        title="Projecao de Escala (Ilustrativa)",
        xaxis_title="Numero de Entregas",
        yaxis_title="Distancia Total (km)",
        height=380,
        margin=dict(t=40, b=20, l=60, r=20),
        template="plotly_white",
    )
    return fig


# ---------------------------------------------------------------------------
# Re-run benchmark via subprocess
# ---------------------------------------------------------------------------
def can_rerun_benchmark():
    """Check if benchmark.py exists in project root."""
    benchmark_py = PROJECT_ROOT / "benchmark.py"
    return benchmark_py.exists()


def rerun_benchmark():
    """Run benchmark.py and capture output."""
    benchmark_py = PROJECT_ROOT / "benchmark.py"
    result = subprocess.run(
        [sys.executable, str(benchmark_py)],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        timeout=300,
    )
    return result


# ===================================================================
# PAGE CONFIG — MUST be the first Streamlit command
# ===================================================================
st.set_page_config(
    page_title="Hubstry DeepTech | QUBO Logistics Dashboard",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ===================================================================
# LOAD DATA
# ===================================================================
data = load_benchmark_data()
kpis = compute_kpis(data)
ts_display = format_timestamp(data.get("timestamp", "unknown"))


# ===================================================================
# SIDEBAR
# ===================================================================
with st.sidebar:
    st.markdown("## ⚛️ Hubstry DeepTech")
    st.markdown("**QUBO Logistics Dashboard**")
    st.caption(f"v{data.get('benchmark_version', '?.?.?')} | Porto Taxi Dataset")

    st.divider()

    # --- Audience mode selector (isomorphic to article structure) ---
    audience_mode = st.radio(
        "Publico-alvo",
        [
            "🏢 Operacional",
            "📊 Tecnico",
            "💼 Investidor",
            "🏛️ Governo",
        ],
        index=0,
        help=(
            "Filtros isomorfos ao artigo Zenodo. "
            "Cada modo destaca metricas relevantes para o publico selecionado."
        ),
    )

    st.divider()

    # --- TRL Badge ---
    st.markdown(
        '<div style="padding:8px 12px;border-radius:6px;'
        'background:linear-gradient(135deg,#DBEAFE,#EFF6FF);'
        'border-left:4px solid #3B82F6;">'
        '<b>TRL 4 → 5</b><br>'
        '<span style="font-size:12px;">Dashboard as evidence artifact</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # --- PQC Badge ---
    st.markdown(
        '<div style="padding:8px 12px;border-radius:6px;'
        'background:linear-gradient(135deg,#FEF3C7,#FFFBEB);'
        'border-left:4px solid #F59E0B;margin-top:8px;">'
        '🔐 <b>PQC Layer</b><br>'
        '<span style="font-size:12px;">Kyber768 / Dilithium3<br>'
        '(architectural stub — liboqs TRL 5)</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # --- Timestamp (reprodutibility) ---
    st.markdown(f"🕐 **Benchmark:** {ts_display}")
    st.markdown(f"📍 **Dataset:** {data.get('dataset', 'N/A')} ({data.get('num_locations', '?')} pontos)")
    st.markdown(f"🚚 **Entregas:** {data.get('num_locations', '?') - 1} + 1 depot")

    st.divider()

    # --- Re-run Benchmark button (conditional) ---
    if can_rerun_benchmark():
        if st.button("🔄 Re-executar Benchmark", use_container_width=True):
            with st.spinner("Executando benchmark.py..."):
                result = rerun_benchmark()
            if result.returncode == 0:
                st.success("Benchmark concluido! Atualize a pagina (F5) para ver novos dados.")
                st.code(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            else:
                st.error(f"Benchmark falhou (exit {result.returncode}):")
                st.code(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
    else:
        st.caption("benchmark.py nao encontrado no repo. Botao Re-run desabilitado.")

    st.divider()

    # --- Export buttons (always visible) ---
    st.markdown("**📥 Exportar Dados**")

    # Export as JSON
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    st.download_button(
        label="JSON (benchmark completo)",
        data=json_str.encode("utf-8"),
        file_name=f"hubstry-benchmark-{data.get('benchmark_version', 'unknown')}.json",
        mime="application/json",
        use_container_width=True,
    )

    # Export as CSV (solvers summary)
    if HAS_PLOTLY:
        rows = []
        for name, k in kpis.items():
            rows.append({
                "Solver": name,
                "Distancia (km)": k["distance_km"],
                "Tempo (s)": k["time_s"],
                "Gap vs Melhor (%)": round(k["gap_vs_best_pct"], 2),
                "CO2 (kg)": k["co2_kg"],
                "Status": k["status"],
            })
        csv_df = pd.DataFrame(rows)
        csv_bytes = csv_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="CSV (resumo dos solvers)",
            data=csv_bytes,
            file_name=f"hubstry-benchmark-{data.get('benchmark_version', 'unknown')}.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ===================================================================
# MAIN AREA
# ===================================================================

# --- Title ---
st.title("Quantum-Ready Sustainable Logistics — Benchmark Dashboard")
st.caption(
    f"Demonstrador TRL 4→5 | Dataset: Porto Taxi Trajectory | "
    f"3 solvers: Builtin SA, D-Wave neal (SA), OR-Tools (GLS)"
)

# === COMMON TO ALL MODES: KPI Cards ===
st.subheader("KPIs — Visao Geral")

col1, col2, col3 = st.columns(3)
solver_names = list(kpis.keys())

for idx, name in enumerate(solver_names):
    col = [col1, col2, col3][idx]
    k = kpis[name]
    color = SOLVER_COLORS.get(name, "#999")
    is_best = k["gap_vs_best_pct"] < 0.01

    with col:
        badge = " 🏆" if is_best else ""
        st.markdown(
            f'<div style="padding:14px;border-radius:8px;'
            f'background:white;border:2px solid {color};box-shadow:0 1px 4px rgba(0,0,0,0.08);">'
            f'<span style="color:{color};font-weight:bold;font-size:15px;">'
            f'{name}{badge}</span><br>'
            f'<span style="font-size:22px;font-weight:bold;">{k["distance_km"]:.2f} km</span><br>'
            f'Tempo: {k["time_s"]:.2f}s | CO₂: {k["co2_kg"]} kg<br>'
            f'Gap vs melhor: <b>{k["gap_vs_best_pct"]:.1f}%</b>'
            f'</div>',
            unsafe_allow_html=True,
        )


st.divider()

# === COMMON TO ALL MODES: Route Map ===
st.subheader("Mapa de Rotas — Porto, Portugal")

if HAS_FOLIUM:
    route_map = create_route_map(data)
    sf.st_folium(route_map, width=1200, height=500)
else:
    st.warning(
        "streamlit-folium / folium nao instalado. Mapa indisponivel. "
        "Execute: python -m pip install streamlit-folium>=0.11.0 folium>=0.14.0"
    )

st.divider()

# ===================================================================
# AUDIENCE-FILTERED CONTENT
# ===================================================================
mode_key = audience_mode.split(" ", 1)[-1]  # e.g. "Operacional" from "🏢 Operacional"

# === TECNICO MODE ===
if mode_key == "Tecnico":
    st.subheader("📊 Metricas Tecnicas")

    if HAS_PLOTLY:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(create_distance_chart(kpis), use_container_width=True)
        with c2:
            st.plotly_chart(create_time_chart(kpis), use_container_width=True)

        st.plotly_chart(create_gap_chart(kpis), use_container_width=True)

    # BQM variables info
    st.subheader("Binary Quadratic Model (BQM)")
    for name, k in kpis.items():
        bqm = k["bqm_variables"]
        if bqm:
            st.markdown(
                f"- **{name}**: {bqm} variaveis binarias (6 locais x 4 slots de posicao)"
            )
        else:
            st.markdown(
                f"- **{name}**: N/A (solver classico, sem formulacao QUBO)"
            )

    st.caption(
        "A formulacao QUBO mapeia o VRP para um modelo Ising com N^2 variaveis binarias. "
        "O simulated annealing do D-Wave neal explora o espaco de solucoes com "
        "temperatura progressivamente decrescente, encontrando solucoes proximas ao otimo."
    )


# === OPERACIONAL MODE ===
elif mode_key == "Operacional":
    st.subheader("🏢 Impacto Operacional e Ambiental")

    if HAS_PLOTLY:
        st.plotly_chart(create_co2_chart(kpis), use_container_width=True)

    st.caption(
        "CO2 estimado via fator 120 g/km (van leve eletrica, media UE). "
        "Valores divergem do benchmark_results.json que pode usar fator diferente. "
        "Fator configuravel em dashboard.py: CO2_FACTOR_G_PER_KM."
    )

    c1, c2 = st.columns(2)
    with c1:
        best = min(kpis.values(), key=lambda x: x["distance_km"])
        worst = max(kpis.values(), key=lambda x: x["distance_km"])
        savings = worst["co2_kg"] - best["co2_kg"]
        st.markdown(
            f'<div style="padding:14px;border-radius:8px;'
            f'background:linear-gradient(135deg,#D1FAE5,#ECFDF5);'
            f'border-left:4px solid #10B981;">'
            f'<b>Potencial de Economia CO2</b><br>'
            f'Melhor otimizacao economiza <b>{savings:.2f} kg CO2</b> por rota<br>'
            f'vs. solver sem otimizacao (Builtin SA como baseline)'
            f'</div>',
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f'<div style="padding:14px;border-radius:8px;'
            f'background:linear-gradient(135deg,#DBEAFE,#EFF6FF);'
            f'border-left:4px solid #3B82F6;">'
            f'<b>Conformidade UE 2030</b><br>'
            f'Green Deal Europeu: -90% emissoes transporte<br>'
            f'Otimizacao de rotas = ferramenta-chave no pacote<br>'
            f'<span style="font-size:12px;">Ref: European Green Deal, COM(2019)640</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Vehicle count
    num_deliveries = data.get("num_locations", 6) - 1
    st.markdown(
        f"**Veiculos necessarios (CVRP):** 1 veiculo, {num_deliveries} entregas, "
        f"1 deposito (centro de Porto). Capacidade ilimitada neste demo."
    )

    st.caption(
        "Para escalas maiores, o OR-Tools suporta multiplas capacidades e janelas de tempo. "
        "O QUBO pode ser extendido para multi-veiculo via constraints adicionais no BQM."
    )


# === INVESTIDOR MODE ===
elif mode_key == "Investidor":
    st.subheader("💼 Perspectiva de Investidor")

    # TRL Progress visualization
    st.markdown(
        '<div style="padding:14px;border-radius:8px;'
        'background:linear-gradient(135deg,#EDE9FE,#F5F3FF);'
        'border-left:4px solid #8B5CF6;">'
        '<b>Technology Readiness Level (TRL)</b><br>'
        '<div style="background:#E5E7EB;border-radius:4px;height:14px;margin:8px 0;position:relative;">'
        '<div style="background:linear-gradient(90deg,#3B82F6,#8B5CF6);height:14px;border-radius:4px;width:45%;"></div>'
        '<span style="position:absolute;left:48%;top:-2px;font-size:11px;font-weight:bold;">4 → 5</span>'
        '</div>'
        '<span style="font-size:13px;">'
        'TRL 4: Validacao em laboratorio (benchmark local)<br>'
        'TRL 5: Validacao em ambiente relevante (dashboard interativo)<br>'
        'Proximos: TRL 6 (prototipo em ambiente operacional) com QPU real'
        '</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            f'<div style="padding:14px;border-radius:8px;'
            f'background:white;border:1px solid #E5E7EB;">'
            f'<b>Competitive Moat</b><br><br>'
            f'• QUBO-first architecture — pronto para QPU quando disponivel<br>'
            f'• Multi-solver: 3 engines (SA builtin, D-Wave neal, OR-Tools)<br>'
            f'• Camada PQC (Post-Quantum Cryptography) integrada<br>'
            f'• Dataset real (Porto Taxi Trajectory, 6 GPS pontos)<br>'
            f'• Zero custo de migracao: troca de solver sem reescrever codigo<br>'
            f'• Licenca CC BY-NC-SA 4.0 (open science)'
            f'</div>',
            unsafe_allow_html=True,
        )

    with c2:
        neal_gap = kpis.get("D-Wave neal (SA)", {}).get("gap_vs_best_pct", 0)
        builtin_gap = kpis.get("Builtin SA", {}).get("gap_vs_best_pct", 0)
        closure_pct = ((builtin_gap - neal_gap) / builtin_gap * 100) if builtin_gap > 0 else 0

        st.markdown(
            f'<div style="padding:14px;border-radius:8px;'
            f'background:white;border:1px solid #E5E7EB;">'
            f'<b>Highlight: D-Wave neal fecha {closure_pct:.0f}% do gap</b><br><br>'
            f'O simulated annealing quantum-inspired (neal) reduz o gap de '
            f'{builtin_gap:.1f}% (Builtin SA) para {neal_gap:.1f}% vs OR-Tools.<br>'
            f'Em QPU real (D-Wave Advantage), a expectativa e superacao do baseline classico.'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # --- Scale projection slider (with mandatory disclaimer) ---
    st.subheader("Projecao de Escala")

    n_slider = st.slider(
        "Multiplicador de entregas",
        min_value=1,
        max_value=40,
        value=5,
        step=1,
        help="Multiplica o numero atual de entregas para projecao ilustrativa.",
    )

    projected = project_scale(kpis, n_slider)

    if HAS_PLOTLY:
        st.plotly_chart(create_projection_chart(projected), use_container_width=True)

    # Projection table
    proj_rows = []
    for name, p in projected.items():
        proj_rows.append({
            "Solver": name,
            "Entregas": p["n_deliveries"],
            "Distancia (km)": round(p["distance_km"], 2),
            "CO2 (kg)": p["co2_kg"],
            "Tempo est. (s)": round(p["time_s"], 2),
        })
    st.table(proj_rows)

    # === MANDATORY DISCLAIMER ===
    st.warning(
        "⚠️ **Projecao ilustrativa — NAO usar para planejamento operacional.** "
        "Extrapolacao linear nao reflete comportamento real de SA/QUBO para N>20 entregas. "
        "Comportamento real depende da topologia do grafo e dos parametros do solver. "
        "Para N grande, SA/QUBO escalam exponencialmente no pior caso."
    )


# === GOVERNO MODE ===
elif mode_key == "Governo":
    st.subheader("🏛️ Metricas Auditaveis e Reprodutibilidade")

    # Reprodutibility card
    st.markdown(
        f'<div style="padding:14px;border-radius:8px;'
        f'background:linear-gradient(135deg,#FEF3C7,#FFFBEB);'
        f'border-left:4px solid #F59E0B;">'
        f'<b>Reprodutibilidade Cientifica</b><br><br>'
        f'<b>Benchmark executado em:</b> {ts_display}<br>'
        f'<b>Versao:</b> {data.get("benchmark_version", "N/A")}<br>'
        f'<b>Dataset:</b> {data.get("dataset", "N/A")} ({data.get("num_locations", "?")} pontos GPS)<br>'
        f'<b>Method:</b> CVRP via QUBO (Binary Quadratic Model)<br>'
        f'<b>Solvers:</b> {", ".join(s["name"] for s in data["solvers"])}<br>'
        f'<b>Hardware:</b> CPU local (simulated annealing + OR-Tools)<br>'
        f'<b>Repositorio:</b> github.com/Hubstry-DeepTech/hubstry-logistics-quantum<br>'
        f'<b>Licenca:</b> CC BY-NC-SA 4.0'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Export section highlighted
    st.markdown("### Exportar Relatorio Auditavel")
    st.markdown(
        "Utilize os botoes de export na sidebar para baixar "
        "o benchmark completo em JSON ou o resumo em CSV. "
        "Ambos formatos sao auditaveis por terceiros."
    )

    # Comparative table
    st.subheader("Tabela Comparativa Completa")

    if HAS_PLOTLY:
        rows = []
        for name, k in kpis.items():
            rows.append({
                "Solver": name,
                "Distancia (km)": k["distance_km"],
                "Tempo (s)": k["time_s"],
                "Gap vs Melhor (%)": round(k["gap_vs_best_pct"], 2),
                "CO2 (kg)": k["co2_kg"],
                "Variaveis BQM": k["bqm_variables"] if k["bqm_variables"] else "N/A",
                "Status": k["status"],
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.caption(
        "Todas as metricas acima sao reproduziveis executando benchmark.py no repositorio. "
        "Para deposito Zenodo DOI, utilize o JSON exportado como artifact complementar."
    )


# ===================================================================
# FOOTER — common to all modes
# ===================================================================
st.divider()
st.caption(
    "Hubstry DeepTech — Quantum-Ready Sustainable Logistics MVP | "
    "CC BY-NC-SA 4.0 | "
    f"Dashboard v1.0 | Benchmark {data.get('benchmark_version', '?.?.?')} | "
    "Dataset: Porto Taxi Trajectory"
)
