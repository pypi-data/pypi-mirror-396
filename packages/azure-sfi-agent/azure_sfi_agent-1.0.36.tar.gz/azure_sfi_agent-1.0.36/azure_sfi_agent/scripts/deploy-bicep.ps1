Param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory=$true)]
    [string]$TemplateFile,

    [Parameter(Mandatory=$false)]
    [string]$ParametersFilePath
)

$ErrorActionPreference = "Stop"

# --- 0. ENVIRONMENT SETUP ---
# Disable all interactive prompts (Crucial for background execution)
$env:AZURE_CORE_DISABLE_CONFIRM_PROMPT = "true"
$env:AZURE_CORE_COLLECT_TELEMETRY = "false" 

# --- 1. PRE-FLIGHT CHECKS ---
Write-Output "Checking Bicep status..."
# We run version check to ensure it's installed. 
# If it fails/prompts, the environment variable above suppresses the hang, and we try install.
try {
    $null = az bicep version 2>&1
}
catch {
    Write-Output "Bicep not found. Attempting silent install..."
    az bicep install
}

# --- 2. ENSURE RESOURCE GROUP (Pure CLI Version) ---
# We use 'az group exists' which returns the string "true" or "false"
Write-Output "Checking Resource Group '$ResourceGroupName'..."
$rgExists = az group exists --name $ResourceGroupName

if ($rgExists -eq "false") {
    Write-Output "Resource Group does not exist. Creating..."
    az group create --name $ResourceGroupName --location "eastus"
}

# --- 3. PREPARE PARAMETERS ---
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

# Construct command args
$AzArgs = @("deployment", "group", "create", "--resource-group", $ResourceGroupName, "--template-file", $TemplateFile)

if ($ParamArgs.Count -gt 0) {
    $AzArgs += "--parameters"
    $AzArgs += $ParamArgs
}
$AzArgs += "--no-prompt"
$AzArgs += "--only-show-errors"

# Execute directly with & operator (most reliable for subprocess)
& az $AzArgs

if ($LASTEXITCODE -eq 0) {
    Write-Output "Deployment Succeeded."
} else {
    Write-Error "Deployment Failed with exit code $LASTEXITCODE"
    exit 1
}