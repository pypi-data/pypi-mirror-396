import time
import requests
from typing import Optional, List, Dict, Any

from .types import (
    SDKConfig,
    TextIngestPayload,
    TextSource,
    ImageIngestPayload,
    SearchPayload,
    SearchOptions,
    MemoryItem,
    IngestResponse,
    SearchResponse,
    ListMemoryResponse,
)


class MemoryClientError(Exception):
    """Custom exception for MemoryClient errors."""
    
    def __init__(self, message: str, status: Optional[int] = None, code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        # 5xx errors and 429 (rate limit) are retryable
        self.is_retryable = status is not None and (status >= 500 or status == 429)


DEFAULT_BASE_URL = "https://api.memorymodel.dev"
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_MAX_RETRIES = 3
DEFAULT_API_VERSION = "v1"


class MemoryClient:
    """
    Official Python SDK for MemoryModel API.
    
    Example:
        client = MemoryClient(api_key="sk_live_...", default_end_user_id="user_123")
        client.add("Hello world")
        results = client.search("greeting")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        default_end_user_id: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        api_version: str = DEFAULT_API_VERSION
    ):
        if not api_key:
            raise MemoryClientError("api_key is required")
        
        self._config = SDKConfig(
            api_key=api_key,
            base_url=base_url,
            default_end_user_id=default_end_user_id
        )
        self._timeout = timeout
        self._max_retries = max_retries
        self._api_version = api_version

    def add(
        self,
        content: str,
        *,
        user_context: Optional[str] = None,
        end_user_id: Optional[str] = None
    ) -> IngestResponse:
        """
        Add a text memory to the cluster.
        
        Args:
            content: The text content to store
            user_context: Optional context about the content
            end_user_id: Override default end user ID
        
        Returns:
            IngestResponse with job_id
        """
        payload = TextIngestPayload(
            source=TextSource(content=content),
            user_context=user_context
        )
        
        response = self._request(
            "POST",
            f"/{self._api_version}/ingest",
            json=payload.model_dump(by_alias=True, exclude_none=True),
            end_user_id=end_user_id
        )
        return IngestResponse.model_validate(response)

    def add_image(
        self,
        image_data: str,
        *,
        user_context: Optional[str] = None,
        end_user_id: Optional[str] = None
    ) -> IngestResponse:
        """
        Add an image memory to the cluster.
        
        Args:
            image_data: Base64 encoded image string
            user_context: Optional context about the image
            end_user_id: Override default end user ID
        
        Returns:
            IngestResponse with job_id and preview_url
        """
        payload = ImageIngestPayload(
            image_data=image_data,
            user_context=user_context
        )
        
        response = self._request(
            "POST",
            f"/{self._api_version}/ingest/image",
            json=payload.model_dump(by_alias=True, exclude_none=True),
            end_user_id=end_user_id
        )
        return IngestResponse.model_validate(response)

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        strategy: str = "centroid_aware",
        end_user_id: Optional[str] = None
    ) -> List[MemoryItem]:
        """
        Search for memories semantically.
        
        Args:
            query: The search query
            limit: Maximum number of results (default: 5)
            strategy: 'centroid_aware' or 'simple'
            end_user_id: Override default end user ID
        
        Returns:
            List of MemoryItem objects
        """
        payload = SearchPayload(
            query=query,
            strategy=strategy,
            options=SearchOptions(limit=limit)
        )
        
        response = self._request(
            "POST",
            f"/{self._api_version}/search",
            json=payload.model_dump(by_alias=True, exclude_none=True),
            end_user_id=end_user_id
        )
        parsed = SearchResponse.model_validate(response)
        return parsed.data

    def list(
        self,
        *,
        limit: int = 50,
        memory_type: Optional[str] = None,
        end_user_id: Optional[str] = None
    ) -> List[MemoryItem]:
        """
        List raw memories (history).
        
        Args:
            limit: Maximum number of results (default: 50)
            memory_type: Optional filter by memory type
            end_user_id: Override default end user ID
        
        Returns:
            List of MemoryItem objects
        """
        params: Dict[str, Any] = {"limit": str(limit)}
        if memory_type:
            params["memoryType"] = memory_type
        
        response = self._request(
            "GET",
            f"/{self._api_version}/memory",
            params=params,
            end_user_id=end_user_id
        )
        parsed = ListMemoryResponse.model_validate(response)
        return parsed.data

    def delete(
        self,
        memory_id: str,
        *,
        end_user_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Delete a specific memory by ID.
        
        Args:
            memory_id: The ID of the memory to delete
            end_user_id: Override default end user ID
        
        Returns:
            Dict with status
        """
        return self._request(
            "DELETE",
            f"/{self._api_version}/memory",
            params={"memoryId": memory_id},
            end_user_id=end_user_id
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json: Optional[Dict] = None,
        params: Optional[Dict] = None,
        end_user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Internal request handler with retry logic."""
        url = f"{self._config.base_url}{endpoint}"
        user_id = end_user_id or self._config.default_end_user_id
        
        if not user_id:
            raise MemoryClientError(
                "end_user_id is required. Pass it in constructor or method call."
            )
        
        headers = {
            "Content-Type": "application/json",
            "x-memory-cluster-access-key": self._config.api_key,
            "x-end-user-id": user_id
        }
        
        last_error: Optional[MemoryClientError] = None
        
        for attempt in range(self._max_retries + 1):
            try:
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    json=json,
                    params=params,
                    timeout=self._timeout
                )
                
                if not response.ok:
                    error_msg = f"API Error {response.status_code}: {response.reason}"
                    error_code = None
                    try:
                        error_data = response.json()
                        if "message" in error_data:
                            error_msg = error_data["message"]
                        elif "error" in error_data:
                            error_msg = error_data["error"]
                        error_code = error_data.get("code")
                    except Exception:
                        pass
                    
                    error = MemoryClientError(error_msg, response.status_code, error_code)
                    
                    # Retry on 5xx or 429
                    if error.is_retryable and attempt < self._max_retries:
                        last_error = error
                        delay = (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                        time.sleep(delay)
                        continue
                    
                    raise error
                
                # Handle 204 No Content
                if response.status_code == 204:
                    return {"status": "deleted"}
                
                return response.json()
                
            except requests.exceptions.Timeout:
                timeout_error = MemoryClientError(
                    f"Request timeout after {self._timeout}s",
                    code="TIMEOUT"
                )
                if attempt < self._max_retries:
                    last_error = timeout_error
                    delay = (2 ** attempt)
                    time.sleep(delay)
                    continue
                raise timeout_error
                
            except requests.exceptions.ConnectionError as e:
                network_error = MemoryClientError(
                    f"Network error: {str(e)}",
                    code="NETWORK_ERROR"
                )
                if attempt < self._max_retries:
                    last_error = network_error
                    delay = (2 ** attempt)
                    time.sleep(delay)
                    continue
                raise network_error
        
        # Should never reach here
        raise last_error or MemoryClientError("Unknown error")
