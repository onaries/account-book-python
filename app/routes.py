import calendar
from datetime import timedelta
from typing import Optional, Union
from fastapi import Form, Query
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from fastapi.types import Any
from fastapi.routing import APIRouter
from fastapi.param_functions import Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from database import get_db
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import select, text, func, extract
from app.consts import TYPE_INCOME, CURRENT_TIMEZONE
from models import (
    Category,
    MainCategory,
    Asset,
    Loan,
    AccountCard,
    Statement,
    AssetHistory,
)
from .schema import (
    CategorySchema,
    MainCategorySchema,
    AssetSchema,
    LoanSchema,
    AccountCardSchema,
    StatementSchema,
    StatementSummarySchema,
    StatementCategorySumSchema,
)
from .in_schema import (
    MainCategoryIn,
    CategoryIn,
    AssetIn,
    LoanIn,
    AccountCardIn,
    StatementIn,
)
from .utils import new_asset_history, convert_message, push_notification

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/main-category", response_model=Page[MainCategorySchema])
async def get_main_categories(
    sort: str = "id",
    order: str = "ASC",
    db: Session = Depends(get_db),
):
    return paginate(db, select(MainCategory).order_by(text(f"{sort} {order}")))


@router.post("/main-category")
async def create_main_category(
    main_category_in: MainCategoryIn, db: Session = Depends(get_db)
):
    new_main_category = MainCategory(
        name=main_category_in.name,
        weekly_limit=main_category_in.weekly_limit,
        category_type=main_category_in.category_type,
    )
    db.add(new_main_category)
    db.commit()
    db.refresh(new_main_category)
    return new_main_category


@router.get("/main-category/all", response_model=list[MainCategorySchema])
async def get_main_categories_all(db: Session = Depends(get_db)):
    return db.query(MainCategory).order_by("category_type").all()


@router.get("/main-category/{id}", response_model=MainCategorySchema)
async def get_main_category(id: int, db: Session = Depends(get_db)):
    return db.query(MainCategory).filter(MainCategory.id == id).first()


@router.put("/main-category/{id}")
async def update_main_category(
    id: int,
    main_category_in: MainCategorySchema,
    db: Session = Depends(get_db),
):
    main_category = db.query(MainCategory).filter(MainCategory.id == id).first()
    main_category.name = main_category_in.name
    main_category.weekly_limit = main_category_in.weekly_limit
    main_category.category_type = main_category_in.category_type
    db.commit()
    db.refresh(main_category)
    return main_category


@router.delete("/main-category/{id}")
async def delete_main_category(id: int, db: Session = Depends(get_db)):
    main_category = db.query(MainCategory).filter(MainCategory.id == id).first()
    db.delete(main_category)
    db.commit()
    return {"message": "Main Category deleted successfully"}


@router.get("/category", response_model=Page[CategorySchema])
async def get_categories(
    sort: str = "id",
    order: str = "ASC",
    db: Session = Depends(get_db),
):
    return paginate(db, select(Category).order_by(text(f"{sort} {order}")))


@router.post("/category")
async def create_category(
    category_in: CategoryIn,
    db: Session = Depends(get_db),
):
    new_category = Category(
        name=category_in.name, main_category_id=category_in.main_category_id
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.get("/category/all", response_model=list[CategorySchema])
async def get_categories_all(db: Session = Depends(get_db)):
    return db.query(Category).order_by("main_category_id").all()


@router.get("/category/{id}")
async def get_category(id: int, db: Session = Depends(get_db)):
    return db.query(Category).filter(Category.id == id).first()


@router.put("/category/{id}")
async def update_category(
    id: int,
    category_in: CategoryIn,
    db: Session = Depends(get_db),
):
    category = db.query(Category).filter(Category.id == id).first()
    category.name = category_in.name
    category.main_category_id = category_in.main_category_id
    db.commit()
    db.refresh(category)
    return category


@router.delete("/category/{id}")
async def delete_category(id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == id).first()
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}


