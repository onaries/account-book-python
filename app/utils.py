from datetime import datetime
from sqlalchemy import func
from models import Asset, AssetHistory, Loan


def new_asset_history(db):
    # asset의 sum 구하기
    asset_sum = db.query(func.sum(Asset.amount)).scalar()

    # loan의 sum 구하기
    loan_sum = db.query(func.sum(Loan.amount)).scalar()

    # asset history 생성
    new_asset_history = AssetHistory(
        amount=asset_sum - loan_sum,
        timestamp=datetime.now(),
    )
    db.add(new_asset_history)
    db.commit()
    db.refresh(new_asset_history)
