from datetime import date

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os


load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///expenses.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
csrf = CSRFProtect(app)


CATEGORIES = [
    "Продукты",
    "Транспорт",
    "Дом",
    "Здоровье",
    "Развлечения",
    "Другое",
]


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    expense_date = db.Column(db.Date, nullable=False, default=date.today)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        amount_text = request.form.get("amount", "").strip()
        category = request.form.get("category", "")
        date_text = request.form.get("expense_date", "")

        try:
            amount = float(amount_text)
        except (ValueError, TypeError):
            amount = 0

        try:
            expense_date = date.fromisoformat(date_text)
        except (ValueError, TypeError):
            expense_date = None

        if not title or len(title) > 150:
            flash("Введите название до 150 символов.")
        elif amount <= 0:
            flash("Сумма должна быть больше нуля.")
        elif category not in CATEGORIES:
            flash("Выберите категорию из списка.")
        elif expense_date is None:
            flash("Укажите корректную дату.")
        else:
            expense = Expense(
                title=title,
                amount=amount,
                category=category,
                expense_date=expense_date,
            )
            db.session.add(expense)
            db.session.commit()
            flash("Расход добавлен.")
            return redirect(url_for("index"))

    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    query = db.select(Expense)

    if start_date:
        try:
            query = query.where(
                Expense.expense_date >= date.fromisoformat(start_date)
            )
        except ValueError:
            flash("Начальная дата указана некорректно.")
            start_date = ""

    if end_date:
        try:
            query = query.where(
                Expense.expense_date <= date.fromisoformat(end_date)
            )
        except ValueError:
            flash("Конечная дата указана некорректно.")
            end_date = ""

    expenses = db.session.execute(
        query.order_by(Expense.expense_date.desc(), Expense.id.desc())
    ).scalars().all()

    total = sum(expense.amount for expense in expenses)
    category_totals = {}

    for expense in expenses:
        category_totals[expense.category] = (
                category_totals.get(expense.category, 0) + expense.amount
        )

    category_totals = sorted(
        category_totals.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    max_category_total = max(
        (amount for _, amount in category_totals),
        default=0,
    )

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        categories=CATEGORIES,
        today=date.today().isoformat(),
        start_date=start_date,
        end_date=end_date,
        category_totals=category_totals,
        max_category_total=max_category_total,
    )

@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):
    expense = db.get_or_404(Expense, expense_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        amount_text = request.form.get("amount", "").strip()
        category = request.form.get("category", "")
        date_text = request.form.get("expense_date", "")

        try:
            amount = float(amount_text)
        except (ValueError, TypeError):
            amount = 0

        try:
            expense_date = date.fromisoformat(date_text)
        except (ValueError, TypeError):
            expense_date = None

        if not title or len(title) > 150:
            flash("Введите название до 150 символов.")
        elif amount <= 0:
            flash("Сумма должна быть больше нуля.")
        elif category not in CATEGORIES:
            flash("Выберите категорию из списка.")
        elif expense_date is None:
            flash("Укажите корректную дату.")
        else:
            expense.title = title
            expense.amount = amount
            expense.category = category
            expense.expense_date = expense_date
            db.session.commit()
            flash("Расход обновлён.")
            return redirect(url_for("index"))

    return render_template(
        "edit_expense.html",
        expense=expense,
        categories=CATEGORIES,
    )

@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    expense = db.get_or_404(Expense, expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash("Расход удалён.")
    return redirect(url_for("index"))


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=False)