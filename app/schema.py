from pydantic import BaseModel, create_model, Field
from pydantic.types import Any
from datetime import datetime


class MainCategorySchema(BaseModel):
    id: int
    name: str
    category_type: int
    weekly_limit: int = None
    created_at: datetime = None
    updated_at: datetime = None

    class Config:
        orm_mode = True


class MainCategoryOut(BaseModel):
    name: str
    category_type: int


class CategorySchema(BaseModel):
    id: int
    name: str
    main_category_id: int
    main_category: MainCategorySchema
    main_category_name: str = Field(None)
    type: int = Field(None)
    created_at: datetime = None
    updated_at: datetime = None

    class Config:
        orm_mode = True

    def __init__(self, **data):
        super().__init__(**data)
        self.main_category_name = self.main_category.name
        self.type = self.main_category.category_type


class CategoryOut(BaseModel):
    id: int
    name: str
    main_category: MainCategoryOut


class AssetSchema(BaseModel):
    id: int
    name: str
    asset_type: int
    amount: int
    description: str = None
    created_at: datetime = None
    updated_at: datetime = None

    class Config:
        orm_mode = True


class LoanSchema(BaseModel):
    id: int
    name: str
    principal: int
    interest_rate: int
    total_months: int
    current_month: int
    amount: int
    payment_amount: int = None
    description: str = None
    created_at: datetime = None
    updated_at: datetime = None

    class Config:
        orm_mode = True


class AccountCardSchema(BaseModel):
    id: int
    name: str
    card_type: int
    amount: int
    description: str = None
    created_at: datetime = None
    updated_at: datetime = None

    class Config:
        orm_mode = True


class AccountSchema(BaseModel):
    id: int
    name: str
    account_type: int
    amount: int
    description: str = None
    created_at: datetime = None
    updated_at: datetime = None

    class Config:
        orm_mode = True


class StatementSchema(BaseModel):
    id: int
    name: str
    category_id: int = None
    account_card_id: int = None
    asset_id: int = None
    loan_id: int = None
    amount: int
    discount: int = 0
    saving: int = 0
    date: datetime
    description: str = None
    created_at: datetime = None
    updated_at: datetime = None
    category: CategorySchema = None
    category_type: int = None
    account_card: AccountCardSchema = None

    class Config:
        orm_mode = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.category_id is not None:
            self.category_type = self.category.main_category.category_type


class AssetHistorySchema(BaseModel):
    id: int
    amount: int
    timestamp: datetime
    created_at: datetime = None
    updated_at: datetime = None

    class Config:
        orm_mode = True


class StatementSummarySchema(BaseModel):
    page_amount: int = 0
    page_discount: int = 0
    page_saving: int = 0
    total_amount: int = 0
    total_discount: int = 0
    total_saving: int = 0


class StatementCategorySumSchema(BaseModel):
    income: int = 0
    expense: int = 0
    expense_saving: int = 0
    saving: int = 0
    discount: int = 0
    total: int = 0
    total_no_discount: int = 0
