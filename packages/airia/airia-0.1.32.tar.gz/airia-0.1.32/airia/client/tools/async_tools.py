from typing import Any, Dict, List, Optional, Literal

from ...types._api_version import ApiVersion
from ...types.api.tools import CreateToolResponse
from .._request_handler import AsyncRequestHandler
from .base_tools import BaseTools


class AsyncTools(BaseTools):
    def __init__(self, request_handler: AsyncRequestHandler):
        super().__init__(request_handler)

    async def create_tool(
        self,
        name: str,
        description: str,
        purpose: str,
        api_endpoint: str,
        method_type: str,
        body: str,
        tool_credentials: Dict[str, Any],
        headers: List[Dict[str, str]] = [],
        parameters: List[Dict[str, Any]] = [],
        request_timeout: int = 100,
        body_type: Literal["Json", "XFormUrlEncoded", "None"] = "Json",
        category: Literal["Action", "Airia", "Mcp"] = "Airia",
        tool_type: str = "Custom",
        provider: str = "Custom",
        route_through_acc: bool = False,
        should_redirect: bool = True,
        acc_group: Optional[str] = None,
        documentation: Optional[str] = None,
        project_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        tool_metadata: Optional[List[Dict[str, Any]]] = None,
        correlation_id: Optional[str] = None,
    ) -> CreateToolResponse:
        """
        Create a new tool in the Airia platform.

        Args:
            name (str): Name of the tool.
            description (str): Brief description of what the tool does.
                Example: "Use this tool to get the current weather in a given location."
            api_endpoint (str): Web API endpoint where the tool sends its requests to
                perform its task.
            method_type (str): HTTP method type. Valid values: "Get", "Post", "Put", "Delete".
            purpose (str): When and why to use this tool.
                Example: "When a user asks about the weather, including current conditions,
                forecasts, or specific weather events."
            body_type (str): Type of the request body. Valid values: "Json", "XFormUrlEncoded", "None".
            category (str): Category of the tool. Valid values: "Action", "Airia", "Mcp".
            provider (str): Provider of the tool.
            tool_type (str): Type of the tool. Valid values: "Custom", "Calculator", "MCP",
                "LoadMemory", "StoreMemory", etc.
            body (str): Body of the request that the tool sends to the API.
            headers (list[dict]): List of headers required when making the API request.
                Each header should be a dictionary with "key" and "value" fields.
                Example: [{"key": "Content-Type", "value": "application/json"}]
            parameters (list[dict]): Collection of parameters required by the tool
                to execute its function.
            request_timeout (int): Request timeout in seconds for tool execution.
            route_through_acc (bool): Flag indicating whether the tool should route
                through the ACC.
            should_redirect (bool): Flag indicating whether the tool should redirect
                with authorization header attached.
            tool_credentials (dict): Tool credentials model.
            acc_group (str, optional): ACC specific group name. If provided, the tool will
                route through this ACC group.
            documentation (str, optional): Documentation for the tool.
            project_id (str, optional): Unique identifier of the project to which the tool
                is associated.
            tags (list[str], optional): List of tags for the tool.
            tool_metadata (list[dict], optional): User provided metadata for the tool definition.
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            CreateToolResponse: A response object containing the created tool details
                including its ID, creation timestamp, configuration, credentials,
                parameters, and all provided metadata.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - Invalid parameters are provided (400)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaAsyncClient
            import asyncio

            async def main():
                client = AiriaAsyncClient(api_key="your_api_key")

                # Create a weather tool with all required parameters
                tool = await client.tools.create_tool(
                    name="get_weather",
                    description="Use this tool to get the current weather in a given location.",
                    api_endpoint="https://api.weather.com/v1/current",
                    method_type="Get",
                    purpose="When a user asks about the weather, including current conditions.",
                    body_type="None",
                    category="Action",
                    provider="WeatherAPI",
                    tool_type="Custom",
                    body="",
                    headers=[],
                    parameters=[],
                    request_timeout=100,
                    route_through_acc=False,
                    should_redirect=False,
                    tool_credentials={}
                )
                print(f"Created tool: {tool.id}")

                # Create an email tool with headers and optional parameters
                tool = await client.tools.create_tool(
                    name="send_email",
                    description="Send an email to a recipient.",
                    api_endpoint="https://api.email-service.com/v1/send",
                    method_type="Post",
                    purpose="When a user wants to send an email message.",
                    body_type="Json",
                    category="Action",
                    provider="EmailService",
                    tool_type="Custom",
                    body='{"to": "{{recipient}}", "subject": "{{subject}}", "body": "{{message}}"}',
                    headers=[
                        {"key": "Content-Type", "value": "application/json"},
                        {"key": "Authorization", "value": "Bearer {{api_key}}"}
                    ],
                    parameters=[
                        {"name": "recipient", "type": "string", "required": True},
                        {"name": "subject", "type": "string", "required": True},
                        {"name": "message", "type": "string", "required": True}
                    ],
                    request_timeout=120,
                    route_through_acc=False,
                    should_redirect=False,
                    tool_credentials={},
                    documentation="This tool sends emails using the Email Service API.",
                    tags=["email", "communication"]
                )
                print(f"Created email tool: {tool.id}")

                await client.close()

            asyncio.run(main())
            ```

        Note:
            - Required parameters: name, description, api_endpoint, method_type, purpose,
              body_type, category, provider, tool_type, body, headers, parameters,
              request_timeout, route_through_acc, should_redirect, and tool_credentials.
            - Optional parameters: acc_group, documentation, project_id, tags, and tool_metadata.
            - The method_type must be one of: "Get", "Post", "Put", "Delete"
            - The body_type must be one of: "Json", "XFormUrlEncoded", "None"
            - The category must be one of: "Action", "Airia", "Mcp"
            - The tool_type must be one of: "Custom", "Calculator", "MCP", "LoadMemory",
              "StoreMemory", etc.
        """
        request_data = self._pre_create_tool(
            name=name,
            description=description,
            api_endpoint=api_endpoint,
            method_type=method_type,
            purpose=purpose,
            body_type=body_type,
            category=category,
            provider=provider,
            tool_type=tool_type,
            body=body,
            headers=headers,
            parameters=parameters,
            request_timeout=request_timeout,
            route_through_acc=route_through_acc,
            should_redirect=should_redirect,
            tool_credentials=tool_credentials,
            acc_group=acc_group,
            documentation=documentation,
            project_id=project_id,
            tags=tags,
            tool_metadata=tool_metadata,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        resp = await self._request_handler.make_request("POST", request_data)

        return CreateToolResponse(**resp)

    async def delete_tool(
        self,
        tool_id: str,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Delete a tool by its ID.

        This method permanently removes a tool from the Airia platform.
        This action cannot be undone.

        Args:
            tool_id (str): The unique identifier of the tool to delete.
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            None: This method returns nothing upon successful deletion.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The tool_id doesn't exist (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaAsyncClient
            import asyncio

            async def main():
                client = AiriaAsyncClient(api_key="your_api_key")

                # Delete a tool
                await client.tools.delete_tool(tool_id="tool_123")
                print("Tool deleted successfully")

                # Handle deletion errors
                from airia.exceptions import AiriaAPIError

                try:
                    await client.tools.delete_tool(tool_id="nonexistent_id")
                except AiriaAPIError as e:
                    if e.status_code == 404:
                        print("Tool not found")
                    else:
                        print(f"Error deleting tool: {e.message}")

                await client.close()

            asyncio.run(main())
            ```

        Note:
            This operation is permanent and cannot be undone. Make sure you have
            the correct tool_id before calling this method.
        """
        request_data = self._pre_delete_tool(
            tool_id=tool_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        await self._request_handler.make_request(
            "DELETE", request_data, return_json=False
        )
