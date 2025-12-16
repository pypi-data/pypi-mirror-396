Param(
  [Parameter(Mandatory=$true)] [string]$ResourceGroupName,
  [Parameter(Mandatory=$true)] [string]$NSPName,
  [Parameter(Mandatory=$true)] [string]$ResourceId
)

$ErrorActionPreference = "Stop"

# --- 1. VALIDATION (No Interactive Prompts) ---
if (-not $ResourceId -or -not $ResourceGroupName -or -not $NSPName) {
    Write-Error "Missing required parameters. Cannot attach NSP interactively."
    exit 1
}

Write-Output "Attaching resource to NSP..."
Write-Output "Resource: $ResourceId"
Write-Output "NSP: $NSPName (RG: $ResourceGroupName)"

try {
  # --- 2. AUTHENTICATION ---
  # Get subscription ID and token using Azure CLI
  # We use CLI because it's already authenticated in this session
  $SubscriptionId = az account show --query id -o tsv
  $token = az account get-access-token --query accessToken -o tsv
  
  if (-not $token) {
      Write-Error "Failed to acquire access token."
      exit 1
  }

  # --- 3. GET NSP PROFILE ---
  # NSP is often in preview, so we use direct REST calls for reliability
  $apiVersion = "2023-07-01-preview"
  $url = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Network/networkSecurityPerimeters/$NSPName/profiles?api-version=$apiVersion"
  $headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }
  
  $response = Invoke-RestMethod -Method Get -Uri $url -Headers $headers -ErrorAction Stop
  $ProfileNSP = $response.value

  # Handle case where multiple profiles exist - default to the first one
  if ($ProfileNSP -is [array]) {
    if ($ProfileNSP.Count -eq 0) {
        Write-Error "No profiles found in NSP '$NSPName'. Please check NSP configuration."
        exit 1
    }
    $ProfileNSP = $ProfileNSP[0]
  }
  elseif (-not $ProfileNSP) {
      Write-Error "Failed to retrieve NSP profile."
      exit 1
  }

  $profileIdString = $ProfileNSP.id

  # --- 4. GENERATE ASSOCIATION NAME ---
  # Create a unique association name by hashing the ResourceID
  # This ensures idempotency: running it twice for the same resource generates the same name
  $hashedResourceID = $ResourceId.GetHashCode().ToString("X")
  $uniqueAssociationName = "nsp-assoc-" + $hashedResourceID
  
  # Ensure the name is unique per timestamp if you prefer, or keep it static for idempotency.
  # Adding a short timestamp to ensure unique logs if re-attached
  $timestamp = Get-Date -Format "MMddHHmm"
  $uniqueAssociationName = "${uniqueAssociationName}-${timestamp}"

  # Ensure the name is under 80 characters
  if ($uniqueAssociationName.Length -gt 80) {
    $uniqueAssociationName = $uniqueAssociationName.Substring(0, 80)
  }

  Write-Output "Creating association: $uniqueAssociationName"

  # --- 5. CREATE ASSOCIATION (PUT) ---
  $assocUrl = "https://management.azure.com/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Network/networkSecurityPerimeters/$NSPName/resourceAssociations/$uniqueAssociationName?api-version=$apiVersion"
  
  $body = @{
    properties = @{
        accessMode = "Learning"
        privateLinkResourceId = $ResourceId
        profile = @{
            id = $profileIdString
        }
    }
  } | ConvertTo-Json -Depth 10

  $putResponse = Invoke-RestMethod -Method Put -Uri $assocUrl -Headers $headers -Body $body -ErrorAction Stop
  
  Write-Output "Successfully attached resource to NSP."
  
} catch {
  Write-Error "Failed to attach resource to NSP. Error: $_"
  exit 1
}