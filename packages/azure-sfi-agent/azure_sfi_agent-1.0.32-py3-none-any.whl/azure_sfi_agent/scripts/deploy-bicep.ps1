Param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory=$true)]
    [string]$TemplateFile,

    [Parameter(Mandatory=$false)]
    [string]$ParametersFilePath
)

$ErrorActionPreference = "Stop"

# 1. Ensure Resource Group Exists
if (-not (Get-AzResourceGroup -Name $ResourceGroupName -ErrorAction SilentlyContinue)) {
    Write-Output "Resource Group '$ResourceGroupName' not found. Creating..."
    az group create --name $ResourceGroupName --location "eastus"
}

# 2. Read parameters from the Temp File (Fixes the loop/hang issue)
$ParamArgs = @()
if (-not [string]::IsNullOrEmpty($ParametersFilePath) -and (Test-Path $ParametersFilePath)) {
    try {
        Write-Output "Reading parameters from: $ParametersFilePath"
        $JsonContent = Get-Content -Raw $ParametersFilePath
        $JsonObj = $JsonContent | ConvertFrom-Json
        
        foreach ($prop in $JsonObj.PSObject.Properties) {
            if (-not [string]::IsNullOrEmpty($prop.Value)) {
                # Add key=value to arguments
                $ParamArgs += "$($prop.Name)=$($prop.Value)"
            }
        }
    }
    catch {
        Write-Error "Failed to parse parameters from file: $_"
        exit 1
    }
}

Write-Output "Starting Bicep deployment..."
Write-Output "Template: $TemplateFile"

# 3. Construct the AZ command dynamically
$AzCommand = @("deployment", "group", "create", "--resource-group", $ResourceGroupName, "--template-file", $TemplateFile)

if ($ParamArgs.Count -gt 0) {
    $AzCommand += "--parameters"
    $AzCommand += $ParamArgs
}

# 4. Execute
& az $AzCommand

if ($LASTEXITCODE -eq 0) {
    Write-Output "Deployment Succeeded."
} else {
    Write-Error "Deployment Failed with exit code $LASTEXITCODE"
    exit 1
}