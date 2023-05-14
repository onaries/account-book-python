from datetime import datetime
from pydantic import BaseModel


class MainCategoryIn(BaseModel):
    name: str
    weekly_limit: int = None
    category_type: int


class CategoryIn(BaseModel):
    name: str
    main_category_id: int


class AssetIn(BaseModel):
    name: str
    asset_type: int
    amount: int
    description: str = None


class LoanIn(BaseModel):
    name: str
    principal: int
    interest_rate: float
    total_months: int
    current_month: int
    payment_amount: int = None
    amount: int
    description: str = None


class AccountCardIn(BaseModel):
    name: str
    card_type: int
    amount: int
    description: str = None


class StatementIn(BaseModel):
    name: str
    category_id: int
    amount: int
    date: datetime
    discount: int = 0
    saving: int = 0
    description: str = None
    account_card_id: int = None
    asset_id: int = None
    loan_id: int = None
    is_alert: bool = False
