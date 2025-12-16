"""MARSGuard SDK: High-level client for enforced schema."""

from __future__ import annotations
from typing import Optional, Dict, Any, Union
import requests
from .schemas import GenerateGuardrailsRequest, MinimalGuardrailsResponse

class MarsGuardClient:
    """
    Client for interacting with the MARSGuard backend using enforced schema.

    Example usage:
        from marsguard.types import AppModel, ModelSpec, GenerateGuardrailsRequest
        from marsguard.sdk import MarsGuardClient

        client = MarsGuardClient()
        req = GenerateGuardrailsRequest(
            app=AppModel(name="My Project", description="desc"),
            domain="insurance",
            model=ModelSpec(name="gpt-4o")
        )
        resp = client.generate_guardrails(req)
        print(resp.guardrails)
    """

    _BACKEND_URL = "https://aiguard-gc-8ca54e85-ms-1-244053109441.us-west2.run.app"
    _ENDPOINT = "/guardrails/generate"

    def __init__(self, headers: Optional[Dict[str, str]] = None) -> None:
        """
        Initialize the MarsGuardClient.

        Args:
            headers (Optional[Dict[str, str]]): Additional headers to include in requests.
        """
        self.base_url = self._BACKEND_URL
        self.headers = headers or {"Content-Type": "application/json", "Accept": "application/json"}

    def generate_guardrails(
        self,
        request: GenerateGuardrailsRequest
    ) -> MinimalGuardrailsResponse:
        """
        Call the /guardrails/generate endpoint with enforced schema.

        Args:
            request (GenerateGuardrailsRequest or dict): The request payload (validated/enforced).

        Returns:
            MinimalGuardrailsResponse: The parsed response from the backend.

        Raises:
            MarsGuardValidationError: If the request or response schema is invalid.
            MarsGuardAPIError: For API errors (non-2xx responses).
            MarsGuardNetworkError: For network/connection errors.

        API Documentation:
            - 200: Returns MinimalGuardrailsResponse with the generated guardrails.
            - 400: Raises MarsGuardAPIError for invalid input (schema or data error).
            - 401/403: Raises MarsGuardAPIError for authentication/authorization errors.
            - 500: Raises MarsGuardAPIError for backend/server errors.

        Example:
            >>> from marsguard.types import AppModel, ModelSpec, GenerateGuardrailsRequest
            >>> from marsguard.sdk import MarsGuardClient
            >>> client = MarsGuardClient()
            >>> req = GenerateGuardrailsRequest(
            ...     app=AppModel(name="My Project", description="desc"),
            ...     domain="insurance",
            ...     model=ModelSpec(name="gpt-4o")
            ... )
            >>> resp = client.generate_guardrails(req)
            >>> print(resp.guardrails)
        """
        from marsguard.exceptions import (
            MarsGuardValidationError,
            MarsGuardAPIError,
            MarsGuardNetworkError,
        )
        if not isinstance(request, GenerateGuardrailsRequest):
            try:
                request = GenerateGuardrailsRequest.model_validate(request)
            except Exception as e:
                raise MarsGuardValidationError(f"Invalid request schema: {e}") from e
        url = f"{self.base_url}{self._ENDPOINT}"
        try:
            resp = requests.post(
                url,
                json=request.model_dump(by_alias=True, exclude_none=True),
                headers=self.headers,
            )
            if not resp.ok:
                raise MarsGuardAPIError(
                    status_code=resp.status_code,
                    message=resp.reason,
                    response_text=resp.text,
                )
            data = resp.json()
            try:
                return MinimalGuardrailsResponse.model_validate(data)
            except Exception as e:
                raise MarsGuardValidationError(f"Invalid response schema: {e}") from e
        except requests.RequestException as req_err:
            raise MarsGuardNetworkError(f"Network error: {req_err}") from req_err
