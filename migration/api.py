import logging
from enum import Enum
from typing import Any
from urllib.parse import parse_qs, urlparse


import httpx


logger = logging.getLogger(__name__)


class EndpointType(Enum):
    REST = '/api/v1/'


class API:
    client: httpx.Client

    def __init__(self, url: str, key: str, endpoint_type: EndpointType = EndpointType.REST):
        headers = { 'Authorization': f'Bearer {key}' }
        self.client = httpx.Client(base_url=url + endpoint_type.value, headers=headers)

    @staticmethod
    def get_next_page_params(resp: httpx.Response) -> dict[str, Any] | None:
        if 'next' not in resp.links:
            return None
        else:
            query_params = parse_qs(urlparse(resp.links['next']['url']).query)
            return query_params

    def get_results_from_pages(
        self, endpoint: str, params: dict[str, Any] | None = None, page_size: int = 50, limit: int | None = None
    ) -> list[dict[str, Any]]:
        extra_params: dict[str, Any]
        if params is not None:
            extra_params = params
        else:
            extra_params = {}
        extra_params.update({ 'per_page': page_size })

        more_pages = True
        page_num = 1
        results: list[dict[str, Any]] = []

        while more_pages:
            logger.debug(f'Params: {extra_params}')
            try:
                resp = self.client.get(url=endpoint, params=extra_params, timeout=10)
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                logger.error(f"HTTP Exception for {exc.request.url} - {exc}")
                raise exc
            results += resp.json()
            next_page_params = API.get_next_page_params(resp)
            if next_page_params is None:
                more_pages = False
            elif limit is not None and limit <= len(results):
                more_pages = False
            else:
                extra_params.update(next_page_params)
                page_num += 1

        if limit is not None and len(results) > limit:
            results = results[:limit]

        logger.debug(f'Number of results: {len(results)}')
        logger.debug(f'Number of pages: {page_num}')
        return results
