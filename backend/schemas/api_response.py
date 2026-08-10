"""
Standard API Response Schemas
"""

from typing import Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Any | None = None
    errors: list[str] = []