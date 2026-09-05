# tools/build_lol.ps1 — ensamblador de partes LOLCODE -> .lol final.
#
# Compliance: no toca Python. Solo PowerShell 5.1+ y archivos locales.
# Comportamiento idéntico a tools/build_lol.py para las cfg actuales.
#
# Uso:
#   .\tools\build_lol.ps1 jajaja.cfg        -> ensambla y escribe
#   .\tools\build_lol.ps1 -CheckAll         -> valida todas las cfg sin escribir
#
# Build determinista: mismas entradas -> mismo SHA-256. Ver hash en la salida.

param(
    [Parameter(Position=0)][string]$Cfg,
    [switch]$CheckAll
)

$ErrorActionPreference = "Stop"

$here   = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo   = Split-Path -Parent $here
$parts  = Join-Path $repo "src\parts"
$builds = Join-Path $repo "builds"

function Assemble {
    param([string]$CfgPath)

    $lines = Get-Content -LiteralPath $CfgPath -Encoding UTF8
    $names = @()
    $out_rel = $null
    foreach ($ln in $lines) {
        $t = $ln.Trim()
        if ($t -eq "" -or $t.StartsWith("#")) {
            if ($t.StartsWith("# out:")) {
                $out_rel = $t.Substring(6).Trim()
            }
            continue
        }
        $names += $t
    }
    if ($names.Count -eq 0) { throw "cfg vacía: $CfgPath" }

    $text = ""
    foreach ($name in $names) {
        $p = Join-Path $parts $name
        if (-not (Test-Path -LiteralPath $p)) { throw "parte no encontrada: $name" }
        $raw = Get-Content -LiteralPath $p -Raw -Encoding UTF8
        $text += $raw.TrimEnd() + "`n"
    }
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    $sha = [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
    $digest = -join ($sha | ForEach-Object { $_.ToString("x2") })

    if ($null -eq $out_rel) {
        $stem = [System.IO.Path]::GetFileNameWithoutExtension($CfgPath)
        $out_rel = "src\$stem.lol"
    }
    [PSCustomObject]@{
        Text   = $text
        Names  = $names
        Digest = $digest
        OutRel = $out_rel
    }
}

if ($CheckAll) {
    Get-ChildItem -Path $builds -Filter *.cfg | ForEach-Object {
        $r = Assemble -CfgPath $_.FullName
        $len = $r.Digest.Substring(0,16)
        Write-Host "$($_.Name): $($r.Names.Count) partes, sha256=$len..."
    }
    exit 0
}

if (-not $Cfg) {
    Write-Host "uso: .\tools\build_lol.ps1 <builds\cfg> [-CheckAll]"
    exit 2
}
$cfgPath = Join-Path $builds $Cfg
$r = Assemble -CfgPath $cfgPath
$out = Join-Path $repo $r.OutRel
New-Item -ItemType Directory -Force -Path (Split-Path $out) | Out-Null
[System.IO.File]::WriteAllText($out, $r.Text, [System.Text.UTF8Encoding]::new($false))
Write-Host "ensamblado: $out"
Write-Host "sha256: $($r.Digest)"
exit 0
