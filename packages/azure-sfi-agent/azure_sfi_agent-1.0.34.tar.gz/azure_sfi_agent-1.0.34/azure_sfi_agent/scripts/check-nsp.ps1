Param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName
)

# Step 1: Get current subscription context using Azure CLI
Write-Host "Using current subscription context..." -ForegroundColor Cyan
$SubscriptionId = az account show --query id -o tsv
if (-not $SubscriptionId) {
    Write-Error "Not logged in to Azure CLI. Run 'az login'."
    exit 1
}
Write-Host "Subscription ID: $SubscriptionId" -ForegroundColor Gray

# Step 2: Get resource group details using Azure CLI
Write-Host "Fetching resource group details for '$ResourceGroupName'..." -ForegroundColor Cyan
$rgJson = az group show --name $ResourceGroupName --output json 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Resource group '$ResourceGroupName' not found." -ForegroundColor Red
    exit 1
}
$resourceGroup = $rgJson | ConvertFrom-Json
$location = $resourceGroup.location
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor Green
Write-Host "Location: $location" -ForegroundColor Green

# Step 3: Get the access token using Azure CLI
Write-Host "`nObtaining Azure access token..." -ForegroundColor Cyan
$token = az account get-access-token --query accessToken -o tsv

# Step 4: Check if NSP exists in the resource group
$nspName = "$ResourceGroupName-nsp"
$url = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Network/networkSecurityPerimeters?api-version=2023-07-01-preview"

$headers = @{
    Authorization = "Bearer $token"
    "Content-Type" = "application/json"
}

Write-Host "`nChecking for existing NSP in resource group '$ResourceGroupName'..." -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Method Get -Uri $url -Headers $headers -ErrorAction Stop
    
    if ($response.value.Count -gt 0) {
        # NSP exists
        $existingNSP = $response.value[0]
        $existingNSPName = $existingNSP.name
        Write-Host "NSP FOUND: '$existingNSPName'" -ForegroundColor Green
        Write-Host "`nNSP already exists in this resource group." -ForegroundColor Yellow
        Write-Host "Use attach-nsp.ps1 to attach resources to this NSP." -ForegroundColor Yellow
        
        # Return NSP details
        return @{
            Exists = $true
            NSPName = $existingNSPName
            ResourceGroup = $ResourceGroupName
            Location = $location
        }
    } else {
        # No NSP found
        Write-Host "NSP NOT FOUND in resource group '$ResourceGroupName'" -ForegroundColor Yellow
        Write-Host "`nCreating new NSP '$nspName'..." -ForegroundColor Cyan
        
        # Get the script directory
        $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
        $deployNSPScript = Join-Path $scriptDir "deploy-nsp.ps1"
        
        if (-Not (Test-Path $deployNSPScript)) {
            Write-Host "ERROR: deploy-nsp.ps1 not found at $deployNSPScript" -ForegroundColor Red
            exit 1
        }
        
        # Call deploy-nsp.ps1
        & $deployNSPScript -ResourceGroupName $ResourceGroupName -Location $location -NSPName $nspName
        
        Write-Host "`nNSP '$nspName' created successfully." -ForegroundColor Green
        
        return @{
            Exists = $false
            NSPName = $nspName
            ResourceGroup = $ResourceGroupName
            Location = $location
            Action = "Created"
        }
    }
} catch {
    Write-Host "ERROR checking NSP: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
