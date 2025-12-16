"""Chat and streaming helpers."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterator, Optional

from ..client import _HTTPClient


def _parse_sse(response: Any) -> Iterator[dict[str, Any]]:
    event: Optional[str] = None
    event_id: Optional[str] = None
    data_lines: list[str] = []

    for raw_line in response.iter_lines():
        if raw_line is None:
            continue
        line = raw_line.decode() if isinstance(raw_line, bytes) else raw_line

        if not line:
            if data_lines:
                payload = "\n".join(data_lines)
                try:
                    payload_data = json.loads(payload)
                except json.JSONDecodeError:
                    payload_data = payload
                yield {
                    "event": event or "message",
                    "id": event_id,
                    "data": payload_data,
                }
            event = None
            event_id = None
            data_lines = []
            continue

        if line.startswith(":"):
            continue  # comment / heartbeat

        if line.startswith("event:"):
            event = line.split(":", 1)[1].strip() or None
        elif line.startswith("id:"):
            event_id = line.split(":", 1)[1].strip() or None
        elif line.startswith("data:"):
            data_lines.append(line.split(":", 1)[1].strip())
        else:
            data_lines.append(line)


class ChatAPI:
    def __init__(self, http: _HTTPClient) -> None:
        self._http = http

    def _build_payload(
        self,
        *,
        message: str,
        external_user_id: str,
        model: Optional[str],
        temperature: Optional[float],
        conversation_id: Optional[str],
        profile: Optional[Dict[str, Any]],
        image_ids: Optional[list[str]],
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "message": message,
            "external_user_id": external_user_id,
        }
        if model is not None:
            payload["model"] = model
        if temperature is not None:
            payload["temperature"] = temperature
        if conversation_id is not None:
            payload["conversation_id"] = conversation_id
        if profile is not None:
            payload["profile"] = profile
        if image_ids is not None:
            payload["image_ids"] = image_ids
        return payload

    def complete(
        self,
        companion_id: str,
        *,
        message: str,
        external_user_id: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        conversation_id: Optional[str] = None,
        profile: Optional[Dict[str, Any]] = None,
        image_ids: Optional[list[str]] = None,
        context_mode: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Send a chat message and get a complete response.

        Args:
            companion_id: The companion to chat with.
            message: The user's message.
            external_user_id: User identifier for memory/personalization.
            model: Optional model override.
            temperature: Optional temperature override.
            conversation_id: Optional conversation to continue.
            profile: Optional user profile data.
            image_ids: Optional image IDs for multimodal chat.
            context_mode: Optional context engine mode override:
                - "legacy": Use traditional system prompt + memory retrieval
                - "layered": Use full context engine (memory, knowledge, actions)
                - None (default): Use companion's configured mode

        Returns:
            Chat completion response.
        """
        payload = self._build_payload(
            message=message,
            external_user_id=external_user_id,
            model=model,
            temperature=temperature,
            conversation_id=conversation_id,
            profile=profile,
            image_ids=image_ids,
        )
        headers: Dict[str, str] = {}
        if context_mode is not None:
            headers["X-Context-Engine"] = context_mode
        result = self._http.request(
            "POST",
            f"/v1/companions/{companion_id}/chat",
            json=payload,
            headers=headers if headers else None,
        )
        if not isinstance(result, dict):  # pragma: no cover - defensive
            raise TypeError("Expected dict payload for chat completion response")
        return result
        

    def stream(
        self,
        companion_id: str,
        *,
        message: str,
        external_user_id: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        conversation_id: Optional[str] = None,
        profile: Optional[Dict[str, Any]] = None,
        image_ids: Optional[list[str]] = None,
        context_mode: Optional[str] = None,
    ) -> Iterator[dict[str, Any]]:
        """
        Send a chat message and stream the response.

        Args:
            companion_id: The companion to chat with.
            message: The user's message.
            external_user_id: User identifier for memory/personalization.
            model: Optional model override.
            temperature: Optional temperature override.
            conversation_id: Optional conversation to continue.
            profile: Optional user profile data.
            image_ids: Optional image IDs for multimodal chat.
            context_mode: Optional context engine mode override:
                - "legacy": Use traditional system prompt + memory retrieval
                - "layered": Use full context engine (memory, knowledge, actions)
                - None (default): Use companion's configured mode

        Yields:
            SSE events with streaming response data.
        """
        payload = self._build_payload(
            message=message,
            external_user_id=external_user_id,
            model=model,
            temperature=temperature,
            conversation_id=conversation_id,
            profile=profile,
            image_ids=image_ids,
        )
        headers: Dict[str, str] = {"Accept": "text/event-stream"}
        if context_mode is not None:
            headers["X-Context-Engine"] = context_mode
        with self._http.stream(
            "POST",
            f"/v1/companions/{companion_id}/chat/stream",
            json=payload,
            headers=headers,
        ) as response:
            yield from _parse_sse(response)
