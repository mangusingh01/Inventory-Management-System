from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    sku: str = Field(min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=1000)
    quantity: int = Field(ge=0)
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)


class ProductCreate(ProductBase):
    """Payload for creating a product."""


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    sku: str | None = Field(default=None, min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=1000)
    quantity: int | None = Field(default=None, ge=0)
    price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)

    @model_validator(mode="after")
    def validate_required_fields_are_not_null(self) -> "ProductUpdate":
        required_fields = ("name", "sku", "quantity", "price")
        for field in required_fields:
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null.")

        return self


class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
