from fastapi import status
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional


class APIException(Exception):
    """Base exception that can return JSON response directly"""
    def __init__(
        self,
        status_code: int = 500,
        error_type: str = "api_error",
        message: str = "An error occurred",
        details: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.status_code = status_code
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        self.headers = headers or {}
        super().__init__(self.message)

    def to_json_response(self) -> JSONResponse:
        """Convert exception to FastAPI JSONResponse"""
        content = {
            "error": self.error_type,
            "message": self.message,
            **self.details
        }
        return JSONResponse(
            status_code=self.status_code,
            content=content,
            headers=self.headers
        )

class DomainNotAllowedException(APIException):
    def __init__(self, domain: str, allowed_domains: list, source: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_type="invalid_domain",
            message=f"Domain '{domain}' is not allowed",
            details={
                "domain": domain,
                "allowed_domains": allowed_domains,
                "source": source,
                "suggestion": f"Please use one of the allowed domains: {', '.join(allowed_domains)}"
            }
        )

class InvalidUrlException(APIException):
    def __init__(self, url: str, reason: str = "Invalid format"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_type="invalid_url",
            message=f"Invalid URL: {url}",
            details={
                "url": url,
                "reason": reason,
                "suggestion": "Please provide a valid URL with protocol (http:// or https://)"
            }
        )

class MergeException(Exception):
    """Base class for exceptions in this module."""
