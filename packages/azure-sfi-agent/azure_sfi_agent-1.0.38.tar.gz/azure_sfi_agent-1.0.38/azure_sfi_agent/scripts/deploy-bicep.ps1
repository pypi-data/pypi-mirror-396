Param(
    [Parameter(Mandatory=$true)] [string]$ResourceGroupName,
    [Parameter(Mandatory=$true)] [string]$TemplateFile,
    [Parameter(Mandatory=$false)] [string]$ParametersFilePath
)

$ErrorActionPreference = "Stop"

# --- 1. DISABLE PROMPTS (Crucial Fix) ---
# This stops the script from asking "Are you sure?" or "Install Bicep?"
$env:AZURE_CORE_DISABLE_CONFIRM_PROMPT = "true"
$env:AZURE_CORE_COLLECT_TELEMETRY = "false" 

# --- 2. ENSURE RESOURCE GROUP ---
# We use 'az group exists' to check without needing the full Az PowerShell module
Write-Output "Checking Resource Group '$ResourceGroupName'..."
$rgExists = az group exists --name $ResourceGroupName

if ($rgExists -eq "false") {
    Write-Output "Resource Group does not exist. Creating..."
    # Create RG silently
    az group create --name $ResourceGroupName --location "eastus" --output none
}

# --- 3. PARSE PARAMETERS ---
$ParamArgs = @()
if (-not [string]::IsNullOrEmpty($ParametersFilePath) -and (Test-Path $ParametersFilePath)) {
    try {
        Write-Output "Reading parameters from: $ParametersFilePath"
        $JsonContent = Get-Content -Raw $ParametersFilePath
        $JsonObj = $JsonContent | ConvertFrom-Json
        
        foreach ($prop in $JsonObj.PSObject.Properties) {
            if (-not [string]::IsNullOrEmpty($prop.Value)) {
                $ParamArgs += "$($prop.Name)=$($prop.Value)"
            }
        }
    }
    catch {
        Write-Error "Failed to parse parameters from file: $_"
        exit 1
    }
}

# --- 4. EXECUTE DEPLOYMENT ---
Write-Output "Starting Deployment..."
Write-Output "Template: $TemplateFile"

# Build the argument list safely
$AzArgs = @("deployment", "group", "create")
$AzArgs += "--resource-group", $ResourceGroupName
$AzArgs += "--template-file", $TemplateFile

if ($ParamArgs.Count -gt 0) {
    $AzArgs += "--parameters"
    $AzArgs += $ParamArgs
}
# Critical flags to prevent hanging
$AzArgs += "--no-prompt"
$AzArgs += "--output", "json"

# Execute using the call operator '&'
& az @AzArgs

if ($LASTEXITCODE -eq 0) {
    Write-Output "Deployment Succeeded."
} else {
    Write-Error "Deployment Failed. Exit Code: $LASTEXITCODE"
    exit 1
}