# Hubstry DeepTech — Dashboard Launcher
# Execute este script a partir da RAIZ do repositorio
# Exemplo: .\run_dashboard.ps1

$ErrorActionPreference = "Stop"

$DASHBOARD_DIR = Join-Path $PSScriptRoot "dashboard"
$REQ_FILE = Join-Path $DASHBOARD_DIR "requirements.txt"
$DASHBOARD_PY = Join-Path $DASHBOARD_DIR "dashboard.py"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Hubstry DeepTech" -ForegroundColor Cyan
Write-Host "  QUBO Logistics Dashboard" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if files exist
if (-not (Test-Path $REQ_FILE)) {
    Write-Host "ERRO: requirements.txt nao encontrado em $REQ_FILE" -ForegroundColor Red
    Write-Host "Certifique-se de que a pasta 'dashboard' esta na raiz do repositorio." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $DASHBOARD_PY)) {
    Write-Host "ERRO: dashboard.py nao encontrado em $DASHBOARD_PY" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "[1/2] Instalando dependencias..." -ForegroundColor Yellow
python -m pip install -r $REQ_FILE --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Falha ao instalar dependencias." -ForegroundColor Red
    Write-Host "Tente manualmente: python -m pip install -r dashboard\requirements.txt" -ForegroundColor Yellow
    exit 1
}
Write-Host "  Dependencias instaladas com sucesso." -ForegroundColor Green

# Launch dashboard
Write-Host ""
Write-Host "[2/2] Lancando dashboard..." -ForegroundColor Yellow
Write-Host "  O navegador abrira automaticamente em http://localhost:8501" -ForegroundColor Gray
Write-Host "  Pressione Ctrl+C no terminal para parar." -ForegroundColor Gray
Write-Host ""

python -m streamlit run $DASHBOARD_PY
