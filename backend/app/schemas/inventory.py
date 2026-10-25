"""Pydantic schemas for inventory items."""
from __future__ import annotations

import datetime as dt
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class InventoryBase(BaseModel):
    category: str = Field(..., max_length=32)
    name: str = Field(..., max_length=120)
    vendor: Optional[str] = None
    serial: Optional[str] = None
    purchased_at: Optional[dt.datetime] = None
    warranty_until: Optional[dt.datetime] = None
    status: str = Field(default="Active")


class InventoryCreate(InventoryBase):
    inv_id: Optional[str] = None


class InventoryUpdate(BaseModel):
    category: Optional[str] = None
    name: Optional[str] = None
    vendor: Optional[str] = None
    serial: Optional[str] = None
    purchased_at: Optional[dt.datetime] = None
    warranty_until: Optional[dt.datetime] = None
    status: Optional[str] = None


class InventoryOut(InventoryBase):
    id: int
    inv_id: str
    purchased: Optional[str] = None
    warranty: Optional[str] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def populate_date_strings(self) -> InventoryOut:
        if self.purchased is None and self.purchased_at is not None:
            self.purchased = self.purchased_at.strftime("%Y-%m-%d") if hasattr(self.purchased_at, "strftime") else str(self.purchased_at)[:10]
        if self.warranty is None and self.warranty_until is not None:
            self.warranty = self.warranty_until.strftime("%Y-%m-%d") if hasattr(self.warranty_until, "strftime") else str(self.warranty_until)[:10]
        return self


class InventoryListResponse(BaseModel):
    items: List[InventoryOut]
    total: int
    page: int
    page_size: int
    pages: int
