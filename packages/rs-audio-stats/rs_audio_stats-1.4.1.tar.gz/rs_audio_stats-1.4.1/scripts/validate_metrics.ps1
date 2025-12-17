param(
  [Parameter(Mandatory=$true)][string]$InputDir,
  [string]$ExePath = "$PSScriptRoot/../rs_audio_stats_v1.2.0_windows_x64.exe",
  [string]$TmpDir = "$PSScriptRoot/../tmp_validation",
  [double]$Tolerance = 0.1
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Ensure-Dir([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) { [void](New-Item -ItemType Directory -Path $Path) }
}

function Get-ExtendedFile([string]$InPath, [string]$WorkDir) {
  $dur = & ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 -- "$InPath" 2>$null
  if (-not [double]::TryParse($dur, [ref]([double]$null))) { return $InPath }
  $d = [double]$dur
  if ($d -ge 15.0) { return $InPath }
  $out = Join-Path $WorkDir ("loop15_" + [IO.Path]::GetFileName($InPath))
  if (-not (Test-Path -LiteralPath $out)) {
    # Loop input to 15s, re-encode to PCM WAV for stability
    & ffmpeg -y -v error -stream_loop 1000 -i "$InPath" -t 15 -acodec pcm_s16le -ar 48000 -- "$out" | Out-Null
  }
  return $out
}

function Parse-Bs1770Gain([string[]]$Lines) {
  $res = @{}
  foreach ($ln in $Lines) {
    if ($ln -match 'I\s*[:=]\s*(-?\d+(?:\.\d+)?)\s*LUFS') { $res.I = [double]$matches[1] }
    if ($ln -match 'LRA\s*[:=]\s*(\d+(?:\.\d+)?)\s*LU\b') { $res.LRA = [double]$matches[1] }
    if ($ln -match '\bS(?:hort)?\b.*?:\s*(-?\d+(?:\.\d+)?)\s*LUFS') { $res.Smax = [double]$matches[1] }
    if ($ln -match '\bM(?:omentary)?\b.*?:\s*(-?\d+(?:\.\d+)?)\s*LUFS') { $res.Mmax = [double]$matches[1] }
    if ($ln -match '(?:TP|True\s*Peak|Peak)\s*[:=]\s*(-?\d+(?:\.\d+)?)\s*dB(?:TP|FS)') { $res.TP = [double]$matches[1] }
  }
  return $res
}

function Parse-AStats([string[]]$Lines) {
  $res = @{}
  foreach ($ln in $Lines) {
    if ($ln -match 'Overall\s+RMS\s+level\s+dB\s*:?\s*(-?\d+(?:\.\d+)?)') { $res.RMSavg = [double]$matches[1] }
    if ($ln -match 'Overall\s+RMS\s+peak\s+dB\s*:?\s*(-?\d+(?:\.\d+)?)') { $res.RMSmax = [double]$matches[1] }
    if ($ln -match 'Overall\s+RMS\s+trough\s+dB\s*:?\s*(-?\d+(?:\.\d+)?)') { $res.RMSmin = [double]$matches[1] }
    if ($ln -match 'Overall\s+peak\s+level\s+dB\s*:?\s*(-?\d+(?:\.\d+)?)') { $res.SamplePeak = [double]$matches[1] }
  }
  return $res
}

function Read-LastJson([string]$Path) {
  # JSONL: take last non-empty line
  $line = Get-Content -LiteralPath $Path | Where-Object { $_.Trim() -ne '' } | Select-Object -Last 1
  if (-not $line) { return $null }
  return $line | ConvertFrom-Json
}

function Diff([string]$name, [double]$a, [double]$b, [double]$tol) {
  if ($a -is [double] -and $b -is [double]) {
    $err = [math]::Abs($a - $b)
    return [PSCustomObject]@{ Name=$name; A=$a; B=$b; Err=$err; Pass=($err -le $tol) }
  } else {
    return [PSCustomObject]@{ Name=$name; A=$a; B=$b; Err=$null; Pass=$false }
  }
}

if (-not (Test-Path -LiteralPath $InputDir)) { throw "InputDir not found: $InputDir" }
Ensure-Dir $TmpDir

# Enumerate WAVs (non-recursive to avoid junctions causing access denied)
$wavFiles = Get-ChildItem -LiteralPath $InputDir -Filter *.wav | Select-Object -ExpandProperty FullName
if (-not $wavFiles) { throw "No WAV files found in $InputDir" }

$summary = @()

foreach ($wav in $wavFiles) {
  Write-Host "Processing: $wav" -ForegroundColor Cyan
  $work = Join-Path $TmpDir ([IO.Path]::GetFileNameWithoutExtension($wav))
  Ensure-Dir $work
  $ext = Get-ExtendedFile -InPath $wav -WorkDir $work

  # Our tool JSON
  $ourJson = Join-Path $work 'our.json'
  & $ExePath -i -s -m -l -tp -sp -rt -rm -ra -json $ourJson -- "$ext" | Out-Null
  $our = Read-LastJson $ourJson
  if (-not $our) { Write-Warning "Our JSON missing for $wav"; continue }

  # bs1770gain (stdout)
  $bsOut = & bs1770gain -- "$ext" 2>&1
  $bs = Parse-Bs1770Gain $bsOut

  # ffmpeg astats (stderr)
  $ffOut = & ffmpeg -v error -nostats -i "$ext" -af "astats=metadata=1:reset=0" -f null - 2>&1
  $ast = Parse-AStats $ffOut

  $rows = @()
  # Compare against bs1770gain
  $rows += Diff 'I (LUFS)' $our.integrated_loudness $bs.I $Tolerance
  $rows += Diff 'Smax (LUFS)' $our.short_term_loudness $bs.Smax $Tolerance
  $rows += Diff 'Mmax (LUFS)' $our.momentary_loudness $bs.Mmax $Tolerance
  $rows += Diff 'LRA (LU)' $our.loudness_range $bs.LRA $Tolerance
  $rows += Diff 'TP (dBFS)' $our.true_peak $bs.TP $Tolerance

  # Compare against FFmpeg (astats)
  $rows += Diff 'RMS avg (dB)' $our.rms_average $ast.RMSavg $Tolerance
  $rows += Diff 'RMS max (dB)' $our.rms_max $ast.RMSmax $Tolerance
  $rows += Diff 'RMS min (dB)' $our.rms_min $ast.RMSmin $Tolerance
  $rows += Diff 'Sample Peak (dBFS)' $our.sample_peak $ast.SamplePeak $Tolerance

  $fail = $rows | Where-Object { -not $_.Pass }
  $summary += [PSCustomObject]@{
    File = $wav
    Passed = ($fail.Count -eq 0)
    Fails = ($fail | Select-Object Name, A, B, Err)
  }

  $rows | Format-Table -AutoSize | Out-String | Write-Host
}

Write-Host "\n===== SUMMARY =====" -ForegroundColor Yellow
$total = $summary.Count
$passed = ($summary | Where-Object Passed).Count
$failed = $total - $passed
Write-Host ("Total: {0}  Passed: {1}  Failed: {2}" -f $total, $passed, $failed)
if ($failed -gt 0) {
  Write-Host "Failed files:" -ForegroundColor Red
  foreach ($s in $summary | Where-Object { -not $_.Passed }) {
    Write-Host "- $($s.File)" -ForegroundColor Red
    $s.Fails | Format-Table -AutoSize | Out-String | Write-Host
  }
}
