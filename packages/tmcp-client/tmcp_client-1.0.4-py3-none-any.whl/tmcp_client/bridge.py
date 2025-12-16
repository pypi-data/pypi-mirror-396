"""TMCP Bridge - Core MCP client implementation for TowardsAGI servers."""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
import httpx
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class TMCPBridge:
    """Lightweight MCP bridge for TowardsAGI MCP servers."""
    
    def __init__(self):
        """Initialize the bridge with environment variables."""
        self.server_url = os.getenv('TOWARDSMCP_SERVER_URL')
        self.resource_name = os.getenv('TOWARDSMCP_RESOURCE')
        self.api_key = os.getenv('TOWARDSMCP_API_KEY')
        
        if not all([self.server_url, self.resource_name, self.api_key]):
            raise ValueError(
                "Missing required environment variables:\n"
                "- TOWARDSMCP_SERVER_URL: The base URL of your TMCP server\n"
                "- TOWARDSMCP_RESOURCE: The resource name to connect to\n"
                "- TOWARDSMCP_API_KEY: Your API key for authentication"
            )
        
        # Ensure server URL ends with /
        if not self.server_url.endswith('/'):
            self.server_url += '/'
        
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'tmcp-client/1.0.0'
            }
        )
        
        logger.info(f"🔗 TMCP Bridge initialized for '{self.resource_name}' at {self.server_url}")
    
    async def get_server_info(self) -> Dict[str, Any]:
        """Get server information and capabilities."""
        try:
            # Try to get resource info first
            url = urljoin(self.server_url, f'api/resources/{self.resource_name}')
            response = await self.client.get(url)
            
            if response.status_code == 200:
                resource_info = response.json()
                return {
                    "name": f"TowardsAGI MCP Server - {self.resource_name}",
                    "version": "1.0.0",
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": {
                        "name": "TowardsAGI MCP Server",
                        "version": "1.0.0",
                        "resource": self.resource_name,
                        "type": resource_info.get("type", "unknown")
                    }
                }
            else:
                logger.warning(f"Could not fetch resource info: HTTP {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Failed to get detailed server info: {e}")
        
        # Fallback server info
        return {
            "name": f"TowardsAGI MCP Server - {self.resource_name}",
            "version": "1.0.0",
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {}
            },
            "serverInfo": {
                "name": "TowardsAGI MCP Server",
                "version": "1.0.0",
                "resource": self.resource_name
            }
        }
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools for the resource."""
        try:
            url = urljoin(self.server_url, f'api/resources/{self.resource_name}/tools')
            response = await self.client.get(url)
            response.raise_for_status()
            
            tools_data = response.json()
            
            # Handle both formats: direct array or nested object with 'tools' key
            if isinstance(tools_data, dict) and 'tools' in tools_data:
                tools_list = tools_data['tools']
            elif isinstance(tools_data, list):
                tools_list = tools_data
            else:
                logger.error(f"Unexpected tools data format: {type(tools_data)}")
                return []
            
            # Convert to MCP format
            mcp_tools = []
            for tool in tools_list:
                mcp_tool = {
                    "name": tool["name"],
                    "description": tool["description"],
                    "inputSchema": tool.get("inputSchema", {
                        "type": "object",
                        "properties": {},
                        "required": []
                    })
                }
                mcp_tools.append(mcp_tool)
            
            logger.info(f"📋 Found {len(mcp_tools)} tools for resource '{self.resource_name}'")
            return mcp_tools
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("❌ Authentication failed. Please check your TOWARDSMCP_API_KEY")
            elif e.response.status_code == 404:
                logger.error(f"❌ Resource '{self.resource_name}' not found")
            else:
                logger.error(f"❌ HTTP {e.response.status_code}: {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"❌ Failed to list tools: {e}")
            return []
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the server."""
        try:
            url = urljoin(self.server_url, 'api/tools/execute')
            
            payload = {
                "tool_name": name,
                "arguments": arguments,
                "resource_name": self.resource_name
            }
            
            logger.debug(f"🔧 Calling tool '{name}' with arguments: {arguments}")
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            api_response = response.json()
            
            # Unwrap the API response to get just the tool result
            if isinstance(api_response, dict) and "result" in api_response:
                tool_result = api_response["result"]
            else:
                tool_result = api_response
            
            # Format as MCP response
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(tool_result, indent=2)
                    }
                ]
            }
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}"
            try:
                error_detail = e.response.json().get("detail", e.response.text)
                error_msg += f": {error_detail}"
            except:
                error_msg += f": {e.response.text}"
            
            logger.error(f"❌ Tool call failed: {error_msg}")
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": f"Error calling tool '{name}': {error_msg}"
                    }
                ],
                "isError": True
            }
        except Exception as e:
            logger.error(f"❌ Tool call failed: {e}")
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": f"Error calling tool '{name}': {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class MCPServer:
    """MCP Server implementation using the TMCP bridge."""
    
    def __init__(self):
        self.bridge = TMCPBridge()
        self.server_info = None
        self.tools = []
    
    async def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the MCP server."""
        try:
            self.server_info = await self.bridge.get_server_info()
            self.tools = await self.bridge.list_tools()
            
            logger.info(f"✅ Initialized with {len(self.tools)} tools")
            
            return {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": self.server_info.get("serverInfo", {
                    "name": "TowardsAGI MCP Server",
                    "version": "1.0.0"
                })
            }
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    async def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request."""
        return {"tools": self.tools}
    
    async def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            raise ValueError("Tool name is required")
        
        return await self.bridge.call_tool(tool_name, arguments)
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request."""
        method = request.get("method")
        params = request.get("params", {})
        # Preserve the exact id from the request - Claude matches responses by id
        # Use 'is None' check because 0 is a valid id but falsy in Python
        request_id = request.get("id")
        if request_id is None:
            request_id = "1"
        
        try:
            if method == "initialize":
                result = await self.initialize(params)
            elif method == "tools/list":
                result = await self.handle_tools_list(params)
            elif method == "tools/call":
                result = await self.handle_tools_call(params)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling request {method}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -1,
                    "message": str(e)
                }
            }
    
    async def run(self):
        """Run the MCP server (stdio mode)."""
        logger.info("🚀 Starting TMCP client bridge...")
        
        try:
            while True:
                # Read JSON-RPC request from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
                try:
                    request = json.loads(line.strip())
                    response = await self.handle_request(request)
                    
                    # Write JSON-RPC response to stdout
                    print(json.dumps(response))
                    sys.stdout.flush()
                    
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Invalid JSON received: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": "error",  # Must be non-null for Claude compatibility
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                    
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down...")
        except Exception as e:
            logger.error(f"❌ Server error: {e}")
            raise
        finally:
            await self.bridge.close()


async def main():
    """Main entry point for the MCP bridge."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )
    
    try:
        server = MCPServer()
        await server.run()
    except Exception as e:
        logger.error(f"❌ Failed to start TMCP client: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
