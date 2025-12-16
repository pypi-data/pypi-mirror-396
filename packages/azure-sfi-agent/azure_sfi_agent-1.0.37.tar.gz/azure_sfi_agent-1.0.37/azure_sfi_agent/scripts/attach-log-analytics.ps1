param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory = $true)]
    [string]$WorkspaceId,
    
    [Parameter(Mandatory = $true)]
    [string]$ResourceId
)

Write-Host "Attaching diagnostic settings to resource..."
Write-Host "Resource ID: $ResourceId"
Write-Host "Workspace ID: $WorkspaceId"
Write-Host ""

# Extract resource name from Resource ID
$resourceName = ($ResourceId -split '/')[-1]
$diagnosticSettingName = "diag-$resourceName"

Write-Host "Creating diagnostic setting: $diagnosticSettingName"
Write-Host ""

try {
    # Get all available diagnostic categories for the resource using Azure CLI
    $categoriesJson = az monitor diagnostic-settings categories list --resource $ResourceId --output json 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to retrieve diagnostic categories for resource."
        exit 1
    }
    
    $categories = $categoriesJson | ConvertFrom-Json
    
    # Build metric and log settings
    $logsArg = @()
    $metricsArg = @()

    foreach ($cat in $categories) {
        if ($cat.categoryType -eq "Metrics") {
            $metricsArg += @{category = $cat.name; enabled = $true}
            Write-Host "  + Metric category: $($cat.name)"
        } else {
            $logsArg += @{category = $cat.name; enabled = $true}
            Write-Host "  + Log category: $($cat.name)"
        }
    }
    
    Write-Host ""
    
    # Create the diagnostic setting using Azure CLI
    if ($logsArg.Count -gt 0 -or $metricsArg.Count -gt 0) {
        
        $azArgs = @(
            "monitor", "diagnostic-settings", "create",
            "--name", $diagnosticSettingName,
            "--resource", $ResourceId,
            "--workspace", $WorkspaceId
        )
        
        if ($logsArg.Count -gt 0) {
            $azArgs += "--logs"
            $azArgs += ($logsArg | ConvertTo-Json -Compress)
        }
        
        if ($metricsArg.Count -gt 0) {
            $azArgs += "--metrics"
            $azArgs += ($metricsArg | ConvertTo-Json -Compress)
        }

        # Execute az command
        & az $azArgs 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Successfully created diagnostic setting '$diagnosticSettingName'." -ForegroundColor Green
        } else {
            # Check if it already exists
            Write-Warning "Diagnostic setting may already exist or resource doesn't support diagnostic settings."
        }
    } else {
        Write-Host "No diagnostic categories found for this resource." -ForegroundColor Yellow
    }
    
} catch {
    Write-Error "Failed to attach diagnostic settings: $_"
    exit 1
}
