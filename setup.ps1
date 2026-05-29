 $base = "https://my-project-download.superz.ai/download/logistics-quantum-mvp"
 $files = @(
  "simulation/simulate_fleet.py",
  "security_layer/pqc_wrapper.py",
  "security_layer/security_bridge.py",
  "core_layer/quantum_optimizer.py",
  "core_layer/sustainability_calc.py",
  "iot_layer/iot_bridge.py",
  "config/settings.py",
  "run_mvp.py",
  "README.md"
)
foreach ($f in $files) {
  $dir = Split-Path $f -Parent
  if ($dir -and !(Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
  Write-Host "Downloading $f ..." -NoNewline
  try {
    Invoke-WebRequest -Uri "$base/$f" -OutFile $f -ErrorAction Stop
    Write-Host " OK" -ForegroundColor Green
  } catch {
    Write-Host " FAIL" -ForegroundColor Red
  }
}
Write-Host "`nDone! Now run: python run_mvp.py" -ForegroundColor Cyan