@router.get("/asset", response_model=Page[AssetSchema])
async def get_assets(
    sort: str = "id", order: str = "ASC", db: Session = Depends(get_db)
):
    return paginate(db, select(Asset).order_by(text(f"{sort} {order}")))


@router.post("/asset")
async def create_asset(
    asset_in: AssetIn,
    db: Session = Depends(get_db),
):
    new_asset = Asset(
        name=asset_in.name,
        asset_type=asset_in.asset_type,
        amount=asset_in.amount,
        description=asset_in.description,
    )
    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    new_asset_history(db)

    return new_asset


@router.get("/asset/all", response_model=list[AssetSchema])
async def get_assets_all(db: Session = Depends(get_db)):
    return db.query(Asset).all()


@router.get("/asset/total")
async def get_assets_total(db: Session = Depends(get_db)):
    return db.query(func.sum(Asset.amount)).scalar()


@router.get("/asset/history")
async def get_assets_history(
    date: date, mode: int = Query(1), db: Session = Depends(get_db)
):
    # 주간모드
    if mode == 1:
        prev = date - timedelta(days=date.weekday() + 1)
        next_date = date + timedelta(days=1)

        query = (
            db.query(AssetHistory)
            .filter(AssetHistory.created_at >= prev)
            .filter(AssetHistory.created_at <= next_date)
            .order_by(AssetHistory.created_at)
            .all()
        )

        # created_at의 day마다 가장 마지막 값만 저장
        result = {}

        for q in query:
            result[q.created_at.strftime("%Y-%m-%d")] = q.amount

        response = []
        for k in result.keys():
            response.append(dict(name=k, value=result[k]))

        return response

    # 월간모드
    elif mode == 2:
        prev = date.replace(day=1)
        next_date = date.replace(day=calendar.monthrange(date.year, date.month)[1])

        query = (
            db.query(AssetHistory)
            .filter(AssetHistory.created_at >= prev)
            .filter(AssetHistory.created_at <= next_date)
            .order_by(AssetHistory.created_at)
            .all()
        )

        # created_at의 day마다 가장 마지막 값만 저장
        result = {}

        for q in query:
            result[q.created_at.strftime("%Y-%m-%d")] = q.amount

        response = []
        for k in result.keys():
            response.append(dict(name=k, value=result[k]))

        return response

    else:
        return None


@router.get("/asset/history/all")
async def get_assets_history_all(db: Session = Depends(get_db)):
    return db.query(AssetHistory).all()


@router.get("/asset/prev")
async def get_assets_prev(db: Session = Depends(get_db)):
    now = datetime.now(CURRENT_TIMEZONE).date()

    # 최근 일주일(일~토)
    prev = now - timedelta(days=1 + now.weekday())
    next_date = now + timedelta(days=1)

    asset_sum = db.query(func.sum(Asset.amount)).scalar()
    loan_sum = db.query(func.sum(Loan.amount)).scalar()

    total_asset = asset_sum - loan_sum

    last_asset = (
        db.query(AssetHistory)
        .filter(AssetHistory.created_at >= prev)
        .filter(AssetHistory.created_at <= next_date)
        .order_by(AssetHistory.created_at)
        .all()
    )

    if last_asset is not None and len(last_asset) > 0:
        first_value = last_asset[0].amount
        diff_sum = 0
        for i in range(1, len(last_asset)):
            diff = last_asset[i].amount - first_value
            diff_sum += diff
            first_value = last_asset[i].amount

        return {
            "total_asset": total_asset,
            "diff_asset": diff_sum,
        }
    else:
        return {
            "total_asset": total_asset,
            "diff_asset": 0,
        }


@router.get("/asset/{id}")
async def get_asset(id: int, db: Session = Depends(get_db)):
    return db.query(Asset).filter(Asset.id == id).first()


