# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["Customer"]


class Customer(BaseModel):
    id: int

    industry: Optional[str] = None

    name: str

    slug: str
