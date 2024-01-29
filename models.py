from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    Float,
    Boolean,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, configure_mappers
from sqlalchemy_continuum import make_versioned
from database import Base

make_versioned(user_cls=None)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(50), unique=True, index=True)
    password = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class MainCategory(Base):
    __versioned__ = {}
    __tablename__ = "main_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    weekly_limit = Column(Integer, nullable=True)
    category_type = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)


class Category(Base):
    __versioned__ = {}
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    main_category_id = Column(Integer, ForeignKey("main_categories.id"))
    main_category = relationship("MainCategory", backref="categories")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class AssetHistory(Base):
    __tablename__ = "asset_histories"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer, default=0)
    timestamp = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Asset(Base):
    __versioned__ = {}
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    asset_type = Column(Integer)
    amount = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Loan(Base):
    __versioned__ = {}
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    principal = Column(Integer, default=0)
    interest_rate = Column(Float, default=0)
    total_months = Column(Integer, default=0)
    payment_amount = Column(Integer, default=0)  # 한달에 상환하는 금액
    current_month = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    amount = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


# 결재 수단
class AccountCard(Base):
    __versioned__ = {}
    __tablename__ = "account_cards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    card_type = Column(Integer)
    amount = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Statement(Base):
    __versioned__ = {}
    __tablename__ = "statements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    account_card_id = Column(Integer, ForeignKey("account_cards.id"))
    asset_id = Column(
        Integer, ForeignKey("assets.id"), nullable=True
    )  # asset_id가 None이 아닌 경우 category_type에 따라 asset의 amount를 변경
    loan_id = Column(
        Integer, ForeignKey("loans.id"), nullable=True
    )  # loan_id가 None이 아닌 경우 category_type에 따라 loan의 amount를 변경 (saving에 등록된 금액을 적용)
    amount = Column(Integer, default=0)
    discount = Column(Integer, default=0)
    saving = Column(Integer, default=0)
    date = Column(DateTime, nullable=False)
    is_fixed = Column(Boolean, default=False)  # 고정지출 여부

    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    category = relationship("Category", backref="statements")
    account_card = relationship("AccountCard", backref="statements")
    asset = relationship("Asset", backref="statements")
    loan = relationship("Loan", backref="statements")


class Memo(Base):
    __tablename__ = "memos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


configure_mappers()
