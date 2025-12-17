from typing import Literal, Optional, Union
from urllib.parse import urljoin

from ...types._api_version import ApiVersion
from .._request_handler import AsyncRequestHandler, RequestHandler


class BaseProject:
    def __init__(self, request_handler: Union[RequestHandler, AsyncRequestHandler]):
        self._request_handler = request_handler

    def _pre_get_projects(
        self,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[Literal["ASC", "DESC"]] = None,
        filter: Optional[str] = None,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for getting projects endpoint.

        Args:
            page_number: The page number to be fetched
            page_size: The number of items per page
            sort_by: Property to sort by
            sort_direction: The direction of the sort, either "ASC" for ascending or "DESC" for descending
            filter: The search filter
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the projects endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(
            self._request_handler.base_url, f"{api_version}/Project/paginated"
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

        request_data = self._request_handler.prepare_request(
            url, params=params, correlation_id=correlation_id
        )

        return request_data

    def _pre_get_project(
        self,
        project_id: str,
        correlation_id: Optional[str] = None,
        api_version: str = ApiVersion.V1.value,
    ):
        """
        Prepare request data for getting a single project endpoint.

        Args:
            project_id: The project identifier (GUID format)
            correlation_id: Optional correlation ID for tracing
            api_version: API version to use for the request

        Returns:
            RequestData: Prepared request data for the project endpoint

        Raises:
            ValueError: If an invalid API version is provided
        """
        if api_version not in ApiVersion.as_list():
            raise ValueError(
                f"Invalid API version: {api_version}. Valid versions are: {', '.join(ApiVersion.as_list())}"
            )
        url = urljoin(
            self._request_handler.base_url, f"{api_version}/Project/{project_id}"
        )
        request_data = self._request_handler.prepare_request(
            url, correlation_id=correlation_id
        )

        return request_data
