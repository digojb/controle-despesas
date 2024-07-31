from flask import Flask, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'
db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(200), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('expenses', lazy=True))
    is_income = db.Column(db.Boolean, nullable=False)  # Campo para indicar se é entrada (True) ou saída (False)

    @staticmethod
    def total_expenses_by_category(category_id):
        total = db.session.query(db.func.sum(Expense.amount)).filter_by(category_id=category_id, is_income=False).scalar()
        return total if total else 0.0

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('budgets', lazy=True))

    @staticmethod
    def get_budget_for_category(category_id):
        budget = Budget.query.filter_by(category_id=category_id).first()
        return budget.amount if budget else 0.0
