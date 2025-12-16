"""Knowledge ingestion helper."""

from __future__ import annotations

import time
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..client import _HTTPClient


FINAL_STATES = {"succeeded", "failed"}


class KnowledgeJobFailed(RuntimeError):
    def __init__(self, job_id: str, error: Optional[str], job_payload: Dict[str, Any]) -> None:
        message = error or "Knowledge ingestion failed"
        super().__init__(f"Knowledge job {job_id} failed: {message}")
        self.job_id = job_id
        self.error = error
        self.job_payload = job_payload


class KnowledgeAPI:
    def __init__(self, http: _HTTPClient) -> None:
        self._http = http

    def ingest(
        self,
        companion_id: str,
        *,
        payload_type: str = "markdown",
        content: Optional[str] = None,
        key: Optional[str] = None,
        asset_id: Optional[str] = None,
    ) -> dict[str, Any]:
        body: Dict[str, Any] = {"type": payload_type}
        if content is not None:
            body["content"] = content
        if key is not None:
            body["key"] = key
        if asset_id is not None:
            body["asset_id"] = asset_id
        response = self._http.request(
            "POST",
            f"/v1/companions/{companion_id}/knowledge",
            json=body,
            expected=(202,),
        )
        if not isinstance(response, dict):  # pragma: no cover - defensive
            raise TypeError("Expected dict payload for knowledge ingestion response")
        return response

    def ingest_file(
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
    ) -> Dict[str, Any]:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        content_type = mime_type or mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        with path.open("rb") as handle:
            files = {"file": (path.name, handle, content_type)}
            data = {"type": payload_type}
            response = self._http.request(
                "POST",
                f"/v1/companions/{companion_id}/knowledge",
                files=files,
                data=data,
                expected=(202,),
            )
        if not isinstance(response, dict):  # pragma: no cover - defensive
            raise TypeError("Expected dict payload for knowledge ingestion response")
        job = response
        if not wait:
            return {"job": job}
        final_job = self.wait(
            job["id"],
            timeout=wait_timeout,
            interval=wait_interval,
            raise_on_failure=raise_on_failure,
        )
        return {"job": final_job}

    def get_job(self, job_id: str) -> dict[str, Any]:
        job = self._http.request("GET", f"/v1/knowledge-jobs/{job_id}")
        if not isinstance(job, dict):  # pragma: no cover - defensive
            raise TypeError("Expected dict payload for knowledge job")
        return job

    def wait(
        self,
        job_id: str,
        *,
        timeout: float = 30.0,
        interval: float = 0.5,
        raise_on_failure: bool = True,
    ) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        while True:
            job = self.get_job(job_id)
            if job.get("status") in FINAL_STATES:
                if job.get("status") == "failed" and raise_on_failure:
                    raise KnowledgeJobFailed(job_id, job.get("error"), job)
                return job
            if time.monotonic() >= deadline:
                return job
            time.sleep(interval)

    def search(
        self,
        companion_id: str,
        *,
        query: str,
        max_results: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        mode: Optional[str] = None,
    ) -> dict[str, Any]:
        body: Dict[str, Any] = {"query": query, "max_results": max_results}
        if filters is not None:
            body["filters"] = filters
        if mode is not None:
            body["mode"] = mode
        response = self._http.request(
            "POST",
            f"/v1/companions/{companion_id}/knowledge/search",
            json=body,
        )
        if not isinstance(response, dict):  # pragma: no cover - defensive
            raise TypeError("Expected dict payload for knowledge search response")
        return response
