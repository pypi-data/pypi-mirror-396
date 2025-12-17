"""
Pydantic models for tool management API responses.

This module defines data structures for tool operations including
creation and configuration within the Airia platform.
"""

from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field


class ToolHeader(BaseModel):
    """Key-value pair header for a tool definition.

    Attributes:
        key: The key of the header
        value: The value of the header
    """

    key: str
    value: str


class ToolParameter(BaseModel):
    """Parameter definition for a tool.

    Attributes:
        name: Name of the parameter
        type: Type of the parameter
        description: Description of what the parameter does
        default: Default value for the parameter
        valid_options: List of valid options for the parameter
        array_item_type: Type of items if this parameter is an array
        parameters: Nested parameters for complex types
        requirement: Whether the parameter is required or optional
    """

    name: str
    type: str
    description: str
    default: Optional[str] = None
    valid_options: Optional[List[str]] = Field(None, alias="validOptions")
    array_item_type: Optional[str] = Field(None, alias="arrayItemType")
    parameters: Optional[List["ToolParameter"]] = None
    requirement: str


class ToolCredentialSettings(BaseModel):
    """Settings for tool credentials.

    Attributes:
        available_credential_types: List of available credential types
        default_value: Default credential value
        platform_supported_oauth_types: List of OAuth types supported by the platform
    """

    available_credential_types: List[str] = Field(alias="availableCredentialTypes")
    default_value: Optional[str] = Field(None, alias="defaultValue")
    platform_supported_oauth_types: List[str] = Field(
        alias="platformSupportedOAuthTypes"
    )


class CredentialEntry(BaseModel):
    """Represents a deserialized object for each entry of a credential.

    Attributes:
        key: The property name of the API Key for credentials data
        value: The value of the credential
    """

    key: str
    value: str


class ToolCredential(BaseModel):
    """Tool credential information.

    Attributes:
        id: Unique identifier for the credential
        name: Name of the credential
        display_identifier_name: Display name for the credential identifier
        created_at: When the credential was created
        project_id: ID of the project this credential belongs to
        type: Type of credential
        expired: Whether the credential has expired
        expires_on: When the credential expires
        administrative_scope: Scope of the credential (e.g., "Tenant")
        user_id: ID of the user who owns the credential
        credential_data: List of credential entries
        custom_credentials: Custom credentials data
        custom_credentials_id: ID of custom credentials
        tenant_id: ID of the tenant this credential belongs to
        origin: Origin of the credential (Platform or Chat)
    """

    id: str
    name: Optional[str] = None
    display_identifier_name: Optional[str] = Field(None, alias="displayIdentifierName")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    project_id: Optional[str] = Field(None, alias="projectId")
    type: str
    expired: Optional[bool] = None
    expires_on: Optional[datetime] = Field(None, alias="expiresOn")
    administrative_scope: str = Field(alias="administrativeScope")
    user_id: Optional[str] = Field(None, alias="userId")
    credential_data: List[CredentialEntry] = Field(default_factory=list, alias="credentialData")
    custom_credentials: Optional[dict] = Field(None, alias="customCredentials")
    custom_credentials_id: Optional[str] = Field(None, alias="customCredentialsId")
    tenant_id: Optional[str] = Field(None, alias="tenantId")
    origin: str


class ToolCredentials(BaseModel):
    """Credentials configuration for a tool.

    Attributes:
        tool_credential_settings: Settings for tool credentials
        tool_credentials: The actual credential object
        tool_credentials_id: ID of the tool credentials
        auth_required: Whether authentication is required
        use_user_credentials: Whether to use user credentials
        user_credential_connector_id: ID of the user credential connector
        use_user_credentials_type: Type of user credentials to use
        credentials_source_type: Source type of the credentials
        use_airia_key_support: Whether Airia key support is enabled
    """

    tool_credential_settings: ToolCredentialSettings = Field(
        alias="toolCredentialSettings"
    )
    tool_credentials: Optional[ToolCredential] = Field(None, alias="toolCredentials")
    tool_credentials_id: Optional[str] = Field(None, alias="toolCredentialsId")
    auth_required: bool = Field(alias="authRequired")
    use_user_credentials: bool = Field(alias="useUserCredentials")
    user_credential_connector_id: Optional[str] = Field(
        None, alias="userCredentialConnectorId"
    )
    use_user_credentials_type: str = Field(alias="useUserCredentialsType")
    credentials_source_type: str = Field(alias="credentialsSourceType")
    use_airia_key_support: bool = Field(alias="useAiriaKeySupport")


