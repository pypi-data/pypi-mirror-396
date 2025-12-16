from mcp.server.fastmcp import FastMCP
import subprocess
import os
import re
import shutil
import json
import time
from typing import Dict, Tuple, Optional, Union, Any

# Initialize the server
mcp = FastMCP("azure-agent")

# --- DEPLOYMENT ENFORCEMENT ---
# CRITICAL: All Azure resource deployments MUST go through MCP server tools.
# Direct az deployment commands are FORBIDDEN to ensure compliance orchestration.
ENFORCE_MCP_DEPLOYMENT = True

# --- INSTRUCTIONS LOADING ---

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
        "3. Create resource group (requires: name, region, project name)\n"
        "4. Create Azure resources with SFI compliance\n"
        "   Usage: create_azure_resource(resource_type, resource_group, **parameters)\n"
        "   \n"
        "   Interactive workflow:\n"
        "   - Call with resource_type (e.g., 'storage-account')\n"
        "   - Agent will ask for missing required parameters\n"
        "   - Provide parameters when prompted\n"
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
    "create-rg": "create-resourcegroup.ps1",
    "deploy-bicep": "deploy-bicep.ps1"
}

# --- HELPERS ---

def run_command(command: list[str]) -> str:
    """Generic command runner."""
    try:
        result = subprocess.run(
            command,
            shell=False, 
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=False,
            stdin=subprocess.DEVNULL,  # Prevents hanging on prompts
            timeout=120
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error running command {' '.join(command)}: {e.stderr}"

def _get_script_path(script_name: str) -> str:
    """Locates the script in the 'scripts' folder."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "scripts", script_name)

def _get_template_path(template_rel: str) -> str:
    """Locates the bicep file relative to server file."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), template_rel)

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
    Automatic NSP attachment workflow:
    1. Check if NSP required for this resource type
    2. Check if NSP exists using check-nsp.ps1
    3. If not exists, deploy NSP using templates/nsp.bicep
    4. Attach resource to NSP using attach-nsp.ps1
    """
    if resource_type not in NSP_MANDATORY_RESOURCES:
        return "" # No action needed

    log = ["\n🔒 NSP Compliance Check:"]
    log.append(f"   ✓ NSP required for {resource_type}")
    
    ps_executable = "pwsh" if shutil.which("pwsh") else "powershell"
    nsp_name = f"{resource_group}-nsp"
    
    # Step 1: Check if NSP exists using check-nsp.ps1
    check_nsp_script = _get_script_path("check-nsp.ps1")
    if not os.path.exists(check_nsp_script):
        log.append("   ⚠️  check-nsp.ps1 not found. Skipping NSP orchestration.")
        return "\n".join(log)
    
    log.append(f"   🔍 Checking NSP in '{resource_group}'...")
    nsp_check_result = run_command([
        ps_executable, "-File", check_nsp_script,
        "-ResourceGroupName", resource_group
    ])
    
    # Step 2: Deploy NSP if not exists
    if "not found" in nsp_check_result.lower() or "does not exist" in nsp_check_result.lower():
        log.append(f"   📦 NSP not found. Creating '{nsp_name}'...")
        
        # Deploy NSP using Bicep template
        nsp_template = _get_template_path("templates/nsp.bicep")
        if not os.path.exists(nsp_template):
            log.append("   ⚠️  NSP template not found. Please create NSP manually.")
            return "\n".join(log)
        
        location = _get_rg_location(resource_group)
        deploy_nsp_script = _get_script_path("deploy-bicep.ps1")
        nsp_params = f"nspName={nsp_name};location={location}"
        
        deploy_result = run_command([
            ps_executable, "-File", deploy_nsp_script,
            "-ResourceGroup", resource_group,
            "-TemplatePath", nsp_template,
            "-Parameters", nsp_params
        ])
        
        if "Error" in deploy_result or "FAILED" in deploy_result:
            log.append(f"   ❌ Failed to create NSP: {deploy_result}")
            return "\n".join(log)
        
        log.append(f"   ✅ NSP created: {nsp_name}")
        time.sleep(5)  # Wait for NSP to be ready
    else:
        log.append(f"   ✓ NSP exists: {nsp_name}")

    # Step 3: Get Resource ID
    resource_id = _get_resource_id(resource_group, resource_type, parameters)
    if not resource_id:
        log.append("   ⚠️  Could not determine resource ID. Skipping NSP attachment.")
        return "\n".join(log)

    # Step 4: Attach resource to NSP using attach-nsp.ps1
    attach_nsp_script = _get_script_path("attach-nsp.ps1")
    if not os.path.exists(attach_nsp_script):
        log.append("   ⚠️  attach-nsp.ps1 not found. Please attach resource manually.")
        return "\n".join(log)
    
    log.append(f"   🔗 Attaching resource to NSP...")
    attach_result = run_command([
        ps_executable, "-File", attach_nsp_script,
        "-ResourceGroupName", resource_group,
        "-NSPName", nsp_name,
        "-ResourceId", resource_id
    ])
    
    if "Error" in attach_result or "FAILED" in attach_result:
        log.append(f"   ❌ Failed to attach resource: {attach_result}")
    else:
        log.append(f"   ✅ Resource attached to NSP successfully")

    return "\n".join(log)

def _orchestrate_log_analytics_attachment(resource_group: str, resource_type: str, parameters: Dict[str, str]) -> str:
    """
    Automatic Log Analytics attachment workflow:
    1. Check if Log Analytics required for this resource type
    2. Check if LAW exists using check-log-analytics.ps1
    3. If not exists, deploy LAW using templates/log-analytics.bicep
    4. Attach diagnostic settings using attach-log-analytics.ps1
    """
    if resource_type not in LOG_ANALYTICS_MANDATORY_RESOURCES:
        return "" # No action needed

    log = ["\n📊 Log Analytics Compliance Check:"]
    log.append(f"   ✓ Log Analytics required for {resource_type}")
    
    ps_executable = "pwsh" if shutil.which("pwsh") else "powershell"
    workspace_name = f"{resource_group}-law"
    
    # Step 1: Check if Log Analytics Workspace exists using check-log-analytics.ps1
    check_law_script = _get_script_path("check-log-analytics.ps1")
    if not os.path.exists(check_law_script):
        log.append("   ⚠️  check-log-analytics.ps1 not found. Skipping Log Analytics orchestration.")
        return "\n".join(log)
    
    log.append(f"   🔍 Checking Log Analytics Workspace in '{resource_group}'...")
    law_check_result = run_command([
        ps_executable, "-File", check_law_script,
        "-ResourceGroupName", resource_group
    ])
    
    # Check if multiple workspaces exist and require user selection
    if "MULTIPLE LOG ANALYTICS WORKSPACES FOUND" in law_check_result or "RequiresSelection" in law_check_result:
        log.append("\n   ⚠️  [ACTION REQUIRED]")
        log.append("   Multiple Log Analytics Workspaces detected in this resource group.")
        log.append("   Please specify which workspace to use for diagnostic settings.")
        log.append("   Diagnostic settings attachment SKIPPED - awaiting user selection.")
        return "\n".join(log)
    
    # Step 2: Deploy Log Analytics Workspace if not exists
    if "not found" in law_check_result.lower() or "does not exist" in law_check_result.lower():
        log.append(f"   📦 Log Analytics Workspace not found. Creating '{workspace_name}'...")
        
        # Deploy LAW using Bicep template
        law_template = _get_template_path("templates/log-analytics.bicep")
        if not os.path.exists(law_template):
            log.append("   ⚠️  Log Analytics template not found. Please create workspace manually.")
            return "\n".join(log)
        
        location = _get_rg_location(resource_group)
        deploy_law_script = _get_script_path("deploy-bicep.ps1")
        law_params = f"workspaceName={workspace_name};location={location}"
        
        deploy_result = run_command([
            ps_executable, "-File", deploy_law_script,
            "-ResourceGroup", resource_group,
            "-TemplatePath", law_template,
            "-Parameters", law_params
        ])
        
        if "Error" in deploy_result or "FAILED" in deploy_result:
            log.append(f"   ❌ Failed to create Log Analytics Workspace: {deploy_result}")
            return "\n".join(log)
        
        log.append(f"   ✅ Log Analytics Workspace created: {workspace_name}")
        time.sleep(10)  # Wait for workspace to be fully provisioned
    else:
        log.append(f"   ✓ Log Analytics Workspace exists: {workspace_name}")
    
    # Step 3: Get workspace ID
    workspace_id = _get_workspace_id(resource_group, workspace_name)
    if not workspace_id:
        log.append("   ⚠️  Could not retrieve workspace ID. Skipping diagnostic settings.")
        return "\n".join(log)

    # Step 4: Get Resource ID
    resource_id = _get_resource_id(resource_group, resource_type, parameters)
    if not resource_id:
        log.append("   ⚠️  Could not determine resource ID. Skipping diagnostic settings.")
        return "\n".join(log)

    # Step 5: Attach diagnostic settings using attach-log-analytics.ps1
    attach_law_script = _get_script_path("attach-log-analytics.ps1")
    if not os.path.exists(attach_law_script):
        log.append("   ⚠️  attach-log-analytics.ps1 not found. Please attach diagnostic settings manually.")
        return "\n".join(log)
    
    log.append(f"   🔗 Attaching diagnostic settings...")
    attach_result = run_command([
        ps_executable, "-File", attach_law_script,
        "-ResourceGroupName", resource_group,
        "-WorkspaceId", workspace_id,
        "-ResourceId", resource_id
    ])
    
    if "Error" in attach_result or "FAILED" in attach_result:
        log.append(f"   ❌ Failed to attach diagnostic settings: {attach_result}")
    else:
        log.append(f"   ✅ Diagnostic settings attached successfully")

    return "\n".join(log)

def _get_subscription_id() -> str:
    """Fetches the current subscription ID."""
    try:
        res = run_command(["az", "account", "show", "--query", "id", "-o", "tsv"])
        return res.strip()
    except:
        return ""

def _get_workspace_id(resource_group: str, workspace_name: str) -> Optional[str]:
    """Retrieves the full resource ID of a Log Analytics workspace."""
    try:
        cmd = [
            "az", "monitor", "log-analytics", "workspace", "show",
            "-g", resource_group,
            "-n", workspace_name,
            "--query", "id",
            "-o", "tsv"
        ]
        result = run_command(cmd)
        return result.strip() if result.strip() else None
    except:
        return None

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
    if resource_type not in TEMPLATE_MAP:
        return f"Unknown resource_type '{resource_type}'."
    template_path = _get_template_path(TEMPLATE_MAP[resource_type])
    if not os.path.exists(template_path):
        return f"Template not found: {template_path}"
    
    # Build parameters string for PowerShell (semicolon-separated key=value pairs)
    param_string = ";".join([f"{k}={v}" for k, v in parameters.items()]) if parameters else ""
    
    # Call deploy-bicep.ps1 script
    script_name = OP_SCRIPTS["deploy-bicep"]
    script_path = _get_script_path(script_name)
    
    if not os.path.exists(script_path):
        return f"Error: Script '{script_name}' not found at {script_path}"
    
    script_params = {
        "ResourceGroup": resource_group,
        "TemplatePath": template_path
    }
    
    if param_string:
        script_params["Parameters"] = param_string
    
    deploy_result = _run_powershell_script(script_path, script_params)
    
    # Check if deployment was successful - look for success indicators
    deployment_successful = (
        "Error" not in deploy_result and 
        "FAILED" not in deploy_result and
        "Failed" not in deploy_result and
        len(deploy_result.strip()) > 0  # Ensure we got some output
    )
    
    if deployment_successful:
        # Wait for resource to be fully provisioned before attaching compliance features
        print(f"⏳ Waiting 15 seconds for {resource_type} to be fully provisioned...")
        time.sleep(15)
        
        # Auto-trigger compliance orchestration
        nsp_logs = _orchestrate_nsp_attachment(resource_group, resource_type, parameters)
        law_logs = _orchestrate_log_analytics_attachment(resource_group, resource_type, parameters)
        
        # Combine all results
        return f"{deploy_result}\n{nsp_logs}\n{law_logs}"
    
    return deploy_result

def _run_powershell_script(script_path: str, parameters: dict) -> str:
    ps_executable = "pwsh" if shutil.which("pwsh") else "powershell"
    cmd = [ps_executable, "-File", script_path]
    for k, v in parameters.items():
        if v is not None and v != "":
            cmd.append(f"-{k}")
            cmd.append(str(v))
    return run_command(cmd)

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
    
    ps_executable = "pwsh" if shutil.which("pwsh") else "powershell"
    result = run_command([
        ps_executable, "-File", attach_law_script,
        "-ResourceGroupName", resource_group,
        "-WorkspaceId", workspace_id,
        "-ResourceId", resource_id
    ])
    
    return result

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
def create_azure_resource(resource_type: str, resource_group: str = None, parameters: str = None) -> str:
    """
    Interactive Azure resource creation with automatic compliance orchestration.
    
    Workflow:
    1. Validates resource type
    2. Requests missing required parameters from user
    3. Deploys resource using Bicep template
    4. Automatically attaches NSP if required (storage-account, key-vault, cosmos-db, sql-db)
    5. Automatically configures Log Analytics if required (monitoring resources)
    
    Args:
        resource_type: Type of resource to create (storage-account, key-vault, openai, ai-search, ai-foundry, cosmos-db, sql-db, log-analytics)
        resource_group: Azure resource group name
        parameters: JSON string of resource-specific parameters (will prompt for missing required params)
    
    Returns:
        Deployment status with compliance orchestration results
    """
    # Validate resource type
    if resource_type not in TEMPLATE_MAP:
        return f"❌ Invalid resource type. Supported types:\n" + "\n".join([f"  - {rt}" for rt in TEMPLATE_MAP.keys()])
    
    # Parse parameters from JSON string if provided
    params_dict = {}
    if parameters:
        try:
            params_dict = json.loads(parameters)
        except json.JSONDecodeError:
            return f"Error: Invalid JSON in parameters. Please provide valid JSON format."
    
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
        if param not in params_dict or not params_dict.get(param):
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
        response.append(f"   1. Deploy the {resource_type}")
        if resource_type in NSP_MANDATORY_RESOURCES:
            response.append(f"   2. ✅ Attach to Network Security Perimeter (NSP)")
        if resource_type in LOG_ANALYTICS_MANDATORY_RESOURCES:
            response.append(f"   3. ✅ Configure Log Analytics diagnostic settings")
        
        return "\n".join(response)
    
    # All parameters provided - proceed with deployment
    return deploy_bicep_resource(resource_group, resource_type, params_dict)

@mcp.tool()
def deploy_bicep_resource(resource_group: str, resource_type: str, parameters: dict[str, str]) -> str:
    """
    Internal deployment function - validates and deploys a resource with automatic compliance orchestration.
    
    ⚠️ Users should call create_azure_resource() instead for interactive parameter collection.
    
    This function:
    1. Validates all parameters against Bicep template
    2. Deploys the resource
    3. Automatically attaches NSP for: storage-account, key-vault, cosmos-db, sql-db
    4. Automatically configures Log Analytics for applicable resources
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
            "To create a resource, use: create_azure_resource(resource_type, ...)\n\n"
            "Example: create_azure_resource('storage-account')\n"
            "The agent will then ask you for required parameters interactively.\n\n"
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
            "💡 Tip: You can provide all parameters at once if you know them:\n"
            "   create_azure_resource('storage-account', resource_group='my-rg', \n"
            "                        storageAccountName='mystg123', location='eastus', accessTier='Hot')"
        )
    return "Unrecognized command. " + get_action_menu()

@mcp.tool()
def show_agent_instructions() -> str:
    return load_agent_instructions()

if __name__ == "__main__":
    mcp.run()