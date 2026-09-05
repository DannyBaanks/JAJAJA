# tests/verify_snapshots.ps1 — corre cada ejemplo via tools/run_jajaja_lol.ps1
# y valida el (output, steps, status) contra tests/snapshots.json.
#
# Requiere LOLCODE_CMD apuntando a lci. No toca Python.
# Devuelve 0 si todos los casos coinciden. (Los SKIP no inflan el conteo MATCH.)
param(
    [string]$LciCmd
)

$ErrorActionPreference = "Stop"

if ($LciCmd) { $env:LOLCODE_CMD = $LciCmd }
if (-not $env:LOLCODE_CMD) { throw "LOLCODE_CMD no definido" }

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Split-Path -Parent $here
$runScript = Join-Path $repo "tools\run_jajaja_lol.ps1"

$data = Get-Content (Join-Path $here "snapshots.json") -Raw -Encoding UTF8 | ConvertFrom-Json

$failures = 0
$total = 0
$script:skipped = 0
foreach ($case in $data.cases) {
    $total += 1
    $name = $case.name
    $stdin = $case.stdin
    $ms = $case.max_steps

    # usar path del snapshot (preciso) con fallback a convenciones
    if ($case.path) { $progPath = Join-Path $repo $case.path }
    else {
        $cand1 = Join-Path $repo "examples\$name"
        $cand2 = Join-Path $repo $name
        $progPath = $null
        if (Test-Path $cand1) { $progPath = $cand1 }
        elseif (Test-Path $cand2) { $progPath = $cand2 }
    }
    if (-not (Test-Path $progPath)) {
        $script:skipped += 1
        Write-Host "SKIP   $name ($progPath no existe)"
        continue
    }

    $argsPy = @(
        "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", $runScript,
        "-Program", $progPath,
        "-MaxSteps", $ms
    )
    if ($stdin) { $argsPy += @("-StdinData", $stdin) }

    $lines = & "$PSHOME\powershell.exe" @argsPy 2>$null
    if ($LASTEXITCODE -ne 0 -and $null -eq $lines) { $lines = @() }

    # última línea = status=... steps=...
    $lines = @($lines | ForEach-Object { "$_" })
    $statusLine = ($lines | Where-Object { $_ -like "status=*" } | Select-Object -Last 1)
    if (-not $statusLine) {
        Write-Host "FAIL   $name (sin status line)"
        $failures += 1
        continue
    }
    if ($statusLine -notmatch "^status=(\S+) steps=(\d+)$") {
        Write-Host "FAIL   $name (status line inválida: $statusLine)"
        $failures += 1
        continue
    }
    $gotStatus = $Matches[1]
    $gotSteps = [int]$Matches[2]
    $gotOutput = (($lines[0..($lines.Count-2)] -join "`n")).TrimEnd("`n")
    $wantOutput = ($case.output).TrimEnd("`n")

    $okOut = ($gotOutput -ceq $wantOutput)

    $wantStatus = $case.status
    $wantSteps = [int]$case.steps

    if ($gotStatus -eq $wantStatus -and $gotSteps -eq $wantSteps -and $okOut) {
        Write-Host "MATCH  $name"
    } else {
        Write-Host "DIFF   $name (got status=$gotStatus steps=$gotSteps out_len=$($gotOutput.Length); want status=$wantStatus steps=$wantSteps out_len=$($case.output.Length))"
        $failures += 1
    }
}
Write-Host ""
Write-Host "$($total - $failures - $script:skipped)/$total snapshots MATCH, $script:skipped SKIP"
exit $(if ($failures -eq 0) { 0 } else { 1 })
