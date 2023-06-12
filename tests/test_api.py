import pytest
import datetime
from . import client, app, override_get_db
from models import MainCategory, Category, Statement, Asset, Loan
from app.consts import TYPE_OUTCOME


def test_create_main_category():
    response = client.post(
        "/api/main-category",
        json={"name": "test", "category_type": 1, "weekly_limit": 100000},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "test"


def test_get_main_categories():
    response = client.get("/api/main-category")
    assert response.status_code == 200
    assert response.json()["items"][0]["name"] == "test"


def test_get_main_category():
    response = client.get("/api/main-category/1")
    assert response.status_code == 200
    assert response.json()["name"] == "test"


def test_update_main_category():
    response = client.put(
        "/api/main-category/1",
        json={"id": 1, "name": "test", "category_type": 1, "weekly_limit": 125000},
    )
    assert response.status_code == 200
    assert response.json()["weekly_limit"] == 125000


def test_get_main_category_all():
    response = client.get("/api/main-category/all")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "test"


def test_delete_main_category():
    response = client.delete("/api/main-category/1")
    assert response.status_code == 200

    db = next(override_get_db())
    assert db.query(MainCategory).count() == 0


def test_create_category():
    create_response = client.post(
        "/api/main-category",
        json={"name": "test", "category_type": 1, "weekly_limit": 100000},
    )

    assert create_response.status_code == 200
    assert create_response.json()["name"] == "test"

    response = client.post(
        "/api/category",
        json={"name": "test", "main_category_id": 1},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "test"


def test_get_categories():
    response = client.get("/api/category")
    assert response.status_code == 200
    assert response.json()["items"][0]["name"] == "test"


def test_get_category():
    response = client.get("/api/category/1")
    assert response.status_code == 200
    assert response.json()["name"] == "test"


def test_update_category():
    response = client.put(
        "/api/category/1",
        json={"id": 1, "name": "test2", "main_category_id": 1},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "test2"


def test_delete_category():
    response = client.delete("/api/category/1")
    assert response.status_code == 200

    db = next(override_get_db())
    assert db.query(Category).count() == 0


def test_create_statement():
    db = next(override_get_db())

    # 지출 카테고리 추가
    db.add(MainCategory(name="생활비", category_type=2, weekly_limit=100000))
    db.commit()

    main_category = db.query(MainCategory).filter(MainCategory.name == "생활비").first()

    db.add(Category(name="test", main_category_id=main_category.id))
    db.commit()
    category = next(override_get_db()).query(Category).first()

    data = {
        "name": "지출1",
        "category_id": category.id,
        "amount": 10000,
        "date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "description": "test",
        "saving": 0,
        "discount": 0,
        "asset_id": None,
        "account_card_id": None,
        "loan_id": None,
        "is_alert": False,
    }

    response = client.post("/api/statement", json=data)

    print(response.json())

    assert response.status_code == 200
    assert response.json()["name"] == "지출1"
    assert response.json()["amount"] == -data["amount"]  # 지출은 -로 저장됨

    # asset_id가 있는 경우
    db.add(Asset(name="테스트 자산", asset_type=1, amount=100000))
    db.commit()

    asset = db.query(Asset).first()
    assert asset.amount == 100000

    data["asset_id"] = asset.id

    response = client.post("/api/statement", json=data)
    assert response.status_code == 200
    db.refresh(asset)
    assert asset.amount == 90000

    # asset_id와 discount이 있는 경우
    data["discount"] = 1000
    response = client.post("/api/statement", json=data)
    assert response.status_code == 200
    db.refresh(asset)
    assert asset.amount == 81000

    # loan_id가 있는 경우
    db.add(
        Loan(
            name="테스트 대출", principal=100000, interest_rate=5, total_months=12, amount=0
        )
    )
    db.commit()

    loan = db.query(Loan).first()
    assert loan.amount == 100000

    # 500,000원중 300,000원이 대출원금상환
    data["loan_id"] = loan.id
    data["amount"] = 500000
    data["saving"] = 300000
    data["asset_id"] = None