class ProjectReference(BaseModel):
    """Reference to a project.

    Attributes:
        id: Project ID
        name: Project name
    """

    id: str
    name: str


class ToolMetadata(BaseModel):
    """Metadata key-value pair for a tool.

    Attributes:
        key: The metadata key
        value: The metadata value
    """

    key: str
    value: str


class CreateToolResponse(BaseModel):
    """Response data for tool creation and retrieval operations.

    This response contains complete information about a tool including
    its configuration, credentials, parameters, and metadata.

    Attributes:
        id: Unique identifier for the tool
        created_at: Timestamp when the tool was created
        updated_at: Timestamp when the tool was last updated
        tool_type: Type of the tool (e.g., "custom")
        name: Name of the tool
        standardized_name: Standardized version of the tool name
        display_name: Display name of the tool (includes provider suffix for gateway tools)
        origin: Origin of the tool
        description: Brief description of what the tool does
        method_type: HTTP method type (Get, Post, Put, Delete)
        purpose: When and why to use this tool
        api_endpoint: Web API endpoint where the tool sends requests
        provider: Provider of the tool
        tool_credentials: Credentials configuration for the tool
        headers: Headers required when making API requests
        body: Body of the request that the tool sends to the API
        body_type: Type of the request body (Json, XFormUrlEncoded, None)
        parameters: List of parameters the tool accepts
        project_id: ID of the project this tool belongs to
        project_name: Name of the project this tool belongs to
        project: Project reference object
        children: Child tool definitions
        route_through_acc: Whether the tool should route through an ACC specific group
        should_redirect: Whether the tool should redirect
        acc_group: ACC specific group name
        documentation: Documentation for the tool
        tags: List of tags associated with the tool
        tool_metadata: List of metadata key-value pairs
        supports_pagination: Whether the tool supports pagination
        category: Category of the tool (Action, Airia, Mcp)
        request_timeout: Request timeout in seconds
    """

    id: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    tool_type: str = Field(alias="toolType")
    name: str
    standardized_name: str = Field(alias="standardizedName")
    display_name: Optional[str] = Field(None, alias="displayName")
    origin: Optional[str] = None
    description: str
    method_type: str = Field(alias="methodType")
    purpose: str
    api_endpoint: str = Field(alias="apiEndpoint")
    provider: str
    tool_credentials: ToolCredentials = Field(alias="toolCredentials")
    headers: List[ToolHeader]
    body: str
    body_type: str = Field(alias="bodyType")
    parameters: List[ToolParameter]
    project_id: Optional[str] = Field(None, alias="projectId")
    project_name: Optional[str] = Field(None, alias="projectName")
    project: Optional[ProjectReference] = None
    children: Optional[List["CreateToolResponse"]] = None
    route_through_acc: bool = Field(alias="routeThroughACC")
    should_redirect: bool = Field(alias="shouldRedirect")
    acc_group: Optional[str] = Field(None, alias="accGroup")
    documentation: Optional[str] = None
    tags: Optional[List[str]] = None
    tool_metadata: Optional[List[ToolMetadata]] = Field(None, alias="toolMetadata")
    supports_pagination: Optional[bool] = Field(None, alias="supportsPagination")
    category: str
    request_timeout: int = Field(alias="requestTimeout")


# Update forward references
ToolParameter.model_rebuild()
CreateToolResponse.model_rebuild()
