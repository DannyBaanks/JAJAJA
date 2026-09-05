# tests/zero_python_check.ps1 — "que ya no salga Python".
#
# Gate: falla si hay .py tracked NO incluido en la whitelist (los restantes
# son ORÁCULOS/EVIDENCIA; no son la superficie activa).
#
# Exit 0 => OK.  Exit 1 => violaciones.

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repo = Split-Path $PSScriptRoot
Set-Location -LiteralPath $repo

# Lista EXPLÍCITA de .py que permanecen permitidos. Usan ruta con "/" como
# separador (estilo git) para que el matching sea canónico.
$WHITELIST_PY = @(
    "jajaja_interpreter.py",
    "jajaja_stdlib.py",
    "host.py",
    "ui_ir.py",
    "check_bootstrap.py",
    "run_examples.py",
    "demo_lolcode.py",
    "test_jajaja.py",
    "test_host.py",
    "test_lolcode_emit.py",
    "test_lolcode_native.py",
    "test_backend_lolcode.py",
    "proofs/conformance_ieo.py",
    "proofs/ja_encoding.py",
    "proofs/tm_to_jajaja.py",
    "backends/lolcode/__init__.py",
    "backends/lolcode/adapter.py",
    "backends/lolcode/emit.py",
    "backends/__init__.py",
    "evidence/lolcode_flip/collect_stats.py",
    "tools/build_lol.py",
    "tools/run_jajaja_lol.py",
    "tools/parity_check.py",
    "tools/turing_parity_lol.py",
    "tools/compare_tm_compile.py",
    "tools/compare_ja_compile.py",
    "tools/compare_ja_run.py",
    "tools/make_snapshots.py"
)

$violations = New-Object System.Collections.Generic.List[string]

$tracked = git ls-files "*.py"
foreach ($f in $tracked) {
    if ($WHITELIST_PY -notcontains $f) {
        $violations.Add("tracked .py fuera de la whitelist: $f")
    }
}

# ningún script activo (.ps1 del flujo) puede invocar py/python3/python
$activePs = @(
    "tools\build_lol.ps1",
    "tools\run_jajaja_lol.ps1",
    "tests\verify_snapshots.ps1"
)
foreach ($p in $activePs) {
    $fpath = Join-Path $repo $p
    if (-not (Test-Path $fpath)) { $violations.Add("script activo no existe: $p"); continue }
    $lines = Get-Content $fpath -Encoding UTF8
    $li = 0
    foreach ($ln in $lines) {
        $li++
        if ($ln.Trim().StartsWith("#")) { continue }
        if ($ln -match '(?<![\w\-])(python|python3|py(?=\s|\b))(?!\w)') {
            $violations.Add("$p linea $li invoca python/py: $($ln.Trim())")
        }
    }
}

if ($violations.Count) {
    Write-Host "ZERO_PYTHON_CHECK: VIOLATIONS"
    foreach ($v in $violations) { Write-Host "  - $v" }
    exit 1
}
Write-Host "ZERO_PYTHON_CHECK: OK"
exit 0