@router.put("/asset/{id}")
async def update_asset(
    id: int,
    asset_in: AssetIn,
    db: Session = Depends(get_db),
):
    asset = db.query(Asset).filter(Asset.id == id).first()
    asset.name = asset_in.name
    asset.asset_type = asset_in.asset_type
    asset.amount = asset_in.amount
    asset.description = asset_in.description
    db.commit()
    db.refresh(asset)

    new_asset_history(db)

    return asset


@router.delete("/asset/{id}")
async def delete_asset(id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == id).first()
    db.delete(asset)
    db.commit()

    new_asset_history(db)

    return {"message": "Asset deleted successfully"}


@router.get("/loan", response_model=Page[LoanSchema])
async def get_loans(
    sort: str = "id", order: str = "ASC", db: Session = Depends(get_db)
):
    return paginate(db, select(Loan).order_by(text(f"{sort} {order}")))


@router.post("/loan")
async def create_loan(
    loan_in: LoanIn,
    db: Session = Depends(get_db),
):
    new_loan = Loan(
        name=loan_in.name,
        principal=loan_in.principal,
        interest_rate=loan_in.interest_rate,
        total_months=loan_in.total_months,
        current_month=loan_in.current_month,
        description=loan_in.description,
        amount=loan_in.amount,
        payment_amount=loan_in.payment_amount,
    )
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)

    new_asset_history(db)

    return new_loan


@router.get("/loan/all")
async def get_loans_all(db: Session = Depends(get_db)):
    return db.query(Loan).all()


@router.get("/loan/total")
async def get_loans_total(db: Session = Depends(get_db)):
    return db.query(func.sum(Loan.amount)).scalar()


@router.get("/loan/{id}")
async def get_loan(id: int, db: Session = Depends(get_db)):
    return db.query(Loan).filter(Loan.id == id).first()


@router.post("/loan/{id}/payment", summary="상환하기")
async def loan_payment(id: int, db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == id).first()
    loan.current_month += 1
    loan.amount = loan.amount - loan.payment_amount
    db.commit()
    db.refresh(loan)

    new_asset_history(db)

    return loan


@router.put("/loan/{id}")
async def update_loan(
    id: int,
    loan_in: LoanIn,
    db: Session = Depends(get_db),
):
    loan = db.query(Loan).filter(Loan.id == id).first()
    loan.name = loan_in.name
    loan.principal = loan_in.principal
    loan.interest_rate = loan_in.interest_rate
    loan.total_months = loan_in.total_months
    loan.current_month = loan_in.current_month
    loan.description = loan_in.description
    loan.amount = loan_in.amount
    loan.payment_amount = loan_in.payment_amount
    db.commit()
    db.refresh(loan)

    new_asset_history(db)
    return loan


@router.delete("/loan/{id}")
async def delete_loan(id: int, db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == id).first()
    db.delete(loan)
    db.commit()

    new_asset_history(db)
    return {"message": "Loan deleted successfully"}


@router.get("/account-card", response_model=Page[AccountCardSchema])
async def get_account_cards(
    sort: str = "id", order: str = "ASC", db: Session = Depends(get_db)
):
    return paginate(db, select(AccountCard).order_by(text(f"{sort} {order}")))


@router.post("/account-card")
async def create_account_card(
    account_card_in: AccountCardIn,
    db: Session = Depends(get_db),
):
    new_account_card = AccountCard(
        name=account_card_in.name,
        card_type=account_card_in.card_type,
        amount=account_card_in.amount,
        description=account_card_in.description,
    )
    db.add(new_account_card)
    db.commit()
    db.refresh(new_account_card)
    return new_account_card


@router.get("/account-card/all", response_model=list[AccountCardSchema])
async def get_account_cards_all(db: Session = Depends(get_db)):
    return db.query(AccountCard).all()


@router.get("/account-card/{id}")
async def get_account_card(id: int, db: Session = Depends(get_db)):
    return db.query(AccountCard).filter(AccountCard.id == id).first()


