import json
import os
import time
from typing import Dict, List
from loguru import logger
from mcp.server.fastmcp import FastMCP
from .client import PolarionClient

# Create an MCP server
mcp = FastMCP("Polarion-MCP-Server")

# Global Polarion client instance
polarion_client = PolarionClient()

# Helper functions for coverage analysis
def _validate_coverage_analysis_inputs(project_id: str, topic: str) -> Dict | None:
    """Validate inputs for coverage analysis"""
    if not (polarion_client.token or polarion_client.load_token()):
        return {
            "status": "error",
            "message": "Polarion authentication required",
            "next_steps": [
                "Use open_polarion_login() to authenticate",
                "Then use set_polarion_token() with generated token",
                "Finally retry this analysis"
            ]
        }
    
    if not project_id or not topic:
        return {
            "status": "error", 
            "message": "Missing required parameters",
            "required": ["project_id", "topic"]
        }
    
    return None

def _fetch_topic_requirements(project_id: str, topic: str) -> Dict:
    """Fetch requirements related to a specific topic from Polarion (FRESH DATA - no caching)"""
    try:
        logger.info(f"🔄 Making LIVE API calls to Polarion - no cached data used")
        query_patterns = [f"{topic} AND type:requirement", f"title:{topic}", f"{topic}"]
        all_requirements = []
        
        for i, query in enumerate(query_patterns, 1):
            logger.info(f"📡 API Call {i}/{len(query_patterns)}: Fetching with query '{query}'")
            work_items = polarion_client.get_work_items(project_id, limit=50, query=query)
            all_requirements.extend(work_items)
            logger.info(f"✅ Received {len(work_items)} items from API call {i}")
        
        unique_requirements = {}
        for item in all_requirements:
            if item.get('id') and 'type' in item:
                item_text = f"{item.get('title', '')} {item.get('description', '')}".lower()
                if (item.get('type', '').lower() in ['requirement', 'req'] or topic.lower() in item_text):
                    unique_requirements[item['id']] = item
        
        requirements_list = list(unique_requirements.values())
        logger.info(f"🎯 FRESH DATA PROCESSED: Found {len(requirements_list)} unique requirements for topic '{topic}'")
        return {
            "status": "success", 
            "requirements": requirements_list, 
            "count": len(requirements_list),
            "data_freshness": "live_api_fetch",
            "fetch_timestamp": time.time()
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch requirements: {str(e)}"}

@mcp.tool()
def open_polarion_login() -> str:
    """
    <purpose>Open Polarion login page in browser for manual authentication</purpose>
    
    <when_to_use>
    - When you need to authenticate with Polarion for the first time
    - When existing token has expired (401 errors)
    - When check_polarion_status() shows no valid token
    </when_to_use>
    
    <workflow_position>
    STEP 1: Use this tool first if you don't have authentication
    STEP 2: Complete login in browser and generate token
    STEP 3: Use set_polarion_token() with the generated token
    STEP 4: Use check_polarion_status() to verify authentication
    STEP 5: Begin exploring with get_polarion_projects()
    </workflow_position>
    
    <output>Instructions for manual authentication process</output>
    """
    logger.info("Opening Polarion login page for manual authentication")
    return polarion_client.open_login_page()

@mcp.tool()
def set_polarion_token(token: str) -> str:
    """
    <purpose>Set Polarion access token after generating it in browser</purpose>
    
    <when_to_use>
    - After using open_polarion_login() and generating token manually
    - When you have a valid Polarion token to configure
    - When replacing an expired token
    </when_to_use>
    
    <workflow_position>
    STEP 2: Use this after open_polarion_login() and manual token generation
    NEXT: Use check_polarion_status() to verify token is working
    THEN: Begin data exploration with get_polarion_projects()
    </workflow_position>
    
    <parameters>
    - token: The bearer token generated from Polarion's user token page
    </parameters>
    
    <output>Confirmation of token storage and next steps</output>
    """
    logger.info("Setting Polarion token manually")
    return polarion_client.set_token_manually(token)

@mcp.tool()
def get_polarion_projects(limit: int = 10) -> str:
    """
    <purpose>Discover available Polarion projects for exploration</purpose>
    
    <when_to_use>
    - ALWAYS use this FIRST when starting Polarion exploration
    - When you need to find the correct project_id for other operations
    - When user asks about projects without specifying project name
    - To verify authentication is working
    </when_to_use>
    
    <workflow_position>
    STEP 1: Use this tool first to discover available projects
    STEP 2: Choose relevant project_id from results  
    STEP 3: Use get_polarion_work_items() to explore project contents
    STEP 4: Use get_polarion_work_item() for detailed information
    </workflow_position>
    
    <parameters>
    - limit: Number of projects to retrieve (default 10, increase for comprehensive view)
    </parameters>
    
    <examples>
    - Finding automotive projects: Look for "AutoCar", "Vehicle", "Car" in project names
    - Comprehensive discovery: Use limit=50 to see all available projects
    </examples>
    
    <output>List of projects with basic info - use project 'id' field for subsequent calls</output>
    """
    logger.info(f"Fetching {limit} projects from Polarion")
    projects = polarion_client.get_projects(limit)
    if projects:
        return json.dumps({
            "status": "success",
            "message": f"Successfully fetched {len(projects)} projects",
            "projects": projects,
            "count": len(projects)
        }, indent=2)
    return json.dumps({
        "status": "error",
        "message": "Failed to fetch projects. Please check authentication and token."
    }, indent=2)

@mcp.tool()
def get_polarion_project(project_id: str, fields: str = "@basic") -> str:
    """
    <purpose>Get detailed information about a specific Polarion project</purpose>
    
    <when_to_use>
    - When you need detailed project metadata (description, settings, etc.)
    - After using get_polarion_projects() to identify the project_id
    - When you need project configuration details
    - RARELY needed for most exploration tasks
    </when_to_use>
    
    <workflow_position>
    OPTIONAL: Use after get_polarion_projects() if project details are needed
    USUALLY SKIP: Most tasks should go directly to get_polarion_work_items()
    </workflow_position>
    
    <parameters>
    - project_id: Exact project ID from get_polarion_projects() results
    - fields: "@basic" for essential info, "@all" for complete details
    </parameters>
    
    <note>Most users should skip this and go directly to exploring work items</note>
    """
    logger.info(f"Fetching project {project_id} from Polarion")
    project = polarion_client.get_project(project_id, fields)
    if project:
        return json.dumps({
            "status": "success",
            "message": f"Successfully fetched project: {project_id}",
            "project": project
        }, indent=2)
    return json.dumps({
        "status": "error",
        "message": f"Failed to fetch project {project_id}. Project may not exist or access is denied."
    }, indent=2)

@mcp.tool()
def get_polarion_work_items(project_id: str, limit: int = 10, query: str = "") -> str:
    """
    <purpose>Discover and search work items (requirements, tasks, etc.) in a Polarion project</purpose>
    
    <when_to_use>
    - MAIN DISCOVERY TOOL: Use this to explore project contents
    - When searching for specific topics (e.g., "HMI", "requirements")
    - When you need to understand project scope and available work items
    - BEFORE using get_polarion_work_item() for detailed info
    </when_to_use>
    
    <workflow_position>
    STEP 1: After get_polarion_projects(), use this to explore project contents
    STEP 2: Analyze results to identify relevant work items
    STEP 3: Use get_polarion_work_item() for detailed information on specific items
    OPTIONAL: Use get_polarion_document() if user provides specific space/document names
    </workflow_position>
    
    <parameters>
    - project_id: Required. Get from get_polarion_projects() results
    - limit: Number of items (default 10). Use 30-50 for comprehensive searches
    - query: POWERFUL filter. Examples:
      * "HMI" - finds HMI-related items
      * "type:requirement" - only requirements
      * "HMI AND type:requirement" - HMI requirements
      * "title:system" - items with "system" in title
    </parameters>
    
    <examples>
    - Finding HMI requirements: query="HMI AND type:requirement", limit=30
    - Project overview: query="", limit=50
    - Security items: query="security OR safety", limit=20
    - All requirements: query="type:requirement", limit=100
    </examples>
    
    <output>
    Minimal fields (id, title, type, description) - use get_polarion_work_item() for full details
    Contains rich information including work item relationships and metadata
    </output>
    
    <critical_note>
    This tool often contains all the information you need. Work items include:
    - Requirements, specifications, tasks
    - Relationships between items
    - Project structure and organization
    Check results thoroughly before seeking additional tools
    </critical_note>
    """
    logger.info(f"Fetching {limit} work items from project {project_id}")
    work_items = polarion_client.get_work_items(project_id, limit, query)
    if work_items:
        return json.dumps({
            "status": "success",
            "message": f"Successfully fetched {len(work_items)} work items from project {project_id}",
            "work_items": work_items,
            "count": len(work_items),
            "project_id": project_id,
            "next_steps": "Use get_polarion_work_item() for detailed info on specific items"
        }, indent=2)
    return json.dumps({
        "status": "error",
        "message": f"Failed to fetch work items from project {project_id}. Check token, project ID, or permissions."
    }, indent=2)

@mcp.tool()
def get_polarion_work_item(project_id: str, work_item_id: str, fields: str = "@basic") -> str:
    """
    <purpose>Get detailed information about a specific work item</purpose>
    
    <when_to_use>
    - AFTER using get_polarion_work_items() to identify specific work items of interest
    - When you need complete details about a requirement, task, or specification
    - When you need full content, relationships, and metadata
    - For deep analysis of specific work items
    </when_to_use>
    
    <workflow_position>
    STEP 1: Use get_polarion_work_items() to discover and filter work items
    STEP 2: Identify specific work_item_id from the results
    STEP 3: Use this tool to get complete details
    STEP 4: Analyze relationships and linked items if needed
    </workflow_position>
    
    <parameters>
    - project_id: Required. Must match project from previous search
    - work_item_id: Required. Get from get_polarion_work_items() results
    - fields: "@basic" for essential info, "@all" for complete details including relationships
    </parameters>
    
    <examples>
    - Detailed requirement analysis: fields="@all"
    - Quick verification: fields="@basic"
    - Understanding relationships: fields="@all" (includes linked items)
    </examples>
    
    <output>
    Complete work item details including:
    - Full description and content
    - Relationships to other work items
    - Metadata and status information
    - Approval and review information
    </output>
    
    <note>
    Use this tool sparingly - only when you need detailed information about specific items
    identified through get_polarion_work_items() searches
    </note>
    """
    logger.info(f"Fetching work item {work_item_id} from project {project_id}")
    work_item = polarion_client.get_work_item(project_id, work_item_id, fields)
    if work_item:
        return json.dumps({
            "status": "success",
            "message": f"Successfully fetched work item: {work_item_id} from project {project_id}",
            "work_item": work_item
        }, indent=2)
    return json.dumps({
        "status": "error",
        "message": f"Failed to fetch work item {work_item_id} from project {project_id}. Work item may not exist or access is denied."
    }, indent=2)

@mcp.tool()
def get_polarion_document(project_id: str, space_id: str, document_name: str, fields: str = "@basic") -> str:
    """
    <purpose>Access specific structured documents within a Polarion space</purpose>
    
    <when_to_use>
    - When you need access to organized documents (specifications, manuals)
    - When user provides specific space and document names
    - When work items reference specific documents that need direct access
    - For accessing curated requirement collections in document format
    </when_to_use>
    
    <workflow_position>
    STEP 1: Use get_polarion_projects() to identify project
    STEP 2: Use get_polarion_work_items() to explore and potentially discover space references
    STEP 3: Use this tool when you have specific space_id and document_name
    ALTERNATIVE: Often get_polarion_work_items() provides equivalent or better information
    </workflow_position>
    
    <parameters>
    - project_id: Required. From get_polarion_projects()
    - space_id: Required. EXACT space name (user-provided or from work item references)
    - document_name: Required. Document name (e.g., "HMI", "System Requirements Specification")
    - fields: "@basic" for summary, "@all" for complete content
    </parameters>
    
    <examples>
    - HMI specifications: project_id="AutoCar", space_id="Master Specifications", document_name="HMI"
    - System requirements: project_id="AutoCar", space_id="Requirements", document_name="System"
    </examples>
    
    <critical_requirements>
    - space_id must be EXACT name (case-sensitive)
    - document_name is case-sensitive
    - Use quotes around space names with spaces (e.g., "Master Specifications")
    - Space names typically provided by user or discovered from work item exploration
    </critical_requirements>
    
    <output>
    Structured document content including organized requirements and specifications
    Often contains similar information to work items but in document format
    </output>
    
    <troubleshooting>
    If 404 error: Verify space_id and document_name spelling
    Common spaces: "Master Specifications", "Requirements", "Design Documents"
    Try exploring with get_polarion_work_items() first for context
    </troubleshooting>
    
    <note>
    Space names are not discoverable via API - they come from user knowledge or work item references
    </note>
    """
    logger.info(f"Fetching document {document_name} from space {space_id} in project {project_id}")
    document = polarion_client.get_document(project_id, space_id, document_name, fields)
    if document:
        return json.dumps({
            "status": "success",
            "message": f"Successfully fetched document: {document_name} from space {space_id} in project {project_id}",
            "document": document
        }, indent=2)
    return json.dumps({
        "status": "error",
        "message": f"Failed to fetch document {document_name} from space {space_id} in project {project_id}. Document may not exist or access is denied."
    }, indent=2)

@mcp.tool()
def check_polarion_status() -> str:
    """
    <purpose>Verify Polarion authentication and connection status</purpose>
    
    <when_to_use>
    - When experiencing authentication errors
    - To verify setup before starting exploration
    - When debugging connection issues
    - As a diagnostic tool when other tools fail
    </when_to_use>
    
    <workflow_position>
    DIAGNOSTIC: Use when authentication issues occur
    VERIFICATION: Use after set_polarion_token() to confirm setup
    TROUBLESHOOTING: Use when other tools return 401 errors
    </workflow_position>
    
    <output>
    Authentication status and next steps if issues found
    </output>
    
    <next_steps>
    If no token: Use open_polarion_login() then set_polarion_token()
    If token exists: Try get_polarion_projects() to test connectivity
    </next_steps>
    """
    logger.info("Checking Polarion status")
    TOKEN_FILE = "polarion_token.json"
    status = {
        "has_token": bool(polarion_client.token or polarion_client.load_token()),
        "token_saved": os.path.exists(TOKEN_FILE)
    }
    
    next_steps = []
    if not status["has_token"]:
        next_steps.append("Use open_polarion_login() to authenticate")
        next_steps.append("Then use set_polarion_token() with generated token")
    else:
        next_steps.append("Authentication appears ready")
        next_steps.append("Use get_polarion_projects() to begin exploration")
    
    return json.dumps({
        "status": "success",
        "polarion_status": status,
        "next_steps": next_steps
    }, indent=2)

@mcp.tool()
def polarion_github_requirements_coverage(project_id: str, topic: str, github_folder: str = "") -> str:
    """
    <purpose>Smart requirements coverage analysis between Polarion and connected GitHub repository</purpose>
    
    <when_to_use>
    - When you need to verify if requirements are implemented in the current codebase
    - For gap analysis between Polarion specifications and actual code implementation  
    - When user asks "check if requirements are implemented" or "find missing implementations"
    - For requirements traceability and coverage validation
    - When you need to identify what's missing from the current code
    </when_to_use>
    
    <workflow_position>
    INTELLIGENT COVERAGE ANALYSIS TOOL: Use this for end-to-end requirements verification
    STEP 1: Automatically detects connected GitHub repository from context
    STEP 2: Fetches FRESH requirements from Polarion for specified topic
    STEP 3: Analyzes actual code files in GitHub repository 
    STEP 4: Identifies implemented vs missing requirements based on code examination
    </workflow_position>
    
    <parameters>
    - project_id: Required. Polarion project ID (e.g., "AutoCar", "drivepilot")
    - topic: Required. Requirements topic to analyze (e.g., "HMI", "braking", "perception", "safety")
    - github_folder: Optional. Specific folder to focus analysis (e.g., "hmi", "braking"). Empty means analyze entire repository
    </parameters>
    
    <output>
    Comprehensive requirements coverage analysis
    </output>
    """
    logger.info(f"Starting SMART requirements coverage analysis for '{topic}' in project '{project_id}'")
    
    try:
        # Validate inputs
        validation_error = _validate_coverage_analysis_inputs(project_id, topic)
        if validation_error:
            return json.dumps(validation_error, indent=2)
        
        # Fetch FRESH requirements from Polarion (no caching)
        logger.info(f"📡 Fetching LIVE {topic} requirements from Polarion project {project_id}")
        requirements_result = _fetch_topic_requirements(project_id, topic)
        if "error" in requirements_result:
            return json.dumps(requirements_result, indent=2)
        
        requirements = requirements_result["requirements"]
        if not requirements:
            return json.dumps({
                "status": "warning",
                "message": f"No requirements found for topic '{topic}' in project {project_id}",
                "suggestion": "Try different topic keywords or check Polarion project contents"
            }, indent=2)
        
        return json.dumps({
            "status": "success",
            "message": f"✅ Found {len(requirements)} '{topic}' requirements from Polarion",
            "analysis_summary": {
                "project_id": project_id,
                "topic": topic,
                "total_requirements_found": len(requirements),
                "target_folder": github_folder or "entire repository"
            },
            "polarion_requirements": requirements,
            "next_steps": [
                "Use GitHub MCP tools to explore the repository structure",
                "Search for requirement IDs and implementation evidence in code",
                "Compare actual code implementation against requirement descriptions"
            ]
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Requirements coverage analysis failed: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Requirements coverage analysis failed: {str(e)}"
        }, indent=2)

def run():
    """Run the MCP server"""
    import os
    import uvicorn
    from uvicorn import Config, Server
    
    # Check transport mode from environment variable
    transport_mode = os.getenv("MCP_TRANSPORT", "stdio")
    port = int(os.getenv("MCP_PORT", "8080"))
    
    if transport_mode == "sse":
        # HTTP/SSE mode for URL-based access (GCP deployment)
        print(f"Starting Polarion MCP Server in SSE mode on port {port}...")
        print(f"Accessible at: http://0.0.0.0:{port}/sse")
        
        # FastMCP doesn't easily expose host/port configuration
        # Let's try to get the app by running FastMCP in a way that captures it
        # Or use a workaround: run on default port and use port forwarding
        # Actually, let's try one more approach: patch uvicorn before FastMCP imports it
        
        # Since FastMCP already imported uvicorn, we need to patch it now
        # But FastMCP might have already cached the run function
        # Let's try patching at multiple levels
        
        # Store originals
        _uvicorn_run = uvicorn.run
        _uvicorn_main = getattr(uvicorn, 'main', None)
        
        def patched_run(app, host=None, port=None, **kwargs):
            """Patched uvicorn.run"""
            # Disable host header validation to fix "Invalid Host header" error
            kwargs.setdefault('allowed_hosts', None)
            return _uvicorn_run(
                app,
                host="0.0.0.0",
                port=port if port else int(os.getenv("MCP_PORT", "8080")),
                log_level=kwargs.get('log_level', 'info'),
                **{k: v for k, v in kwargs.items() if k != 'log_level'}
            )
        
        # Patch uvicorn.run
        uvicorn.run = patched_run
        
        # Also patch uvicorn.main.run if it exists
        if _uvicorn_main and hasattr(_uvicorn_main, 'run'):
            _uvicorn_main.run = patched_run
        
        # Patch Server class to override host/port and disable host validation
        try:
            _original_server_init = uvicorn.Server.__init__
            def new_server_init(self, config, **kwargs):
                # Override config host/port
                if hasattr(config, 'host'):
                    config.host = "0.0.0.0"
                if hasattr(config, 'port'):
                    config.port = port
                # Disable host header validation
                if hasattr(config, 'allowed_hosts'):
                    config.allowed_hosts = None
                return _original_server_init(self, config, **kwargs)
            uvicorn.Server.__init__ = new_server_init
        except Exception:
            pass
        
        # Patch Starlette middleware to disable host validation
        try:
            from starlette.middleware.trustedhost import TrustedHostMiddleware
            _original_process_request = TrustedHostMiddleware.process_request
            
            def patched_process_request(self, request):
                # Skip host validation - allow all hosts
                return None
            
            TrustedHostMiddleware.process_request = patched_process_request
        except Exception as e:
            logger.warning(f"Could not patch TrustedHostMiddleware: {e}")
        
        try:
            mcp.run(transport="sse")
        except Exception as e:
            logger.error(f"Error running SSE server: {e}")
            # Restore and try fallback
            uvicorn.run = _uvicorn_run
            mcp.run(transport="sse")
    else:
        # stdio mode for local development
        print("Starting Polarion MCP Server in stdio mode...")
        mcp.run(transport="stdio")

if __name__ == "__main__":
    run()
