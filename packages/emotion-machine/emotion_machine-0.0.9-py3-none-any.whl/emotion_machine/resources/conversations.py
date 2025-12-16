"""Conversation retrieval helper."""

from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import urlencode

from ..client import _HTTPClient


class ConversationAPI:
    def __init__(self, http: _HTTPClient) -> None:
        self._http = http

    def create(
        self,
        companion_id: str,
        external_user_id: str,
    ) -> dict[str, Any]:
        """Create a new conversation for a companion.

        Useful when you need to upload images before sending any messages.

        Returns:
            dict with conversation_id
        """
        payload = self._http.request(
            "POST",
            f"/v1/companions/{companion_id}/conversations",
            json={"external_user_id": external_user_id},
        )
        if not isinstance(payload, dict):  # pragma: no cover - defensive
            raise TypeError("Expected dict payload for create conversation response")
        return payload

    def get(self, conversation_id: str) -> dict[str, Any]:
        convo = self._http.request("GET", f"/v1/conversations/{conversation_id}")
        if not isinstance(convo, dict):  # pragma: no cover - defensive
            raise TypeError("Expected dict payload for conversation response")
        return convo

    def list(
        self,
        companion_id: str,
        *,
        limit: int = 50,
        offset: int = 0,
        external_user_id: Optional[str] = None,
        external_user_prefix: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        params = {
            "limit": limit,
            "offset": offset,
        }
        if external_user_id:
            params["external_user_id"] = external_user_id
        if external_user_prefix:
            params["external_user_prefix"] = external_user_prefix

        query = urlencode(params)
        path = f"/v1/companions/{companion_id}/conversations"
        if query:
            path = f"{path}?{query}"
        payload = self._http.request("GET", path)
        if not isinstance(payload, list):  # pragma: no cover - defensive
            raise TypeError("Expected list payload for conversation collection")
        return payload

    def upload_image(
        self,
        companion_id: str,
        conversation_id: str,
        *,
        file_path: str,
        mime_type: Optional[str] = None,
    ) -> dict[str, Any]:
        """Upload an image to a conversation for use in chat."""
        import mimetypes
        from pathlib import Path

        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content_type = mime_type or mimetypes.guess_type(file_path)[0] or "application/octet-stream"

        with open(file_path, "rb") as f:
            files = {"file": (path_obj.name, f, content_type)}
            # Use the underlying httpx client directly for multipart upload
            response = self._http._client.post(
                f"/v1/companions/{companion_id}/conversations/{conversation_id}/images",
                files=files,
            )
            if response.status_code != 201:
                from ..client import APIError
                try:
                    detail = response.json()
                except Exception:
                    detail = {"detail": response.text}
                message = detail.get("detail") or detail.get("message") or response.text
                raise APIError(response.status_code, message, payload=detail)
            return response.json()

    def list_images(
        self,
        companion_id: str,
        conversation_id: str,
    ) -> list[dict[str, Any]]:
        """List all images in a conversation."""
        payload = self._http.request(
            "GET",
            f"/v1/companions/{companion_id}/conversations/{conversation_id}/images",
        )
        if not isinstance(payload, list):  # pragma: no cover - defensive
            raise TypeError("Expected list payload for images collection")
        return payload