@router.put("/account-card/{id}")
async def update_account_card(
    id: int,
    account_card_in: AccountCardIn,
    db: Session = Depends(get_db),
):
    account_card = db.query(AccountCard).filter(AccountCard.id == id).first()
    account_card.name = account_card_in.name
    account_card.card_type = account_card_in.card_type
    account_card.amount = account_card_in.amount
    account_card.description = account_card_in.description
    db.commit()
    db.refresh(account_card)
    return account_card


@router.delete("/account-card/{id}")
async def delete_account_card(id: int, db: Session = Depends(get_db)):
    account_card = db.query(AccountCard).filter(AccountCard.id == id).first()
    db.delete(account_card)
    db.commit()
    return {"message": "Account card deleted successfully"}


@router.get("/statement", response_model=Page[StatementSchema])
async def get_statements(
    sort: str = "id",
    order: str = "ASC",
    type: int = None,
    date_lte: Optional[date] = None,
    date_gte: Optional[date] = None,
    category_id: Optional[int] = None,
    main_category_id: Optional[int] = None,
    is_fixed: bool = Query(None),
    db: Session = Depends(get_db),
):
    statement_list = (
        db.query(Statement)
        .join(Category, Statement.category_id == Category.id)
        .join(MainCategory)
    )

    if date_lte is not None:
        date_lte = date_lte + timedelta(days=1)
        statement_list = statement_list.filter(Statement.date < date_lte)
    if date_gte is not None:
        statement_list = statement_list.filter(Statement.date >= date_gte)
    if type is not None:
        statement_list = statement_list.filter(MainCategory.category_type == type)
    if category_id is not None:
        statement_list = statement_list.filter(Statement.category_id == category_id)
    if main_category_id is not None:
        statement_list = statement_list.filter(
            Category.main_category_id == main_category_id
        )
    if is_fixed is not None:
        statement_list = statement_list.filter(Statement.is_fixed == is_fixed)

    if sort == "id":
        sort = "statements_id"

    statement_list = statement_list.order_by(text(f"{sort} {order}"))

    return paginate(db, statement_list)


@router.post("/statement")
async def create_statement(
    statement_in: StatementIn,
    db: Session = Depends(get_db),
):
    new_statement = Statement(
        name=statement_in.name,
        category_id=statement_in.category_id,
        amount=statement_in.amount,
        discount=statement_in.discount,
        date=statement_in.date,
        saving=statement_in.saving,
        description=statement_in.description,
        account_card_id=statement_in.account_card_id,
        asset_id=statement_in.asset_id,
        loan_id=statement_in.loan_id,
        is_fixed=statement_in.is_fixed,
    )
    category = (
        db.query(Category).filter(Category.id == statement_in.category_id).first()
    )
    change_asset = False

    # 지출일 때 마이너스
    if category.main_category.category_type != TYPE_INCOME:
        if statement_in.amount > 0:
            new_statement.amount = -statement_in.amount

    asset = None
    # asset가 있을 때
    if statement_in.asset_id is not None:
        asset = db.query(Asset).filter(Asset.id == statement_in.asset_id).first()
        asset.amount += statement_in.amount
        change_asset = True

    loan = None
    # loan이 있을 때
    if statement_in.loan_id is not None:
        loan = db.query(Loan).filter(Loan.id == statement_in.loan_id).first()
        loan.amount -= statement_in.saving
        change_asset = True

    db.add(new_statement)
    db.commit()
    db.refresh(new_statement)

    if change_asset:
        if asset is not None:
            db.refresh(asset)
        if loan is not None:
            db.refresh(loan)
        new_asset_history(db)

    if statement_in.is_alert:
        message = convert_message(db, new_statement)
        push_notification(message)

    return new_statement


