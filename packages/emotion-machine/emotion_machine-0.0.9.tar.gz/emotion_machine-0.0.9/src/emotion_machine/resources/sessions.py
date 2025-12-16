"""Voice session helpers."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..client import _HTTPClient


class SessionAPI:
    def __init__(self, http: _HTTPClient) -> None:
        self._http = http

    def create(
        self,
        companion_id: str,
        *,
        conversation_id: Optional[str] = None,
        external_user_id: Optional[str] = None,
        voice_config: Optional[Dict[str, Any]] = None,
        context_mode: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Create a voice session for real-time audio conversation.

        Args:
            companion_id: The companion to start a session with.
            conversation_id: Optional existing conversation to continue.
            external_user_id: Optional user identifier for tracking.
            voice_config: Optional voice configuration:
                - pipeline_type: "openai-realtime" (default) or "stt-llm-tts"
                - voice_name: Voice to use (e.g., "alloy", "sage", "echo")
                - temperature: LLM temperature (0.0-1.0)
                - realtimeModel: Model for openai-realtime pipeline
            context_mode: Optional context engine mode override:
                - "legacy": Use traditional system prompt + memory retrieval
                - "layered": Use full context engine (memory, knowledge, actions)
                - None (default): Use companion's configured mode

        Returns:
            Session response containing:
                - id: Session ID
                - conversation_id: Conversation ID (new or existing)
                - ws_url: WebSocket URL to connect for audio streaming
        """
        payload: Dict[str, Any] = {"companionId": companion_id}

        if conversation_id is not None:
            payload["conversationId"] = conversation_id
        if external_user_id is not None:
            payload["externalUserId"] = external_user_id
        if voice_config is not None:
            payload["voiceConfig"] = voice_config
        if context_mode is not None:
            payload["contextMode"] = context_mode

        return self._http.request("POST", "/v1/sessions", json=payload, expected=(201,))

    def update(
        self,
        session_id: str,
        *,
        voice_config: Optional[Dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Update a voice session's configuration.

        Note: Cannot update sessions with active WebSocket connections.

        Args:
            session_id: The session to update.
            voice_config: New voice configuration to apply.

        Returns:
            {"status": "updated"} on success.

        Raises:
            APIError: 409 Conflict if session has active connection.
        """
        payload: Dict[str, Any] = {}
        if voice_config is not None:
            payload["voiceConfig"] = voice_config

        return self._http.request("PATCH", f"/v1/sessions/{session_id}", json=payload)
