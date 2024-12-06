from flask import render_template, flash, redirect, url_for, request
from app.main import bp
from app import db
from app.models import Expense, Income
from datetime import datetime

@bp.route('/')
@bp.route('/index')
def index():
    # מקבל את סיכום ההוצאות וההכנסות האחרונות
    expenses = Expense.query.order_by(Expense.date.desc()).limit(5).all()
    incomes = Income.query.order_by(Income.date.desc()).limit(5).all()
    total_expenses = sum(expense.amount for expense in Expense.query.all())
    total_income = sum(income.amount for income in Income.query.all())
    balance = total_income - total_expenses
    
    return render_template('index.html', title='בית',
                         expenses=expenses, incomes=incomes,
                         total_expenses=total_expenses,
                         total_income=total_income,
                         balance=balance)

@bp.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if request.method == 'POST':
        expense = Expense(
            amount=float(request.form['amount']),
            category=request.form['category'],
            description=request.form['description'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d')
        )
        db.session.add(expense)
        db.session.commit()
        flash('ההוצאה נשמרה בהצלחה!')
        return redirect(url_for('main.expenses'))
    
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('expenses.html', title='ניהול הוצאות', expenses=expenses)

@bp.route('/income', methods=['GET', 'POST'])
def income():
    if request.method == 'POST':
        income = Income(
            amount=float(request.form['amount']),
            source=request.form['source'],
            description=request.form['description'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d')
        )
        db.session.add(income)
        db.session.commit()
        flash('ההכנסה נשמרה בהצלחה!')
        return redirect(url_for('main.income'))
    
    incomes = Income.query.order_by(Income.date.desc()).all()
    return render_template('income.html', title='ניהול הכנסות', incomes=incomes)

@bp.route('/report')
def report():
    expenses = Expense.query.all()
    incomes = Income.query.all()
    
    # מחשב סיכומים לפי קטגוריה
    expenses_by_category = {}
    for expense in expenses:
        expenses_by_category[expense.category] = expenses_by_category.get(expense.category, 0) + expense.amount
    
    total_expenses = sum(expense.amount for expense in expenses)
    total_income = sum(income.amount for income in incomes)
    balance = total_income - total_expenses
    
    return render_template('report.html', title='דוחות',
                         expenses_by_category=expenses_by_category,
                         total_expenses=total_expenses,
                         total_income=total_income,
                         balance=balance)