@router.get("/statement/summary", response_model=StatementSummarySchema)
async def get_statement_summary(
    sort: str = "id",
    order: str = "ASC",
    type: int = None,
    date_lte: date = None,
    date_gte: date = None,
    category_id: int = None,
    main_category_id: int = None,
    is_fixed: bool = Query(None),
    size: int = Query(50, gt=0, le=100),
    page: int = Query(1, gt=0),
    db: Session = Depends(get_db),
):
    statement_list = (
        db.query(Statement)
        .join(Category, Statement.category_id == Category.id)
        .join(MainCategory)
    )

    if date_lte is not None:
        statement_list = statement_list.filter(Statement.date <= date_lte)
    if date_gte is not None:
        statement_list = statement_list.filter(Statement.date >= date_gte)
    if type is not None:
        statement_list = statement_list.filter(MainCategory.category_type == type)
    if category_id is not None:
        statement_list = statement_list.filter(Statement.category_id == category_id)
    if main_category_id is not None:
        statement_list = statement_list.filter(
            Category.main_category_id == main_category_id
        )
    if is_fixed is not None:
        statement_list = statement_list.filter(Statement.is_fixed == is_fixed)

    statement_list = statement_list.order_by(text(f"{sort} {order}"))

    # pagination
    page_statement_list = statement_list.offset((page - 1) * size).limit(size)
    page_subquery = page_statement_list.subquery()

    page_result = db.query(
        func.sum(page_subquery.c.amount).label("amount"),
        func.sum(page_subquery.c.discount).label("discount"),
        func.sum(page_subquery.c.saving).label("saving"),
    ).all()

    # total
    total_subquery = statement_list.subquery()
    total_result = db.query(
        func.sum(total_subquery.c.amount).label("amount"),
        func.sum(total_subquery.c.discount).label("discount"),
        func.sum(total_subquery.c.saving).label("saving"),
    ).all()

    data = StatementSummarySchema()
    data.page_amount = page_result[0][0] if page_result[0][0] else 0
    data.page_discount = page_result[0][1] if page_result[0][1] else 0
    data.page_saving = page_result[0][2] if page_result[0][2] else 0

    data.total_amount = total_result[0][0] if total_result[0][0] else 0
    data.total_discount = total_result[0][1] if total_result[0][1] else 0
    data.total_saving = total_result[0][2] if total_result[0][2] else 0

    return data


@router.get("/statement/category", summary="카테고리별 합계", response_model=list)
async def statement_category(
    mode: int,
    date: date,
    category_type: int,
    sub: bool = False,
    db: Session = Depends(get_db),
):
    # 주간 합계
    if mode == 1:
        # 해당 주의 일요일 구하기
        if date.weekday() == 6:
            sunday = date
        else:
            sunday = date - timedelta(days=date.weekday() + 1)

        if sub:
            category_list = (
                db.query(Category)
                .join(MainCategory)
                .filter(MainCategory.category_type == category_type)
                .all()
            )

            statement_list = (
                db.query(
                    Category.id,
                    Category.name,
                    func.sum(Statement.amount).label("amount"),
                    func.sum(Statement.discount).label("discount"),
                )
                .join(Category, Statement.category_id == Category.id)
                .join(MainCategory)
                .filter(Statement.date >= sunday)
                .filter(Statement.date < sunday + timedelta(days=7))
                .filter(MainCategory.category_type == category_type)
                .group_by(Category.id)
            )

        else:
            category_list = (
                db.query(MainCategory)
                .filter(MainCategory.category_type == category_type)
                .all()
            )

            statement_list = (
                db.query(
                    MainCategory.id,
                    MainCategory.name,
                    func.sum(Statement.amount).label("amount"),
                    func.sum(Statement.discount).label("discount"),
                )
                .join(Category, Statement.category_id == Category.id)
                .join(MainCategory)
                .filter(Statement.date >= sunday)
                .filter(Statement.date < sunday + timedelta(days=7))
                .filter(MainCategory.category_type == category_type)
                .group_by(MainCategory.id)
            )

        data = list()
        total_amount = 0
        total_discount = 0
        for category in category_list:
            # statement_list의 [0]번째 값에 해당하는 category 업데이트
            amount = 0
            discount = 0
            for statement in statement_list:
                if category.id == statement[0]:
                    if category_type == 2 and statement[2] < 0:
                        amount = statement[2] * -1
                    else:
                        amount = statement[2]
                    discount = statement[3]
                    break

            total_amount += amount
            total_discount += discount

            data.append(dict(name=category.name, amount=amount, discount=discount))
        data.append(dict(name="합계", amount=total_amount, discount=total_discount))
        return data

    elif mode == 2:
        category_list = (
            db.query(MainCategory)
            .filter(MainCategory.category_type == category_type)
            .all()
        )

        month_start = date.replace(day=1)
        month_end = date.replace(
            day=calendar.monthrange(date.year, date.month)[1]
        ) + timedelta(days=1)

        statement_list = (
            db.query(
                MainCategory.id,
                MainCategory.name,
                func.sum(Statement.amount).label("amount"),
                func.sum(Statement.discount).label("discount"),
            )
            .join(Category, Statement.category_id == Category.id)
            .join(MainCategory)
            .filter(Statement.date >= month_start)
            .filter(Statement.date <= month_end)
            .filter(MainCategory.category_type == category_type)
            .group_by(MainCategory.id)
        )

        data = list()
        total_amount = 0
        total_discount = 0
        for category in category_list:
            # statement_list의 [0]번째 값에 해당하는 category 업데이트
            amount = 0
            discount = 0
            for statement in statement_list:
                if category.id == statement[0]:
                    if category_type == 2 and statement[2] < 0:
                        amount = statement[2] * -1
                    else:
                        amount = statement[2]
                    discount = statement[3]
                    break

            total_amount += amount
            total_discount += discount

            data.append(dict(name=category.name, amount=amount, discount=discount))
        data.append(dict(name="합계", amount=total_amount, discount=total_discount))
        return data

    return


