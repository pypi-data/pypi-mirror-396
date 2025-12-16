Param(
  [Parameter(Mandatory=$true)] [string]$ResourceGroupName,
  [Parameter(Mandatory=$true)] [string]$Region,
  [Parameter(Mandatory=$true)] [string]$ProjectName
)

$ErrorActionPreference = "Stop"

Write-Host "Creating Resource Group '$ResourceGroupName' in '$Region'..."

az group create `
  --name $ResourceGroupName `
  --location $Region `
  --tags "Project=$ProjectName" `
  --output none

if ($LASTEXITCODE -eq 0) { 
  Write-Host "Resource Group created successfully."
} else { 
  Write-Host "Resource Group creation failed."
  exit 1 
}