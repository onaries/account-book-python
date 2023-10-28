from datetime import datetime
from pydantic import BaseModel, Field


class MainCategoryIn(BaseModel):
    name: str
    weekly_limit: int | None = Field(default=None)
    category_type: int


class CategoryIn(BaseModel):
    name: str
    main_category_id: int


class AssetIn(BaseModel):
    name: str
    asset_type: int
    amount: int
    description: str | None = Field(default=None)


class LoanIn(BaseModel):
    name: str
    principal: int
    interest_rate: float
    total_months: int
    current_month: int = 0
    payment_amount: int | None = Field(default=None)
    amount: int = 0
    description: str | None = Field(default=None)


class AccountCardIn(BaseModel):
    name: str
    card_type: int
    amount: int
    description: str | None = Field(default=None)


class StatementIn(BaseModel):
    name: str
    category_id: int
    amount: int
    date: datetime
    discount: int = 0
    saving: int = 0
    description: str | None = Field(default=None)
    account_card_id: int | None
    asset_id: int | None = Field(default=None)
    loan_id: int | None = Field(default=None)
    is_alert: bool = Field(default=False)
    is_fixed: bool = Field(default=False)