@router.get("/statement/subcategory", summary="카테고리별 합계")
async def statement_subcategory(
    mode: int, date: date, main_category: int, db: Session = Depends(get_db)
):
    # 주간 합계
    if mode == 1:
        # 해당 주의 일요일 구하기
        if date.weekday() == 6:
            sunday = date
        else:
            sunday = date - timedelta(days=date.weekday() + 1)

        category_list = (
            db.query(Category)
            .join(MainCategory)
            .filter(MainCategory.id == main_category)
            .all()
        )

        statement_list = (
            db.query(
                Category.id,
                Category.name,
                func.sum(Statement.amount).label("amount"),
            )
            .join(Category, Statement.category_id == Category.id)
            .join(MainCategory)
            .filter(Statement.date >= sunday)
            .filter(Statement.date < sunday + timedelta(days=7))
            .filter(MainCategory.id == main_category)
            .group_by(Category.id)
        )

        data = list()
        for category in category_list:
            # statement_list의 [0]번째 값에 해당하는 category 업데이트
            amount = 0
            for statement in statement_list:
                if category.id == statement[0]:
                    if category.main_category.category_type == 2 and statement[2] < 0:
                        amount = statement[2] * -1
                    else:
                        amount = statement[2]
                    break

            data.append(dict(name=category.name, amount=amount))
        return data


@router.get("/statement/total", response_model=StatementCategorySumSchema)
async def get_statement_total(mode: int, date: date, db: Session = Depends(get_db)):
    # 주간 합계
    if mode == 1:
        new_date = date.replace(hour=0, minute=0, second=0, microsecond=0)

        # 해당 주의 월요일 구하기
        if new_date.weekday() == 0:
            monday = new_date
        else:
            monday = new_date - timedelta(days=new_date.weekday())

        db.query(Statement).filter(Statement.date >= monday).filter(
            Statement.date <= monday + timedelta(days=6)
        )

    elif mode == 2:
        pass

    # 카테고리별 합계
    elif mode == 3:
        category_sum = (
            db.query(
                MainCategory.category_type,
                func.sum(Statement.amount),
                func.sum(Statement.saving),
            )
            .join(Category, Category.id == Statement.category_id)
            .join(MainCategory)
            .filter(extract("month", Statement.date) == date.month)
            .group_by(MainCategory.category_type)
            .all()
        )

        discount_sum = (
            db.query(func.sum(Statement.discount))
            .filter(extract("month", Statement.date) == date.month)
            .first()
        )

        data = StatementCategorySumSchema()

        for i in category_sum:
            if i[0] == 1:
                data.income = i[1]
            elif i[0] == 2:
                data.expense = i[1]
                data.expense_saving = i[2]
            elif i[0] == 3:
                data.saving = i[1]

        data.discount = discount_sum[0] if discount_sum[0] else 0

        data.total = data.income + data.expense + data.saving + data.discount
        data.total_no_discount = data.income + data.expense + data.saving

        return data
    return


