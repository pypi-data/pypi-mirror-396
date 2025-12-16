# Attach a newly created resource to Network Security Perimeter
# Used after deploying a resource to associate it with an NSP

param(
  [Parameter(Mandatory=$false)] [string]$ResourceID,
  [Parameter(Mandatory=$false)] [string]$ResourceGroupName,
  [Parameter(Mandatory=$false)] [string]$NspName
)

if (-not $ResourceID) { $ResourceID = Read-Host "Enter Resource ID to attach" }
if (-not $ResourceGroupName) { $ResourceGroupName = Read-Host "Enter Resource Group Name" }
if (-not $NspName) { $NspName = Read-Host "Enter NSP Name" }

Write-Host "`nAttaching resource to NSP..." -ForegroundColor Cyan
Write-Host "Resource ID: $ResourceID" -ForegroundColor Gray
Write-Host "NSP: $NspName in Resource Group: $ResourceGroupName" -ForegroundColor Gray

try {
  # Get subscription ID and token using Azure CLI
  $SubscriptionId = az account show --query id -o tsv
  $token = az account get-access-token --query accessToken -o tsv
  
  # Get the NSP profile using REST API
  $url = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Network/networkSecurityPerimeters/$NspName/profiles?api-version=2023-07-01-preview"
  $headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }
  
  $response = Invoke-RestMethod -Method Get -Uri $url -Headers $headers -ErrorAction Stop
  $ProfileNSP = $response.value

  # Handle case where multiple profiles exist - select the first one
  if ($ProfileNSP -is [array]) {
    Write-Host "Multiple NSP profiles found. Using the first profile." -ForegroundColor Yellow
    $ProfileNSP = $ProfileNSP[0]
  }

  # Ensure we have a valid profile ID as a string
  $profileIdString = $ProfileNSP.id

  # Create a unique association name by hashing the ResourceID and adding a timestamp
  $hashedResourceID = $ResourceID.GetHashCode().ToString("X")
  $uniqueAssociationName = "nsp-assoc-" + $hashedResourceID + "-" + (Get-Date -Format "MMddHHmmss")

  # Ensure the name is under 80 characters
  if ($uniqueAssociationName.Length -gt 80) {
    $uniqueAssociationName = $uniqueAssociationName.Substring(0, 80)
  }

  Write-Host "`nCreating association: $uniqueAssociationName" -ForegroundColor Cyan

  # Create association using REST API
  $assocUrl = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Network/networkSecurityPerimeters/$NspName/resourceAssociations/$uniqueAssociationName?api-version=2023-07-01-preview"
  
  $body = @{
    properties = @{
        accessMode = "Learning"
        privateLinkResourceId = $ResourceID
        profile = @{
            id = $profileIdString
        }
    }
  } | ConvertTo-Json -Depth 10

  Invoke-RestMethod -Method Put -Uri $assocUrl -Headers $headers -Body $body -ErrorAction Stop | Format-List
  
  Write-Host "`nSuccessfully attached resource to NSP" -ForegroundColor Green
  Write-Host "Association Name: $uniqueAssociationName" -ForegroundColor Cyan
  
} catch {
  Write-Host "`nFailed to attach resource to NSP. Error: $_" -ForegroundColor Red
  exit 1
}
