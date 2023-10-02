if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole("Administrators")) {
    Start-Process powershell.exe "-File `"$PSCommandPath`" -NoNewWindow -Wait" -WorkingDirectory $PSScriptRoot -Verb RunAs;
    exit;
}

Get-ScheduledTask | Where-Object TaskPath -eq "\Microsoft\Windows\DMMGamePlayerFastLauncher\" | Unregister-ScheduledTask -Confirm:$false
$schtasks = Join-Path -Path (Split-Path -Path ($PSScriptRoot) -Parent) -ChildPath "data\schtasks"
Get-ChildItem -Path $schtasks | ForEach-Object { schtasks.exe /create /xml $_.FullName /tn "\Microsoft\Windows\DMMGamePlayerFastLauncher\$($_.Name -replace '\.xml$')" }
Read-Host -Prompt "Press Enter to exit"