@router.get("/statement/name_list")
async def get_statement_name_list(q: str = Query(...), db: Session = Depends(get_db)):
    query = db.query(Statement).filter(Statement.name.ilike(f"%{q}%"))

    query = query.with_entities(Statement.name).distinct()
    name_dict = list()
    [name_dict.append(dict(name=i[0])) for i in query.all()]

    return name_dict


@router.get("/statement/calendar")
async def get_statement_calendar(date: date, db: Session = Depends(get_db)):
    sub_query = (
        select(Statement, MainCategory.category_type)
        .select_from(Statement)
        .join(Category, Statement.category_id == Category.id)
        .join(MainCategory)
        .filter(extract("year", Statement.date) == date.year)
        .filter(extract("month", Statement.date) == date.month)
        .subquery()
    )

    query = (
        select(
            extract("day", sub_query.c.created_at).label("day"),
            sub_query.c.category_type,
            func.sum(sub_query.c.amount),
        )
        .select_from(sub_query)
        .group_by("day", sub_query.c.category_type)
    )

    return db.execute(query).all()


@router.get("/statement/{id}")
async def get_statement(id: int, db: Session = Depends(get_db)):
    return db.query(Statement).filter(Statement.id == id).first()


@router.put("/statement/{id}")
async def update_statement(
    id: int,
    statement_in: StatementIn,
    db: Session = Depends(get_db),
):
    statement = db.query(Statement).filter(Statement.id == id).first()
    statement.name = statement_in.name
    statement.category_id = statement_in.category_id
    statement.account_card_id = statement_in.account_card_id
    statement.amount = statement_in.amount
    statement.discount = statement_in.discount

    if statement.category.main_category.category_type != TYPE_INCOME:
        if statement_in.amount > 0:
            statement.amount *= -1

    statement.date = statement_in.date
    statement.saving = statement_in.saving
    statement.description = statement_in.description
    statement.is_fixed = statement_in.is_fixed
    db.commit()
    db.refresh(statement)
    return statement


@router.delete("/statement/{id}")
async def delete_statement(id: int, db: Session = Depends(get_db)):
    statement = db.query(Statement).filter(Statement.id == id).first()

    if statement.asset_id is not None:
        asset = db.query(Asset).filter(Asset.id == statement.asset_id).first()
        if statement.amount < 0:
            asset.amount += statement.amount
        else:
            asset.amount -= statement.amount
        db.commit()
        db.refresh(asset)

    if statement.loan_id is not None:
        loan = db.query(Loan).filter(Loan.id == statement.loan_id).first()
        loan.amount -= statement.amount  # 이미 - 처리 되어있음
        db.commit()
        db.refresh(loan)

    db.delete(statement)
    db.commit()
    return {"message": "Statement deleted successfully"}


@router.post("/statement/{id}/message")
async def create_statement_message(
    id: int,
    db: Session = Depends(get_db),
):
    statement = db.query(Statement).filter(Statement.id == id).first()

    if statement is None:
        raise HTTPException(status_code=404, detail="Statement not found")

    message = convert_message(db, statement)

    return message


@router.post("/statement/{id}/alert")
async def create_statement_alert(
    id: int,
    db: Session = Depends(get_db),
):
    statement = db.query(Statement).filter(Statement.id == id).first()

    if statement is None:
        raise HTTPException(status_code=404, detail="Statement not found")

    message = convert_message(db, statement)
    push_notification(message)

    return ""
