# tests/verify_sin_python.ps1 — corre el pipeline completo en un hijo PowerShell
# cuyo PATH ha sido limpiado de cualquier interpretación de Python.
# Si algo falla, ZERO_PYTHON = NOT_DEMONSTRATED.

$ErrorActionPreference = "Stop"

$repo = Split-Path $PSScriptRoot
$lci = $env:LOLCODE_CMD
if (-not $lci) {
    Write-Host "ERROR: define LOLCODE_CMD con la ruta a lci.exe (runtime LOLCODE externo)"
    exit 2
}

# Cleanup PATH: filtrar cualquier directorio que mentione "python", "py" launcher o similar
$limpia = ($env:PATH -split ";" | Where-Object {
    $p = $_.ToLower()
    ($p -notmatch "python") -and ($p -notmatch "\\py(?=\w)?\\?" -or $p -match "py\.exe$") -and ($p -notmatch "\\apps\\python") -and ($p -notmatch "^c:\\python")
}) -join ";"

Write-Host "=== JAJAJA zero-python check ==="
Write-Host "PATH limpiado (se muestran las trayectorias que quedaron):"
($limpia -split ";" | Select-Object -First 10) | ForEach-Object { "  $_" }
Write-Host "  ..."
Write-Host ""

$jobs = @(
    @{ name = "BUILD";   script = "tools\build_lol.ps1 jajaja.cfg" },
    @{ name = "SNAPSHOTS"; script = "tests\verify_snapshots.ps1" },
    @{ name = "ZERO_PYTHON_GATE"; script = "tests\zero_python_check.ps1" }
)

$failed = 0
foreach ($j in $jobs) {
    Write-Host "--- $($j.name) ---"
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "powershell.exe"
    $psi.Arguments = "-NoProfile -ExecutionPolicy Bypass -Command `"`$env:PATH='$($limpia -replace "'", "''")'; `$env:LOLCODE_CMD='$lci'; Set-Location '$repo'; $($j.script); exit `$LASTEXITCODE`""
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $p = [System.Diagnostics.Process]::Start($psi)
    $out = $p.StandardOutput.ReadToEnd()
    $err = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    Write-Host ($out.TrimEnd())
    if ($err.Trim()) { Write-Host "# stderr: $($err.Trim())" }
    if ($p.ExitCode -ne 0) {
        Write-Host "FAIL exit=$($p.ExitCode)"
        $failed++
    } else {
        Write-Host "OK"
    }
    Write-Host ""
}

if ($failed -gt 0) { Write-Host ">>> ZERO_PYTHON = NOT_DEMONSTRATED"; exit 1 }
Write-Host ">>> ZERO_PYTHON = DEMONSTRATED para: BUILD, SNAPSHOTS, GATE"
exit 0
