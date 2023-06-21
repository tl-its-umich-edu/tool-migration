import logging
from dataclasses import dataclass
from enum import Enum
from json import JSONDecodeError
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt
)

logger = logging.getLogger(__name__)


class EndpointType(Enum):
    REST = '/api/v1/'


@dataclass
class GetResponseData:
    data: Any
    next_page_params: dict[str, Any] | None


class API:
    client: httpx.Client

    def __init__(
        self,
        url: str,
        key: str, endpoint_type: EndpointType = EndpointType.REST,
        timeout: int = 10
    ):
        headers = { 'Authorization': f'Bearer {key}' }
        self.client = httpx.Client(base_url=url + endpoint_type.value, headers=headers, timeout=timeout)

    @staticmethod
    def get_next_page_params(resp: httpx.Response) -> dict[str, Any] | None:
        if 'next' not in resp.links:
            return None
        else:
            query_params = parse_qs(urlparse(resp.links['next']['url']).query)
            return query_params

    @retry(
        stop=stop_after_attempt(4),
        retry=retry_if_exception_type((httpx.HTTPError, JSONDecodeError)),
        reraise=True,
        before_sleep=before_sleep_log(logger, logging.WARN)
    )
    def get(self, url: str, params: dict[str, Any] | None = None) -> GetResponseData:
        resp = self.client.get(url=url, params=params)
        resp.raise_for_status()
        data = resp.json()
        next_page_params = self.get_next_page_params(resp)
        return GetResponseData(data, next_page_params)

    @retry(
        stop=stop_after_attempt(4),
        retry=retry_if_exception_type((httpx.HTTPError, JSONDecodeError)),
        reraise=True,
        before_sleep=before_sleep_log(logger, logging.WARN)
    )
    def put(self, url: str, params: dict[str, Any] | None = None) -> Any:
        resp = self.client.put(url=url, params=params)
        resp.raise_for_status()
        return resp.json()

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
            data = self.get(url=endpoint, params=extra_params)
            results += data.data
            if data.next_page_params is None:
                more_pages = False
            elif limit is not None and limit <= len(results):
                more_pages = False
            else:
                extra_params.update(data.next_page_params)
                page_num += 1

        if limit is not None and len(results) > limit:
            results = results[:limit]

        logger.debug(f'Number of results: {len(results)}')
        logger.debug(f'Number of pages: {page_num}')
        return results
