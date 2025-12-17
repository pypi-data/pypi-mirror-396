param (
    [string]$CargoExe = "./target/x86_64-pc-windows-gnu/release/rs_audio_stats.exe"
)

$wavFiles = Get-ChildItem -Path "./sample_voice" -Filter "*.wav"
if ($wavFiles.Count -eq 0) {
    Write-Host "No WAV files found in sample_voice/"
    exit 1
}

function Parse-Bs1770gain {
    param([string]$file)
    $output = & bs1770gain -f -i -s -m -l -sp -tp "$file" 2>&1
    $result = @{}
    foreach ($line in $output) {
        if ($line -match "Integrated loudness:\s+([-\d\.]+) LUFS") { $result["i"] = [double]$matches[1] }
        elseif ($line -match "Short-term max:\s+([-\d\.]+) LUFS") { $result["s"] = [double]$matches[1] }
        elseif ($line -match "Momentary max:\s+([-\d\.]+) LUFS") { $result["m"] = [double]$matches[1] }
        elseif ($line -match "Loudness range:\s+([-\d\.]+) LU") { $result["l"] = [double]$matches[1] }
        elseif ($line -match "Sample peak:\s+([-\d\.]+) dBFS") { $result["sp"] = [double]$matches[1] }
        elseif ($line -match "True peak:\s+([-\d\.]+) dBFS") { $result["tp"] = [double]$matches[1] }
    }
    return $result
}

function Parse-Ffmpeg {
    param([string]$file)
    $output = & ffmpeg -hide_banner -nostats -i "$file" -filter_complex "ebur128=metadata=1" -f null - 2>&1
    $result = @{}
    foreach ($line in $output) {
        if ($line -match "RMS level min:\s+([-\d\.]+) dB") { $result["rt"] = [double]$matches[1] }
        elseif ($line -match "RMS level max:\s+([-\d\.]+) dB") { $result["rm"] = [double]$matches[1] }
        elseif ($line -match "RMS level avg:\s+([-\d\.]+) dB") { $result["ra"] = [double]$matches[1] }
    }
    return $result
}

$threshold = 0.1

foreach ($wav in $wavFiles) {
    Write-Host "Testing file: $($wav.Name)"

    # run rust program
    $rustOut = & $CargoExe "$($wav.FullName)" 2>&1
    $rustVals = @{}
    foreach ($line in $rustOut) {
        if ($line -match "(-i|-s|-m|-l|-sp|-tp|-rt|-rm|-ra):\s+([-\d\.]+)") {
            $rustVals[$matches[1]] = [double]$matches[2]
        }
    }

    $bsVals = Parse-Bs1770gain $wav.FullName
    $ffVals = Parse-Ffmpeg $wav.FullName

    $allKeys = @("i","s","m","l","sp","tp","rt","rm","ra")
    foreach ($k in $allKeys) {
        if ($rustVals.ContainsKey("-$k")) {
            $rv = $rustVals["-$k"]
            $tv = $null
            if ($bsVals.ContainsKey($k)) { $tv = $bsVals[$k] }
            elseif ($ffVals.ContainsKey($k)) { $tv = $ffVals[$k] }
            if ($null -ne $tv) {
                $diff = [math]::Abs($rv - $tv)
                $status = if ($diff -le $threshold) { "OK" } else { "NG" }
                "{0,-15} {1,8} {2,8} {3,8} {4}" -f $k, $rv, $tv, $diff, $status
            }
        }
    }
    ""
}