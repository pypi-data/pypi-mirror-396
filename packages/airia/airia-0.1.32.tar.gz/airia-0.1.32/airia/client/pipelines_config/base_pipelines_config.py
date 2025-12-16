from typing import Literal, Optional, Union
from urllib.parse import urljoin

from ...types._api_version import ApiVersion
from .._request_handler import AsyncRequestHandler, RequestHandler


class BasePipelinesConfig:
    def __init__(self, request_handler: Union[RequestHandler, AsyncRequestHandler]):
        self._request_handler = request_handler

    def _pre_get_pipeline_config(
        self,
        pipeline_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for getting pipeline configuration endpoint.

        Args:
            pipeline_id: ID of the pipeline to get configuration for
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the pipeline config endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(
            self._request_handler.base_url,
            f"{api_version}/PipelinesConfig/{pipeline_id}",
        )
        request_data = self._request_handler.prepare_request(
            url, correlation_id=correlation_id
        )

        return request_data

    def _pre_export_pipeline_definition(
        self,
        pipeline_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for exporting pipeline definition endpoint.

        Args:
            pipeline_id: ID of the pipeline to export definition for
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the export pipeline definition endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(
            self._request_handler.base_url,
            f"{api_version}/PipelinesConfig/export/{pipeline_id}",
        )
        request_data = self._request_handler.prepare_request(
            url, correlation_id=correlation_id
        )

        return request_data

    def _pre_get_pipelines_config(
        self,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[Literal["ASC", "DESC"]] = None,
        filter: Optional[str] = None,
        project_id: Optional[str] = None,
        model_credential_source_type: Optional[Literal["UserProvided", "Library"]] = None,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for getting pipelines configuration endpoint.

        Args:
            page_number: The page number to be fetched
            page_size: The number of items per page
            sort_by: Property to sort by
            sort_direction: The direction of the sort, either "ASC" for ascending or "DESC" for descending
            filter: The search filter
            project_id: Optional project ID filter
            model_credential_source_type: Optional filter to return only pipelines using models with specified source type ("UserProvided" or "Library")
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the pipelines config endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(
            self._request_handler.base_url,
            f"{api_version}/PipelinesConfig",
        )
        params = {}
        if page_number is not None:
            params["PageNumber"] = page_number
        if page_size is not None:
            params["PageSize"] = page_size
        if sort_by is not None:
            params["SortBy"] = sort_by
        if sort_direction is not None:
            params["SortDirection"] = sort_direction
        if filter is not None:
            params["Filter"] = filter
        if project_id is not None:
            params["projectId"] = project_id
        if model_credential_source_type is not None:
            params["modelCredentialSourceType"] = model_credential_source_type

        request_data = self._request_handler.prepare_request(
            url, params=params, correlation_id=correlation_id
        )

        return request_data

    def _pre_delete_pipeline(
        self,
        pipeline_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for deleting a pipeline by ID.

        This internal method constructs the URL for pipeline deletion
        requests using the provided pipeline identifier.

        Args:
            pipeline_id: ID of the pipeline to delete
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the pipeline deletion endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(
            self._request_handler.base_url,
            f"{api_version}/PipelinesConfig/{pipeline_id}",
        )
        request_data = self._request_handler.prepare_request(
            url, correlation_id=correlation_id
        )

        return request_data
