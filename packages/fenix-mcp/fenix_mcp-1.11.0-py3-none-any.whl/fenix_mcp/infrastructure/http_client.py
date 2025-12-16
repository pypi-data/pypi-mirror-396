# SPDX-License-Identifier: MIT
"""HTTP client with retries and simple instrumentation."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

import requests
from requests import Response, Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass(slots=True)
class HttpClient:
    """Simple synchronous HTTP client used by the API layer."""

    base_url: str
    timeout: float = 30.0
    default_headers: Optional[Mapping[str, str]] = None
    _logger: logging.Logger = field(init=False, repr=False)
    _session: Session = field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_logger", logging.getLogger("fenix_mcp.http"))
        object.__setattr__(self, "_session", self._build_session())

    def _build_session(self) -> Session:
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST", "PATCH", "DELETE", "PUT"),
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        json: Optional[Mapping[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Response:
        url = f"{self.base_url}{endpoint}"
        merged_headers = dict(self.default_headers or {})
        merged_headers.update(headers or {})

        self._logger.debug(
            "HTTP request",
            extra={
                "method": method,
                "url": url,
                "params": params,
                "has_body": json is not None,
            },
        )

        response = self._session.request(
            method=method.upper(),
            url=url,
            json=json,
            params=params,
            headers=merged_headers,
            timeout=self.timeout,
        )

        self._logger.debug(
            "HTTP response",
            extra={
                "status": response.status_code,
                "url": url,
                "request_id": response.headers.get("x-request-id"),
            },
        )

        return response
