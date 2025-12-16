Param(
    [Parameter(Mandatory=$true)] [string]$ResourceGroupName,
    [Parameter(Mandatory=$true)] [string]$WorkspaceId,
    [Parameter(Mandatory=$true)] [string]$ResourceId
)
$ErrorActionPreference = "Stop"

$diagName = "diag-" + ($ResourceId -split '/')[-1]
Write-Output "Creating diagnostic setting '$diagName'..."

# Create diagnostic setting for 'allLogs' and 'AllMetrics'
az monitor diagnostic-settings create `
    --name $diagName `
    --resource $ResourceId `
    --workspace $WorkspaceId `
    --logs '[{"categoryGroup":"allLogs","enabled":true}]' `
    --metrics '[{"category":"AllMetrics","enabled":true}]' `
    --output none 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Output "Diagnostic setting created."
} else {
    Write-Output "Diagnostic setting creation failed or not supported for this resource type."
}