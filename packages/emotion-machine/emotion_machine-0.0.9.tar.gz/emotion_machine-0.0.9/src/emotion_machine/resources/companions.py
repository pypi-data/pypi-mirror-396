"""Companion resource helpers."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..client import _HTTPClient


class CompanionAPI:
    def __init__(self, http: _HTTPClient) -> None:
        self._http = http

    def list(self) -> list[dict[str, Any]]:
        data = self._http.request("GET", "/v1/companions")
        if not isinstance(data, list):  # pragma: no cover - defensive
            raise TypeError("Expected list payload for companions list")
        return data

    def create(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> dict[str, Any]:
        payload: Dict[str, Any] = {"name": name}
        if description is not None:
            payload["description"] = description
        if config is not None:
            payload["config"] = config
        return self._http.request("POST", "/v1/companions", json=payload, expected=(201,))

    def get(self, companion_id: str) -> dict[str, Any]:
        return self._http.request("GET", f"/v1/companions/{companion_id}")

    def update(
        self,
        companion_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> dict[str, Any]:
        payload: Dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if config is not None:
            payload["config"] = config
        return self._http.request("PATCH", f"/v1/companions/{companion_id}", json=payload)

    def profile_schema_upsert(self, companion_id: str, schema: Dict[str, Any]) -> dict[str, Any]:
        return self._http.request(
            "PUT",
            f"/v1/companions/{companion_id}/profile-schema",
            json={"schema": schema},
        )

    def profile_schema_get(self, companion_id: str) -> dict[str, Any]:
        return self._http.request("GET", f"/v1/companions/{companion_id}/profile-schema")

    def delete(self, companion_id: str) -> None:
        """Delete a companion."""
        self._http.request("DELETE", f"/v1/companions/{companion_id}", expected=(204,))
