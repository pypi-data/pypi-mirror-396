"""HTTP client and top-level SDK interface."""

from __future__ import annotations

import os
from contextlib import AbstractContextManager, contextmanager
from typing import Any, Dict, Iterable, Iterator, Optional

import httpx


DEFAULT_BASE_URL = os.getenv("EM_API_BASE_URL", "http://localhost:8100")


class APIError(RuntimeError):
    """Represents an HTTP error raised by the Emotion Machine API."""

    def __init__(self, status_code: int, message: str, payload: Optional[dict] = None) -> None:
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code
        self.message = message
        self.payload = payload or {}


class _HTTPClient(AbstractContextManager["_HTTPClient"]):
    """Minimal HTTPX wrapper with shared error handling."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        *,
        timeout: Optional[float] = 30.0,
    ) -> None:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "emotion-machine-sdk/0",
        }
        self._client = httpx.Client(base_url=base_url, timeout=timeout, headers=headers)

    def close(self) -> None:
        self._client.close()

    def __exit__(self, *exc_info: object) -> None:  # pragma: no cover - delegated
        self.close()

    def request(self, method: str, path: str, *, expected: Iterable[int] = (200, 201), **kwargs: Any) -> Any:
        response = self._client.request(method, path, **kwargs)
        if response.status_code not in expected:
            detail: Dict[str, Any]
            try:
                detail = response.json()
            except Exception:  # pragma: no cover - defensive
                detail = {"detail": response.text}
            message = detail.get("detail") or detail.get("message") or response.text
            raise APIError(response.status_code, message, payload=detail)
        if response.headers.get("Content-Type", "").startswith("application/json"):
            return response.json()
        return response.text

    @contextmanager
    def stream(self, method: str, path: str, *, expected: Iterable[int] = (200,), **kwargs: Any) -> Iterator[httpx.Response]:
        with self._client.stream(method, path, **kwargs) as response:
            if response.status_code not in expected:
                body = response.read()
                try:
                    detail = httpx.Response(200, content=body).json()
                except Exception:  # pragma: no cover - defensive
                    detail = {"detail": body.decode()}
                message = detail.get("detail") or detail.get("message") or body.decode()
                raise APIError(response.status_code, message, payload=detail)
            yield response


class EmotionMachine:
    """Primary SDK entrypoint."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = 30.0,
    ) -> None:
        key = api_key or os.getenv("EM_API_KEY")
        if not key:
            raise ValueError("API key is required. Set EM_API_KEY or pass api_key explicitly.")
        base = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._http = _HTTPClient(key, base, timeout=timeout)

        # Lazily import to avoid circular references during packaging.
        from .resources.chat import ChatAPI
        from .resources.companions import CompanionAPI
        from .resources.conversations import ConversationAPI
        from .resources.knowledge import KnowledgeAPI
        from .resources.sessions import SessionAPI

        self.companions = CompanionAPI(self._http)
        self.knowledge = KnowledgeAPI(self._http)
        self.chat = ChatAPI(self._http)
        self.conversations = ConversationAPI(self._http)
        self.sessions = SessionAPI(self._http)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "EmotionMachine":  # pragma: no cover - context convenience
        return self

    def __exit__(self, *exc_info: object) -> None:  # pragma: no cover - context convenience
        self.close()

    # Convenience methods delegating to resource helpers
    def list_companions(self) -> list[dict[str, Any]]:
        return self.companions.list()

    def create_companion(self, *, name: str, description: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> dict[str, Any]:
        return self.companions.create(name=name, description=description, config=config)

    def get_companion(self, companion_id: str) -> dict[str, Any]:
        return self.companions.get(companion_id)

    def update_companion(
        self,
        companion_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> dict[str, Any]:
        return self.companions.update(companion_id, name=name, description=description, config=config)

    def upsert_profile_schema(self, companion_id: str, schema: Dict[str, Any]) -> dict[str, Any]:
        return self.companions.profile_schema_upsert(companion_id, schema)

    def get_profile_schema(self, companion_id: str) -> dict[str, Any]:
        return self.companions.profile_schema_get(companion_id)

    def ingest_knowledge(
        self,
        companion_id: str,
        *,
        payload_type: str = "markdown",
        content: Optional[str] = None,
        key: Optional[str] = None,
        asset_id: Optional[str] = None,
    ) -> dict[str, Any]:
        return self.knowledge.ingest(
            companion_id,
            payload_type=payload_type,
            content=content,
            key=key,
            asset_id=asset_id,
        )

    def ingest_knowledge_file(
        self,
        companion_id: str,
        *,
        file_path: str,
        payload_type: str = "markdown",
        mime_type: Optional[str] = None,
        wait: bool = True,
        wait_timeout: float = 60.0,
        wait_interval: float = 0.5,
        raise_on_failure: bool = True,
    ) -> dict[str, Any]:
        return self.knowledge.ingest_file(
            companion_id,
            file_path=file_path,
            payload_type=payload_type,
            mime_type=mime_type,
            wait=wait,
            wait_timeout=wait_timeout,
            wait_interval=wait_interval,
            raise_on_failure=raise_on_failure,
        )

    def wait_for_job(
        self,
        job_id: str,
        *,
        timeout: float = 30.0,
        interval: float = 0.5,
        raise_on_failure: bool = True,
    ) -> dict[str, Any]:
        return self.knowledge.wait(
            job_id,
            timeout=timeout,
            interval=interval,
            raise_on_failure=raise_on_failure,
        )

    def search_knowledge(
        self,
        companion_id: str,
        *,
        query: str,
        max_results: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        mode: Optional[str] = None,
    ) -> dict[str, Any]:
        return self.knowledge.search(
            companion_id,
            query=query,
            max_results=max_results,
            filters=filters,
            mode=mode,
        )

    def upload_knowledge_asset(
        self,
        companion_id: str,
        *,
        file_path: str,
        mime_type: Optional[str] = None,
    ) -> dict[str, Any]:
        return self.knowledge.upload_asset(companion_id, file_path=file_path, mime_type=mime_type)

    def list_knowledge_assets(self, companion_id: str, *, limit: int = 50) -> list[dict[str, Any]]:
        return self.knowledge.list_assets(companion_id, limit=limit)

    def ingest_file(
        self,
        companion_id: str,
        *,
        file_path: str,
        payload_type: str = "text",
        mime_type: Optional[str] = None,
        wait: bool = True,
        wait_timeout: float = 60.0,
        wait_interval: float = 0.5,
        raise_on_failure: bool = True,
    ) -> Dict[str, Any]:
        return self.knowledge.ingest_file(
            companion_id,
            file_path=file_path,
            payload_type=payload_type,
            mime_type=mime_type,
            wait=wait,
            wait_timeout=wait_timeout,
            wait_interval=wait_interval,
            raise_on_failure=raise_on_failure,
        )

    def delete_companion(self, companion_id: str) -> None:
        """Delete a companion."""
        return self.companions.delete(companion_id)

    def chat_completion(
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
        return self.chat.complete(
            companion_id,
            message=message,
            external_user_id=external_user_id,
            model=model,
            temperature=temperature,
            conversation_id=conversation_id,
            profile=profile,
            image_ids=image_ids,
            context_mode=context_mode,
        )

    def chat_stream(
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
        return self.chat.stream(
            companion_id,
            message=message,
            external_user_id=external_user_id,
            model=model,
            temperature=temperature,
            conversation_id=conversation_id,
            profile=profile,
            image_ids=image_ids,
            context_mode=context_mode,
        )

    def create_conversation(
        self,
        companion_id: str,
        external_user_id: str,
    ) -> dict[str, Any]:
        """Create a new conversation for a companion.

        Useful when you need to upload images before sending any messages.
        """
        return self.conversations.create(companion_id, external_user_id)

    def get_conversation(self, conversation_id: str) -> dict[str, Any]:
        return self.conversations.get(conversation_id)

    def list_conversations(
        self,
        companion_id: str,
        *,
        limit: int = 50,
        offset: int = 0,
        external_user_id: Optional[str] = None,
        external_user_prefix: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        return self.conversations.list(
            companion_id,
            limit=limit,
            offset=offset,
            external_user_id=external_user_id,
            external_user_prefix=external_user_prefix,
        )

    def upload_image(
        self,
        companion_id: str,
        conversation_id: str,
        *,
        file_path: str,
        mime_type: Optional[str] = None,
    ) -> dict[str, Any]:
        """Upload an image to a conversation for use in chat."""
        return self.conversations.upload_image(
            companion_id,
            conversation_id,
            file_path=file_path,
            mime_type=mime_type,
        )

    def list_images(
        self,
        companion_id: str,
        conversation_id: str,
    ) -> list[dict[str, Any]]:
        """List all images in a conversation."""
        return self.conversations.list_images(companion_id, conversation_id)

    def create_session(
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
            voice_config: Optional voice configuration dict.
            context_mode: Optional context engine mode override:
                - "legacy": Use traditional system prompt + memory retrieval
                - "layered": Use full context engine (memory, knowledge, actions)
                - None (default): Use companion's configured mode

        Returns a dict with 'id', 'conversation_id', and 'ws_url'.
        Connect to ws_url with a WebSocket client to stream audio.
        """
        return self.sessions.create(
            companion_id,
            conversation_id=conversation_id,
            external_user_id=external_user_id,
            voice_config=voice_config,
            context_mode=context_mode,
        )

    def update_session(
        self,
        session_id: str,
        *,
        voice_config: Optional[Dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Update a voice session's configuration.

        Note: Cannot update sessions with active WebSocket connections.
        """
        return self.sessions.update(session_id, voice_config=voice_config)
