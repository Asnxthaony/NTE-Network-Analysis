#Requires -Version 7.0

function Get-DeviceIdFromRegistry {
    try {
        $ndidHex = (Get-ItemProperty -Path "HKCU:\Software\PWRD\Pgp" -Name "ndid_v2").ndid_v2
    } catch {
        return $null
    }
    if (-not $ndidHex) { return $null }

    $encBytes = [System.Convert]::FromHexString($ndidHex)

    for ($i = 0; $i -lt $encBytes.Length; $i++) {
        $encBytes[$i] = (($encBytes[$i] -bxor 0xAB) - 1) -band 0xFF
    }

    # pwrdxou83579asfg
    $entropy = [Convert]::FromHexString("676673613937353338756F786472777000")

    $scopes = @(
        [Security.Cryptography.DataProtectionScope]::CurrentUser,
        [Security.Cryptography.DataProtectionScope]::LocalMachine
    )

    foreach ($scope in $scopes) {
        try {
            $plain = [Security.Cryptography.ProtectedData]::Unprotect($encBytes, $entropy, $scope)
            if ($null -eq $plain) { continue }

            if ($plain.Length -gt 0 -and $plain[-1] -eq 0) {
                $plain = [Text.Encoding]::UTF8.GetString($plain, 0, $plain.Length - 1)
            }

            return $plain
        }
        catch {}
    }

    return $null
}


$deviceId = Get-DeviceIdFromRegistry
if ($deviceId) {
    Write-Host "NDID (Registry)：$deviceId" -ForegroundColor Green
}

function Get-DeviceIdFromSystem {
    $diskSerial = (Get-CimInstance Win32_DiskDrive -Filter "DeviceID LIKE '%PHYSICALDRIVE0%'").SerialNumber
    $diskSerial = $diskSerial ? $diskSerial.Trim() : ""

    $cpuId = (Get-CimInstance Win32_Processor | Select-Object -First 1).ProcessorId
    $cpuId = $cpuId ? $cpuId.Trim() : ""

    $mac = (Get-CimInstance Win32_NetworkAdapterConfiguration | Where-Object IPEnabled -eq $true | Select-Object -First 1).MACAddress
    $mac = $mac ? ($mac -replace '[^0-9A-Fa-f]', '').ToLower() : '000000000000'

    $raw = "$cpuId$diskSerial"
    $hash = [Security.Cryptography.MD5]::HashData([Text.Encoding]::UTF8.GetBytes($raw))
    $hash = [Convert]::ToHexString($hash).ToLower()

    return "${hash}_${mac}"
}

$deviceId2 = Get-DeviceIdFromSystem
if ($deviceId2) {
    Write-Host "NDID (System)：$deviceId2" -ForegroundColor Green
}
