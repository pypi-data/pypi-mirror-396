from __future__ import annotations

from typing import Any, Optional


class ApiError(Exception):
    """Represents an error response from the bpost API or transport layer."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.details = details

    def __str__(self) -> str:  # pragma: no cover - simple formatting
        base = super().__str__()
        if self.status_code is not None:
            base += f" (status_code={self.status_code})"
        return base
