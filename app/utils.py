import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from sqlalchemy import func, extract, select
from sqlalchemy.orm import Session
from models import Asset, AssetHistory, Loan, Statement, Category, MainCategory
from app.consts import TYPE_OUTCOME, TYPE_SAVING, TYPE_INCOME, CURRENT_TIMEZONE


load_dotenv()


def new_asset_history(db):
    # asset의 sum 구하기
    asset_sum = db.query(func.sum(Asset.amount)).scalar()

    # loan의 sum 구하기
    loan_sum = db.query(func.sum(Loan.amount)).scalar()

    # asset history 생성
    new_asset_history = AssetHistory(
        amount=asset_sum - loan_sum,
        timestamp=func.now(),
    )
    db.add(new_asset_history)
    db.commit()
    db.refresh(new_asset_history)


def convert_message(db: Session, statement):
    now = datetime.now(CURRENT_TIMEZONE)
    message = ""
    date = statement.date.strftime("%Y/%m/%d %H:%M")

    format1 = "{:,}"
    format2 = "{:.2f}"

    amount = format1.format(
        statement.amount if statement.amount > 0 else statement.amount * -1
    )
    discount = format1.format(statement.discount)
    discount_percent = format2.format(statement.discount / statement.amount * -100)
    account_card = (
        statement.account_card.name if statement.account_card_id is not None else "없음"
    )

    sum_query = (
        select(func.sum(Statement.amount))
        .select_from(Statement)
        .join(Category, Statement.category_id == Category.id)
        .join(MainCategory)
        .filter(extract("year", Statement.date) == now.year)
        .filter(extract("month", Statement.date) == now.month)
        .filter(
            MainCategory.category_type == statement.category.main_category.category_type
        )
    )
    sum_query = db.execute(sum_query).first()

    if sum_query[0] is None:
        type_sum = 0

    elif sum_query[0] < 0:
        type_sum = sum_query[0] * -1

    else:
        type_sum = sum_query[0]

    if statement.category.main_category.category_type == TYPE_INCOME:
        message = (
            f"💵수입\n[{statement.category.main_category.name}-{statement.category.name}]"
            f"\n{statement.name}\n{amount}원"
            f"\n{account_card}"
            f"\n{date}"
            f"\n월 수입 {format1.format(type_sum)}원"
        )

    elif statement.category.main_category.category_type == TYPE_OUTCOME:
        if statement.category.main_category.weekly_limit is not None:
            # 지출한 주의 날짜 구하기
            sunday = statement.date - timedelta(days=statement.date.weekday() + 1)
            sunday = sunday.replace(hour=0, minute=0, second=0, microsecond=0)
            saturday = sunday + timedelta(days=7)
            saturday = saturday.replace(hour=23, minute=59, second=59, microsecond=0)

            weekly_sum_amount_query = (
                select(func.sum(Statement.amount), func.sum(Statement.discount))
                .select_from(Statement)
                .join(Category, Statement.category_id == Category.id)
                .filter(Statement.date >= sunday)
                .filter(Statement.date <= saturday)
                .filter(
                    Category.main_category_id == statement.category.main_category_id
                )
            )
            weekly_sum_amount_query = db.execute(weekly_sum_amount_query).first()

            weekly_sum_amount = 0
            if weekly_sum_amount_query[0] is None:
                pass
            else:
                weekly_sum_amount = (
                    statement.category.main_category.weekly_limit
                    + weekly_sum_amount_query[0]
                    + weekly_sum_amount_query[1]
                )

            message = (
                f"💳지출\n[{statement.category.main_category.name}-{statement.category.name}]"
                f"\n{statement.name}\n{amount}원 (할인 {discount}원 {discount_percent}%)"
                f"\n{account_card}"
                f"\n{format1.format(weekly_sum_amount)}원 남음"
                f"\n{date}"
                f"\n월 지출 {format1.format(type_sum)}원"
            )
        else:
            message = (
                f"💳지출\n[{statement.category.main_category.name}-{statement.category.name}]"
                f"\n{statement.name}\n{amount}원 (할인 {discount}원 {discount_percent}%)"
                f"\n{account_card}"
                f"\n{date}"
                f"\n월 지출 {format1.format(type_sum)}원"
            )

    elif statement.category.main_category.category_type == TYPE_SAVING:
        message = (
            f"💰저축\n[{statement.category.main_category.name}-{statement.category.name}]"
            f"\n{statement.name}\n{amount}원"
            f"\n{account_card}"
            f"\n{date}"
            f"\n월 저축 {format1.format(type_sum)}원"
        )

    return message


def push_notification(message):
    url = "https://api.telegram.org/bot{}/sendMessage".format(
        os.getenv("TELEGRAM_TOKEN")
    )

    try:
        headers = {"Content-Type": "application/json; charset=utf-8"}
        r1 = requests.post(
            url,
            data=json.dumps(
                {"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": message}
            ),
            headers=headers,
        )

    except Exception as e:
        print(e)
        print("텔레그램 메시지 전송 실패")
