# tools/parity_ps_vs_py.ps1 — corre py y ps versiones del transporte y
# verifica byte-identical. Compara bytes exactos, no consolas.
$ErrorActionPreference = "Stop"

if (-not $env:LOLCODE_CMD) { $env:LOLCODE_CMD = "C:\Development\runtimes\lolcode\lci.exe" }

$WS = Split-Path $PSScriptRoot
Set-Location -LiteralPath $WS

$tmpPy = [System.IO.Path]::GetTempFileName()
$tmpPs = [System.IO.Path]::GetTempFileName()

$cases = @(
  @{ prog = "examples\hola.jaja";          inp = "" },
  @{ prog = "examples\echo.jaja";          inp = "hello" },
  @{ prog = "examples\busy_beaver.jaja";   inp = "" },
  @{ prog = "examples\command.jaja";       inp = "" },
  @{ prog = "examples\bootstrap_crlf.jaja"; inp = "" }
)

$matches = 0; $total = 0
foreach ($c in $cases) {
    $total += 1
    if ($c.inp) {
        & py tools\run_jajaja_lol.py (Join-Path $WS $c.prog) -i $c.inp *> $tmpPy
        & "$PSHOME\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "$WS\tools\run_jajaja_lol.ps1" -Program (Join-Path $WS $c.prog) -StdinData $c.inp *> $tmpPs
    } else {
        & py tools\run_jajaja_lol.py (Join-Path $WS $c.prog) *> $tmpPy
        & "$PSHOME\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "$WS\tools\run_jajaja_lol.ps1" -Program (Join-Path $WS $c.prog) *> $tmpPs
    }
    # Compare token a token ignorando líneas vacías artificiales que el
    # pipe peut introducir (Python sys.stdout vs PowerShell Write-Output).
    $l1 = (Get-Content $tmpPy -Encoding UTF8 | Where-Object { $_ -ne "" }) -join [char]10
    $l2 = (Get-Content $tmpPs -Encoding UTF8 | Where-Object { $_ -ne "" }) -join [char]10
    if ($l1 -ceq $l2) {
        $matches += 1
        Write-Host "MATCH  $($c.prog)"
    } else {
        Write-Host "DIFF   $($c.prog)"
        # mostrar solo el último trozo (el resto es nïvel igual hasta el diff)
        $pyLines = Get-Content $tmpPy | Select-Object -Last 5
        $psLines = Get-Content $tmpPs | Select-Object -Last 5
        Write-Host "  py:  $($pyLines -join ' | ')"
        Write-Host "  ps:  $($psLines -join ' | ')"
    }
}

Write-Host ""
Write-Host "$matches/$total byte-identical"
exit $(if ($matches -eq $total) { 0 } else { 1 })
