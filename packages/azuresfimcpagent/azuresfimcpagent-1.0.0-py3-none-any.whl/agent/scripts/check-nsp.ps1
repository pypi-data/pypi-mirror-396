Param(
    [Parameter(Mandatory=$true)] [string]$ResourceGroupName
)
$ErrorActionPreference = "Stop"

# Use basic AZ CLI JSON output to avoid module dependencies
$nspList = az resource list --resource-group $ResourceGroupName --resource-type "Microsoft.Network/networkSecurityPerimeters" --output json | ConvertFrom-Json

if ($nspList.Count -gt 0) {
    Write-Output "NSP FOUND: $($nspList[0].name)"
} else {
    Write-Output "NSP NOT FOUND. Creating..."
    # Quick creation of NSP if missing
    $nspName = "$ResourceGroupName-nsp"
    az resource create --resource-group $ResourceGroupName --name $nspName --resource-type "Microsoft.Network/networkSecurityPerimeters" --location "eastus" --properties "{}" --output none
    Write-Output "NSP '$nspName' created."
}