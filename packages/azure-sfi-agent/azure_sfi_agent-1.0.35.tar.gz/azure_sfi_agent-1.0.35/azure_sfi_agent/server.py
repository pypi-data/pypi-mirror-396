from mcp.server.fastmcp import FastMCP
import subprocess
import os
import re
import shutil
import json
import time
import tempfile
from typing import Dict, Tuple, Optional, Union, Any

# Initialize the server
mcp = FastMCP("azure-agent")

# --- DEPLOYMENT ENFORCEMENT ---
# CRITICAL: All Azure resource deployments MUST go through MCP server tools.
# Direct az deployment commands are FORBIDDEN to ensure compliance orchestration.
ENFORCE_MCP_DEPLOYMENT = True

AGENT_INSTRUCTIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AGENT_INSTRUCTIONS.md")

def load_agent_instructions() -> str:
    """Load the AGENT_INSTRUCTIONS.md file content if present."""
    if os.path.exists(AGENT_INSTRUCTIONS_FILE):
        try:
            with open(AGENT_INSTRUCTIONS_FILE, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Failed to read instructions: {e}"
    return "Instructions file not found."

def get_action_menu() -> str:
    return (
        "Available actions:\n"
        "1. List all active permissions (Live Fetch)\n"
        "2. List all accessible resources (optional resource group)\n"
        "3. Check if resource group exists\n"
        "4. Create resource group (requires: name, region, project name)\n"
        "5. Create Azure resources with SFI compliance\n"
        "   Usage: create_azure_resource(resource_type, resource_group, parameters)\n"
        "   \n"
        "   Interactive workflow:\n"
        "   - Call with resource_type (e.g., 'storage-account')\n"
        "   - Agent will ask for missing required parameters\n"
        "   - Provide parameters as dict when prompted\n"
        "   - Agent deploys resource and automatically:\n"
        "     ✓ Attaches NSP for: storage-account, key-vault, cosmos-db, sql-db\n"
        "     ✓ Configures Log Analytics for monitoring resources\n"
        "   \n"
        "   Supported types: storage-account | key-vault | openai | ai-search | ai-foundry | cosmos-db | sql-db | log-analytics"
    )

GREETING_PATTERN = re.compile(r"\b(hi|hello|hey|greetings|good (morning|afternoon|evening))\b", re.IGNORECASE)

def is_greeting(text: str) -> bool:
    return bool(GREETING_PATTERN.search(text))

def normalize(text: str) -> str:
    return text.lower().strip()

# --- CONFIGURATION ---

# Resources that MUST be attached to NSP after creation
NSP_MANDATORY_RESOURCES = [
    "storage-account", # ADLS is usually a storage account with HNS enabled
    "key-vault",
    "cosmos-db",
    "sql-db"
]

# Resources that MUST have diagnostic settings (Log Analytics) attached after creation
LOG_ANALYTICS_MANDATORY_RESOURCES = [
    "logic-app",
    "function-app",
    "app-service",
    "key-vault",
    "synapse",
    "data-factory",
    "ai-hub",
    "ai-project",
    "ai-foundry",
    "ai-services",
    "ai-search",
    "front-door",
    "virtual-machine",
    "redis-cache",
    "redis-enterprise"
]

# Bicep Templates (All deployments MUST go through MCP server for compliance orchestration)
# Added Cosmos and SQL support
TEMPLATE_MAP = {
    "storage-account": "templates/storage-account.bicep",
    "key-vault": "templates/azure-key-vaults.bicep",
    "openai": "templates/azure-openai.bicep",
    "ai-search": "templates/ai-search.bicep",
    "ai-foundry": "templates/ai-foundry.bicep",
    "cosmos-db": "templates/cosmos-db.bicep",
    "sql-db": "templates/sql-db.bicep",
    "log-analytics": "templates/log-analytics.bicep"
}

# 3. Operational Scripts (Permissions/Listings)
OP_SCRIPTS = {
    "permissions": "list-permissions.ps1",
    "resources": "list-resources.ps1",
    "create-rg": "create-resourcegroup.ps1"
}

# --- HELPERS ---

def run_command(command: list[str], timeout: int = 120) -> str:
    """Generic command runner with timeout."""
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True,
            timeout=timeout,
            shell=False
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds: {' '.join(command)}"
    except subprocess.CalledProcessError as e:
        return f"Error running command {' '.join(command)}: {e.stderr}"
    except Exception as e:
        return f"Error executing command {' '.join(command)}: {str(e)}"

def _get_script_path(script_name: str) -> str:
    """Locates the script in the 'scripts' folder."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "scripts", script_name)

def _get_template_path(template_rel: str) -> str:
    """Locates the bicep file relative to server file."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), template_rel)

def _check_resource_group_exists(resource_group: str) -> Tuple[bool, str]:
    """
    Checks if a resource group exists and user has access to it using PowerShell.
    Returns (exists: bool, message: str)
    """
    try:
        # Use PowerShell to run 'az group exists' command
        ps_executable = "pwsh" if shutil.which("pwsh") else "powershell"
        
        ps_command = f"$result = az group exists --name {resource_group} 2>$null; if ($LASTEXITCODE -eq 0) {{ $result }} else {{ 'ERROR' }}"
        
        result = subprocess.run(
            [ps_executable, "-NoProfile", "-NonInteractive", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )
        
        output = result.stdout.strip().lower()
        
        if "error" in output or result.returncode != 0:
            return False, f"Could not verify resource group '{resource_group}'. Please ensure you are logged in to Azure."
        
        if output == "true":
            return True, f"Resource group '{resource_group}' exists and is accessible."
        elif output == "false":
            return False, f"Resource group '{resource_group}' does not exist. Please create it first using create_resource_group()."
        else:
            return False, f"Could not verify resource group '{resource_group}': {output}"
            
    except Exception as e:
        return False, f"Error checking resource group '{resource_group}': {str(e)}"

# --- NSP ORCHESTRATION HELPERS ---

def _get_rg_location(resource_group: str) -> str:
    """Fetches location of the resource group."""
    try:
        res = run_command(["az", "group", "show", "-n", resource_group, "--query", "location", "-o", "tsv"])
        return res.strip()
    except:
        return "eastus" # Fallback

def _get_resource_id(resource_group: str, resource_type: str, parameters: Dict[str, str]) -> Optional[str]:
    """
    Attempts to find the Resource ID based on parameters provided during creation.
    We look for common naming parameter keys.
    """
    # Common parameter names for resource names in Bicep templates
    name_keys = [
        "name", "accountName", "keyVaultName", "serverName", "databaseName", "storageAccountName",
        "workspaceName", "searchServiceName", "serviceName", "vmName", "virtualMachineName",
        "siteName", "functionAppName", "appServiceName", "logicAppName", "workflowName",
        "factoryName", "cacheName", "frontDoorName", "clusterName"
    ]
    
    resource_name = None
    for key in name_keys:
        if key in parameters:
            resource_name = parameters[key]
            break
            
    # If we couldn't find a specific name, we might check the deployment output, 
    # but for now, we fail gracefully if we can't identify the resource name.
    if not resource_name:
        return None

    # Map internal types to Azure Resource Provider types for CLI lookup
    provider_map = {
        "storage-account": "Microsoft.Storage/storageAccounts",
        "key-vault": "Microsoft.KeyVault/vaults",
        "cosmos-db": "Microsoft.DocumentDB/databaseAccounts",
        "sql-db": "Microsoft.Sql/servers",
        "logic-app": "Microsoft.Logic/workflows",
        "function-app": "Microsoft.Web/sites",
        "app-service": "Microsoft.Web/sites",
        "synapse": "Microsoft.Synapse/workspaces",
        "data-factory": "Microsoft.DataFactory/factories",
        "ai-hub": "Microsoft.MachineLearningServices/workspaces",
        "ai-project": "Microsoft.MachineLearningServices/workspaces",
        "ai-foundry": "Microsoft.CognitiveServices/accounts",
        "ai-services": "Microsoft.CognitiveServices/accounts",
        "ai-search": "Microsoft.Search/searchServices",
        "front-door": "Microsoft.Network/frontDoors",
        "virtual-machine": "Microsoft.Compute/virtualMachines",
        "redis-cache": "Microsoft.Cache/redis",
        "redis-enterprise": "Microsoft.Cache/redisEnterprise"
    }
    
    provider = provider_map.get(resource_type)
    if not provider:
        return None

    try:
        cmd = [
            "az", "resource", "show", 
            "-g", resource_group, 
            "-n", resource_name, 
            "--resource-type", provider, 
            "--query", "id", "-o", "tsv"
        ]
        return run_command(cmd).strip()
    except:
        return None

def _orchestrate_nsp_attachment(resource_group: str, resource_type: str, parameters: Dict[str, str]) -> str:
    """
    Checks requirements and performs NSP creation/attachment using check-nsp.ps1.
    """
    if resource_type not in NSP_MANDATORY_RESOURCES:
        return "" # No action needed

    log = ["\n[NSP Orchestration Triggered]"]
    
    # 1. Run check-nsp.ps1 to ensure NSP exists (creates if needed)
    check_nsp_script = _get_script_path("check-nsp.ps1")
    if not os.path.exists(check_nsp_script):
        log.append("[WARNING] check-nsp.ps1 not found. Skipping NSP orchestration.")
        return "\n".join(log)
    
    log.append(f"Checking/Creating NSP in '{resource_group}'...")
    nsp_check_result = _run_powershell_script(
        check_nsp_script,
        {"ResourceGroupName": resource_group},
        timeout=30
    )
    log.append(nsp_check_result)
    nsp_name = f"{resource_group}-nsp"

    # 2. Get Resource ID
    resource_id = _get_resource_id(resource_group, resource_type, parameters)
    if not resource_id:
        return "\n".join(log) + "\n[WARNING] Could not determine Resource ID. Skipping NSP attachment. Please attach manually."

    # 3. Attach Resource using attach-nsp.ps1
    attach_nsp_script = _get_script_path("attach-nsp.ps1")
    if not os.path.exists(attach_nsp_script):
        log.append("[WARNING] attach-nsp.ps1 not found. Please attach resource manually.")
        return "\n".join(log)
    
    log.append(f"Attaching resource to NSP '{nsp_name}'...")
    attach_result = _run_powershell_script(
        attach_nsp_script,
        {
            "ResourceGroupName": resource_group,
            "NSPName": nsp_name,
            "ResourceId": resource_id
        },
        timeout=30
    )
    
    if "Error" in attach_result or "FAILED" in attach_result:
        log.append(f"FAILED to attach resource: {attach_result}")
    else:
        log.append("Resource successfully attached to NSP.")
        log.append(attach_result)

    return "\n".join(log)

def _orchestrate_log_analytics_attachment(resource_group: str, resource_type: str, parameters: Dict[str, str]) -> str:
    """
    Checks requirements and performs Log Analytics Workspace creation/diagnostic settings attachment.
    If multiple workspaces exist, requires user to specify which one to use.
    """
    if resource_type not in LOG_ANALYTICS_MANDATORY_RESOURCES:
        return "" # No action needed

    log = ["\n[Log Analytics Orchestration Triggered]"]
    
    # 1. Run check-log-analytics.ps1 to ensure Log Analytics Workspace exists (creates if needed)
    check_law_script = _get_script_path("check-log-analytics.ps1")
    if not os.path.exists(check_law_script):
        log.append("[WARNING] check-log-analytics.ps1 not found. Skipping Log Analytics orchestration.")
        return "\n".join(log)
    
    log.append(f"Checking/Creating Log Analytics Workspace in '{resource_group}'...")
    law_check_result = _run_powershell_script(
        check_law_script,
        {"ResourceGroupName": resource_group},
        timeout=30
    )
    log.append(law_check_result)
    
    # Check if multiple workspaces exist and require user selection
    if "MULTIPLE LOG ANALYTICS WORKSPACES FOUND" in law_check_result or "RequiresSelection" in law_check_result:
        log.append("\n[ACTION REQUIRED]")
        log.append("Multiple Log Analytics Workspaces detected in this resource group.")
        log.append("Please specify which workspace to use for diagnostic settings by providing the workspace name or ID.")
        log.append("Diagnostic settings attachment SKIPPED - awaiting user selection.")
        return "\n".join(log)
    
    # Extract workspace ID from output or construct it
    workspace_name = f"{resource_group}-law"
    workspace_id = f"/subscriptions/{_get_subscription_id()}/resourceGroups/{resource_group}/providers/Microsoft.OperationalInsights/workspaces/{workspace_name}"

    # 2. Get Resource ID
    resource_id = _get_resource_id(resource_group, resource_type, parameters)
    if not resource_id:
        return "\n".join(log) + "\n[WARNING] Could not determine Resource ID. Skipping diagnostic settings attachment. Please attach manually."

    # 3. Attach Diagnostic Settings using attach-log-analytics.ps1
    attach_law_script = _get_script_path("attach-log-analytics.ps1")
    if not os.path.exists(attach_law_script):
        log.append("[WARNING] attach-log-analytics.ps1 not found. Please attach diagnostic settings manually.")
        return "\n".join(log)
    
    log.append(f"Attaching diagnostic settings to resource...")
    attach_result = _run_powershell_script(
        attach_law_script,
        {
            "ResourceGroupName": resource_group,
            "WorkspaceId": workspace_id,
            "ResourceId": resource_id
        },
        timeout=30
    )
    
    if "Error" in attach_result or "FAILED" in attach_result:
        log.append(f"FAILED to attach diagnostic settings: {attach_result}")
    else:
        log.append("Diagnostic settings successfully attached.")
        log.append(attach_result)

    return "\n".join(log)

def _get_subscription_id() -> str:
    """Fetches the current subscription ID."""
    try:
        res = run_command(["az", "account", "show", "--query", "id", "-o", "tsv"])
        return res.strip()
    except:
        return ""

# --- PARSERS ---

def _get_script_parameters(script_path: str) -> dict:
    """Parses a PowerShell script Param() block."""
    required = []
    optional = []
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        param_block_match = re.search(r'Param\s*\((.*?)\)', content, re.IGNORECASE | re.DOTALL)
        if param_block_match:
            lines = param_block_match.group(1).split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'): continue
                var_match = re.search(r'\$([a-zA-Z0-9_]+)', line)
                if var_match:
                    param_name = var_match.group(1)
                    if '=' in line: optional.append(param_name)
                    else: required.append(param_name)
    except Exception as e:
        return {"error": str(e)}
    return {"required": sorted(list(set(required))), "optional": sorted(list(set(optional)))}

def _parse_bicep_parameters(template_path: str) -> Dict[str, Tuple[bool, Optional[str]]]:
    params: Dict[str, Tuple[bool, Optional[str]]] = {}
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_strip = line.strip()
                if line_strip.startswith('param '):
                    m = re.match(r"param\s+(\w+)\s+[^=\n]+(?:=\s*(.+))?", line_strip)
                    if m:
                        name = m.group(1)
                        default_raw = m.group(2).strip() if m.group(2) else None
                        required = default_raw is None
                        params[name] = (required, default_raw)
    except Exception:
        pass
    return params

def _validate_bicep_parameters(resource_type: str, provided: Dict[str, str]) -> Tuple[bool, str, Dict[str, Tuple[bool, Optional[str]]]]:
    if resource_type not in TEMPLATE_MAP:
        return False, f"Unknown resource_type '{resource_type}'.", {}
    template_path = _get_template_path(TEMPLATE_MAP[resource_type])
    if not os.path.exists(template_path):
        return False, f"Template not found at {template_path}", {}
    params = _parse_bicep_parameters(template_path)
    missing = [p for p, (req, _) in params.items() if req and (p not in provided or provided[p] in (None, ""))]
    if missing:
        return False, f"Missing required parameters: {', '.join(missing)}", params
    return True, "OK", params

def _deploy_bicep(resource_group: str, resource_type: str, parameters: Dict[str,str]) -> str:
    # 1. Validate Template Path (from TEMPLATE_MAP)
    if resource_type not in TEMPLATE_MAP:
        return f"Unknown resource_type '{resource_type}'."
    
    # Python calculates the specific template path here
    template_rel_path = TEMPLATE_MAP[resource_type]
    template_abs_path = os.path.abspath(_get_template_path(template_rel_path))
    
    if not os.path.exists(template_abs_path):
        return f"Template not found: {template_abs_path}"
    
    # 2. Locate the UNIVERSAL wrapper script
    deploy_script_name = "deploy-bicep.ps1"
    deploy_script_path = _get_script_path(deploy_script_name)
    
    if not os.path.exists(deploy_script_path):
        return f"Error: '{deploy_script_name}' not found in scripts folder."

    # 3. Write Parameters to a Temporary File (Fixes the loop/hang)
    import json
    
    # Create a temp file that is NOT automatically deleted on close
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        json.dump(parameters, temp_file)
        temp_file_path = temp_file.name

    try:
        # 4. Pass the TEMPLATE path and PARAM file path to PowerShell
        script_args = {
            "ResourceGroupName": resource_group,
            "TemplateFile": template_abs_path,
            "ParametersFilePath": temp_file_path
        }

        # 5. Execute
        deploy_result = _run_powershell_script(deploy_script_path, script_args)
        
    finally:
        # 6. Cleanup the temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    
    # 7. Compliance Orchestration
    if "Deployment Succeeded" in deploy_result:
        nsp_logs = _orchestrate_nsp_attachment(resource_group, resource_type, parameters)
        law_logs = _orchestrate_log_analytics_attachment(resource_group, resource_type, parameters)
        return f"{deploy_result}\n{nsp_logs}\n{law_logs}"
    
    return deploy_result

def _run_powershell_script(script_path: str, parameters: dict, timeout: int = 60) -> str:
    """Run PowerShell script with timeout and non-interactive mode."""
    ps_executable = "pwsh" if shutil.which("pwsh") else "powershell"
    
    # Use -NonInteractive to prevent any prompts that could hang
    cmd = [
        ps_executable, 
        "-NoProfile", 
        "-NonInteractive",
        "-ExecutionPolicy", "Bypass", 
        "-File", script_path
    ]
    
    for k, v in parameters.items():
        if v is not None and v != "":
            cmd.append(f"-{k}")
            cmd.append(str(v))
    
    try:
        # Run with timeout and environment that prevents interactive prompts
        env = os.environ.copy()
        env["POWERSHELL_TELEMETRY_OPTOUT"] = "1"
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,  # Don't raise on non-zero exit
            env=env,
            stdin=subprocess.DEVNULL  # Prevent any stdin reading
        )
        
        # Return both stdout and stderr for better debugging
        output = result.stdout.strip()
        error_output = result.stderr.strip()
        
        if result.returncode != 0:
            return f"Script exited with code {result.returncode}\nOutput: {output}\nError: {error_output}"
        
        return output if output else "Script completed successfully (no output)"
        
    except subprocess.TimeoutExpired:
        return f"Error: PowerShell script timed out after {timeout} seconds. The script may be waiting for input or stuck in a loop."
    except FileNotFoundError:
        return f"Error: PowerShell executable '{ps_executable}' not found"
    except Exception as e:
        return f"Error executing PowerShell script: {str(e)}"

# --- INTENT PARSING ---

def parse_intent(text: str) -> str:
    t = normalize(text)
    if is_greeting(t): return "greeting"
    if any(k in t for k in ["menu", "help", "options"]): return "menu"
    if any(k in t for k in ["list permissions", "show permissions", "check permissions"]): return "permissions"
    if "list resources" in t or "show resources" in t or re.search(r"resources in", t): return "resources"
    if any(k in t for k in ["create rg", "create resource group", "new rg", "new resource group"]): return "create-rg"
    if any(k in t for k in ["create", "deploy", "provision"]): return "create"
    return "unknown"

def extract_resource_group(text: str) -> Optional[str]:
    m = re.search(r"resources in ([A-Za-z0-9-_\.]+)", text, re.IGNORECASE)
    return m.group(1) if m else None

# --- TOOLS ---

@mcp.tool()
def azure_login() -> str:
    """Initiates Azure login."""
    return run_command(["az", "login", "--use-device-code"])

@mcp.tool()
def list_permissions(user_principal_name: str = None, force_refresh: bool = True) -> str:
    """
    Lists active role assignments. 
    Uses force_refresh=True by default to ensure recent role activations are captured.
    """
    script_name = OP_SCRIPTS["permissions"]
    script_path = _get_script_path(script_name)
    
    if not os.path.exists(script_path):
        return f"Error: Script '{script_name}' not found."

    params = {}
    if user_principal_name:
        params["UserPrincipalName"] = user_principal_name
    
    # Note: The subprocess call itself ensures a new process is spawned, 
    # preventing variable caching in Python. 
    return _run_powershell_script(script_path, params)

@mcp.tool()
def list_resources(resource_group_name: str = None) -> str:
    """Lists Azure resources (all or by group)."""
    script_name = OP_SCRIPTS["resources"]
    script_path = _get_script_path(script_name)
    if not os.path.exists(script_path): return f"Error: Script '{script_name}' not found."
    params = {}
    if resource_group_name: params["ResourceGroup"] = resource_group_name
    return _run_powershell_script(script_path, params)

@mcp.tool()
def check_resource_group(resource_group_name: str) -> str:
    """
    Checks if a resource group exists and is accessible.
    
    Args:
        resource_group_name: Name of the resource group to check
    
    Returns:
        Status message indicating if the resource group exists and is accessible
    """
    if not resource_group_name or not resource_group_name.strip():
        return "❌ Error: Resource group name is required."
    
    exists, message = _check_resource_group_exists(resource_group_name)
    
    if exists:
        # Also fetch additional details using PowerShell
        try:
            ps_executable = "pwsh" if shutil.which("pwsh") else "powershell"
            ps_command = f"az group show --name {resource_group_name} --query '{{location:location, tags:tags, provisioningState:properties.provisioningState}}' --output json"
            
            result = subprocess.run(
                [ps_executable, "-NoProfile", "-NonInteractive", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=30,
                check=False
            )
            
            if result.returncode == 0 and result.stdout:
                return f"✅ {message}\n\nDetails:\n{result.stdout}"
            else:
                return f"✅ {message}"
        except:
            return f"✅ {message}"
    else:
        return f"❌ {message}"

@mcp.tool()
def debug_environment() -> str:
    """Checks the Azure environment versions to debug hanging issues."""
    try:
        # Run a simple version check
        # This will tell us if 'az' is accessible and if bicep is installed
        result = subprocess.run(
            ["az", "bicep", "version"], 
            capture_output=True, 
            text=True, 
            timeout=10,
            shell=True # Using shell=True for this simple debug command often bypasses path issues
        )
        return f"✅ Azure CLI Bicep Status:\n{result.stdout}\nErrors (if any): {result.stderr}"
    except subprocess.TimeoutExpired:
        return "❌ TIMEOUT: 'az bicep version' hung. This confirms the CLI is waiting for user input."
    except Exception as e:
        return f"❌ Execution Error: {str(e)}"
    
@mcp.tool()
def create_resource_group(resource_group_name: str, region: str, project_name: str) -> str:
    """Creates an Azure resource group with project tagging."""
    if not resource_group_name or not region or not project_name:
        return "Error: All parameters (resource_group_name, region, project_name) are required."
    
    script_name = OP_SCRIPTS["create-rg"]
    script_path = _get_script_path(script_name)
    if not os.path.exists(script_path): 
        return f"Error: Script '{script_name}' not found."
    
    params = {
        "ResourceGroupName": resource_group_name,
        "Region": region,
        "ProjectName": project_name
    }
    return _run_powershell_script(script_path, params)

@mcp.tool()
def attach_diagnostic_settings(resource_group: str, workspace_id: str, resource_id: str) -> str:
    """
    Manually attaches diagnostic settings to a resource with a specified Log Analytics Workspace.
    Use this when multiple workspaces exist and user needs to select one.
    
    Args:
        resource_group: Resource group name
        workspace_id: Full resource ID of the Log Analytics Workspace
        resource_id: Full resource ID of the resource to attach diagnostic settings to
    """
    if not resource_group or not workspace_id or not resource_id:
        return "STOP: All parameters (resource_group, workspace_id, resource_id) are required."
    
    attach_law_script = _get_script_path("attach-log-analytics.ps1")
    if not os.path.exists(attach_law_script):
        return "Error: attach-log-analytics.ps1 not found."
    
    result = _run_powershell_script(
        attach_law_script,
        {
            "ResourceGroupName": resource_group,
            "WorkspaceId": workspace_id,
            "ResourceId": resource_id
        },
        timeout=30
    )
    
    return result

# Deprecated PowerShell script deployment methods removed.
# All deployments MUST use deploy_bicep_resource() for compliance orchestration.

@mcp.tool()
def get_bicep_requirements(resource_type: str) -> str:
    """(Bicep Path) Returns required/optional params for a Bicep template."""
    if resource_type not in TEMPLATE_MAP:
        return f"Unknown resource_type. Valid: {', '.join(TEMPLATE_MAP.keys())}"
    template_path = _get_template_path(TEMPLATE_MAP[resource_type])
    params = _parse_bicep_parameters(template_path)
    structured = {
        "required": [p for p, (req, _) in params.items() if req],
        "optional": [p for p, (req, _) in params.items() if not req],
        "defaults": {p: default for p, (req, default) in params.items() if default is not None}
    }
    return json.dumps(structured, indent=2)

@mcp.tool()
def create_azure_resource(resource_type: str, resource_group: str = "", parameters: dict = None) -> str:
    """
    Interactive Azure resource creation with automatic compliance orchestration.
    
    Workflow:
    1. Validates resource type
    2. Checks if resource group exists
    3. Requests missing required parameters from user
    4. Deploys resource using Bicep template
    5. Automatically attaches NSP if required (storage-account, key-vault, cosmos-db, sql-db)
    6. Automatically configures Log Analytics if required (monitoring resources)
    
    Args:
        resource_type: Type of resource to create (storage-account, key-vault, openai, ai-search, ai-foundry, cosmos-db, sql-db, log-analytics)
        resource_group: Azure resource group name (required)
        parameters: Dict of resource-specific parameters (will prompt for missing required params)
    
    Returns:
        Deployment status with compliance orchestration results
    
    Example:
        create_azure_resource(
            resource_type="storage-account",
            resource_group="my-rg",
            parameters={"storageAccountName": "mystg123", "location": "eastus"}
        )
    """
    # Initialize parameters if None
    if parameters is None:
        parameters = {}
    
    # Validate resource type
    if resource_type not in TEMPLATE_MAP:
        return f"❌ Invalid resource type. Supported types:\n" + "\n".join([f"  - {rt}" for rt in TEMPLATE_MAP.keys()])
    
    # Get template requirements
    template_path = _get_template_path(TEMPLATE_MAP[resource_type])
    param_info = _parse_bicep_parameters(template_path)
    required_params = [p for p, (req, _) in param_info.items() if req]
    optional_params = [p for p, (req, _) in param_info.items() if not req]
    
    # Check for missing parameters
    missing_params = []
    if not resource_group or not resource_group.strip():
        missing_params.append("resource_group")
    
    for param in required_params:
        if param not in parameters or not parameters.get(param):
            missing_params.append(param)
    
    # If parameters are missing, provide interactive prompt
    if missing_params:
        response = [f"📋 Creating {resource_type} - Please provide the following parameters:\n"]
        
        if "resource_group" in missing_params:
            response.append("  ✓ resource_group: (Azure resource group name)")
        
        for param in [p for p in missing_params if p != "resource_group"]:
            default_val = param_info[param][1]
            if default_val:
                response.append(f"  ✓ {param}: (default: {default_val})")
            else:
                response.append(f"  ✓ {param}: (required)")
        
        if optional_params:
            response.append(f"\n📌 Optional parameters: {', '.join(optional_params)}")
        
        response.append(f"\n💡 Once you provide these, I'll:\n")
        response.append(f"   1. Verify resource group exists")
        response.append(f"   2. Deploy the {resource_type}")
        if resource_type in NSP_MANDATORY_RESOURCES:
            response.append(f"   3. ✅ Attach to Network Security Perimeter (NSP)")
        if resource_type in LOG_ANALYTICS_MANDATORY_RESOURCES:
            response.append(f"   4. ✅ Configure Log Analytics diagnostic settings")
        
        return "\n".join(response)
    
    # All parameters provided - check RG exists first, then deploy
    rg_exists, rg_msg = _check_resource_group_exists(resource_group)
    if not rg_exists:
        return f"❌ {rg_msg}\n\n💡 Create it first: create_resource_group(resource_group_name='{resource_group}', region='eastus', project_name='your-project')"
    
    # RG exists - proceed with deployment
    return deploy_bicep_resource(resource_group, resource_type, parameters)

@mcp.tool()
def deploy_bicep_resource(resource_group: str, resource_type: str, parameters: dict[str, str]) -> str:
    """
    Internal deployment function - validates and deploys a resource with automatic compliance orchestration.
    
    ⚠️ Users should call create_azure_resource() instead for interactive parameter collection.
    
    This function:
    1. Validates resource group exists
    2. Validates all parameters against Bicep template
    3. Deploys the resource
    4. Automatically attaches NSP for: storage-account, key-vault, cosmos-db, sql-db
    5. Automatically configures Log Analytics for applicable resources
    """
    # Strict validation - reject if resource_group or resource_type is empty
    if not resource_group or not resource_group.strip():
        return "STOP: Resource group name is required. Please provide the resource group name."
    
    if not resource_type or not resource_type.strip():
        return f"STOP: Resource type is required. Valid types: {', '.join(TEMPLATE_MAP.keys())}"
    
    # Validate parameters against template
    ok, msg, parsed_params = _validate_bicep_parameters(resource_type, parameters)
    if not ok:
        # Provide helpful message with requirement details
        req_params = [p for p, (req, _) in parsed_params.items() if req]
        return f"STOP: {msg}\n\nPlease call get_bicep_requirements('{resource_type}') to see all required parameters.\nRequired: {', '.join(req_params) if req_params else 'unknown'}"
    
    return _deploy_bicep(resource_group, resource_type, parameters)

@mcp.tool()
def agent_dispatch(user_input: str) -> str:
    """High-level dispatcher for conversational commands."""
    intent = parse_intent(user_input)
    if intent in ("greeting", "menu"): return get_action_menu()
    if intent == "permissions": return list_permissions(force_refresh=True)
    if intent == "resources":
        rg = extract_resource_group(user_input)
        return list_resources(rg) if rg else list_resources()
    if intent == "create-rg":
        return (
            "Resource Group creation flow:\n\n"
            "Please provide:\n"
            "1. Resource Group Name\n"
            "2. Region (e.g., eastus, westus2, westeurope)\n"
            "3. Project Name (for tagging)\n\n"
            "Then call: create_resource_group(resource_group_name, region, project_name)"
        )
    if intent == "create":
        return (
            "🚀 Azure Resource Creation (Interactive Mode)\n\n"
            "To create a resource, use: create_azure_resource(resource_type, resource_group, parameters)\n\n"
            "Example: create_azure_resource(\n"
            "    resource_type='storage-account',\n"
            "    resource_group='my-rg',\n"
            "    parameters={'storageAccountName': 'mystg123', 'location': 'eastus'}\n"
            ")\n\n"
            "The agent will ask you for missing required parameters interactively.\n\n"
            "Supported resource types:\n"
            "  • storage-account (ADLS Gen2 enabled by default)\n"
            "  • key-vault\n"
            "  • openai\n"
            "  • ai-search\n"
            "  • ai-foundry\n"
            "  • cosmos-db\n"
            "  • sql-db\n"
            "  • log-analytics\n\n"
            "✅ Automatic Compliance:\n"
            "  - NSP attachment for: storage-account, key-vault, cosmos-db, sql-db\n"
            "  - Log Analytics for: monitoring-enabled resources\n\n"
            "💡 Tip: Start with just resource_type to see required parameters:\n"
            "   create_azure_resource(resource_type='storage-account')"
        )
    return "Unrecognized command. " + get_action_menu()

@mcp.tool()
def show_agent_instructions() -> str:
    return load_agent_instructions()

def main():
    """Entry point for the MCP server when installed as a package."""
    mcp.run()

if __name__ == "__main__":
    main()