from typing import Any, Dict, List

from funcy import lflatten
from pydantic import BaseModel

from rhino_health.lib.rest_api.api_request import APIRequest
from rhino_health.lib.rest_api.api_response import APIResponse
from rhino_health.lib.rest_api.request_adapter import RequestAdapter


class PaginationData(BaseModel):
    next_url: str = ""
    current_count: int = 0
    total_count: int = 0
    all_results: List[Any] = []


class RhinoPaginator(RequestAdapter):
    """
    Support pagination for limit&offset as well as page&page_size requests.
    """

    DEFAULT_ACCEPTED_STATUS_CODES = [200, 201]

    def before_request(self, api_request: APIRequest, adapter_kwargs: Dict):
        get_all_pages = adapter_kwargs.get("get_all_pages", False)
        if get_all_pages:
            if api_request.pagination_data is None:
                api_request.pagination_data = PaginationData()
                # Clear any of these params
                api_request.params.pop("limit", None)
                api_request.params.pop("offset", None)
                api_request.params.pop("page", None)  # For page size we keep the current page size
            elif api_request.pagination_data.next_url is not None:
                api_request.url = api_request.pagination_data.next_url

    def after_request(
        self, api_request: APIRequest, api_response: APIResponse, adapter_kwargs: Dict
    ):
        has_pages = adapter_kwargs.get("has_pages", False)
        get_all_pages = adapter_kwargs.get("get_all_pages", False)
        valid_status_codes = adapter_kwargs.get(
            "accepted_status_codes", self.DEFAULT_ACCEPTED_STATUS_CODES
        )
        if (
            has_pages
            and api_response.status_code in valid_status_codes
            and api_response.request_status == APIRequest.RequestStatus.SUCCESS
        ):
            results = api_response.parsed_response
            pagination_data = api_request.pagination_data
            pagination_metadata = api_response.parsed_meta.get("pagination", {})

            if get_all_pages:
                pagination_data.all_results.append(results)
                if pagination_data.current_count == 0:
                    pagination_data.total_count = pagination_metadata.get("count", 0)
                    pagination_data.current_count = len(results)
                else:
                    pagination_data.current_count += len(results)
                if pagination_data.current_count < pagination_data.total_count:
                    api_request.request_status = (
                        APIRequest.RequestStatus.PENDING
                    )  # Tell the system to continue on
                    api_request.request_count = 0  # Allow retries to continue
                    next_url = pagination_metadata.get("next", None)
                    if not next_url:
                        print("Warning: Request failed to fetch all pages")
                    else:
                        pagination_data.next_url = next_url.replace(api_request.base_url, "")
                        return  # Let the handler fetch the next page
                results = pagination_data.all_results

            api_response.parsed_response = lflatten(results)  # Return the results we have
