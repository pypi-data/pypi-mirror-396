"""
Base API client for GoMask backend
"""

import json
from typing import Dict, Any, Optional, Union

import httpx
from httpx import Response, HTTPStatusError, RequestError

from gomask.auth.middleware import create_api_headers, get_auth_context
from gomask.utils.logger import logger


class APIError(Exception):
    """Base exception for API errors"""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Response] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response
        self.details = []

        # Try to extract details from response
        if response:
            try:
                data = response.json()
                if 'errors' in data:
                    self.details = data['errors']
                elif 'warnings' in data:
                    self.details = data['warnings']
            except:
                pass


class GoMaskAPIClient:
    """Base API client for GoMask backend communication"""

    DEFAULT_TIMEOUT = 30.0  # seconds
    DEFAULT_API_URL = "https://app.gomask.ai"

    def __init__(
        self,
        base_url: Optional[str] = None,
        secret: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT
    ):
        """
        Initialize the API client

        Args:
            base_url: Base URL for the API
            secret: Authentication secret
            timeout: Request timeout in seconds
        """
        self.base_url = (base_url or self.DEFAULT_API_URL).rstrip('/')
        self.secret = secret
        self.timeout = timeout

        # Create HTTP client
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            follow_redirects=True
        )

        # Validate authentication exists
        self._validate_auth()

    def _validate_auth(self) -> None:
        """Validate that authentication secret exists"""
        auth_context = get_auth_context(self.secret)
        if not auth_context:
            logger.warning("No authentication secret available")

    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get headers for a request"""
        return create_api_headers(self.secret, additional_headers)

    def _handle_response(self, response: Response) -> Dict[str, Any]:
        """
        Handle API response

        Args:
            response: HTTP response

        Returns:
            Parsed JSON response

        Raises:
            APIError: If response indicates an error
        """
        # Check for HTTP errors
        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_message = error_data.get('detail', response.text)
            except (json.JSONDecodeError, KeyError):
                error_message = response.text or f"HTTP {response.status_code}"

            raise APIError(
                f"API error: {error_message}",
                status_code=response.status_code,
                response=response
            )

        # Parse JSON response
        try:
            return response.json()
        except json.JSONDecodeError:
            # Return text for non-JSON responses
            return {"text": response.text}

    def _build_url(self, path: str) -> str:
        """
        Build full URL from base URL and path

        Args:
            path: API endpoint path

        Returns:
            Complete URL
        """
        # Remove leading slash from path if present
        path = path.lstrip('/')
        # Ensure base_url ends with a slash
        base = self.base_url if self.base_url.endswith('/') else f"{self.base_url}/"
    
        return f"{base}{path}"

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request

        Args:
            path: API endpoint path
            params: Query parameters
            headers: Additional headers

        Returns:
            Parsed response data
        """
        url = self._build_url(path)
        headers = self._get_headers(headers)

        try:
            response = self.client.get(url, params=params, headers=headers)
            return self._handle_response(response)
        except RequestError as e:
            raise APIError(f"Request failed: {e}")

    def post(
        self,
        path: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make a POST request

        Args:
            path: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Additional headers

        Returns:
            Parsed response data
        """
        
        url = self._build_url(path)

        headers = self._get_headers(headers)
        # Prepare request body
        if isinstance(data, dict):
            json_data = data
            content = None
        else:
            json_data = None
            content = data

        try:
            response = self.client.post(
                url,
                json=json_data,
                content=content,
                params=params,
                headers=headers
            )
            
            return self._handle_response(response)
        except RequestError as e:
            raise APIError(f"Request failed: {e}")

    def put(
        self,
        path: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make a PUT request

        Args:
            path: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Additional headers

        Returns:
            Parsed response data
        """
        url = self._build_url(path)
        headers = self._get_headers(headers)

        # Prepare request body
        if isinstance(data, dict):
            json_data = data
            content = None
        else:
            json_data = None
            content = data

        try:
            response = self.client.put(
                url,
                json=json_data,
                content=content,
                params=params,
                headers=headers
            )
            return self._handle_response(response)
        except RequestError as e:
            raise APIError(f"Request failed: {e}")

    def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make a DELETE request

        Args:
            path: API endpoint path
            params: Query parameters
            headers: Additional headers

        Returns:
            Parsed response data
        """
        url = self._build_url(path)
        headers = self._get_headers(headers)

        try:
            response = self.client.delete(url, params=params, headers=headers)
            return self._handle_response(response)
        except RequestError as e:
            raise APIError(f"Request failed: {e}")

    def health_check(self) -> bool:
        """
        Check if the API is healthy

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = self.get("/health")
            return response.get("status") == "healthy"
        except APIError:
            return False

    def close(self) -> None:
        """Close the HTTP client"""
        self.client.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()