from flask import render_template, redirect, url_for, flash, request
from app.main import bp
from app.models import Expense, Income
from app import db
from flask_login import login_required, current_user
from datetime import datetime

@bp.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('index.html', title='ברוכים הבאים')
    
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).limit(5).all()
    incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).limit(5).all()
    
    total_expenses = db.session.query(db.func.sum(Expense.amount)).filter_by(user_id=current_user.id).scalar() or 0
    total_income = db.session.query(db.func.sum(Income.amount)).filter_by(user_id=current_user.id).scalar() or 0
    balance = total_income - total_expenses
    
    return render_template('index.html', title='דף הבית',
                         expenses=expenses, incomes=incomes,
                         total_expenses=total_expenses,
                         total_income=total_income,
                         balance=balance)

@bp.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    if request.method == 'POST':
        expense = Expense(
            amount=float(request.form['amount']),
            category=request.form['category'],
            description=request.form['description'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
            user_id=current_user.id
        )
        db.session.add(expense)
        db.session.commit()
        flash('ההוצאה נוספה בהצלחה')
        return redirect(url_for('main.expenses'))

    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    return render_template('expenses.html', title='הוצאות', expenses=expenses)

@bp.route('/income', methods=['GET', 'POST'])
@login_required
def income():
    if request.method == 'POST':
        income = Income(
            amount=float(request.form['amount']),
            source=request.form['source'],
            description=request.form['description'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
            user_id=current_user.id
        )
        db.session.add(income)
        db.session.commit()
        flash('ההכנסה נוספה בהצלחה')
        return redirect(url_for('main.income'))

    incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).all()
    return render_template('income.html', title='הכנסות', incomes=incomes)

@bp.route('/report')
@login_required
def report():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    incomes = Income.query.filter_by(user_id=current_user.id).all()
    
    total_expenses = sum(expense.amount for expense in expenses)
    total_income = sum(income.amount for income in incomes)
    balance = total_income - total_expenses
    
    # Group expenses by category
    expenses_by_category = {}
    for expense in expenses:
        if expense.category in expenses_by_category:
            expenses_by_category[expense.category] += expense.amount
        else:
            expenses_by_category[expense.category] = expense.amount
    
    return render_template('report.html', title='דוחות',
                         expenses=expenses,
                         incomes=incomes,
                         total_expenses=total_expenses,
                         total_income=total_income,
                         balance=balance,
                         expenses_by_category=expenses_by_category)
