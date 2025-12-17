from typing import List, Literal, Optional

from ...types._api_version import ApiVersion
from ...types.api.deployments import GetDeploymentResponse, GetDeploymentsResponse
from .._request_handler import AsyncRequestHandler
from .base_deployments import BaseDeployments


class AsyncDeployments(BaseDeployments):
    def __init__(self, request_handler: AsyncRequestHandler):
        super().__init__(request_handler)

    async def get_deployments(
        self,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[Literal["ASC", "DESC"]] = None,
        filter: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_recommended: Optional[bool] = None,
        project_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V2.value,
    ) -> GetDeploymentsResponse:
        """
        Retrieve a paged list of deployments asynchronously.

        This method fetches deployments from the Airia platform with optional filtering
        by tags and recommendation status. The response includes detailed information
        about each deployment including associated pipelines, data sources, and user prompts.

        Args:
            page_number: The page number to be fetched
            page_size: The number of items per page
            sort_by: Property to sort by
            sort_direction: The direction of the sort, either "ASC" for ascending or "DESC" for descending
            filter: The search filter
            tags: Optional list of tags to filter deployments by
            is_recommended: Optional filter by recommended status
            project_id: Optional filter by project id
            correlation_id: Optional correlation ID for request tracing
            api_version: API version to use (defaults to V2)

        Returns:
            GetDeploymentsResponse: Paged response containing deployment items and total count

        Raises:
            AiriaAPIError: If the API request fails
            ValueError: If an invalid API version is provided

        Example:
            ```python
            client = AiriaAsyncClient(api_key="your-api-key")

            # Basic usage with filtering
            deployments = await client.deployments.get_deployments(
                tags=["production", "nlp"],
                is_recommended=True
            )

            # With pagination and sorting
            deployments = await client.deployments.get_deployments(
                page_number=1,
                page_size=20,
                sort_by="deploymentName",
                sort_direction="ASC",
                filter="text-analysis"
            )

            print(f"Found {deployments.total_count} deployments")
            for deployment in deployments.items:
                print(f"- {deployment.deployment_name}")
            ```
        """
        request_data = self._pre_get_deployments(
            page_number=page_number,
            page_size=page_size,
            sort_by=sort_by,
            sort_direction=sort_direction,
            filter=filter,
            tags=tags,
            is_recommended=is_recommended,
            correlation_id=correlation_id,
            api_version=api_version,
        )

        response = await self._request_handler.make_request("GET", request_data)

        if project_id is not None:
            response["items"] = [
                item for item in response["items"] if item["projectId"] == project_id
            ]

        return GetDeploymentsResponse(**response)

    async def get_deployment(
        self,
        deployment_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ) -> GetDeploymentResponse:
        """
        Retrieve a single deployment by ID asynchronously.

        This method fetches a specific deployment from the Airia platform using its
        unique identifier. The response includes complete information about the deployment
        including associated pipelines, data sources, user prompts, and configuration settings.

        Args:
            deployment_id: The unique identifier of the deployment to retrieve
            correlation_id: Optional correlation ID for request tracing
            api_version: API version to use (defaults to V1)

        Returns:
            GetDeploymentResponse: Complete deployment information

        Raises:
            AiriaAPIError: If the API request fails or deployment is not found
            ValueError: If an invalid API version is provided

        Example:
            ```python
            client = AiriaAsyncClient(api_key="your-api-key")
            deployment = await client.deployments.get_deployment("deployment-id-123")
            print(f"Deployment: {deployment.deployment_name}")
            print(f"Description: {deployment.description}")
            print(f"Project: {deployment.project_id}")
            ```
        """
        request_data = self._pre_get_deployment(
            deployment_id=deployment_id,
            correlation_id=correlation_id,
            api_version=api_version,
        )

        response = await self._request_handler.make_request("GET", request_data)

        return GetDeploymentResponse(**response)
