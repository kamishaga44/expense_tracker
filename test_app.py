import pytest

from app import app, db, Expense


@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        yield app.test_client()

        db.session.remove()
        db.drop_all()


def add_expense(client, title="Продукты", amount="2500",
                category="Продукты", expense_date="2026-10-12"):
    return client.post(
        "/",
        data={
            "title": title,
            "amount": amount,
            "category": category,
            "expense_date": expense_date,
        },
        follow_redirects=True,
    )


def test_home_page_opens(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Мои расходы".encode() in response.data


def test_add_expense(client):
    response = add_expense(client)

    assert response.status_code == 200
    assert "Продукты".encode() in response.data

    expense = db.session.execute(
        db.select(Expense)
    ).scalars().first()

    assert expense is not None
    assert expense.amount == 2500


def test_total_calculation(client):
    add_expense(client, title="Продукты", amount="2500")
    response = add_expense(
        client,
        title="Транспорт",
        amount="500",
        category="Транспорт",
    )

    assert b"3000.00" in response.data


def test_reject_invalid_amount(client):
    response = add_expense(client, amount="-100")

    assert "Сумма должна быть больше нуля.".encode() in response.data

    expenses = db.session.execute(
        db.select(Expense)
    ).scalars().all()

    assert len(expenses) == 0


def test_reject_empty_title(client):
    response = add_expense(client, title="   ")

    assert "Введите название до 150 символов.".encode() in response.data

    expenses = db.session.execute(
        db.select(Expense)
    ).scalars().all()

    assert len(expenses) == 0


def test_reject_invalid_category(client):
    response = add_expense(client, category="Несуществующая категория")

    assert "Выберите категорию из списка.".encode() in response.data

    expenses = db.session.execute(
        db.select(Expense)
    ).scalars().all()

    assert len(expenses) == 0


def test_date_filter(client):
    add_expense(
        client,
        title="Январь",
        amount="1000",
        expense_date="2026-01-10",
    )
    add_expense(
        client,
        title="Февраль",
        amount="2000",
        expense_date="2026-02-10",
    )

    response = client.get(
        "/?start_date=2026-02-01&end_date=2026-02-28"
    )

    assert "Февраль".encode() in response.data
    assert "Январь".encode() not in response.data
    assert b"2000.00" in response.data


def test_delete_expense(client):
    add_expense(client)

    expense = db.session.execute(
        db.select(Expense)
    ).scalars().first()

    response = client.post(
        f"/delete/{expense.id}",
        follow_redirects=True,
    )

    assert response.status_code == 200

    remaining = db.session.execute(
        db.select(Expense)
    ).scalars().all()

    assert len(remaining) == 0


def test_edit_expense(client):
    add_expense(client)

    expense = db.session.execute(
        db.select(Expense)
    ).scalars().first()

    response = client.post(
        f"/edit/{expense.id}",
        data={
            "title": "Новые продукты",
            "amount": "3500",
            "category": "Дом",
            "expense_date": "2026-10-11",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    updated = db.session.get(Expense, expense.id)

    assert updated.title == "Новые продукты"
    assert updated.amount == 3500
    assert updated.category == "Дом"
    assert updated.expense_date.isoformat() == "2026-10-11"


def test_edit_page_opens(client):
    add_expense(client)

    expense = db.session.execute(
        db.select(Expense)
    ).scalars().first()

    response = client.get(f"/edit/{expense.id}")

    assert response.status_code == 200
    assert "Редактировать расход".encode() in response.data


def test_delete_unknown_expense(client):
    response = client.post("/delete/999", follow_redirects=True)

    assert response.status_code == 404
