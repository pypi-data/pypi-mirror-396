from typing import List, Optional

from ...types._api_version import ApiVersion
from ...types.api.models import ModelItem
from .._request_handler import AsyncRequestHandler
from .base_models import BaseModels


class AsyncModels(BaseModels):
    def __init__(self, request_handler: AsyncRequestHandler):
        super().__init__(request_handler)

    async def list_models(
        self,
        project_id: Optional[str] = None,
        include_global: bool = True,
        page_number: int = 1,
        page_size: int = 50,
        sort_by: str = "updatedAt",
        sort_direction: str = "DESC",
        correlation_id: Optional[str] = None,
    ) -> List[ModelItem]:
        """
        Retrieve a list of models accessible to the authenticated user.

        This method fetches information about all models that the current user
        has access to, optionally filtered by project. Models can be either
        library-provided or user-configured.

        Args:
            project_id (str, optional): Filter models by project ID. If provided,
                returns models associated with this project.
            include_global (bool, optional): Whether to include global/library models
                in the results. Defaults to True.
            page_number (int, optional): Page number for pagination. Defaults to 1.
            page_size (int, optional): Number of items per page. Defaults to 50.
            sort_by (str, optional): Field to sort results by. Defaults to "updatedAt".
            sort_direction (str, optional): Sort direction, either "ASC" or "DESC".
                Defaults to "DESC".
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            List[ModelItem]: A list of ModelItem objects containing model
                information including configuration, pricing, and capabilities.
                Returns an empty list if no models are found.

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaAsyncClient

            client = AiriaAsyncClient(api_key="your_api_key")

            # Get all accessible models
            models = await client.models.list_models()

            for model in models:
                print(f"Model: {model.display_name}")
                print(f"Provider: {model.provider}")
                print(f"Type: {model.type}")
                print(f"Has tool support: {model.has_tool_support}")
                print("---")

            # Get models for a specific project
            project_models = await client.models.list_models(
                project_id="12345678-1234-1234-1234-123456789abc",
                include_global=False
            )
            ```

        Note:
            The returned models are filtered based on the authenticated user's
            permissions. Users will only see models they have been granted access to.
        """
        request_data = self._pre_list_models(
            project_id=project_id,
            include_global=include_global,
            page_number=page_number,
            page_size=page_size,
            sort_by=sort_by,
            sort_direction=sort_direction,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        resp = await self._request_handler.make_request("GET", request_data)

        if "items" not in resp or len(resp["items"]) == 0:
            return []

        return [ModelItem(**item) for item in resp["items"]]

    async def delete_model(
        self,
        model_id: str,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Delete a model by its ID.

        This method permanently deletes a model from the Airia platform. Once deleted,
        the model cannot be recovered. Only models that the authenticated user has
        permission to delete can be removed.

        Args:
            model_id (str): The unique identifier of the model to delete.
            correlation_id (str, optional): A unique identifier for request tracing
                and logging. If not provided, one will be automatically generated.

        Returns:
            None

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - Model not found (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)

        Example:
            ```python
            from airia import AiriaAsyncClient

            client = AiriaAsyncClient(api_key="your_api_key")

            # Delete a specific model
            await client.models.delete_model(
                model_id="12345678-1234-1234-1234-123456789abc"
            )
            print("Model deleted successfully")

            # Delete with correlation ID for tracking
            await client.models.delete_model(
                model_id="12345678-1234-1234-1234-123456789abc",
                correlation_id="my-correlation-id"
            )
            ```

        Note:
            This operation is irreversible. Ensure you have the correct model ID
            before calling this method. You must have delete permissions for the
            specified model.
        """
        request_data = self._pre_delete_model(
            model_id=model_id,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )
        await self._request_handler.make_request(
            "DELETE", request_data, return_json=False
        )
