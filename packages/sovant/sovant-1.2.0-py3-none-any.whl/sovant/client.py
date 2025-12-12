import os
import json
import time
import httpx
from typing import Any, Dict, Optional, Callable
from .models import MemoryCreate, SearchQuery

class SovantError(Exception):
    def __init__(self, message: str, code: str, status: int | None = None, details: Any | None = None):
        super().__init__(message)
        self.code = code
        self.status = status
        self.details = details

class Sovant:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        on_request: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_response: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[SovantError], None]] = None
    ):
        self.api_key = api_key or os.getenv("SOVANT_API_KEY")
        if not self.api_key:
            raise ValueError("Missing api_key")
        self.base_url = (base_url or os.getenv("SOVANT_BASE_URL") or "https://sovant.ai").rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.on_request = on_request
        self.on_response = on_response
        self.on_error = on_error
        self._client = httpx.Client(
            timeout=self.timeout,
            headers={
                "authorization": f"Bearer {self.api_key}",
                "content-type": "application/json"
            }
        )

    def _request(self, method: str, url: str, **kwargs):
        """Internal request method with retry logic and telemetry"""
        start_time = time.time()

        # Telemetry: onRequest hook
        if self.on_request:
            try:
                self.on_request({
                    "method": method,
                    "url": url,
                    "body": kwargs.get("json") or kwargs.get("content")
                })
            except:
                pass

        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                r = self._client.request(method, url, **kwargs)

                if r.status_code >= 400:
                    try:
                        body = r.json()
                    except Exception:
                        body = {"message": r.text}
                    msg = body.get("message") or str(r.reason_phrase) if hasattr(r, 'reason_phrase') else 'Error'
                    code = body.get("code") or f"HTTP_{r.status_code}"
                    error = SovantError(msg, code, r.status_code, body)

                    # Retry on 429 (rate limit) or 5xx errors
                    if attempt < self.max_retries and (r.status_code == 429 or r.status_code >= 500):
                        last_error = error
                        delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        time.sleep(delay)
                        continue

                    # Telemetry: onError hook
                    if self.on_error:
                        try:
                            self.on_error(error)
                        except:
                            pass

                    raise error

                # Success - telemetry: onResponse hook
                duration = (time.time() - start_time) * 1000  # Convert to ms
                if self.on_response:
                    try:
                        self.on_response({
                            "method": method,
                            "url": url,
                            "status": r.status_code,
                            "duration": duration
                        })
                    except:
                        pass

                if not r.text:
                    return None
                try:
                    return r.json()
                except Exception:
                    return r.text

            except httpx.TimeoutException as e:
                error = SovantError("Request timeout", "TIMEOUT", 408)
                if attempt < self.max_retries:
                    last_error = error
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                raise error

            except httpx.NetworkError as e:
                error = SovantError(str(e), "NETWORK_ERROR", 0)
                if attempt < self.max_retries:
                    last_error = error
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                raise error

        # If we exhausted retries, raise the last error
        raise last_error or SovantError("Max retries exceeded", "MAX_RETRIES", 0)

    def memory_create(self, create: MemoryCreate):
        # Convert data field to content field for API
        body = create.model_dump()
        if 'data' in body:
            body['content'] = json.dumps(body.pop('data')) if not isinstance(body.get('data'), str) else body.pop('data')

        # Ensure type has a default
        if 'type' not in body or body['type'] is None:
            body['type'] = 'journal'

        return self._request("POST", f"{self.base_url}/api/v1/memory", json=body)

    def memory_get(self, id: str):
        return self._request("GET", f"{self.base_url}/api/v1/memories/{id}")

    def memory_search(self, q: SearchQuery):
        params = {}
        if q.query:
            params['query'] = q.query
        if q.type:
            params['type'] = q.type
        if q.tags:
            params['tags'] = ','.join(q.tags)
        if q.thread_id:
            params['thread_id'] = q.thread_id
        if q.limit:
            params['limit'] = str(q.limit)
        if q.from_date:
            params['from_date'] = q.from_date
        if q.to_date:
            params['to_date'] = q.to_date
        return self._request("GET", f"{self.base_url}/api/v1/memory/search", params=params)

    def memory_recall(self, query: str, thread_id: str | None = None, limit: int | None = None):
        """
        Hybrid recall with profile awareness

        Uses multi-stage pipeline (profile fast-path + lexical + semantic)
        Guarantees profile facts (name/age/location) when available

        Use recall() for conversational queries ("who am I?", "what do you know about me?")
        Use memory_search() for pure semantic topic lookup

        Args:
            query: The search query (required)
            thread_id: Optional thread context for thread-scoped recall
            limit: Maximum results to return (default 8, max 50)
        """
        params = {'query': query}
        if thread_id:
            params['thread_id'] = thread_id
        if limit:
            params['limit'] = str(limit)
        return self._request("GET", f"{self.base_url}/api/v1/memory/recall", params=params)

    def memory_update(self, id: str, patch: Dict[str, Any]):
        # Convert data field to content field if present
        if 'data' in patch:
            patch['content'] = json.dumps(patch.pop('data')) if not isinstance(patch.get('data'), str) else patch.pop('data')
        return self._request("PATCH", f"{self.base_url}/api/v1/memories/{id}", json=patch)

    def memory_delete(self, id: str):
        return self._request("DELETE", f"{self.base_url}/api/v1/memories/{id}")

    def memory_create_batch(self, memories: list[Dict[str, Any]]):
        """
        Batch create multiple memories in a single request

        Args:
            memories: List of memory objects (max 100)

        Returns:
            BatchResponse with individual results
        """
        operations = []
        for mem in memories:
            data = mem.copy()
            # Convert data field to content field
            if 'data' in data:
                data['content'] = json.dumps(data.pop('data')) if not isinstance(data.get('data'), str) else data.pop('data')
            # Ensure type has default
            if 'type' not in data or data['type'] is None:
                data['type'] = 'journal'
            operations.append({
                "operation": "create",
                "data": data
            })

        return self._request("POST", f"{self.base_url}/api/v1/memory/batch", json=operations)