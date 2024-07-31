from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Category, Expense, Budget, app
from datetime import datetime
from datetime import datetime, timedelta
from datetime import date, datetime, timedelta
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify


@app.route('/')
def index():
    categories = Category.query.all()
    expenses = Expense.query.all()
    budgets = Budget.query.all()

    total_income = db.session.query(db.func.sum(Expense.amount)).filter_by(is_income=True).scalar() or 0.0
    total_expense = db.session.query(db.func.sum(Expense.amount)).filter_by(is_income=False).scalar() or 0.0
    total_balance = total_income - total_expense

    # Prepare data for the pie chart
    category_expense_data = []
    for category in categories:
        total_expenses = Expense.total_expenses_by_category(category.id)
        if total_expenses > 0:
            category_expense_data.append({
                'category': category.name,
                'total_expenses': total_expenses
            })

    alerts = []
    for category in categories:
        total_expenses = Expense.total_expenses_by_category(category.id)
        budget = Budget.get_budget_for_category(category.id)
        if budget and total_expenses > budget:
            alerts.append(f"Atenção! Você ultrapassou o orçamento para a categoria {category.name}. Orçamento: {budget}, Gastos: {total_expenses}")

    category_expense_data_json = json.dumps(category_expense_data)

    return render_template('index.html', categories=categories, expenses=expenses, budgets=budgets, 
                           total_income=total_income, total_expense=total_expense, total_balance=total_balance, 
                           alerts=alerts, category_expense_data_json=category_expense_data_json)


@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash('Despesa excluída com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/add_category', methods=['POST'])
def add_category():
    data = request.get_json()
    name = data.get('name')
    if name:
        new_category = Category(name=name)
        db.session.add(new_category)
        db.session.commit()
        return jsonify(success=True, category={'id': new_category.id, 'name': new_category.name})
    return jsonify(success=False)

@app.route('/delete_budgets', methods=['POST'])
def delete_budgets():
    budget_ids = request.form.getlist('budget_ids')
    for budget_id in budget_ids:
        budget = Budget.query.get(budget_id)
        db.session.delete(budget)
    db.session.commit()
    return redirect(url_for('set_budget'))

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        amount = request.form['amount']
        date = request.form['date']
        description = request.form['description']
        category_id = request.form.get('category', type=int)
        is_income = request.form['is_income'] == 'true'

        new_expense = Expense(amount=amount, date=datetime.strptime(date, '%Y-%m-%d'), description=description, category_id=category_id, is_income=is_income)
        db.session.add(new_expense)
        db.session.commit()

        # Verificar se o orçamento foi ultrapassado (apenas para despesas)
        if not is_income:
            total_expenses = Expense.total_expenses_by_category(category_id)
            budget = Budget.get_budget_for_category(category_id)
            if total_expenses > budget:
                flash(f"Atenção! Você ultrapassou o orçamento para a categoria '{Category.query.get(category_id).name}'. Orçamento: {budget}, Gastos: {total_expenses}", 'warning')

        return redirect(url_for('index'))

    categories = Category.query.all()
    return render_template('add_expense.html', categories=categories)


@app.route('/view_expenses', methods=['GET', 'POST'])
def view_expenses():
    today = datetime.today().date()
    if request.method == 'POST':
        month = int(request.form.get('month'))
        year = int(request.form.get('year'))
        start_date = date(year, month, 1)
    else:
        start_date = today.replace(day=1)
        month = start_date.month
        year = start_date.year

    # Calculate the last day of the month
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    expenses = Expense.query.filter(Expense.date >= start_date, Expense.date < end_date).order_by(Expense.date.desc()).all()
    return render_template('view_expenses.html', expenses=expenses, start_date=start_date)



@app.route('/set_budget', methods=['GET', 'POST'])
def set_budget():
    if request.method == 'POST':
        amount = request.form['amount']
        category_id = request.form['category']
        budget = Budget(amount=amount, category_id=category_id)
        db.session.add(budget)
        db.session.commit()
        return redirect(url_for('set_budget'))
    
    categories = Category.query.all()
    budgets = Budget.query.all()
    return render_template('set_budget.html', categories=categories, budgets=budgets)

if __name__ == '__main__':
    app.run(debug=True)
