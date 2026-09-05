# tools/run_jajaja_lol.ps1 — corre un .jaja vía sin Python.
#
# Transporte frame-based idéntico a run_jajaja_lol.py:
#   input:  <<N>> por newline, <<T>> por tab, <<S1>> split source/stdin,
#           <<S2>> split stdin/max_steps, <<EOF>> end.
#   output: línea final "<|JAJAJA|status=X|steps=N|>"
#
# Uso:
#   .\tools\run_jajaja_lol.ps1 examples\hola.jaja
#   .\tools\run_jajaja_lol.ps1 examples\echo.jaja -Input "hello"
#   .\tools\run_jajaja_lol.ps1 program.jaja -MaxSteps 3
#
# Requiere LOLCODE_CMD apuntando al ejecutable lci, o lci en PATH.

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, Position=0)][string]$Program,
    [string]$StdinData = "",
    [int]$MaxSteps = 200000
)

$ErrorActionPreference = "Stop"

function Resolve-Lci {
    if ($env:LOLCODE_CMD -and (Test-Path $env:LOLCODE_CMD)) { return $env:LOLCODE_CMD }
    $p = Get-Command lci -ErrorAction SilentlyContinue
    if ($p) { return $p.Source }
    $p = Get-Command lci.exe -ErrorAction SilentlyContinue
    if ($p) { return $p.Source }
    throw "no external LOLCODE runtime (set LOLCODE_CMD or put lci on PATH)"
}

function Encode-Stream([string]$src, [string]$stdin_data, [int]$max_steps) {
    $out = New-Object System.Text.StringBuilder
    function EmitText([string]$s) {
        foreach ($c in $s.ToCharArray()) {
            if ($c -eq "`n") { [void]$out.Append("<<N>>`n") }
            elseif ($c -eq "`t") { [void]$out.Append("<<T>>`n") }
            else { [void]$out.Append($c).Append("`n") }
        }
    }
    EmitText($src)
    [void]$out.Append("<<N>>").Append("`n")
    [void]$out.Append("<<S1>>").Append("`n")
    EmitText($stdin_data)
    [void]$out.Append("<<S2>>").Append("`n")
    EmitText($max_steps.ToString())
    [void]$out.Append("<<EOF>>").Append("`n")
    return $out.ToString()
}

function Decode-Out([string]$stdout_text) {
    $framePrefix = "<|JAJAJA|status="
    $marker = "`n" + $framePrefix
    $cut = $stdout_text.LastIndexOf($marker)
    if ($cut -lt 0) { throw "frame not found in runtime stdout: $($stdout_text.Substring([Math]::Max(0,$stdout_text.Length-200)))" }
    $before = $stdout_text.Substring(0, $cut)
    $frame = $stdout_text.Substring($cut + 1).Split("`n")[0]
    if (-not $frame.StartsWith($framePrefix)) { throw "unparseable frame $frame" }
    $body = $frame.Substring($framePrefix.Length)
    $parts = $body -split [regex]::Escape("|steps="), 2
    $status = $parts[0]
    $stepsStr = ($parts[1] -split [regex]::Escape("|>"))[0]
    return @($before, [int]$stepsStr, $status)
}

$progItem = Resolve-Path -LiteralPath $Program -ErrorAction Stop
$progPath = $progItem.ProviderPath
# Paridad con Python: convertir CRLF -> LF (Python open() en modo texto hace
# esta normalización; [System.IO.File]::ReadAllText lo lee crudo).
$source = [System.IO.File]::ReadAllText($progPath, [System.Text.UTF8Encoding]::new($false)) -replace "`r`n", "`n"
$lci = Resolve-Lci
$stream = Encode-Stream $source $StdinData $MaxSteps

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $lci
$runtimePath = Join-Path (Split-Path (Split-Path $MyInvocation.MyCommand.Path -Parent) -Parent) 'src\jajaja.lol'
$psi.Arguments = "`"$runtimePath`""
$psi.UseShellExecute = $false
$psi.RedirectStandardInput = $true
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.StandardOutputEncoding = [System.Text.UTF8Encoding]::new($false)
$psi.StandardErrorEncoding = [System.Text.UTF8Encoding]::new($false)

$proc = [System.Diagnostics.Process]::Start($psi)
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$bytes = $utf8NoBom.GetBytes($stream)
$proc.StandardInput.BaseStream.Write($bytes, 0, $bytes.Length)
$proc.StandardInput.BaseStream.Flush()
$proc.StandardInput.Close()
$stdoutText = $proc.StandardOutput.ReadToEnd()
$stderrText = $proc.StandardError.ReadToEnd()
$proc.WaitForExit()

if ($proc.ExitCode -ne 0) {
    Write-Host "TRANSPORT_ERROR: lci exit=$($proc.ExitCode): $($stderrText.Trim())" -ForegroundColor Red
    exit 2
}

$res = Decode-Out $stdoutText
$output = $res[0]; $steps = $res[1]; $status = $res[2]

# Compone la respuesta y la saca por el stdout del script vía Write-Output
# (capturable por pipe/archivo).
$outputFinal = $output
if ($output.Length -and -not $output.EndsWith("`n")) { $outputFinal += "`n" }
$outputFinal += "status=$status steps=$steps"
Write-Output $outputFinal
exit ([int]($status -ne "HALTED"))
