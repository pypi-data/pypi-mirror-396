from typing import Optional

from ...types._api_version import ApiVersion
from ...types.api.data_vector_search import GetFileChunksResponse
from .._request_handler import AsyncRequestHandler
from .base_data_vector_search import BaseDataVectorSearch


class AsyncDataVectorSearch(BaseDataVectorSearch):
    def __init__(self, request_handler: AsyncRequestHandler):
        super().__init__(request_handler)

    async def get_file_chunks(
        self,
        data_store_id: str,
        file_id: str,
        page_number: int = 1,
        page_size: int = 50,
        correlation_id: Optional[str] = None,
    ) -> GetFileChunksResponse:
        """
        Retrieve chunks from a specific file in a data store.

        This method retrieves chunks from a file in the specified data store.

        Args:
            data_store_id: The unique identifier of the data store (GUID format)
            file_id: The unique identifier of the file (GUID format)
            page_number: The page number (1-based). Default is 1.
            page_size: The page size. Maximum supported value is 100. Default is 50.
            correlation_id: Optional correlation ID for request tracing

        Returns:
            GetFileChunksResponse: Object containing the chunks and pagination information

        Raises:
            AiriaAPIError: If the API request fails, including cases where:
                - The data_store_id doesn't exist (404)
                - The file_id doesn't exist (404)
                - Authentication fails (401)
                - Access is forbidden (403)
                - Server errors (5xx)
            ValueError: If required parameters are missing or invalid

        Example:
            ```python
            from airia import AiriaAsyncClient
            import asyncio

            async def main():
                client = AiriaAsyncClient(api_key="your_api_key")

                # Get file chunks with default pagination
                chunks_response = await client.data_vector_search.get_file_chunks(
                    data_store_id="your_data_store_id",
                    file_id="your_file_id"
                )

                # Get file chunks with custom pagination
                chunks_response = await client.data_vector_search.get_file_chunks(
                    data_store_id="your_data_store_id",
                    file_id="your_file_id",
                    page_number=2,
                    page_size=100
                )

                # Access the chunks
                for chunk in chunks_response.chunks:
                    print(f"Chunk: {chunk.chunk}")
                    print(f"Document: {chunk.document_name}")
                    if chunk.score is not None:
                        print(f"Score: {chunk.score}")

                await client.close()

            asyncio.run(main())
            ```
        """
        request_data = self._pre_get_file_chunks(
            data_store_id=data_store_id,
            file_id=file_id,
            page_number=page_number,
            page_size=page_size,
            correlation_id=correlation_id,
            api_version=ApiVersion.V1.value,
        )

        response = await self._request_handler.make_request(
            "GET", request_data, return_json=True
        )
        return GetFileChunksResponse(**response)
