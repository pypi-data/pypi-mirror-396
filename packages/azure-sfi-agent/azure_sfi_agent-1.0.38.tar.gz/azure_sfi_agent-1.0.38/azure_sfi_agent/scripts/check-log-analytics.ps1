Param(
    [Parameter(Mandatory=$true)] [string]$ResourceGroupName
)
$ErrorActionPreference = "Stop"

$workspaces = az monitor log-analytics workspace list --resource-group $ResourceGroupName --output json | ConvertFrom-Json

if ($workspaces.Count -gt 0) {
    if ($workspaces.Count -eq 1) {
        Write-Output "LOG ANALYTICS WORKSPACE FOUND: $($workspaces[0].name)"
    } else {
        Write-Output "MULTIPLE LOG ANALYTICS WORKSPACES FOUND"
    }
} else {
    Write-Output "LOG ANALYTICS WORKSPACE NOT FOUND. Creating..."
    $wsName = "$ResourceGroupName-law"
    az monitor log-analytics workspace create --resource-group $ResourceGroupName --workspace-name $wsName --location "eastus" --output none
    Write-Output "Workspace '$wsName' created."
}