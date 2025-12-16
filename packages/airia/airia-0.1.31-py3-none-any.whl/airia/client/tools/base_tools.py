from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

from ...types._api_version import ApiVersion
from .._request_handler import AsyncRequestHandler, RequestHandler


class BaseTools:
    def __init__(self, request_handler: Union[RequestHandler, AsyncRequestHandler]):
        self._request_handler = request_handler

    def _pre_create_tool(
        self,
        name: str,
        description: str,
        api_endpoint: str,
        method_type: str,
        purpose: str,
        body_type: str,
        category: str,
        provider: str,
        tool_type: str,
        body: str,
        headers: List[Dict[str, str]],
        parameters: List[Dict[str, Any]],
        request_timeout: int,
        route_through_acc: bool,
        should_redirect: bool,
        tool_credentials: Dict[str, Any],
        acc_group: Optional[str] = None,
        documentation: Optional[str] = None,
        project_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        tool_metadata: Optional[List[Dict[str, Any]]] = None,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for creating a new tool.

        This internal method constructs the URL and payload for tool creation
        requests, including all tool configuration and metadata.

        Args:
            name: Name of the tool
            description: Brief description of what the tool does
            api_endpoint: Web API endpoint where the tool sends its requests
            method_type: HTTP method type (Get, Post, Put, Delete)
            purpose: When and why to use this tool
            body_type: Type of the request body (Json, XFormUrlEncoded, None)
            category: Category of the tool (Action, Airia, Mcp)
            provider: Provider of the tool
            tool_type: Type of the tool (Custom, Calculator, MCP, etc.)
            body: Body of the request that the tool sends to the API
            headers: List of headers required when making the API request
            parameters: Collection of parameters required by the tool
            request_timeout: Request timeout in seconds for tool execution
            route_through_acc: Flag indicating whether the tool should route through the ACC
            should_redirect: Flag indicating whether the tool should redirect with authorization header
            tool_credentials: Tool credentials
            acc_group: Optional ACC specific group name
            documentation: Optional documentation for the tool
            project_id: Optional unique identifier of the project to which the tool is associated
            tags: Optional list of tags for the tool
            tool_metadata: Optional user provided metadata for the tool definition
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the tool creation endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(self._request_handler.base_url, f"{api_version}/Tools")

        payload: Dict[str, Any] = {
            "name": name,
            "description": description,
            "apiEndpoint": api_endpoint,
            "methodType": method_type,
            "purpose": purpose,
            "bodyType": body_type,
            "category": category,
            "provider": provider,
            "toolType": tool_type,
            "body": body,
            "headers": headers,
            "parameters": parameters,
            "requestTimeout": request_timeout,
            "routeThroughACC": route_through_acc,
            "shouldRedirect": should_redirect,
            "toolCredentials": tool_credentials,
        }

        # Add optional fields only if they are provided
        if acc_group is not None:
            payload["accGroup"] = acc_group
        if documentation is not None:
            payload["documentation"] = documentation
        if project_id is not None:
            payload["projectId"] = project_id
        if tags is not None:
            payload["tags"] = tags
        if tool_metadata is not None:
            payload["toolMetadata"] = tool_metadata

        request_data = self._request_handler.prepare_request(
            url=url, payload=payload, correlation_id=correlation_id
        )

        return request_data

    def _pre_delete_tool(
        self,
        tool_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for deleting a tool by ID.

        This internal method constructs the URL for tool deletion
        requests using the provided tool identifier.

        Args:
            tool_id: ID of the tool to delete
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the tool deletion endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(
            self._request_handler.base_url,
            f"{api_version}/Tools/{tool_id}",
        )
        request_data = self._request_handler.prepare_request(
            url, correlation_id=correlation_id
        )

        return request_data
