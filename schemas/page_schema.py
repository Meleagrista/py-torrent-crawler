from typing import Dict, Any

from pydantic import BaseModel, HttpUrl, Field


class Page(BaseModel):
    url: HttpUrl = Field(..., description="URL of the page.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the page.")
